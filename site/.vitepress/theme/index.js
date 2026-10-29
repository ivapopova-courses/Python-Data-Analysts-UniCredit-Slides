import { onMounted } from 'vue'
import { useData } from 'vitepress'
import CourseTheme from '@sciscend/course-kit/theme'
import PyRunCode from './PyRunCode.vue'
import DataFile from './DataFile.vue'
import { setupCodeFold } from './codeFold.js'
import { setupScrollHash } from './scrollHash.js'
import { setupOsTabs } from './osTabs.js'
import './codeFold.css'
import './diagram.css'
import './sidebar.css'
import './navbar.css'
import './footer.css'

// The course-kit theme, plus the runnable Python blocks (PyRunCode.vue, Pyodide),
// the preview of a sample data file (<DataFile file="loans.csv" />, DataFile.vue),
// folding of long code blocks (codeFold.js), the same Windows / Linux tab in all
// command blocks (osTabs.js) and the #section of the page on screen
// in the address bar (scrollHash.js), the ProgressBG logo in the footer (footer.css).
// Taken from JS-Basics-Practical-IBM/Slides.
export default {
  ...CourseTheme,
  enhanceApp(ctx) {
    CourseTheme.enhanceApp?.(ctx)
    ctx.app.component('PyRunCode', PyRunCode)
    ctx.app.component('DataFile', DataFile)
  },
  setup() {
    CourseTheme.setup?.()
    // codeFold changes the page's HTML, so it must start only after Vue has hydrated
    // it; earlier changes made Vue duplicate the runnable blocks of long pages
    onMounted(setupCodeFold)
    onMounted(setupOsTabs)
    const data = useData()  // works only here, in setup
    onMounted(() => setupScrollHash(data))
  }
}
