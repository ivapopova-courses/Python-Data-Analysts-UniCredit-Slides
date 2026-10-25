// Commands for the terminal are written once per operating system, as a VitePress
// code group with the tabs "Windows" (first, the default) and "Linux / macOS":
//
//   ::: code-group
//   ```bat [Windows]
//   ...
//   ```
//   ```bash [Linux / macOS]
//   ...
//   ```
//   :::
//
// This keeps all code groups of the site on the same tab: a click on "Linux / macOS"
// in one group switches every group (on this page and on the next ones), and the
// choice is remembered in the browser. Groups with other tab names are not touched.

const KEY = 'course-code-tab'

function remembered() {
  try { return localStorage.getItem(KEY) } catch { return null }
}

function remember(title) {
  try { localStorage.setItem(KEY, title) } catch { /* private mode: not remembered */ }
}

// show the tab `title` in one group, if it has one (the same thing VitePress does
// on a click, without scrolling)
function select(group, title) {
  const labels = [...group.querySelectorAll(':scope > .tabs > label')]
  const i = labels.findIndex(label => label.textContent.trim() === title)
  if (i < 0) return
  const input = group.querySelector(`input[id="${labels[i].htmlFor}"]`)
  if (input) input.checked = true
  const blocks = group.querySelector(':scope > .blocks')
  if (!blocks) return
  for (const [j, block] of [...blocks.children].entries()) block.classList.toggle('active', j === i)
}

function selectAll(title, except) {
  for (const group of document.querySelectorAll('.vp-code-group')) {
    if (group !== except) select(group, title)
  }
}

export function setupOsTabs() {
  window.addEventListener('click', event => {
    const input = event.target
    if (!input.matches?.('.vp-code-group input')) return
    const label = input.parentElement.querySelector(`label[for="${input.id}"]`)
    const title = label?.textContent.trim()
    if (!title) return
    remember(title)
    selectAll(title, input.parentElement.parentElement)
  })
  // the pages of a client-side navigation: apply the remembered tab to new groups
  const apply = () => { const title = remembered(); if (title) selectAll(title) }
  let queued = false
  const later = () => {
    if (queued) return
    queued = true
    requestAnimationFrame(() => { queued = false; apply() })
  }
  new MutationObserver(later).observe(document.querySelector('#app') || document.body, { childList: true, subtree: true })
  apply()
}
