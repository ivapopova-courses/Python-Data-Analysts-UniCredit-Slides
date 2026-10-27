// Reads a sample data file for the preview of DataFile.vue - in the browser, without
// Python, so the preview opens at once:
//
// - CSV: any separator (the one used most in the first line), UTF-8 (with or without
//   a BOM) or, if the bytes are not UTF-8, cp1251; quotes as in Python's csv module.
// - JSON: as text.
// - Excel .xlsx: a zip of XML files, unzipped with the browser's DecompressionStream;
//   the first row of a sheet is its header; cells with a date format become ISO dates.
// - SQLite .db: a small reader of the file format (tables with a rowid, the usual
//   kind; a database without a -wal file).
//
// parseData(name, bytes) returns
//   { kind: 'csv' | 'json' | 'xlsx' | 'db', size, encoding, bom, sep, text, tables }
// text: the file as text (CSV, JSON) or the CREATE TABLE statements (db);
// tables: [{ name, columns, rows, numeric, bad, empty, rowLabel }], one per sheet or
// table, where rows are { n, cells }: n is the line (CSV) or row (Excel) in the file,
// cells is null for an empty line; bad counts the rows whose number of fields is not
// the number of columns. No fetching here: DataFile.vue loads the bytes.

export async function parseData(name, bytes) {
  const ext = name.split('.').pop().toLowerCase()
  const size = bytes.length
  if (ext === 'xlsx') return { kind: 'xlsx', size, tables: await readXlsx(bytes) }
  if (ext === 'db' || ext === 'sqlite') return { kind: 'db', size, ...readSqlite(bytes) }
  const { text, encoding, bom } = decodeText(bytes)
  if (ext === 'json') return { kind: 'json', size, encoding, bom, text, tables: [] }
  const sep = guessSeparator(text)
  const [head, ...rest] = parseCsv(text, sep)
  const rows = rest.map(r => ({ n: r.line, cells: r.fields }))
  return { kind: 'csv', size, encoding, bom, sep, text, tables: [table(name, head?.fields ?? [], rows, 'line')] }
}

const view = bytes => new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength)
const tags = (node, tag) => Array.from(node.getElementsByTagName(tag))
const NUMBER = /^-?\d+(\.\d+)?$/

function table(name, columns, rows, rowLabel) {
  // a column is numeric (right-aligned) if all its values are numbers
  const numeric = columns.map((_, j) => {
    let seen = false
    for (const { cells } of rows) {
      const v = cells?.[j]
      if (v == null || v === '') continue
      if (typeof v !== 'number' && !NUMBER.test(v)) return false
      seen = true
    }
    return seen
  })
  const bad = rows.filter(r => r.cells && r.cells.length !== columns.length).length
  const empty = rows.filter(r => !r.cells).length
  return { name, columns, rows, numeric, bad, empty, rowLabel }
}

// ---------------------------------------------------------------------------
// Text and CSV

function decodeText(bytes) {
  const bom = bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf
  try {
    // the decoder drops the BOM
    return { text: new TextDecoder('utf-8', { fatal: true }).decode(bytes), encoding: 'utf-8', bom }
  } catch {
    // not UTF-8: the Windows encoding of Cyrillic, as in old exports (regions_bg.csv)
    return { text: new TextDecoder('windows-1251').decode(bytes), encoding: 'cp1251', bom: false }
  }
}

function guessSeparator(text) {
  const first = text.slice(0, text.search(/\r?\n|$/)).replace(/"[^"]*"/g, '')
  let best = ','
  let most = 0
  for (const sep of [',', ';', '\t', '|']) {
    const count = first.split(sep).length - 1
    if (count > most) { best = sep; most = count }
  }
  return best
}

// [{ line, fields }]: line is where the record starts (a quoted field can span lines);
// fields is null for an empty line (Python's csv module gives [] for it)
function parseCsv(text, sep) {
  const records = []
  const n = text.length
  let i = 0
  let line = 1
  while (i < n) {
    const start = line
    if (text[i] === '\n' || (text[i] === '\r' && text[i + 1] === '\n')) {
      records.push({ line: start, fields: null })
      i += text[i] === '\r' ? 2 : 1
      line++
      continue
    }
    const fields = []
    let field = ''
    let quoted = false   // the field started with a quote
    let inQuotes = false
    for (; i < n; i++) {
      const c = text[i]
      if (inQuotes) {
        if (c === '"' && text[i + 1] === '"') { field += '"'; i++ }
        else if (c === '"') inQuotes = false
        else { if (c === '\n') line++; field += c }
      } else if (c === '"' && field === '' && !quoted) { inQuotes = quoted = true }
      else if (c === sep) { fields.push(field); field = ''; quoted = false }
      else if (c === '\n' || c === '\r') break
      else field += c
    }
    fields.push(field)
    records.push({ line: start, fields })
    if (text[i] === '\r') i++
    if (text[i] === '\n') i++
    line++
  }
  return records
}

// ---------------------------------------------------------------------------
// Excel .xlsx

// the files of a zip archive: name => Promise of its text
async function unzip(bytes) {
  const dv = view(bytes)
  let end = bytes.length - 22
  while (end >= 0 && dv.getUint32(end, true) !== 0x06054b50) end--
  if (end < 0) throw new Error('not a zip file')
  const utf8 = new TextDecoder()
  const entries = {}
  let p = dv.getUint32(end + 16, true)
  for (let k = dv.getUint16(end + 10, true); k > 0; k--) {
    const nameLength = dv.getUint16(p + 28, true)
    entries[utf8.decode(bytes.subarray(p + 46, p + 46 + nameLength))] = {
      method: dv.getUint16(p + 10, true),
      size: dv.getUint32(p + 20, true),
      offset: dv.getUint32(p + 42, true)
    }
    p += 46 + nameLength + dv.getUint16(p + 30, true) + dv.getUint16(p + 32, true)
  }
  return async name => {
    const e = entries[name]
    if (!e) return null
    const start = e.offset + 30 + dv.getUint16(e.offset + 26, true) + dv.getUint16(e.offset + 28, true)
    const data = bytes.subarray(start, start + e.size)
    if (e.method === 0) return utf8.decode(data)
    const stream = new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw'))
    return utf8.decode(await new Response(stream).arrayBuffer())
  }
}

async function readXlsx(bytes) {
  const read = await unzip(bytes)
  const xml = async name => {
    const text = await read(name)
    return text && new DOMParser().parseFromString(text, 'application/xml')
  }
  const text = node => tags(node, 't').map(t => t.textContent).join('')

  const workbook = await xml('xl/workbook.xml')
  const target = {}
  for (const r of tags(await xml('xl/_rels/workbook.xml.rels'), 'Relationship')) {
    const t = r.getAttribute('Target')
    target[r.getAttribute('Id')] = t.startsWith('/') ? t.slice(1) : 'xl/' + t
  }
  const shared = await xml('xl/sharedStrings.xml')
  const strings = shared ? tags(shared, 'si').map(text) : []
  const dates = dateStyles(await xml('xl/styles.xml'))

  const value = c => {
    const type = c.getAttribute('t') || 'n'
    const v = c.getElementsByTagName('v')[0]?.textContent
    if (type === 'inlineStr') return text(c)
    if (v == null) return ''
    if (type === 's') return strings[+v] ?? ''
    if (type === 'b') return v === '1' ? 'TRUE' : 'FALSE'
    if (type !== 'n') return v   // str (a formula's text), e (an error)
    if (dates.has(+(c.getAttribute('s') || 0))) return excelDate(+v)
    return Number((+v).toPrecision(15))   // as Excel shows it: 0.8654, not 0.8653999999999999
  }

  const tables = []
  for (const sheet of tags(workbook, 'sheet')) {
    const doc = await xml(target[sheet.getAttribute('r:id')])
    const grid = tags(doc, 'row').map(row => {
      const cells = []
      for (const c of tags(row, 'c')) cells[column(c.getAttribute('r'))] = value(c)
      return { n: +row.getAttribute('r'), cells: Array.from(cells, v => v ?? '') }
    })
    const [head, ...rows] = grid
    tables.push(table(sheet.getAttribute('name'), head?.cells ?? [], rows, 'row'))
  }
  return tables
}

// "C12" => 2
function column(ref) {
  let n = 0
  for (const ch of ref.match(/^[A-Z]+/)[0]) n = n * 26 + ch.charCodeAt(0) - 64
  return n - 1
}

// the numbers of the cell styles that show a date (built-in or own number format)
function dateStyles(styles) {
  const set = new Set()
  if (!styles) return set
  const own = {}
  for (const f of tags(styles, 'numFmt')) own[f.getAttribute('numFmtId')] = f.getAttribute('formatCode')
  const xfs = styles.getElementsByTagName('cellXfs')[0]
  if (!xfs) return set
  tags(xfs, 'xf').forEach((xf, i) => {
    const id = +xf.getAttribute('numFmtId')
    const code = (own[id] || '').replace(/"[^"]*"|\[[^\]]*\]|\\./g, '')
    if ((id >= 14 && id <= 22) || (id >= 45 && id <= 47) || /[dmyhs]/i.test(code)) set.add(i)
  })
  return set
}

// Excel counts days from 30.12.1899; 25569 is 01.01.1970
function excelDate(serial) {
  const iso = new Date(Math.round((serial - 25569) * 86400000)).toISOString()
  return iso.endsWith('T00:00:00.000Z') ? iso.slice(0, 10) : iso.slice(0, 19).replace('T', ' ')
}

// ---------------------------------------------------------------------------
// SQLite .db (format: https://www.sqlite.org/fileformat.html)

function readSqlite(bytes) {
  if (new TextDecoder().decode(bytes.subarray(0, 15)) !== 'SQLite format 3') throw new Error('not an SQLite database')
  const dv = view(bytes)
  const pageSize = dv.getUint16(16) === 1 ? 65536 : dv.getUint16(16)
  const usable = pageSize - bytes[20]
  const encoding = dv.getUint32(56)
  const decoder = new TextDecoder(encoding === 2 ? 'utf-16le' : encoding === 3 ? 'utf-16be' : 'utf-8')

  // a cell's payload; a long one goes on in overflow pages
  const payload = (p, size) => {
    const maxLocal = usable - 35
    if (size <= maxLocal) return bytes.subarray(p, p + size)
    const minLocal = Math.floor((usable - 12) * 32 / 255) - 23
    let local = minLocal + (size - minLocal) % (usable - 4)
    if (local > maxLocal) local = minLocal
    const out = new Uint8Array(size)
    out.set(bytes.subarray(p, p + local))
    let have = local
    let page = dv.getUint32(p + local)
    while (have < size && page) {
      const base = (page - 1) * pageSize
      const take = Math.min(usable - 4, size - have)
      out.set(bytes.subarray(base + 4, base + 4 + take), have)
      have += take
      page = dv.getUint32(base)
    }
    return out
  }

  const record = buf => {
    const rv = view(buf)
    const [headerSize, first] = varint(buf, 0)
    const types = []
    for (let p = first; p < headerSize;) {
      const [type, n] = varint(buf, p)
      types.push(type)
      p += n
    }
    let p = headerSize
    const take = n => { const at = p; p += n; return at }
    return types.map(t => {
      switch (t) {
        case 0: return null
        case 1: return rv.getInt8(take(1))
        case 2: return rv.getInt16(take(2))
        case 3: { const at = take(3); return rv.getInt8(at) * 65536 + rv.getUint16(at + 1) }
        case 4: return rv.getInt32(take(4))
        case 5: { const at = take(6); return rv.getInt16(at) * 2 ** 32 + rv.getUint32(at + 2) }
        case 6: return Number(rv.getBigInt64(take(8)))
        case 7: return rv.getFloat64(take(8))
        case 8: return 0
        case 9: return 1
        default: {
          const length = (t - (t % 2 ? 13 : 12)) / 2
          const at = take(length)
          return t % 2 ? decoder.decode(buf.subarray(at, at + length)) : `(blob, ${length} bytes)`
        }
      }
    })
  }

  // all rows of a table b-tree, in rowid order
  const rows = root => {
    const out = []
    const walk = page => {
      const base = (page - 1) * pageSize
      const h = base + (page === 1 ? 100 : 0)   // page 1 starts with the file header
      const cells = dv.getUint16(h + 3)
      if (bytes[h] === 5) {   // interior page: the child pages, then the right-most one
        for (let i = 0; i < cells; i++) walk(dv.getUint32(base + dv.getUint16(h + 12 + 2 * i)))
        walk(dv.getUint32(h + 8))
      } else if (bytes[h] === 13) {   // leaf page: the rows
        for (let i = 0; i < cells; i++) {
          let p = base + dv.getUint16(h + 8 + 2 * i)
          const [size, a] = varint(bytes, p)
          const [rowid, b] = varint(bytes, p + a)
          p += a + b
          out.push({ rowid, values: record(payload(p, size)) })
        }
      } else {
        throw new Error(`page ${page}: not a table page`)
      }
    }
    walk(root)
    return out
  }

  // sqlite_master (page 1): type, name, tbl_name, rootpage, sql
  const tables = []
  const schema = []
  for (const { values: [type, name, , root, sql] } of rows(1)) {
    if (type !== 'table' || name.startsWith('sqlite_') || /without\s+rowid/i.test(sql)) continue
    schema.push(sql.replace(/\n\s*/g, '\n    ') + ';')
    const defs = columnDefs(sql)
    // an INTEGER PRIMARY KEY column is the rowid; the row stores NULL for it
    const alias = defs.findIndex(d => /^\S+\s+integer\s+primary\s+key\b/i.test(d.def))
    const data = rows(root).map((r, i) => ({
      n: i + 1,
      cells: defs.map((_, j) => (j === alias ? r.rowid : r.values[j] ?? null))
    }))
    tables.push(table(name, defs.map(d => d.name), data, '#'))
  }
  return { tables, text: schema.join('\n\n') + '\n' }
}

function varint(bytes, p) {
  let v = 0
  for (let i = 0; i < 8; i++) {
    const b = bytes[p + i]
    v = v * 128 + (b & 0x7f)
    if (b < 0x80) return [v, i + 1]
  }
  return [v * 256 + bytes[p + 8], 9]
}

// the column definitions of a CREATE TABLE: [{ name, def }], without the table constraints
function columnDefs(sql) {
  const body = sql.slice(sql.indexOf('(') + 1, sql.lastIndexOf(')'))
  const parts = []
  let part = ''
  let depth = 0
  let quote = null
  for (const c of body) {
    if (quote) { if (c === quote) quote = null }
    else if (c === '"' || c === "'" || c === '`') quote = c
    else if (c === '[') quote = ']'
    else if (c === '(') depth++
    else if (c === ')') depth--
    else if (c === ',' && depth === 0) { parts.push(part); part = ''; continue }
    part += c
  }
  parts.push(part)
  return parts
    .map(p => p.trim())
    .filter(p => p && !/^(constraint|primary|unique|check|foreign)\b/i.test(p))
    .map(def => ({ def, name: def.match(/^("[^"]*"|\[[^\]]*\]|`[^`]*`|\S+)/)[1].replace(/^["[`]|["\]`]$/g, '') }))
}
