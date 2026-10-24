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

export const PYODIDE_VERSION = '314.0.7'
const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`

// the data files, as URLs of the built site (Vite copies them into the build)
const dataFiles = import.meta.glob('../../../data/*', { query: '?url', import: 'default', eager: true })

const DRIVER = `
import base64, io, os, sys, traceback, warnings
os.environ.setdefault("MPLBACKEND", "AGG")
os.environ.setdefault("COLUMNS", "200")   # pandas: print wide tables without "..." (the output scrolls)
warnings.filterwarnings("ignore", message=".*non-interactive.*")

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

async def _course_run(source):
    from pyodide.code import eval_code_async
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

let pyodidePromise = null
let queue = Promise.resolve()

async function startPython(onStatus) {
  onStatus?.('loading')
  const { loadPyodide } = await import(/* @vite-ignore */ INDEX_URL + 'pyodide.mjs')
  const py = await loadPyodide({ indexURL: INDEX_URL })
  py.FS.mkdirTree('/home/pyodide/data')
  for (const [file, url] of Object.entries(dataFiles)) {
    const response = await fetch(url)
    if (!response.ok) throw new Error(`cannot load ${url}: ${response.status}`)
    py.FS.writeFile('/home/pyodide/data/' + file.split('/').pop(), new Uint8Array(await response.arrayBuffer()))
  }
  py.FS.chdir('/home/pyodide')
  await py.runPythonAsync(DRIVER)
  return py
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
 * output line (and every figure, as base64 PNG in text). onStatus('loading' |
 * 'packages' | 'running') tells what is happening.
 */
export function runPython(source, write, onStatus) {
  const job = queue.then(async () => {
    let py
    try {
      py = await python(onStatus)
    } catch (error) {
      write({ kind: 'error', text: `Python could not be loaded (${error.message}). Check the internet connection and try again.` })
      return
    }
    try {
      onStatus?.('packages')
      await py.loadPackagesFromImports(source, { messageCallback: () => {} })
    } catch (error) {
      write({ kind: 'error', text: String(error.message || error) })
    }
    onStatus?.('running')
    py.setStdout({ batched: text => write({ kind: 'log', text }) })
    py.setStderr({ batched: text => write({ kind: 'error', text }) })
    const run = py.globals.get('_course_run')
    const result = await run(source)
    for (const png of result.toJs()) write({ kind: 'image', text: png })
    result.destroy()
    run.destroy()
  })
  queue = job.catch(() => {})
  return job
}
