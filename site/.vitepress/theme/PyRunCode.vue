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
        runTitle: 'Run (Ctrl+Enter while editing)', hintEdit: 'Ctrl+Enter runs the code', hint: 'Edit the code and run it again',
        figure: 'Figure' },
  bg: { run: 'Изпълни', edit: 'Промени', done: 'Готово', reset: 'Върни', empty: '(няма изход)',
        loading: 'зарежда се Python (първия път отнема няколко секунди)...', packages: 'зареждат се пакети...', running: 'изпълнява се...',
        runTitle: 'Изпълни (Ctrl+Enter при промяна)', hintEdit: 'Ctrl+Enter изпълнява кода', hint: 'Променете кода и го изпълнете отново',
        figure: 'Графика' }
}
const { lang } = useData()
const t = computed(() => (String(lang.value || '').startsWith('bg') ? TEXT.bg : TEXT.en))

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
.py-figure { display: block; max-width: 100%; margin: 8px 0; background: #fff; border-radius: 4px; }
</style>
