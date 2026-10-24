import { posix } from 'node:path'
import { defineCourse } from '@sciscend/course-kit/config'
import { withLocales } from '../../i18n/i18n.mjs'
import { pythonRun } from './pythonRun.mjs'
import { releasedUpTo } from './released.mjs'

const footerMessage = 'Python for Data Analysts'

// all lectures in `npm run dev` and TRAINER=1 builds, only the released ones in
// `npm run build` (the public site) - see released.mjs
const showAll = process.env.TRAINER === '1' || process.argv.includes('dev')
const lectureNo = link => Number(link.match(/(?:^|\/)lectures\/(\d\d)-/)?.[1] || 0)
const isReleased = link => showAll || lectureNo(link) <= releasedUpTo

const lectures = [
  { text: '1. Introduction, syntax, types', link: '/lectures/01-intro-syntax-types' },
  { text: '2. Conditions and loops', link: '/lectures/02-conditions-and-loops' },
  { text: '3. Lists, tuples, sets', link: '/lectures/03-lists-tuples-sets' },
  { text: '4. Functions', link: '/lectures/04-functions' }
].filter(it => isReleased(it.link))

const course = defineCourse({
  title: 'Python for Data Analysts',
  description: 'From SQL and SAS to Python, pandas and NumPy',
  lang: 'en',
  // private trainer notes: a folder next to this repo, never published
  trainerDir: '../trainer',
  nav: [
    { text: 'Agenda', link: '/agenda' },
    { text: 'Lectures', link: lectures.at(-1).link },
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
  ],
  footerMessage
})

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
