// ```python run  -> the code block gets "Run", "Edit" and "Reset" buttons
// (theme/PyRunCode.vue). The course-kit only knows ```js run, so this adds the
// Python variant to the markdown config that defineCourse() returns. Call it
// before withLocales(): the translated pages are rendered with the same options.
export function pythonRun(config) {
  const markdown = (config.markdown ??= {})
  const kitConfig = markdown.config
  markdown.config = md => {
    kitConfig?.(md)
    const fence = md.renderer.rules.fence
    md.renderer.rules.fence = (tokens, idx, options, env, self) => {
      const token = tokens[idx]
      const info = token.info.trim().split(/\s+/)
      const lang = info[0].split('{')[0]   // python{2,4} run: lines 2 and 4 highlighted
      if ((lang === 'python' || lang === 'py') && info.includes('run')) {
        token.info = info.filter(word => word !== 'run').join(' ')
        const code = Buffer.from(token.content, 'utf8').toString('base64')
        return `<PyRunCode code="${code}">${fence(tokens, idx, options, env, self)}</PyRunCode>`
      }
      return fence(tokens, idx, options, env, self)
    }
  }
  return config
}
