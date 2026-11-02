<script setup>
// A ```python run block with "Run", "Edit" and "Reset" buttons. The code runs in
// the browser with Pyodide (see pyRunner.js); print() output, the value of the last
// line and matplotlib figures are shown under the block. The buttons are in
// Bulgarian on the /bg/ pages. Same CSS classes as the kit's RunCode.
import { ref, computed, nextTick } from 'vue'
import { useData } from 'vitepress'
import { runPython } from './pyRunner.js'

const props = defineProps({ code: { type: String, required: true } })

const TEXT = {
  en: { run: 'Run', edit: 'Edit', done: 'Done', reset: 'Reset', empty: '(no output)',
        loading: 'loading Python (the first time takes a few seconds)...', packages: 'loading packages...', running: 'running...',
        slow: 'still loading Python - the network is slow...',
        runTitle: 'Run (Ctrl+Enter while editing)', hintEdit: 'Ctrl+Enter runs the code', hint: 'Edit the code and run it again',
        figure: 'Figure' },
  bg: { run: 'Изпълни', edit: 'Промени', done: 'Готово', reset: 'Върни', empty: '(няма изход)',
        loading: 'зарежда се Python (първия път отнема няколко секунди)...', packages: 'зареждат се пакети...', running: 'изпълнява се...',
        slow: 'Python все още се зарежда - мрежата е бавна...',
        runTitle: 'Изпълни (Ctrl+Enter при промяна)', hintEdit: 'Ctrl+Enter изпълнява кода', hint: 'Променете кода и го изпълнете отново',
        figure: 'Графика' }
}

// What went wrong and what to do (pyRunner.js names the problem; {detail} = its detail)
const RUN_LOCALLY = {
  en: 'Until then, copy the example and run it in VS Code or Jupyter on your computer, in the folder of your Homework repository (the data/ folder is there).',
  bg: 'Дотогава копирайте примера и го изпълнете във VS Code или Jupyter на компютъра си, в папката на repository-то с домашните (там е папката data/).'
}
const ALLOW_CDN = {
  en: 'Ask your IT team to allow https://cdn.jsdelivr.net/pyodide/. ' + RUN_LOCALLY.en,
  bg: 'Помолете IT отдела да разреши https://cdn.jsdelivr.net/pyodide/. ' + RUN_LOCALLY.bg
}
const PROBLEMS = {
  en: {
    noWasm: 'Python cannot start: WebAssembly is switched off in this browser (for example, by the "enhanced security" mode of Microsoft Edge or by a company policy). Allow it for this site, or use another browser.',
    offline: 'Python could not be loaded: this computer is offline. Connect to the internet and click Run again.',
    blocked: 'Python could not be loaded: the network stops these files from cdn.jsdelivr.net: {detail}. A firewall, a proxy or a browser extension (for example, an ad blocker) blocks them. ' + ALLOW_CDN.en,
    stdlib: 'Python could not be loaded: its standard library (python_stdlib.zip from cdn.jsdelivr.net) did not arrive complete. A proxy or a virus scanner on the network probably changes it. ' + ALLOW_CDN.en,
    timeout: 'Python did not start in 5 minutes: the network is very slow, or a proxy changes the files on the way. Reload the page and try again. If it happens again: ' + ALLOW_CDN.en,
    packages: 'These packages could not be loaded: {detail}. The network stops their files (.whl) from cdn.jsdelivr.net. ' + ALLOW_CDN.en,
    pypi: 'openpyxl (needed for Excel files) could not be installed from PyPI ({detail}). The network probably blocks pypi.org or files.pythonhosted.org. Ask your IT team to allow them. ' + RUN_LOCALLY.en,
    data: 'Python started, but the sample data could not be loaded ({detail}). Reload the page and click Run again.',
    other: 'Python could not be loaded ({detail}). Reload the page and click Run again. If it happens again: press F12, open "Console" and send the red and yellow lines to your trainer.',
    runner: 'The example could not run ({detail}). Reload the page and click Run again.'
  },
  bg: {
    noWasm: 'Python не може да стартира: WebAssembly е изключен в този браузър (например от режима "enhanced security" на Microsoft Edge или от фирмена политика). Разрешете го за този сайт или ползвайте друг браузър.',
    offline: 'Python не се зареди: компютърът няма връзка с интернет. Свържете се и натиснете "Изпълни" отново.',
    blocked: 'Python не се зареди: мрежата спира тези файлове от cdn.jsdelivr.net: {detail}. Спира ги защитна стена (firewall), прокси или разширение на браузъра (например блокер на реклами). ' + ALLOW_CDN.bg,
    stdlib: 'Python не се зареди: стандартната му библиотека (python_stdlib.zip от cdn.jsdelivr.net) не пристигна цяла. Вероятно прокси или антивирусна програма в мрежата я променя. ' + ALLOW_CDN.bg,
    timeout: 'Python не стартира за 5 минути: мрежата е много бавна или прокси променя файловете по пътя. Презаредете страницата и опитайте отново. Ако се повтори: ' + ALLOW_CDN.bg,
    packages: 'Тези пакети не се заредиха: {detail}. Мрежата спира файловете им (.whl) от cdn.jsdelivr.net. ' + ALLOW_CDN.bg,
    pypi: 'openpyxl (нужен за Excel файловете) не се инсталира от PyPI ({detail}). Вероятно мрежата спира pypi.org или files.pythonhosted.org. Помолете IT отдела да ги разреши. ' + RUN_LOCALLY.bg,
    data: 'Python стартира, но примерните данни не се заредиха ({detail}). Презаредете страницата и натиснете "Изпълни" отново.',
    other: 'Python не се зареди ({detail}). Презаредете страницата и натиснете "Изпълни" отново. Ако се повтори: натиснете F12, отворете "Console" и изпратете червените и жълтите редове на преподавателя.',
    runner: 'Примерът не можа да се изпълни ({detail}). Презаредете страницата и натиснете "Изпълни" отново.'
  }
}

const { lang } = useData()
const isBg = computed(() => String(lang.value || '').startsWith('bg'))
const t = computed(() => (isBg.value ? TEXT.bg : TEXT.en))

function problemText(line) {
  const texts = isBg.value ? PROBLEMS.bg : PROBLEMS.en
  return (texts[line.problem] || texts.other).replace('{detail}', line.detail || '?')
}

function decode(b64) {
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0))
  return new TextDecoder().decode(bytes).replace(/\n$/, '')
}

const original = decode(props.code)
const source = ref(original)
const editing = ref(false)
const ran = ref(false)
const status = ref('')
const lines = ref([])
const editor = ref(null)
let runId = 0

const changed = computed(() => source.value !== original)
const rows = computed(() => Math.max(3, source.value.split('\n').length + 1))

async function run() {
  const id = ++runId
  lines.value = []
  ran.value = true
  status.value = 'running'
  // output of an earlier run of this block (still in the queue) is dropped
  const write = line => { if (id === runId) lines.value.push(line) }
  const onStatus = s => { if (id === runId) status.value = s }
  await runPython(source.value, write, onStatus)
  if (id === runId) status.value = ''
}

async function toggleEdit() {
  editing.value = !editing.value
  if (editing.value) {
    await nextTick()
    editor.value && editor.value.focus()
  }
}

function reset() {
  runId++
  source.value = original
  lines.value = []
  ran.value = false
  status.value = ''
}

function onKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run() }
  if (e.key === 'Tab') {
    e.preventDefault()
    const el = e.target
    const s = el.selectionStart
    source.value = source.value.slice(0, s) + '    ' + source.value.slice(el.selectionEnd)
    nextTick(() => { el.selectionStart = el.selectionEnd = s + 4 })
  }
}
</script>

<template>
  <div class="run-code" :class="{ editing }">
    <div v-show="!editing && !changed" class="run-code-view"><slot /></div>
    <pre v-show="!editing && changed" class="run-code-plain"><code>{{ source }}</code></pre>
    <textarea
      v-if="editing"
      ref="editor"
      v-model="source"
      class="run-code-editor"
      :rows="rows"
      spellcheck="false"
      @keydown="onKeydown"
    />
    <div class="run-code-bar">
      <button class="run" :title="t.runTitle" @click="run">{{ t.run }}</button>
      <button @click="toggleEdit">{{ editing ? t.done : t.edit }}</button>
      <button v-if="changed || ran" @click="reset">{{ t.reset }}</button>
      <span class="hint">{{ editing ? t.hintEdit : t.hint }}</span>
    </div>
    <div v-if="ran" class="run-code-output py-output">
      <template v-for="(line, i) in lines" :key="i">
        <img v-if="line.kind === 'image'" class="py-figure" :src="'data:image/png;base64,' + line.text" :alt="t.figure + ' ' + (i + 1)">
        <div v-else-if="line.problem" class="error py-problem">{{ problemText(line) }}</div>
        <div v-else :class="line.kind">{{ line.text }}</div>
      </template>
      <div v-if="status" class="empty">{{ t[status] }}</div>
      <div v-else-if="lines.length === 0" class="empty">{{ t.empty }}</div>
    </div>
  </div>
</template>

<style>
/* pandas tables are wide: keep the columns aligned and scroll sideways */
.py-output > div { white-space: pre; }
.py-output { overflow-x: auto; }
.py-output > div.py-problem { white-space: pre-wrap; }   /* a long message wraps */
.py-figure { display: block; max-width: 100%; margin: 8px 0; background: #fff; border-radius: 4px; }
</style>
