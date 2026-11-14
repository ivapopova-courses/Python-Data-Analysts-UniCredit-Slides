import fs from 'node:fs'

// `clients.csv` or `data/clients.csv` (inline code with the name of a sample data
// file, Slides/data/*) -> a link that opens the Sample data page in a new tab with
// the preview of that file (sample-data?file=clients.csv; theme/DataFile.vue opens
// the dialog). Not in headings, not inside a link, not on the Sample data page
// itself (it has the preview buttons). The core rule only marks the tokens, so the
// i18n segmenting (i18n/i18n.mjs) sees the same Markdown. Call it before
// withLocales(): the Bulgarian pages link to /bg/sample-data.
export function dataLinks(config) {
  const files = new Set(fs.readdirSync(new URL('../../data/', import.meta.url)))
  const base = config.base || '/'
  const markdown = (config.markdown ??= {})
  const kitConfig = markdown.config
  markdown.config = md => {
    kitConfig?.(md)
    md.core.ruler.push('data_links', state => {
      const page = state.env.relativePath || ''
      if (/(^|\/)sample-data\.md$/.test(page)) return
      const bg = page.startsWith('bg/')
      state.tokens.forEach((block, i) => {
        if (block.type !== 'inline' || !block.children) return
        if (state.tokens[i - 1]?.type === 'heading_open') return
        let inLink = 0
        for (const t of block.children) {
          if (t.type === 'link_open') inLink++
          else if (t.type === 'link_close') inLink--
          else if (t.type === 'code_inline' && !inLink) {
            const name = t.content.replace(/^data\//, '')
            if (files.has(name)) {
              t.meta = { ...t.meta, dataLink: `${base}${bg ? 'bg/' : ''}sample-data?file=${encodeURIComponent(name)}`, bg }
            }
          }
        }
      })
    })
    const codeInline = md.renderer.rules.code_inline
    md.renderer.rules.code_inline = (tokens, idx, options, env, self) => {
      const html = codeInline(tokens, idx, options, env, self)
      const link = tokens[idx].meta?.dataLink
      if (!link) return html
      const title = tokens[idx].meta.bg ? 'Преглед на файла (нов раздел)' : 'Preview the file (new tab)'
      return `<a class="data-link" href="${link}" target="_blank" rel="noopener" title="${title}">${html}</a>`
    }
  }
  return config
}
