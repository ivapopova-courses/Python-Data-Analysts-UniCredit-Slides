// The sample data (Slides/data/*) as URLs of the built site, by file name: Vite
// copies the files into the build (the small ones become data: URLs).
// Used by pyRunner.js (Python's data/ folder) and DataFile.vue (the preview).
const urls = import.meta.glob('../../../data/*', { query: '?url', import: 'default', eager: true })

export const dataFiles = Object.fromEntries(
  Object.entries(urls).map(([path, url]) => [path.split('/').pop(), url])
)
