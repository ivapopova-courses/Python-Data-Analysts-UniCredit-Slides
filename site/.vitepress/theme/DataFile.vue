<script setup>
// The name of a sample data file, data/<file>, as a button that opens a preview of
// the file in a dialog: a table with a filter (a CSV file, the sheets of an Excel
// file, the tables of a database), the file as text (CSV, JSON; the CREATE TABLE
// statements of a database) and a Download button. In Markdown:
//   <DataFile file="loans.csv" />
// The file is read in the browser by dataPreview.js. The labels are in Bulgarian on
// the /bg/ pages.
import { ref, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { useData } from 'vitepress'
import { dataFiles } from './dataFiles.js'
import { parseData } from './dataPreview.js'

const props = defineProps({ file: { type: String, required: true } })

const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`
const TEXT = {
  en: { preview: 'Preview the file', table: 'Table', text: 'Text', sql: 'SQL', filter: 'Filter the rows',
        download: 'Download', close: 'Close', loading: 'Loading...', error: 'The file could not be read',
        line: 'line', row: 'row', separator: 'separator', tab: 'tab', bomTitle: 'Byte Order Mark: 3 invisible bytes at the start of the file (Excel\'s "CSV UTF-8")',
        emptyLine: '(empty line)', noMatch: 'No row has this text.', showAll: n => `Show all ${n}`,
        rows: n => plural(n, 'row', 'rows'), columns: n => plural(n, 'column', 'columns'),
        lines: n => plural(n, 'line', 'lines'), sheets: n => plural(n, 'sheet', 'sheets'),
        tables: n => plural(n, 'table', 'tables'),
        bad: n => plural(n, 'row with a wrong number of fields', 'rows with a wrong number of fields'),
        empty: n => plural(n, 'empty line', 'empty lines'),
        fields: (got, want) => `${got} fields, the header has ${want}`,
        matches: (n, total) => `${plural(n, 'row', 'rows')} of ${total} have this text`,
        first: n => `the first ${n} are shown` },
  bg: { preview: 'Преглед на файла', table: 'Таблица', text: 'Текст', sql: 'SQL', filter: 'Филтър на редовете',
        download: 'Изтегли', close: 'Затвори', loading: 'Зарежда се...', error: 'Файлът не може да се прочете',
        line: 'ред', row: 'ред', separator: 'разделител', tab: 'табулация', bomTitle: 'Byte Order Mark: 3 невидими байта в началото на файла ("CSV UTF-8" на Excel)',
        emptyLine: '(празен ред)', noMatch: 'Няма ред с този текст.', showAll: n => `Покажи всички ${n}`,
        rows: n => plural(n, 'ред', 'реда'), columns: n => plural(n, 'колона', 'колони'),
        lines: n => plural(n, 'ред', 'реда'), sheets: n => plural(n, 'лист', 'листа'),
        tables: n => plural(n, 'таблица', 'таблици'),
        bad: n => plural(n, 'ред с грешен брой полета', 'реда с грешен брой полета'),
        empty: n => plural(n, 'празен ред', 'празни реда'),
        fields: (got, want) => `${got} полета, а заглавният ред има ${want}`,
        matches: (n, total) => `${plural(n, 'ред', 'реда')} от ${total} съдържат този текст`,
        first: n => `показани са първите ${n}` }
}
const { lang } = useData()
const t = computed(() => (String(lang.value || '').startsWith('bg') ? TEXT.bg : TEXT.en))

const STEP = 500   // rows shown at first: long tables stay fast
const open = ref(false)
const data = ref(null)
const error = ref('')
const tab = ref(0)          // the sheet or table
const mode = ref('table')   // 'table' | 'text'
const query = ref('')
const limit = ref(STEP)
const dialog = ref(null)

const url = computed(() => dataFiles[props.file])
const current = computed(() => data.value?.tables[tab.value])
const filtered = computed(() => {
  const rows = current.value?.rows ?? []
  const q = query.value.trim().toLowerCase()
  if (!q) return rows
  return rows.filter(r => r.cells?.some(v => v != null && String(v).toLowerCase().includes(q)))
})
const shown = computed(() => filtered.value.slice(0, limit.value))
const lines = computed(() => (data.value?.text ?? '').replace(/\r?\n$/, '').split(/\r?\n/))
const size = computed(() => {
  const n = data.value?.size ?? 0
  return n < 1024 ? `${n} B` : `${(n / 1024).toFixed(1)} KB`
})
const encoding = computed(() => {
  const d = data.value
  if (!d?.encoding) return ''
  return d.encoding === 'cp1251' ? 'cp1251' : d.bom ? 'UTF-8 + BOM' : 'UTF-8'
})

watch([tab, query], () => { limit.value = STEP })

async function show() {
  open.value = true
  await nextTick()
  dialog.value?.showModal()
  document.documentElement.classList.add('data-file-open')
  if (data.value) return
  error.value = ''
  try {
    const response = await fetch(url.value)
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`)
    data.value = await parseData(props.file, new Uint8Array(await response.arrayBuffer()))
    mode.value = data.value.tables.length ? 'table' : 'text'
  } catch (e) {
    error.value = `${t.value.error}: ${e.message || e}`
  }
}

function close() {
  dialog.value?.close()
}

function onClose() {
  open.value = false
  document.documentElement.classList.remove('data-file-open')
}

// a click on the dark area around the dialog closes it
function onClick(e) {
  if (e.target === dialog.value) close()
}

onBeforeUnmount(onClose)

const cellText = v => (v == null ? 'NULL' : String(v))
const cellClass = (v, j) => ({ num: current.value.numeric[j], null: v == null, blank: v === '' })
</script>

<template>
  <button type="button" class="data-file" :title="t.preview" @click="show">
    <code>data/{{ file }}</code>
    <svg class="data-file-icon" viewBox="0 0 16 16" aria-hidden="true">
      <path d="M2 2.5h12v11H2zM2 6h12M2 9.75h12M6.5 6v7.5" fill="none" stroke="currentColor" stroke-width="1.3" />
    </svg>
  </button>
  <Teleport to="body">
    <dialog v-if="open" ref="dialog" class="data-file-dialog" :aria-label="'data/' + file" @close="onClose" @click="onClick">
      <div class="df-box">
        <header class="df-head">
          <code class="df-name">data/{{ file }}</code>
          <span v-if="data" class="df-meta">
            <span v-if="data.kind === 'xlsx'">{{ t.sheets(data.tables.length) }}</span>
            <span v-if="data.kind === 'db'">{{ t.tables(data.tables.length) }}</span>
            <span v-if="data.kind === 'json'">{{ t.lines(lines.length) }}</span>
            <span v-if="data.sep">{{ t.separator }} <code>{{ data.sep === '\t' ? t.tab : data.sep }}</code></span>
            <span v-if="encoding">{{ encoding }}</span>
            <span>{{ size }}</span>
          </span>
          <span class="df-actions">
            <a class="df-button" :href="url" :download="file">{{ t.download }}</a>
            <button type="button" class="df-close" :title="t.close" :aria-label="t.close" @click="close">
              <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 3.5l9 9M12.5 3.5l-9 9" stroke="currentColor" stroke-width="1.6" /></svg>
            </button>
          </span>
        </header>

        <div v-if="data && (data.tables.length > 1 || (data.text && data.tables.length))" class="df-bar">
          <span v-if="data.text && data.tables.length" class="df-group" role="group">
            <button type="button" :class="{ on: mode === 'table' }" :aria-pressed="mode === 'table'" @click="mode = 'table'">{{ t.table }}</button>
            <button type="button" :class="{ on: mode === 'text' }" :aria-pressed="mode === 'text'" @click="mode = 'text'">{{ data.kind === 'db' ? t.sql : t.text }}</button>
          </span>
          <span v-if="mode === 'table' && data.tables.length > 1" class="df-group" role="group">
            <button
              v-for="(tb, i) in data.tables"
              :key="tb.name"
              type="button"
              :class="{ on: tab === i }"
              :aria-pressed="tab === i"
              @click="tab = i"
            >{{ tb.name }}</button>
          </span>
        </div>

        <div v-if="mode === 'table' && current" class="df-bar df-info">
          <span>{{ t.rows(current.rows.length) }}, {{ t.columns(current.columns.length) }}</span>
          <span v-if="current.bad" class="df-warn">{{ t.bad(current.bad) }}</span>
          <span v-if="current.empty" class="df-warn">{{ t.empty(current.empty) }}</span>
          <input v-model="query" type="search" class="df-filter" :placeholder="t.filter" :aria-label="t.filter">
        </div>

        <div class="df-body">
          <p v-if="error" class="df-message df-error">{{ error }}</p>
          <p v-else-if="!data" class="df-message">{{ t.loading }}</p>
          <pre v-else-if="mode === 'text'" class="df-text"><span v-for="(l, i) in lines" :key="i" :data-n="i + 1"><b v-if="i === 0 && data.bom" class="df-bom" :title="t.bomTitle">BOM</b>{{ l }}</span></pre>
          <template v-else-if="current">
            <table class="df-table">
              <thead>
                <tr>
                  <th class="df-n">{{ current.rowLabel === '#' ? '#' : t[current.rowLabel] }}</th>
                  <th v-for="(c, j) in current.columns" :key="j" :class="{ num: current.numeric[j] }">{{ c }}</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="r in shown" :key="r.n">
                  <tr v-if="!r.cells" class="bad">
                    <td class="df-n">{{ r.n }}</td>
                    <td class="df-note" :colspan="current.columns.length">{{ t.emptyLine }}</td>
                  </tr>
                  <tr
                    v-else
                    :class="{ bad: r.cells.length !== current.columns.length }"
                    :title="r.cells.length !== current.columns.length ? t.fields(r.cells.length, current.columns.length) : null"
                  >
                    <td class="df-n">{{ r.n }}</td>
                    <td v-for="(v, j) in r.cells" :key="j" :class="cellClass(v, j)">{{ cellText(v) }}</td>
                  </tr>
                </template>
              </tbody>
            </table>
            <p v-if="!filtered.length" class="df-message">{{ t.noMatch }}</p>
          </template>
        </div>

        <footer v-if="mode === 'table' && current && (query.trim() || filtered.length > shown.length)" class="df-foot">
          <span v-if="query.trim()">{{ t.matches(filtered.length, current.rows.length) }}</span>
          <template v-if="filtered.length > shown.length">
            <span>{{ t.first(shown.length) }}</span>
            <button type="button" class="df-button" @click="limit = Infinity">{{ t.showAll(filtered.length) }}</button>
          </template>
        </footer>
      </div>
    </dialog>
  </Teleport>
</template>

<style scoped>
.data-file {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0;
  border: 0;
  background: none;
  font: inherit;
  color: var(--vp-code-link-color);
  cursor: pointer;
  white-space: nowrap;
}
.data-file code {
  color: var(--vp-code-link-color);
  transition: color 0.25s;
}
.data-file:hover code,
.data-file:hover {
  color: var(--vp-code-link-hover-color);
}
.data-file-icon {
  width: 14px;
  height: 14px;
  flex: none;
}

.data-file-dialog {
  width: min(1200px, calc(100vw - 32px));
  height: min(86vh, 900px);
  max-width: none;
  max-height: none;
  padding: 0;
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  box-shadow: var(--vp-shadow-5);
  overflow: hidden;
}
.data-file-dialog::backdrop {
  background: rgba(0, 0, 0, 0.55);
}
.df-box {
  display: flex;
  flex-direction: column;
  height: 100%;
  font-size: 14px;
}
.df-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 16px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--vp-c-divider);
}
.df-name {
  font-family: var(--vp-font-family-mono);
  font-size: 15px;
  font-weight: 600;
}
.df-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 2px 14px;
  color: var(--vp-c-text-2);
  font-size: 13px;
}
.df-meta code,
.df-bom {
  padding: 0 5px;
  border-radius: 4px;
  background: var(--vp-c-default-soft);
  font-family: var(--vp-font-family-mono);
}
.df-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}
.df-button,
.df-group button {
  padding: 2px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 999px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font: inherit;
  font-size: 13px;
  font-weight: 500;
  line-height: 22px;
  text-decoration: none;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
}
.df-button:hover,
.df-group button:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}
.df-close {
  display: flex;
  padding: 4px;
  border: 0;
  border-radius: 6px;
  background: none;
  color: var(--vp-c-text-2);
  cursor: pointer;
}
.df-close:hover {
  background: var(--vp-c-default-soft);
  color: var(--vp-c-text-1);
}
.df-close svg {
  width: 18px;
  height: 18px;
}
.df-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--vp-c-divider);
}
.df-group {
  display: flex;
  flex-wrap: wrap;
}
.df-group button {
  border-radius: 0;
  margin-left: -1px;
}
.df-group button:first-child {
  border-radius: 999px 0 0 999px;
  margin-left: 0;
}
.df-group button:last-child {
  border-radius: 0 999px 999px 0;
}
.df-group button.on {
  position: relative;
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
}
.df-info {
  color: var(--vp-c-text-2);
  font-size: 13px;
}
.df-warn {
  padding: 0 8px;
  border-radius: 4px;
  background: var(--vp-c-warning-soft);
  color: var(--vp-c-warning-1);
}
.df-filter {
  width: 220px;
  max-width: 100%;
  margin-left: auto;
  padding: 3px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font: inherit;
  font-size: 14px;
}
.df-filter:focus {
  border-color: var(--vp-c-brand-1);
  outline: none;
}
.df-body {
  flex: 1;
  overflow: auto;
  overscroll-behavior: contain;
}
.df-message {
  margin: 0;
  padding: 16px;
  color: var(--vp-c-text-2);
}
.df-error {
  color: var(--vp-c-danger-1);
}

.df-table {
  border-collapse: separate;
  border-spacing: 0;
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  line-height: 1.5;
}
.df-table th,
.df-table td {
  padding: 3px 12px;
  border-bottom: 1px solid var(--vp-c-divider);
  text-align: left;
  white-space: pre;   /* the spaces of messy text stay visible */
}
.df-table th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--vp-c-bg-soft);
  font-weight: 600;
}
.df-table .num {
  text-align: right;
}
.df-table td.blank {
  background: var(--vp-c-default-soft);
}
.df-table td.null {
  color: var(--vp-c-text-3);
  font-style: italic;
}
.df-table .df-n {
  position: sticky;
  left: 0;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-3);
  text-align: right;
  user-select: none;
}
.df-table th.df-n {
  z-index: 2;
  background: var(--vp-c-bg-soft);
  font-weight: 500;
}
.df-table tbody tr:hover td {
  background-color: var(--vp-c-default-soft);
}
.df-table tbody tr:hover td.df-n {
  background: linear-gradient(var(--vp-c-default-soft), var(--vp-c-default-soft)), var(--vp-c-bg);
}
.df-table tr.bad td {
  background: var(--vp-c-warning-soft);
}
.df-table tr.bad td.df-n {
  background: linear-gradient(var(--vp-c-warning-soft), var(--vp-c-warning-soft)), var(--vp-c-bg);
}
.df-table .df-note {
  color: var(--vp-c-warning-1);
  font-family: var(--vp-font-family-base);
  font-style: italic;
}

.df-text {
  margin: 0;
  padding: 8px 16px 8px 0;
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  line-height: 1.6;
  white-space: pre;
}
.df-text > span {
  display: block;
}
.df-text > span::before {
  content: attr(data-n);
  display: inline-block;
  width: 4em;
  margin-right: 16px;
  color: var(--vp-c-text-3);
  text-align: right;
  user-select: none;
}
.df-bom {
  margin-right: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--vp-c-warning-1);
  background: var(--vp-c-warning-soft);
}

.df-foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 16px;
  padding: 8px 16px;
  border-top: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-2);
  font-size: 13px;
}

/* phones: the whole screen */
@media (max-width: 640px) {
  .data-file-dialog {
    width: 100vw;
    height: 100dvh;
    border: 0;
    border-radius: 0;
  }
  .df-filter {
    width: 100%;
    margin-left: 0;
  }
}
</style>

<style>
/* the page behind an open preview does not scroll */
html.data-file-open {
  overflow: hidden;
}
</style>
