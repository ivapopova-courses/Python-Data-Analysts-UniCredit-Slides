import { onMounted } from 'vue'
import { useData } from 'vitepress'
import CourseTheme from '@sciscend/course-kit/theme'
import PyRunCode from './PyRunCode.vue'
import { setupCodeFold } from './codeFold.js'
import { setupScrollHash } from './scrollHash.js'
import { setupOsTabs } from './osTabs.js'
import './codeFold.css'
import './diagram.css'

// The course-kit theme, plus the runnable Python blocks (PyRunCode.vue, Pyodide),
// folding of long code blocks (codeFold.js), the same Windows / Linux tab in all
// command blocks (osTabs.js) and the #section of the page on screen
// in the address bar (scrollHash.js). Taken from JS-Basics-Practical-IBM/Slides.
export default {
  ...CourseTheme,
  enhanceApp(ctx) {
    CourseTheme.enhanceApp?.(ctx)
    ctx.app.component('PyRunCode', PyRunCode)
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
