import { posix } from 'node:path'
import { defineCourse } from '@sciscend/course-kit/config'
import { withLocales } from '../../i18n/i18n.mjs'
import { pythonRun } from './pythonRun.mjs'
import { releasedUpTo } from './released.mjs'

// the footer (shown only on the home page - VitePress hides it next to the side
// menu): "Created for" and the ProgressBG logo, in place of the course-kit's
// "<course> - SciScend"; the text is translated in i18n/bg/_site.po
const footerMessage = 'Created for'

// all lectures are listed in the side menu; in `npm run build` (the public site)
// only the released ones are links, the others plain text - see released.mjs
const showAll = process.env.TRAINER === '1' || process.argv.includes('dev')
const lectureNo = link => Number(link.match(/(?:^|\/)lectures\/(\d\d)-/)?.[1] || 0)
const isReleased = link => showAll || lectureNo(link) <= releasedUpTo

const lectures = [
  { text: '1. Introduction, syntax, types', link: '/lectures/01-intro-syntax-types' },
  { text: '2. Conditions and loops', link: '/lectures/02-conditions-and-loops' },
  { text: '3. Lists, tuples, sets', link: '/lectures/03-lists-tuples-sets' },
  { text: '4. Functions', link: '/lectures/04-functions' },
  { text: '5. Lists (advanced)', link: '/lectures/05-lists-advanced' },
  { text: '6. Dictionaries', link: '/lectures/06-dictionaries' },
  { text: '7. Text processing', link: '/lectures/07-text-processing' },
  { text: '8. Regular expressions', link: '/lectures/08-regular-expressions' },
  { text: '9. Errors and files', link: '/lectures/09-errors-and-files' },
  { text: '10. Modules and Git', link: '/lectures/10-modules-and-git' },
  { text: '11. OOP: classes and objects', link: '/lectures/11-oop-classes' },
  { text: '12. OOP: nomenclatures', link: '/lectures/12-oop-nomenclatures' },
  { text: '13. Databases', link: '/lectures/13-databases' },
  { text: '14. NumPy and pandas', link: '/lectures/14-numpy-pandas-intro' },
  { text: '15. pandas: select, group, join', link: '/lectures/15-pandas-select-aggregate-join' },
  { text: '16. pandas: reports, project', link: '/lectures/16-pandas-reports-project' }
].map(it => (isReleased(it.link) ? it : { text: it.text })) // no link: grey text (theme/sidebar.css)

const course = defineCourse({
  title: 'Python for Data Analysts',
  description: 'From SQL and SAS to Python, pandas and NumPy',
  lang: 'en',
  // private trainer notes: a folder next to this repo, never published
  trainerDir: '../trainer',
  // the "In this page" column from 1152px (VitePress: 1280px), so it shows on a
  // laptop at 100% zoom
  asideMinWidth: 1152,
  nav: [
    { text: 'Agenda', link: '/agenda' },
    { text: 'Lectures', link: lectures.filter(it => it.link).at(-1).link },
    { text: 'Project', link: '/project' }
  ],
  sidebar: [
    {
      text: 'Course',
      items: [
        { text: 'Home', link: '/' },
        { text: 'Agenda', link: '/agenda' },
        { text: 'How to use these pages', link: '/how-to' },
        { text: 'Sample data', link: '/sample-data' },
        { text: 'Animations', link: '/under-the-hood' },
        { text: 'Final project', link: '/project' }
      ]
    },
    {
      text: 'Lectures',
      items: lectures
    }
  ]
})

course.themeConfig.footer = {
  message: `${footerMessage} <a class="footer-logo" href="https://progressbg.net" target="_blank" rel="noopener">` +
    `<img src="${course.base}images/progressbg-logo.png" alt="ProgressBG"></a>`
}

// unreleased lectures: no page (English and Bulgarian), and every link to them
// (agenda, index, cross-references) is rendered as its plain text
if (!showAll) {
  course.srcExclude = Array.from({ length: 99 - releasedUpTo }, (_, i) => String(releasedUpTo + 1 + i).padStart(2, '0'))
    .flatMap(nn => [`lectures/${nn}-*.md`, `*/lectures/${nn}-*.md`])
  const kitConfig = course.markdown.config
  course.markdown.config = md => {
    kitConfig(md)
    md.core.ruler.push('unreleased_links', state => {
      for (const block of state.tokens) {
        if (block.type !== 'inline' || !block.children) continue
        const out = []
        const drop = [] // per open link: is it dropped?
        for (const t of block.children) {
          if (t.type === 'link_open') {
            const href = t.attrGet('href') || ''
            const target = /^([a-z]+:|\/|#)/i.test(href) ? href : posix.join(posix.dirname(state.env.relativePath || ''), href)
            const hidden = !isReleased(target)
            drop.push(hidden)
            if (hidden) continue
          } else if (t.type === 'link_close' && drop.pop()) continue
          out.push(t)
        }
        block.children = out
      }
    })
  }
}

// ```python run blocks: Run / Edit / Reset with Python in the browser (Pyodide),
// see pythonRun.mjs and theme/PyRunCode.vue
pythonRun(course)

// withLocales: adds the Bulgarian version (site/bg/, generated from i18n/bg/*.po)
// and the EN / BG button - see i18n/README.md
export default await withLocales(course, { footerMessage })
