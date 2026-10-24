// Shared engine of the step-by-step animations: scenario tabs, Back / Next /
// Play, keyboard, deep links (#3 = scenario 3, #3.5 = its step 5), light / dark
// theme, and the two languages. Each page gives its scenarios and draws a step.
//
// Language: English by default, Bulgarian with ?lang=bg. The Bulgarian copy
// bg/<page>.html only redirects here with ?lang=bg (so the i18n build of the site
// can link the Bulgarian pages to it). Every text is a pair [English, Bulgarian].
(function () {
    'use strict'

    const LANG = new URLSearchParams(location.search).get('lang') === 'bg' ? 'bg' : 'en'
    const tr = t => (Array.isArray(t) ? (LANG === 'bg' ? t[1] : t[0]) : t)
    const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    document.documentElement.lang = LANG

    // `code` in an explanation becomes <code>; **bold** becomes <b>
    const rich = t => esc(tr(t))
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')

    const PY_TOKENS = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|\b(and|or|not|is|in|if|elif|else|for|while|break|continue|pass|def|return|global|nonlocal|lambda|match|case|del|import|from|None|True|False)\b|(\b\d[\d_]*(?:\.\d+)?(?:e-?\d+)?\b)|\b(print|type|id|int|float|str|bool|round|len|sum|min|max|range|enumerate|sorted|list|tuple|set)\b(?=\()/g
    function highlightPy(line) {
        let out = ''
        let last = 0
        line.replace(PY_TOKENS, (m, c, s, k, n, b, at) => {
            out += esc(line.slice(last, at))
            const cls = c ? 'c' : s ? 's' : k ? 'k' : n ? 'n' : 'b'
            out += `<span class="hl-${cls}">${esc(m)}</span>`
            last = at + m.length
            return m
        })
        return out + esc(line.slice(last))
    }

    const UI = {
        first: ['To the start (Home)', 'Към началото (Home)'],
        back: ['Back', 'Назад'],
        backTitle: ['Back (Left arrow)', 'Назад (стрелка наляво)'],
        next: ['Next', 'Напред'],
        nextTitle: ['Next (Right arrow or Space)', 'Напред (стрелка надясно или интервал)'],
        play: ['Play', 'Пусни'],
        pause: ['Pause', 'Пауза'],
        playTitle: ['Auto-play (P)', 'Автоматично (P)'],
        theme: ['Light / dark theme', 'Светла / тъмна тема'],
        step: ['step', 'стъпка'],
        of: ['of', 'от'],
        adv: ['advanced', 'за напреднали'],
        langTitle: ['Bulgarian version', 'English version'],
    }
    const ICON = {
        first: '<svg viewBox="0 0 16 16"><path d="M3 3h2v10H3zM13 3L6 8l7 5z"/></svg>',
        back: '<svg viewBox="0 0 16 16"><path d="M11 3L4 8l7 5z"/></svg>',
        next: '<svg viewBox="0 0 16 16"><path d="M5 3l7 5-7 5z"/></svg>',
        play: '<svg viewBox="0 0 16 16"><path d="M5 3l8 5-8 5z"/></svg>',
        pause: '<svg viewBox="0 0 16 16"><path d="M4 3h3v10H4zM9 3h3v10H9z"/></svg>',
        theme: '<svg viewBox="0 0 16 16"><path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm0 2v10a5 5 0 0 1 0-10z"/></svg>',
    }

    function start(cfg) {
        const $ = id => document.getElementById(id)
        document.title = tr(cfg.title)
        $('title').innerHTML = `${esc(tr(cfg.title))}<small>${esc(tr(cfg.subtitle))}</small>`
        $('firstBtn').innerHTML = ICON.first
        $('firstBtn').title = tr(UI.first)
        $('prevBtn').innerHTML = ICON.back + esc(tr(UI.back))
        $('prevBtn').title = tr(UI.backTitle)
        $('nextBtn').innerHTML = esc(tr(UI.next)) + ICON.next
        $('nextBtn').title = tr(UI.nextTitle)
        $('playBtn').title = tr(UI.playTitle)
        $('themeBtn').innerHTML = ICON.theme
        $('themeBtn').title = tr(UI.theme)
        const langBtn = $('langBtn')
        langBtn.textContent = LANG === 'bg' ? 'EN' : 'BG'
        langBtn.title = tr(UI.langTitle)

        // theme: the saved choice, else the system's
        try {
            const saved = localStorage.getItem('anim-theme')
            if (saved) document.documentElement.dataset.theme = saved
        } catch { /* no storage */ }
        $('themeBtn').onclick = () => {
            const dark = document.documentElement.dataset.theme
                ? document.documentElement.dataset.theme === 'dark'
                : matchMedia('(prefers-color-scheme: dark)').matches
            document.documentElement.dataset.theme = dark ? 'light' : 'dark'
            try { localStorage.setItem('anim-theme', dark ? 'light' : 'dark') } catch { /* no storage */ }
            render(false)
        }

        const tabs = $('tabs')
        cfg.scenarios.forEach((sc, i) => {
            const b = document.createElement('button')
            b.className = 'tab'
            b.setAttribute('role', 'tab')
            b.innerHTML = `${i + 1}. ${rich(sc.tab)}` + (sc.advanced ? `<span class="adv">${esc(tr(UI.adv))}</span>` : '')
            b.onclick = () => select(i, 0)
            tabs.appendChild(b)
        })

        let sc = 0
        let step = 0
        let states = []
        let timer = null

        function setHash() {
            const hash = `#${sc + 1}` + (step ? `.${step + 1}` : '')
            history.replaceState(null, '', location.pathname + location.search + hash)
            langBtn.href = location.pathname + (LANG === 'bg' ? '' : '?lang=bg') + hash
        }

        function render(animate) {
            const s = states[step]
            const prev = step > 0 ? states[step - 1] : null
            cfg.render(cfg.scenarios[sc], s, animate ? prev : null)
            $('explain').innerHTML = rich(s.text)
            $('counter').textContent = `${tr(UI.step)} ${step + 1} ${tr(UI.of)} ${states.length}`
            $('prevBtn').disabled = step === 0
            $('firstBtn').disabled = step === 0
            $('nextBtn').disabled = step === states.length - 1
            ;[...tabs.children].forEach((b, i) => b.setAttribute('aria-selected', String(i === sc)))
            setHash()
        }

        function select(i, j) {
            sc = Math.max(0, Math.min(cfg.scenarios.length - 1, i))
            states = cfg.build(cfg.scenarios[sc])
            step = Math.max(0, Math.min(states.length - 1, j))
            setPlaying(false)
            cfg.setup?.(cfg.scenarios[sc])
            render(false)
        }

        function go(j) {
            if (j < 0 || j >= states.length) return
            const forward = j === step + 1
            step = j
            render(forward)
        }

        function setPlaying(on) {
            clearInterval(timer)
            timer = null
            if (on) {
                if (step === states.length - 1) go(0)
                timer = setInterval(() => {
                    if (step >= states.length - 1) setPlaying(false)
                    else go(step + 1)
                }, cfg.playMs || 2800)
            }
            $('playBtn').innerHTML = on ? ICON.pause + esc(tr(UI.pause)) : ICON.play + esc(tr(UI.play))
        }

        $('firstBtn').onclick = () => go(0)
        $('prevBtn').onclick = () => go(step - 1)
        $('nextBtn').onclick = () => go(step + 1)
        $('playBtn').onclick = () => setPlaying(!timer)
        document.addEventListener('keydown', e => {
            if (e.ctrlKey || e.metaKey || e.altKey) return
            if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); go(step + 1) }
            else if (e.key === 'ArrowLeft') go(step - 1)
            else if (e.key === 'Home') go(0)
            else if (e.key === 'End') go(states.length - 1)
            else if (e.key === 'p' || e.key === 'P') setPlaying(!timer)
        })
        addEventListener('resize', () => render(false))

        function fromHash() {
            const [a, b] = location.hash.slice(1).split('.')
            select((parseInt(a, 10) || 1) - 1, (parseInt(b, 10) || 1) - 1)
        }
        addEventListener('hashchange', fromHash)
        fromHash()
    }

    window.Anim = { LANG, tr, esc, rich, highlightPy, start }
})()
