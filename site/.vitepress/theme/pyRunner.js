// Runs the ```python run examples in the browser with Pyodide (CPython compiled to
// WebAssembly, with numpy, pandas, matplotlib and more). Used by PyRunCode.vue.
//
// - Pyodide is loaded from the CDN on the first Run (about 10 MB; pandas adds more),
//   then cached by the browser. One Python for the whole site.
// - The sample data (Slides/data/*) is copied into Python's file system as data/...,
//   so `pd.read_csv("data/loans.csv")` works like in the Homework repository.
// - Every example runs in its own fresh namespace; the value of a last line that is an
//   expression is printed (like in Jupyter), so `df.head()` shows the table.
// - matplotlib figures are returned as PNG images.
// - Runs are queued: one example runs at a time.
// - When something fails, write() gets { kind: 'error', problem, detail }: a key of
//   PROBLEMS in PyRunCode.vue (which has the text in both languages). Most problems
//   come from networks (firewalls, proxies) that block or change the files of the CDN,
//   so the runner checks those files and names the ones that did not arrive.

import { dataFiles } from './dataFiles.js'   // the files of data/, by name

export const PYODIDE_VERSION = '314.0.7'
const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`

// The files Python needs to start (all from INDEX_URL), with the bytes a real file
// starts with. A proxy that blocks a file often sends its own HTML page instead.
const START_FILES = {
  'pyodide.mjs': '',
  'pyodide.asm.mjs': '',
  'pyodide.asm.wasm': '\0asm',
  'python_stdlib.zip': 'PK',
  'pyodide-lock.json': '{'
}
const SLOW_MS = 20_000      // still loading after this: check the files, say "slow"
const GIVE_UP_MS = 300_000  // Pyodide hangs (no error) when pyodide.asm.wasm is damaged

/** A problem that PyRunCode.vue explains to the student (key = PROBLEMS key). */
class RunProblem extends Error {
  constructor(key, detail = '') {
    super(detail ? `${key}: ${detail}` : key)
    this.key = key
    this.detail = detail
  }
}

/** The last line of an error (a Python traceback ends with the error itself). */
function lastLine(error) {
  const lines = String(error?.message || error).trim().split('\n')
  return lines[lines.length - 1].trim()
}

/** Why one start file does not arrive as it should, or null when it is fine. */
async function checkFile(name) {
  try {
    const response = await fetch(INDEX_URL + name)
    if (!response.ok) return `HTTP ${response.status}`
    const type = response.headers.get('content-type') || ''
    const reader = response.body.getReader()
    const { value = new Uint8Array() } = await reader.read()   // the first bytes are enough
    reader.cancel().catch(() => {})
    const start = String.fromCharCode(...value.subarray(0, 4))
    if (/html/i.test(type) || !start.startsWith(START_FILES[name])) return `replaced by something else (${type || 'no type'})`
    return null
  } catch (error) {
    return `no answer (${error.message})`
  }
}

/** The names of the start files that do not arrive; the details go to the console. */
async function blockedFiles() {
  const names = Object.keys(START_FILES)
  const why = await Promise.all(names.map(checkFile))
  const blocked = names.filter((name, i) => why[i])
  if (blocked.length) {
    console.warn('Python: files that do not arrive from ' + INDEX_URL + ':\n' +
      blocked.map(name => `  ${name}: ${why[names.indexOf(name)]}`).join('\n'))
  }
  return blocked
}

/** Turns a failed start into a RunProblem that says what to do. */
async function explain(error) {
  if (error instanceof RunProblem) return error
  console.warn('Python could not be loaded:', error)
  if (navigator.onLine === false) return new RunProblem('offline')
  const blocked = await blockedFiles()
  if (blocked.length) return new RunProblem('blocked', blocked.join(', '))
  // Python started but could not read its standard library: exit(1) after
  // "Fatal Python error: Failed to import encodings module"
  if (/exit\(1\)/.test(error?.message)) return new RunProblem('stdlib')
  return new RunProblem('other', lastLine(error))
}

/**
 * Watches the start of Python: a failed download of pyodide.asm.wasm makes Pyodide
 * hang without an error, so a failed fetch or a long wait checks the files.
 * `stalled` rejects with a RunProblem when the start will not finish.
 */
function watchStart(onStatus) {
  let reject
  let stopped = false
  const stalled = new Promise((_, r) => { reject = r })
  stalled.catch(() => {})
  const check = async () => {
    const blocked = await blockedFiles()
    if (stopped) return
    if (blocked.length) reject(new RunProblem('blocked', blocked.join(', ')))
    else onStatus?.('slow')
  }
  const onRejection = event => {
    if (/fetch/i.test(String(event.reason?.message ?? event.reason))) check()
  }
  window.addEventListener('unhandledrejection', onRejection)
  const timers = [
    setTimeout(check, SLOW_MS),
    setTimeout(() => reject(new RunProblem('timeout')), GIVE_UP_MS)
  ]
  return {
    stalled,
    stop() {
      stopped = true
      timers.forEach(clearTimeout)
      window.removeEventListener('unhandledrejection', onRejection)
    }
  }
}

const DRIVER = `
import base64, io, os, sys, traceback, warnings
os.environ.setdefault("MPLBACKEND", "AGG")
os.environ.setdefault("COLUMNS", "200")   # pandas: print wide tables without "..." (the output scrolls)
warnings.filterwarnings("ignore", message=".*non-interactive.*")
# savefig() of an example: a deprecation warning inside Pyodide's matplotlib, not the example's fault
warnings.filterwarnings("ignore", message="The [xy] parameter as float was deprecated")

class _LineEnd:
    """sys.stdout that remembers whether the output ends with a new line: the
    batched output of Pyodide shows a line only when it ends, so the runner adds
    the missing one (print(..., end=",") as the last print)."""
    def __init__(self, stream):
        self._stream = stream
        self.open_line = False
    def write(self, text):
        if text:
            self.open_line = not text.endswith(chr(10))
        return self._stream.write(text)
    def __getattr__(self, name):
        return getattr(self._stream, name)

async def _course_openpyxl(source):
    """Pyodide has no openpyxl package: install it from PyPI (micropip) the first
    time an example works with Excel files, so read_excel / to_excel run too.
    micropip itself is loaded by runPython (EXCEL), without its messages. runPython
    calls this first on its own, to tell a blocked PyPI from an error of the example;
    the call in _course_run is then a no-op (it stays for run-examples.mjs)."""
    text = source.lower()
    if not any(word in text for word in ("excel", "openpyxl", ".xlsx")):
        return
    try:
        import openpyxl
    except ImportError:
        import micropip
        await micropip.install("openpyxl")

async def _course_run(source):
    from pyodide.code import eval_code_async
    await _course_openpyxl(source)
    namespace = {"__name__": "__main__"}
    stdout = sys.stdout
    sys.stdout = tracked = _LineEnd(stdout)
    try:
        result = await eval_code_async(source, namespace, filename="<example>")
        if result is not None:
            print(repr(result))
    except BaseException as error:
        # show only the lines of the example, not the ones of this runner
        tb = error.__traceback__
        while tb is not None and tb.tb_frame.f_code.co_filename != "<example>":
            tb = tb.tb_next
        traceback.print_exception(type(error), error, tb)
    finally:
        sys.stdout = stdout
    if tracked.open_line:
        stdout.write(chr(10))   # chr(10): no backslash in this JS string
    images = []
    plt = sys.modules.get("matplotlib.pyplot")
    if plt is not None:
        for number in plt.get_fignums():
            buffer = io.BytesIO()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")   # deprecation warnings of the Agg backend
                plt.figure(number).savefig(buffer, format="png", bbox_inches="tight")
            images.append(base64.b64encode(buffer.getvalue()).decode("ascii"))
        plt.close("all")
    sys.stdout.flush()
    sys.stderr.flush()
    return images
`

// the examples that need openpyxl (the same words as in _course_openpyxl)
const EXCEL = /excel|openpyxl|\.xlsx/i

let pyodidePromise = null
let queue = Promise.resolve()

async function loadCore() {
  const { loadPyodide } = await import(/* @vite-ignore */ INDEX_URL + 'pyodide.mjs')
  return loadPyodide({ indexURL: INDEX_URL })
}

async function startPython(onStatus) {
  if (typeof WebAssembly === 'undefined') throw new RunProblem('noWasm')
  if (navigator.onLine === false) throw new RunProblem('offline')
  onStatus?.('loading')
  const watch = watchStart(onStatus)
  let py
  try {
    py = await Promise.race([loadCore(), watch.stalled])
  } catch (error) {
    throw await explain(error)
  } finally {
    watch.stop()
  }
  py.FS.mkdirTree('/home/pyodide/data')
  for (const [file, url] of Object.entries(dataFiles)) {
    let response
    try {
      response = await fetch(url)
    } catch (error) {
      throw new RunProblem('data', `${file}: ${error.message}`)
    }
    if (!response.ok) throw new RunProblem('data', `${file}: HTTP ${response.status}`)
    py.FS.writeFile('/home/pyodide/data/' + file, new Uint8Array(await response.arrayBuffer()))
  }
  py.FS.chdir('/home/pyodide')
  await py.runPythonAsync(DRIVER)
  return py
}

/** Loads the packages the example imports (and openpyxl for Excel examples). */
async function loadPackages(py, source) {
  const failed = []
  const options = { messageCallback: () => {}, errorCallback: message => failed.push(message) }
  await py.loadPackagesFromImports(source, options)
  if (EXCEL.test(source)) await py.loadPackage('micropip', options)
  if (failed.length) {
    console.warn('Python: packages that could not be loaded:\n' + failed.join('\n'))
    const names = [...new Set(failed.join('\n').match(/(?<=while loading )[\w.-]+/g) ?? [])]
    throw new RunProblem(navigator.onLine === false ? 'offline' : 'packages', names.join(', ') || lastLine(failed[0]))
  }
  if (EXCEL.test(source)) {
    const install = py.globals.get('_course_openpyxl')
    try {
      await install(source)
    } catch (error) {
      console.warn('Python: openpyxl could not be installed:', error)
      throw new RunProblem('pypi', lastLine(error))
    } finally {
      install.destroy()
    }
  }
}

function python(onStatus) {
  pyodidePromise ??= startPython(onStatus).catch(error => {
    pyodidePromise = null // try again on the next Run
    throw error
  })
  return pyodidePromise
}

/**
 * Runs one example. write({ kind: 'log' | 'error' | 'image', text }) gets every
 * output line (and every figure, as base64 PNG in text); a problem comes as
 * write({ kind: 'error', problem, detail }) (see the top of this file).
 * onStatus('loading' | 'slow' | 'packages' | 'running') tells what is happening.
 * The returned promise never rejects.
 */
export function runPython(source, write, onStatus) {
  const job = queue.then(async () => {
    try {
      const py = await python(onStatus)
      py.setStdout({ batched: text => write({ kind: 'log', text }) })
      py.setStderr({ batched: text => write({ kind: 'error', text }) })
      onStatus?.('packages')
      await loadPackages(py, source)
      onStatus?.('running')
      const run = py.globals.get('_course_run')
      try {
        const result = await run(source)
        for (const png of result.toJs()) write({ kind: 'image', text: png })
        result.destroy()
      } finally {
        run.destroy()
      }
    } catch (error) {
      if (!(error instanceof RunProblem)) console.warn('Python:', error)
      const problem = error instanceof RunProblem ? error : new RunProblem('runner', lastLine(error))
      write({ kind: 'error', problem: problem.key, detail: problem.detail })
    }
  })
  queue = job
  return job
}
