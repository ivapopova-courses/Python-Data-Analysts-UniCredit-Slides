"""Makes the diagrams of the lectures: site/public/diagrams/<name>.svg (English)
and site/public/diagrams/bg/<name>.svg (Bulgarian).

    python tools/make-diagrams.py

The texts of both languages are here, next to the layout, so a change of the
layout changes both. The i18n build links the Bulgarian pages to the bg/ copy by
itself (see i18n/README.md). The SVGs have a transparent background and dark text;
in dark mode the site inverts them (img.diagram in theme/custom.css).
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parents[1] / "site" / "public" / "diagrams"

INK = "#1f2328"
MUTED = "#5b616b"
COLORS = {
    "blue": ("#e3edfb", "#3b6fc4"),
    "green": ("#e2f2e0", "#4f8a45"),
    "orange": ("#fdebd3", "#c97a1c"),
    "red": ("#f9dedb", "#c4302b"),
    "gray": ("#f3f1ec", "#8c8578"),
    "violet": ("#ece4f8", "#7b48c4"),
}
SANS = "Segoe UI, Noto Sans, Roboto, Helvetica Neue, Arial, sans-serif"
MONO = "JetBrains Mono, Cascadia Code, Consolas, DejaVu Sans Mono, monospace"


class Svg:
    def __init__(self, width, height, title):
        self.w, self.h, self.title = width, height, title
        self.parts = []

    def rect(self, x, y, w, h, color, dash=False, radius=10):
        fill, stroke = COLORS[color]
        extra = ' stroke-dasharray="6 4"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
                          f'fill="{fill}" stroke="{stroke}" stroke-width="2"{extra}/>')

    def text(self, x, y, s, size=15, weight=400, mono=False, color=INK, anchor="start"):
        family = MONO if mono else SANS
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
                          f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}" xml:space="preserve">{escape(s)}</text>')

    def lines(self, x, y, items, size=14, gap=21, anchor="start"):
        """items: str (sans) or (str, options) - options: mono, color, weight."""
        for i, item in enumerate(items):
            s, opt = (item, {}) if isinstance(item, str) else item
            self.text(x, y + i * gap, s, size=opt.get("size", size), mono=opt.get("mono", False),
                      color=opt.get("color", INK), weight=opt.get("weight", 400), anchor=anchor)

    def box(self, x, y, w, h, color, title, items=(), dash=False, center=False, title_size=16):
        self.rect(x, y, w, h, color, dash)
        tx = x + w / 2 if center else x + 14
        anchor = "middle" if center else "start"
        self.text(tx, y + 26, title, size=title_size, weight=700, anchor=anchor)
        self.lines(tx, y + 50, items, anchor=anchor)

    def arrow(self, x1, y1, x2, y2, color=MUTED, dash=False, curve=None):
        extra = ' stroke-dasharray="6 4"' if dash else ""
        if curve:
            cx, cy = curve
            d = f"M{x1},{y1} Q{cx},{cy} {x2},{y2}"
        else:
            d = f"M{x1},{y1} L{x2},{y2}"
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2" '
                          f'marker-end="url(#head)"{extra}/>')

    def diamond(self, cx, cy, w, h, color, label, mono=True, size=14):
        fill, stroke = COLORS[color]
        pts = f"{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}"
        self.parts.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        self.text(cx, cy + 5, label, size=size, mono=mono, anchor="middle")

    def poly(self, points, color=MUTED, dash=False, head=True):
        """an arrow along the points [(x, y), ...]"""
        extra = ' stroke-dasharray="6 4"' if dash else ""
        marker = ' marker-end="url(#head)"' if head else ""
        d = "M" + " L".join(f"{x},{y}" for x, y in points)
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2"{marker}{extra}/>')

    def raw(self, svg):
        self.parts.append(svg)

    def render(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img">\n'
                f"<title>{escape(self.title)}</title>\n"
                f'<defs><marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
                f'fill="{MUTED}"/></marker></defs>\n' + "\n".join(self.parts) + "\n</svg>\n")


# ---------------------------------------------------------------------------
# run-python: three ways to run code -> the interpreter -> the result

RUN = {
    "en": {
        "title": "From your code to the result",
        "code": "Your code",
        "script": "A script", "repl": "The REPL", "cell": "A notebook cell",
        "interp": "The Python interpreter (CPython)",
        "s1": "1. Check the syntax", "s1b": "a SyntaxError stops here",
        "s2": "2. Compile to bytecode",
        "s3": "3. Run the bytecode", "s3b": "in the Python virtual machine",
        "result": "The result",
        "r": ["printed text", "files, databases", "tables, charts"],
        "err": "or an error: a traceback",
    },
    "bg": {
        "title": "От вашия код до резултата",
        "code": "Вашият код",
        "script": "Скрипт", "repl": "REPL", "cell": "Клетка в notebook",
        "interp": "Интерпретаторът на Python (CPython)",
        "s1": "1. Проверка на синтаксиса", "s1b": "SyntaxError спира тук",
        "s2": "2. Превод до bytecode",
        "s3": "3. Изпълнение на bytecode", "s3b": "във виртуалната машина на Python",
        "result": "Резултатът",
        "r": ["отпечатан текст", "файлове, бази данни", "таблици, графики"],
        "err": "или грешка: traceback",
    },
}


def run_python(t):
    s = Svg(920, 340, t["title"])
    s.text(20, 24, t["code"], size=13, weight=700, color=MUTED)
    ys = [40, 135, 230]
    s.box(20, ys[0], 230, 76, "green", t["script"], [("python hello.py", {"mono": True})])
    s.box(20, ys[1], 230, 76, "green", t["repl"], [(">>> 2 + 3", {"mono": True})])
    s.box(20, ys[2], 230, 76, "green", t["cell"], [("Shift+Enter", {"mono": True})])
    for y, to in zip(ys, (120, 170, 220)):
        s.arrow(252, y + 38, 302, to)
    s.rect(306, 14, 350, 312, "blue")
    s.text(481, 42, t["interp"], size=16, weight=700, anchor="middle")
    steps = [(t["s1"], t["s1b"], False), (t["s2"], "__pycache__/*.pyc", True), (t["s3"], t["s3b"], False)]
    for i, (a, b, mono) in enumerate(steps):
        y = 62 + i * 88
        s.rect(326, y, 310, 64, "gray")
        s.text(342, y + 26, a, size=15, weight=700)
        s.text(342, y + 49, b, size=14, mono=mono, color=MUTED)
        if i < 2:
            s.arrow(481, y + 64, 481, y + 86)
    s.arrow(658, 170, 704, 170)
    s.box(708, 70, 196, 200, "orange", t["result"], t["r"] + [(t["err"], {"color": "#c4302b"})])
    return s.render()


# ---------------------------------------------------------------------------
# venv: the system Python and two projects with their own .venv

VENV = {
    "en": {
        "title": "Virtual environments: one per project",
        "system": "The system Python",
        "sys1": "python.org, Python 3.12",
        "sys2": "only the standard library",
        "own": "its own python and packages",
        "list": "the list",
        "create": "py -m venv .venv",
        "install": "pip install -r",
    },
    "bg": {
        "title": "Виртуални среди: по една за всеки проект",
        "system": "Системният Python",
        "sys1": "python.org, Python 3.12",
        "sys2": "само стандартната библиотека",
        "own": "свой python и свои пакети",
        "list": "списъкът",
        "create": "py -m venv .venv",
        "install": "pip install -r",
    },
}


def venv(t):
    s = Svg(920, 400, t["title"])
    s.box(300, 12, 320, 92, "gray", t["system"], [(t["sys1"], {"mono": False}), (t["sys2"], {"color": MUTED})],
          center=True)
    projects = [
        (40, "Homework/", ["pandas 2.3", "numpy 2.3", "jupyterlab 4.4"], ["pandas>=2.2", "numpy>=2.0", "..."]),
        (480, "old-report/", ["pandas 2.2", "numpy 1.26", "openpyxl 3.1"], ["pandas==2.2.3", "numpy==1.26.4", "..."]),
    ]
    for x, folder, packages, reqs in projects:
        s.rect(x, 150, 400, 236, "gray", dash=True)
        s.text(x + 14, 176, folder, size=16, weight=700, mono=True)
        s.box(x + 16, 192, 200, 180, "blue", ".venv/", [("python.exe", {"mono": True})]
              + [(p, {"mono": True}) for p in packages] + [(t["own"], {"color": MUTED, "size": 12})])
        s.box(x + 240, 192, 146, 130, "orange", "requirements.txt", [(r, {"mono": True, "size": 13}) for r in reqs],
              title_size=13)
        s.text(x + 313, 342, t["install"], size=13, mono=True, anchor="middle")
        s.arrow(x + 270, 324, x + 220, 290)
    s.arrow(330, 104, 150, 190)
    s.arrow(590, 104, 590, 190)
    s.text(228, 136, t["create"], size=13, mono=True, anchor="end")
    s.text(600, 136, t["create"], size=13, mono=True)
    return s.render()


# ---------------------------------------------------------------------------
# if-elif-else: the conditions are tested in order, the first true one wins

IFS = {
    "en": {
        "title": "if / elif / else: the first true condition wins",
        "true": "True", "false": "False",
        "b1": "block 1", "b2": "block 2", "b3": "block 3",
        "b3n": "else: when no condition was true",
        "after": "the code after the if statement",
        "sql": "The same in SQL:",
        "note": ["Only one block runs.", "The later conditions are not", "even tested."],
    },
    "bg": {
        "title": "if / elif / else: печели първото вярно условие",
        "true": "True", "false": "False",
        "b1": "блок 1", "b2": "блок 2", "b3": "блок 3",
        "b3n": "else: когато нито едно условие не е вярно",
        "after": "кодът след if конструкцията",
        "sql": "Същото в SQL:",
        "note": ["Изпълнява се само един блок.", "Следващите условия дори", "не се проверяват."],
    },
}


def if_elif_else(t):
    green = COLORS["green"][1]
    red = COLORS["red"][1]
    s = Svg(920, 420, t["title"])
    s.arrow(200, 8, 200, 36)
    s.diamond(200, 70, 250, 64, "orange", "if condition_1:")
    s.diamond(200, 180, 250, 64, "orange", "elif condition_2:")
    for y, label in ((70, t["b1"]), (180, t["b2"])):
        s.arrow(325, y, 398, y, color=green)
        s.text(360, y - 8, t["true"], size=12, weight=700, color=green, anchor="middle")
        s.box(400, y - 26, 170, 52, "green", label, center=True)
    s.arrow(200, 102, 200, 146, color=red)
    s.text(210, 128, t["false"], size=12, weight=700, color=red)
    s.arrow(200, 212, 200, 256, color=red)
    s.text(210, 238, t["false"], size=12, weight=700, color=red)
    s.box(75, 258, 250, 62, "gray", t["b3"], [(t["b3n"], {"size": 12, "color": MUTED})], center=True)
    s.poly([(570, 70), (640, 70), (640, 352)])
    s.poly([(570, 180), (640, 180)], head=False)
    s.poly([(200, 320), (200, 352)])
    s.poly([(640, 352), (640, 362), (420, 362)], head=False)
    s.rect(75, 362, 590, 48, "blue")
    s.text(370, 392, t["after"], size=15, weight=700, anchor="middle")
    s.text(690, 60, t["sql"], size=13, weight=700, color=MUTED)
    s.lines(690, 84, [("CASE", {"mono": True}), ("  WHEN condition_1", {"mono": True}),
                      ("    THEN ...", {"mono": True}), ("  WHEN condition_2", {"mono": True}),
                      ("    THEN ...", {"mono": True}), ("  ELSE ...", {"mono": True}), ("END", {"mono": True})],
            size=13, gap=19)
    s.lines(690, 240, t["note"], size=13, gap=19)
    return s.render()


# ---------------------------------------------------------------------------
# loop-simple: the plain while and for loops, without break and continue

LOOPS = {
    "en": {
        "title": "The flow of a while loop and a for loop",
        "true": "True", "false": "False",
        "next": "the next item", "none": "no more items",
        "block": "block",
        "again": ["the end of the block:", "test again"],
        "after": "the code after the loop",
        "note": "break and continue change this flow: sections 13 - 14.",
    },
    "bg": {
        "title": "Как протичат цикълът while и цикълът for",
        "true": "True", "false": "False",
        "next": "следващият елемент", "none": "няма повече",
        "block": "блок",
        "again": ["краят на блока:", "провери отново"],
        "after": "кодът след цикъла",
        "note": "break и continue променят този ход: раздели 13 - 14.",
    },
}


def loop_simple(t):
    green = COLORS["green"][1]
    red = COLORS["red"][1]
    s = Svg(920, 330, t["title"])
    for ox, label, yes, no in ((0, "while condition:", t["true"], t["false"]),
                               (460, "for item in sequence:", t["next"], t["none"])):
        cx = ox + 165
        s.arrow(cx, 8, cx, 38)
        s.diamond(cx, 72, 270, 64, "orange", label, size=13)
        s.arrow(cx, 104, cx, 138, color=green)
        s.text(cx + 10, 126, yes, size=12, weight=700, color=green)
        s.box(cx - 80, 140, 160, 46, "green", t["block"], center=True)
        # the end of the block: back to the test
        s.poly([(cx - 80, 163), (ox + 15, 163), (ox + 15, 22), (cx, 22), (cx, 38)], color=MUTED)
        s.lines(ox + 25, 212, t["again"], size=13, gap=18)
        # the test is False / no more items: after the loop
        s.poly([(cx + 135, 72), (cx + 205, 72), (cx + 205, 238)], color=red)
        s.text(cx + 145, 64, no, size=12, weight=700, color=red)
        s.rect(cx + 85, 240, 200, 46, "blue")
        s.text(cx + 185, 268, t["after"], size=14, weight=700, anchor="middle")
    s.text(460, 318, t["note"], size=13, color=MUTED, anchor="middle")
    return s.render()


# ---------------------------------------------------------------------------
# loop-flow: a while loop with continue and break

LOOP = {
    "en": {
        "title": "The flow of a loop, with continue and break",
        "true": "True", "false": "False",
        "b1": "block 1", "b2": "block 2",
        "after": "the code after the loop",
        "continue": [("continue:", {"weight": 700, "color": "#7b48c4"}), ("the next", {"color": "#7b48c4"}),
                     ("iteration", {"color": "#7b48c4"})],
        "break": "break: leave the loop now",
        "again": "the end of the block: test again",
        "for": ["for item in sequence: the same flow -", "the test is \"is there a next item?\""],
        "else": ["The else of a loop runs when the test", "is False - never after a break."],
    },
    "bg": {
        "title": "Как протича един цикъл, с continue и break",
        "true": "True", "false": "False",
        "b1": "блок 1", "b2": "блок 2",
        "after": "кодът след цикъла",
        "continue": [("continue:", {"weight": 700, "color": "#7b48c4"}), ("следващата", {"color": "#7b48c4"}),
                     ("итерация", {"color": "#7b48c4"})],
        "break": "break: излез от цикъла веднага",
        "again": "краят на блока: провери отново",
        "for": ["for item in sequence: същото -", "проверката е \"има ли следващ елемент?\""],
        "else": ["else на цикъла се изпълнява, когато", "проверката е False - никога след break."],
    },
}


def loop_flow(t):
    green = COLORS["green"][1]
    red = COLORS["red"][1]
    violet = COLORS["violet"][1]
    s = Svg(920, 480, t["title"])
    s.arrow(320, 8, 320, 38)
    s.diamond(320, 72, 250, 64, "orange", "while condition:")
    s.arrow(320, 104, 320, 128, color=green)
    s.text(330, 122, t["true"], size=12, weight=700, color=green)
    s.box(230, 130, 180, 46, "green", t["b1"], center=True)
    s.arrow(320, 176, 320, 204)
    s.diamond(320, 236, 260, 60, "violet", "if continue_condition:", size=13)
    s.arrow(320, 266, 320, 300, color=red)
    s.text(330, 290, t["false"], size=12, weight=700, color=red)
    s.diamond(320, 332, 260, 60, "red", "if break_condition:", size=13)
    s.arrow(320, 362, 320, 396, color=red)
    s.text(330, 386, t["false"], size=12, weight=700, color=red)
    s.box(230, 398, 180, 46, "green", t["b2"], center=True)
    # continue: back to the test
    s.poly([(190, 236), (110, 236), (110, 72), (193, 72)], color=violet)
    s.lines(116, 258, t["continue"], size=13, gap=18)
    s.text(150, 228, t["true"], size=12, weight=700, color=violet, anchor="middle")
    # the end of block 2: back to the test
    s.poly([(230, 421), (50, 421), (50, 22), (320, 22), (320, 38)], color=MUTED)
    s.text(60, 466, t["again"], size=13, color=MUTED)
    # the test is False: after the loop
    s.poly([(445, 72), (720, 72), (720, 396)], color=red)
    s.text(470, 64, t["false"], size=12, weight=700, color=red)
    # break: after the loop
    s.poly([(450, 332), (640, 332), (640, 396)], color=red)
    s.text(462, 324, t["true"], size=12, weight=700, color=red)
    s.text(462, 352, t["break"], size=13, weight=700, color=red)
    s.rect(580, 398, 320, 52, "blue")
    s.text(740, 430, t["after"], size=15, weight=700, anchor="middle")
    s.lines(470, 150, t["for"], size=13, gap=19)
    s.lines(470, 220, t["else"], size=13, gap=19, )
    return s.render()


# ---------------------------------------------------------------------------
# list-indexing: indexes from the start and from the end, and a slice

INDEX = {
    "en": {
        "title": "The indexes of a list",
        "pos": "index from the start", "neg": "index from the end",
        "examples": "Examples:",
        "error": "loans[6]    -> IndexError", "error2": "there is no 7th item",
    },
    "bg": {
        "title": "Индексите на един list",
        "pos": "индекс от началото", "neg": "индекс от края",
        "examples": "Примери:",
        "error": "loans[6]    -> IndexError", "error2": "няма 7-ми елемент",
    },
}

ITEMS = ["L01", "L02", "L03", "L04", "L05", "L06"]


def list_indexing(t):
    green = COLORS["green"][1]
    blue = COLORS["blue"][1]
    s = Svg(920, 270, t["title"])
    x0, w, y = 190, 105, 82
    s.text(20, 30, "loans = [\"L01\", \"L02\", \"L03\", \"L04\", \"L05\", \"L06\"]", size=15, mono=True)
    s.text(x0 - 14, y - 12, t["pos"], size=12, color=green, anchor="end")
    s.text(x0 - 14, y + 92, t["neg"], size=12, color=blue, anchor="end")
    for i, item in enumerate(ITEMS):
        x = x0 + i * w
        s.rect(x, y, w, 56, "orange" if i in (0, 2, 5) else "gray", radius=4)
        s.text(x + w / 2, y + 35, f'"{item}"', size=16, mono=True, anchor="middle")
        s.text(x + w / 2, y - 12, str(i), size=16, weight=700, mono=True, color=green, anchor="middle")
        s.text(x + w / 2, y + 92, str(i - len(ITEMS)), size=16, weight=700, mono=True, color=blue, anchor="middle")
    s.text(20, 205, t["examples"], size=13, weight=700, color=MUTED)
    s.lines(20, 229, [('loans[0]    -> "L01"', {"mono": True}), ('loans[2]    -> "L03"', {"mono": True})],
            size=14, gap=21)
    s.lines(330, 229, [('loans[-1]   -> "L06"', {"mono": True}), ('loans[5]    -> "L06"', {"mono": True})],
            size=14, gap=21)
    s.text(620, 229, t["error"], size=14, mono=True, color=COLORS["red"][1])
    s.text(620, 250, t["error2"], size=13, color=MUTED)
    return s.render()


SLICE = {
    "en": {
        "title": "Slices of a list: the numbers of a slice are the cuts between the items",
        "cuts": "the cuts", "neg": "from the end",
        "slice": "loans[1:4] - from cut 1 to cut 4: 3 items",
        "examples": "Examples:",
        "every2": "loans[::2]  -> every 2nd", "reversed": "loans[::-1] -> reversed", "copy": "loans[:]    -> a copy",
    },
    "bg": {
        "title": "Срезове на list: числата на среза са разрезите между елементите",
        "cuts": "разрезите", "neg": "от края",
        "slice": "loans[1:4] - от разрез 1 до разрез 4: 3 елемента",
        "examples": "Примери:",
        "every2": "loans[::2]  -> всеки 2-ри", "reversed": "loans[::-1] -> обърнат", "copy": "loans[:]    -> копие",
    },
}


def list_slicing(t):
    green = COLORS["green"][1]
    blue = COLORS["blue"][1]
    orange = COLORS["orange"][1]
    s = Svg(920, 340, t["title"])
    x0, w, y = 190, 105, 82
    s.text(20, 30, "loans = [\"L01\", \"L02\", \"L03\", \"L04\", \"L05\", \"L06\"]", size=15, mono=True)
    s.text(x0 - 18, y - 16, t["cuts"], size=12, color=green, anchor="end")
    s.text(x0 - 18, y + 84, t["neg"], size=12, color=blue, anchor="end")
    for i, item in enumerate(ITEMS):
        x = x0 + i * w
        s.rect(x, y, w, 56, "orange" if 1 <= i <= 3 else "gray", radius=4)
        s.text(x + w / 2, y + 35, f'"{item}"', size=16, mono=True, anchor="middle")
    for i in range(len(ITEMS) + 1):
        x = x0 + i * w
        s.raw(f'<path d="M{x},{y - 10} L{x},{y + 66}" stroke="{green}" stroke-width="2.5"/>')
        s.text(x, y - 16, str(i), size=16, weight=700, mono=True, color=green, anchor="middle")
        if i < len(ITEMS):
            s.text(x, y + 84, str(i - len(ITEMS)), size=15, weight=700, mono=True, color=blue, anchor="middle")
    # the slice bracket, from cut 1 to cut 4
    s.poly([(x0 + w, 186), (x0 + w, 196), (x0 + 4 * w, 196), (x0 + 4 * w, 186)], color=orange, head=False)
    s.text(x0 + 2.5 * w, 218, t["slice"], size=14, weight=700, color=orange, anchor="middle")
    s.text(20, 252, t["examples"], size=13, weight=700, color=MUTED)
    s.lines(20, 276, [('loans[1:4]  -> ["L02", "L03", "L04"]', {"mono": True}),
                      ('loans[:2]   -> ["L01", "L02"]', {"mono": True}),
                      ('loans[-2:]  -> ["L05", "L06"]', {"mono": True})], size=14, gap=21)
    s.lines(450, 276, [(t["every2"], {"mono": True}), (t["reversed"], {"mono": True}),
                       (t["copy"], {"mono": True})], size=14, gap=21)
    return s.render()


# ---------------------------------------------------------------------------
# set-operations: union, intersection, difference, symmetric difference

SETS = {
    "en": {
        "title": "Set operations and their SQL names",
        "ops": [("union", "in a or in b"), ("intersection", "in both"),
                ("difference", "in a, not in b"), ("symmetric difference", "in one of them only")],
        "nosql": "(no keyword)",
    },
    "bg": {
        "title": "Операции с множества и имената им в SQL",
        "ops": [("обединение", "в a или в b"), ("сечение", "и в двете"),
                ("разлика", "в a, но не в b"), ("симетрична разлика", "само в едното")],
        "nosql": "(няма дума)",
    },
}


def set_operations(t):
    fill, stroke = COLORS["blue"]
    s = Svg(920, 330, t["title"])
    rows = [("a | b", "a.union(b)", "UNION", "{1, 2, 3, 4}"),
            ("a & b", "a.intersection(b)", "INTERSECT", "{3}"),
            ("a - b", "a.difference(b)", "EXCEPT / MINUS", "{1, 2}"),
            ("a ^ b", "a.symmetric_difference(b)", t["nosql"], "{1, 2, 4}")]
    # the region to fill in each panel: which circles, and which one is cut out
    shapes = [(("a", None), ("b", None)), (("a", "in-b"),), (("a", "out-b"),), (("a", "out-b"), ("b", "out-a"))]
    s.text(460, 26, "a = {1, 2, 3}     b = {3, 4}", size=15, mono=True, anchor="middle")
    for i, ((name, desc), (op, method, sql, result), regions) in enumerate(zip(t["ops"], rows, shapes)):
        x = 15 + i * 227
        cx_a, cx_b, cy, r = x + 78, x + 130, 110, 48
        centre = {"a": cx_a, "b": cx_b}
        s.raw(f'<defs><clipPath id="in-b-{i}"><circle cx="{cx_b}" cy="{cy}" r="{r}"/></clipPath>'
              f'<mask id="out-b-{i}"><rect x="{x}" y="40" width="227" height="150" fill="white"/>'
              f'<circle cx="{cx_b}" cy="{cy}" r="{r}" fill="black"/></mask>'
              f'<mask id="out-a-{i}"><rect x="{x}" y="40" width="227" height="150" fill="white"/>'
              f'<circle cx="{cx_a}" cy="{cy}" r="{r}" fill="black"/></mask></defs>')
        s.raw('<g opacity="0.45">')
        for circle, cut in regions:
            attr = ""
            if cut == "in-b":
                attr = f' clip-path="url(#in-b-{i})"'
            elif cut:
                attr = f' mask="url(#{cut}-{i})"'
            s.raw(f'<circle cx="{centre[circle]}" cy="{cy}" r="{r}" fill="{stroke}"{attr}/>')
        s.raw('</g>')
        for cx, label, lx in ((cx_a, "a", cx_a - 30), (cx_b, "b", cx_b + 30)):
            s.raw(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{stroke}" stroke-width="2"/>')
            s.text(lx, cy + 6, label, size=17, weight=700, mono=True, anchor="middle")
        mid = x + 104
        s.text(mid, 188, name, size=15, weight=700, anchor="middle")
        s.text(mid, 207, desc, size=13, color=MUTED, anchor="middle")
        s.text(mid, 236, op, size=15, weight=700, mono=True, anchor="middle")
        s.text(mid, 258, method, size=12, mono=True, color=MUTED, anchor="middle")
        s.text(mid, 282, "SQL: " + sql, size=13, anchor="middle")
        s.text(mid, 310, "-> " + result, size=14, mono=True, anchor="middle")
    return s.render()


# ---------------------------------------------------------------------------
# scope-legb: where Python looks for a name

LEGB = {
    "en": {
        "title": "Where Python looks for a name: L, E, G, B",
        "b": "B - Built-in: the names of Python",
        "g": "G - Global: the names of the file (module)",
        "e": "E - Enclosing: the function around",
        "l": "L - Local: the function that runs",
        "order": "Python looks from the inside out:",
        "first": "the first name found is used;",
        "none": "not found anywhere: NameError",
        "assign": ["An assignment inside a function", "makes a LOCAL name - unless", "global / nonlocal says otherwise."],
    },
    "bg": {
        "title": "Къде Python търси едно име: L, E, G, B",
        "b": "B - Built-in: имената на Python",
        "g": "G - Global: имената на файла (модула)",
        "e": "E - Enclosing: обхващащата функция",
        "l": "L - Local: функцията, която се изпълнява",
        "order": "Python търси отвътре навън:",
        "first": "използва първото намерено име;",
        "none": "не е намерено никъде: NameError",
        "assign": ["Присвояване във функция", "създава ЛОКАЛНО име - освен ако", "global / nonlocal не казва друго."],
    },
}


def scope_legb(t):
    s = Svg(920, 400, t["title"])
    s.rect(15, 15, 600, 370, "gray")
    s.text(32, 42, t["b"], size=15, weight=700)
    s.text(32, 64, "print, len, sum, range, round, ...", size=13, mono=True, color=MUTED)
    s.rect(35, 80, 560, 290, "blue")
    s.text(52, 106, t["g"], size=15, weight=700)
    s.text(52, 128, "REPORT_DATE = \"2026-09-30\"", size=13, mono=True)
    s.rect(55, 145, 520, 210, "orange")
    s.text(72, 171, t["e"], size=15, weight=700)
    s.text(72, 193, "def report(loans):", size=13, mono=True)
    s.text(72, 212, "    currency = \"EUR\"", size=13, mono=True)
    s.rect(75, 228, 480, 112, "green")
    s.text(92, 254, t["l"], size=15, weight=700)
    s.text(92, 276, "    def line(amount):", size=13, mono=True)
    s.text(92, 295, "        text = f\"{amount:,.2f} {currency}\"", size=13, mono=True)
    s.text(92, 314, "        return text", size=13, mono=True)
    s.poly([(560, 300), (600, 300), (600, 40)], color=COLORS["red"][1])
    s.text(640, 60, t["order"], size=14, weight=700)
    s.lines(640, 86, [("L -> E -> G -> B", {"mono": True, "weight": 700}), t["first"],
                      (t["none"], {"color": COLORS["red"][1]})], size=14, gap=22)
    s.lines(640, 200, t["assign"], size=13, gap=20)
    return s.render()


# ---------------------------------------------------------------------------
# table-rows: a table as a list of rows - a row, a column, a cell

TABLE = {
    "en": {
        "title": "A table as a list of rows",
        "row": "a row: rows[1]",
        "col": "a column: [row[2] for row in rows]",
        "cell": "a cell: rows[1][2]",
        "cell2": "first the row, then the column",
        "header": "header",
    },
}
TABLE["bg"] = dict(TABLE["en"])   # TODO: Bulgarian texts (the lecture is not translated yet)


def table_rows(t):
    blue, green, orange = COLORS["blue"][1], COLORS["green"][1], COLORS["orange"][1]
    s = Svg(920, 300, t["title"])
    header = ["loan_id", "product", "outstanding", "stage"]
    rows = [["L000001", "investment", "1044231.30", "1"],
            ["L000002", "investment", "651927.30", "2"],
            ["L000003", "credit_card", "644.25", "2"]]
    widths = [130, 150, 150, 80]
    x0, y0, h = 100, 40, 42
    xs = [x0 + sum(widths[:i]) for i in range(len(widths))]
    s.text(x0 - 16, y0 + 27, t["header"], size=13, color=MUTED, anchor="end")
    for j, name in enumerate(header):
        s.rect(xs[j], y0, widths[j], h, "gray", radius=0)
        s.text(xs[j] + widths[j] / 2, y0 + 27, name, size=14, weight=700, mono=True, anchor="middle")
    for i, row in enumerate(rows):
        y = y0 + h * (i + 1) + 8
        s.text(x0 - 16, y + 27, f"rows[{i}]", size=14, mono=True, color=MUTED, anchor="end")
        for j, value in enumerate(row):
            color = "orange" if (i == 1 and j == 2) else "blue" if i == 1 else "green" if j == 2 else "gray"
            s.rect(xs[j], y, widths[j], h, color, radius=0)
            s.text(xs[j] + widths[j] / 2, y + 27, value, size=14, mono=True, anchor="middle")
    right = x0 + sum(widths) + 20
    s.arrow(right + 120, y0 + h * 2 + 8 + 21, right + 4, y0 + h * 2 + 8 + 21, color=blue)
    s.text(right + 128, y0 + h * 2 + 8 + 26, t["row"], size=14, weight=700, color=blue)
    cx = xs[2] + widths[2] / 2
    s.arrow(cx, 262, cx, y0 + h * 4 + 12, color=green)
    s.text(cx, 284, t["col"], size=14, weight=700, color=green, anchor="middle")
    s.text(right + 30, y0 + 16, t["cell"], size=14, weight=700, color=orange)
    s.text(right + 30, y0 + 36, t["cell2"], size=13, color=orange)
    s.arrow(right + 60, y0 + 44, xs[2] + widths[2] - 10, y0 + h * 2 + 12, color=orange, curve=(right + 40, y0 + 90))
    return s.render()


# ---------------------------------------------------------------------------
# dict-lookup: one lookup table in three forms - SAS format, SQL table, Python dict

LOOKUP = {
    "en": {
        "title": "One lookup table, three forms",
        "sas": "SAS: a format", "sql": "SQL: a lookup table", "py": "Python: a dictionary",
        "use": "use it", "missing": "not found",
    },
}
LOOKUP["bg"] = dict(LOOKUP["en"])   # TODO: Bulgarian texts (the lecture is not translated yet)


def dict_lookup(t):
    s = Svg(920, 330, t["title"])
    w, h, y = 280, 210, 20
    boxes = [
        ("orange", t["sas"], ["proc format;", "  value $prod", "    'mortgage'  = 'Mortgage loan'",
                               "    'overdraft' = 'Overdraft'", "    other       = 'Other';", "run;"]),
        ("blue", t["sql"], ["TABLE product_names", "code       name", "---------  -------------",
                             "mortgage   Mortgage loan", "overdraft  Overdraft"]),
        ("green", t["py"], ["product_names = {", '  "mortgage": "Mortgage loan",', '  "overdraft": "Overdraft",',
                             "}"]),
    ]
    uses = [("put(code, $prod.)", "other = 'Other'"),
            ("LEFT JOIN ... ON code", "COALESCE(name, 'Other')"),
            ("product_names[code]", 'product_names.get(code, "Other")')]
    for i, ((color, title, lines), (use, missing)) in enumerate(zip(boxes, uses)):
        x = 15 + i * (w + 20)
        s.rect(x, y, w, h, color)
        s.text(x + 14, y + 26, title, size=16, weight=700)
        s.lines(x + 14, y + 54, [(line, {"mono": True}) for line in lines], size=12, gap=20)
        s.text(x + 14, y + h + 34, t["use"] + ":", size=13, color=MUTED)
        s.text(x + 14, y + h + 54, use, size=13, mono=True)
        s.text(x + 14, y + h + 78, t["missing"] + ":", size=13, color=MUTED)
        s.text(x + 14, y + h + 98, missing, size=12, mono=True)
    return s.render()


# ---------------------------------------------------------------------------
# class-objects: a class is a blueprint; objects are made from it

CLASSOBJ = {
    "en": {
        "title": "A class and two objects",
        "cls": "class Loan  (the blueprint)",
        "obj": "an object (an instance)",
        "made": "Loan(...) makes an object",
        "shared": "the methods are shared by all objects",
    },
}
CLASSOBJ["bg"] = dict(CLASSOBJ["en"])   # TODO: Bulgarian texts (the lecture is not translated yet)


def class_objects(t):
    s = Svg(920, 330, t["title"])
    s.box(20, 30, 330, 270, "blue", t["cls"], [
        ("def __init__(self, loan_id, product,", {"mono": True, "size": 12}),
        ("             amount, outstanding):", {"mono": True, "size": 12}),
        ("    self.loan_id = loan_id", {"mono": True, "size": 12}),
        ("    self.product = product", {"mono": True, "size": 12}),
        ("    ...", {"mono": True, "size": 12}),
        ("", {}),
        ("def repaid_share(self):", {"mono": True, "size": 12}),
        ("    return 1 - self.outstanding", {"mono": True, "size": 12}),
        ("               / self.amount", {"mono": True, "size": 12}),
    ])
    objects = [("first", ["loan_id = 'L000001'", "product = 'investment'", "amount = 1156900.0",
                          "outstanding = 1044231.3"]),
               ("second", ["loan_id = 'L000002'", "product = 'investment'", "amount = 1977400.0",
                           "outstanding = 651927.3"])]
    for i, (name, lines) in enumerate(objects):
        y = 30 + i * 150
        s.box(560, y, 340, 120, "green", f"{name}  -  {t['obj']}", [(l, {"mono": True, "size": 13}) for l in lines],
              title_size=14)
        s.arrow(352, 90 + i * 120, 556, y + 50)
    s.text(455, 160, t["made"], size=13, color=MUTED, anchor="middle")
    s.text(20, 322, t["shared"], size=13, color=MUTED)
    return s.render()


# ---------------------------------------------------------------------------
# nomenclature: the four parts of the client's sentence as the parts of a class

NOMEN = {
    "en": {
        "title": "A nomenclature as a class",
        "parts": [("data", "codes: {code: label}"), ("metadata", "name, version, valid_from, owner"),
                  ("validation rules", "__post_init__, validate(values)"),
                  ("processing methods", "lookup(), apply(rows, ...), the unmapped report")],
        "cls": "class Nomenclature",
        "banded": "BandedNomenclature", "banded2": "ranges: DPD, PD -> grade",
        "hier": "HierarchicalNomenclature", "hier2": "code -> parent",
        "registry": "Registry", "registry2": "has nomenclatures; applies them",
        "isa": "is a", "hasa": "has",
        "datasets": "loans.csv, clients.csv, ratings_history.csv, ...",
    },
}
NOMEN["bg"] = dict(NOMEN["en"])   # TODO: Bulgarian texts (the lecture is not translated yet)


def nomenclature_diagram(t):
    s = Svg(920, 360, t["title"])
    s.rect(20, 20, 430, 250, "blue")
    s.text(40, 48, t["cls"], size=17, weight=700, mono=True)
    for i, (part, how) in enumerate(t["parts"]):
        y = 70 + i * 48
        s.rect(40, y, 390, 40, "gray", radius=6)
        s.text(54, y + 17, part, size=14, weight=700)
        s.text(54, y + 33, how, size=12, mono=True, color=MUTED)
    s.box(520, 20, 380, 60, "green", t["banded"], [t["banded2"]], title_size=15)
    s.box(520, 100, 380, 60, "green", t["hier"], [t["hier2"]], title_size=15)
    s.box(520, 200, 380, 70, "orange", t["registry"], [t["registry2"]], title_size=15)
    s.arrow(516, 50, 454, 80)
    s.text(486, 56, t["isa"], size=12, color=MUTED, anchor="middle")
    s.arrow(516, 130, 454, 130)
    s.text(486, 124, t["isa"], size=12, color=MUTED, anchor="middle")
    s.arrow(516, 235, 454, 220, dash=True)
    s.text(486, 248, t["hasa"], size=12, color=MUTED, anchor="middle")
    s.arrow(710, 272, 710, 310)
    s.text(710, 334, t["datasets"], size=14, mono=True, anchor="middle")
    return s.render()


# ---------------------------------------------------------------------------
# homework-repos (how-to page): the course repository, your repository, your folder

REPOS = {
    "en": {
        "title": "The three copies of the Homework repository",
        "course": "The course repository (GitHub)",
        "name": "name in Git:",
        "course2": "only the trainer changes it",
        "own": "Your own repository (GitHub)",
        "own2": "private; only you change it",
        "pc": "The folder on your computer",
        "pc2": "you write and run the code here, in VS Code",
        "clone": "git clone", "clone2": "once, at the start",
        "pull": "git pull ... upstream main", "pull2": "the new tasks, every session",
        "push": "git push", "push2": "your solutions",
    },
    "bg": {
        "title": "Трите копия на Homework repository",
        "course": "Repository-то на курса (GitHub)",
        "name": "име в Git:",
        "course2": "само преподавателят го променя",
        "own": "Вашето repository (GitHub)",
        "own2": "частно (private); само вие го променяте",
        "pc": "Папката на вашия компютър",
        "pc2": "тук пишете и пускате кода, във VS Code",
        "clone": "git clone", "clone2": "веднъж, в началото",
        "pull": "git pull ... upstream main", "pull2": "новите задачи, всяко занятие",
        "push": "git push", "push2": "вашите решения",
    },
}


def homework_repos(t):
    s = Svg(920, 380, t["title"])
    s.box(20, 16, 390, 116, "blue", t["course"], [
        ("Python-Data-Analysts-UniCredit-Homework", {"mono": True, "size": 13}),
        (t["name"] + " upstream", {"mono": False}),
        (t["course2"], {"color": MUTED, "size": 13})])
    s.box(510, 16, 390, 116, "green", t["own"], [
        ("your-user/python-course-homework", {"mono": True, "size": 13}),
        (t["name"] + " origin", {"mono": False}),
        (t["own2"], {"color": MUTED, "size": 13})])
    s.box(210, 252, 500, 112, "orange", t["pc"], [
        ("C:\\Users\\you\\python-course\\", {"mono": True, "size": 13}),
        ("    Python-Data-Analysts-UniCredit-Homework\\", {"mono": True, "size": 13}),
        (t["pc2"], {"color": MUTED, "size": 13})])
    s.arrow(110, 134, 270, 250, dash=True)
    s.text(52, 178, t["clone"], size=14, mono=True, weight=700)
    s.text(52, 197, t["clone2"], size=13, color=MUTED)
    s.arrow(250, 134, 360, 250)
    s.text(300, 166, t["pull"], size=14, mono=True, weight=700)
    s.text(300, 185, t["pull2"], size=13, color=MUTED)
    s.arrow(600, 250, 700, 134)
    s.text(668, 196, t["push"], size=14, mono=True, weight=700)
    s.text(668, 215, t["push2"], size=13, color=MUTED)
    return s.render()


# ---------------------------------------------------------------------------
# terminal-prompt (how-to page): the parts of the prompt in the terminal

PROMPT = {
    "en": {
        "title": "The terminal: the prompt and a command",
        "venv": ["(.venv): the virtual", "environment is on"],
        "folder": ["the current folder:", "the commands work here"],
        "cmd": ["your command;", "Enter runs it"],
        "out": "the answer of the command",
        "again": "the prompt again: ready for the next command",
    },
    "bg": {
        "title": "Терминалът: промптът и една команда",
        "venv": ["(.venv): виртуалната", "среда е активна"],
        "folder": ["текущата папка:", "командите работят тук"],
        "cmd": ["вашата команда;", "Enter я изпълнява"],
        "out": "отговорът на командата",
        "again": "промптът отново: готов за следващата команда",
    },
}


def terminal_prompt(t):
    s = Svg(920, 290, t["title"])
    s.rect(10, 80, 900, 160, "gray", radius=8)
    cw, x0 = 9.2, 24        # the width of one character, forced with textLength
    parts = [("(.venv) ", COLORS["green"][1], 400),
             ("C:\\Users\\you\\python-course\\Python-Data-Analysts-UniCredit-Homework", COLORS["blue"][1], 400),
             (">", INK, 400), ("git status", INK, 700)]

    def mono_line(x, y, text, color=INK, weight=400):
        s.raw(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="15" font-weight="{weight}" fill="{color}" '
              f'textLength="{len(text) * cw:.1f}" lengthAdjust="spacingAndGlyphs" xml:space="preserve">{escape(text)}</text>')

    spans, x = [], x0
    for text, color, weight in parts:
        mono_line(x, 120, text, color, weight)
        spans.append((x, x + len(text) * cw))
        x += len(text) * cw
    mono_line(x0, 148, "On branch main", MUTED)
    mono_line(x0, 170, "Your branch is up to date with 'origin/main'.", MUTED)
    prompt = "(.venv) C:\\Users\\you\\python-course\\Python-Data-Analysts-UniCredit-Homework>"
    mono_line(x0, 212, prompt)
    cursor = x0 + len(prompt) * cw + 2
    s.raw(f'<rect x="{cursor:.1f}" y="198" width="9" height="18" fill="{INK}"/>')
    # brackets over the parts of the first line, and their labels above the terminal
    for (a, b), label, anchor in zip((spans[0], spans[1], spans[3]), (t["venv"], t["folder"], t["cmd"]),
                                     ("start", "middle", "end")):
        a, b = a + 1, (b - 8 if label is t["venv"] else b - 1)
        s.raw(f'<path d="M{a:.1f},104 L{a:.1f},98 L{b:.1f},98 L{b:.1f},104" fill="none" stroke="{MUTED}" '
              f'stroke-width="1.6"/>')
        mid = (a + b) / 2
        s.raw(f'<path d="M{mid:.1f},98 L{mid:.1f},52" fill="none" stroke="{MUTED}" stroke-width="1.6" '
              f'stroke-dasharray="3 3"/>')
        tx = {"start": a, "middle": mid, "end": b}[anchor]
        s.lines(tx, 22, label, size=14, gap=19, anchor=anchor)
    s.raw(f'<path d="M{x0 + 46 * cw + 6:.1f},166 L{x0 + 52 * cw:.1f},166" fill="none" stroke="{MUTED}" '
          f'stroke-width="1.6"/>')
    s.text(x0 + 52 * cw + 8, 171, t["out"], size=14, color=MUTED)
    s.arrow(cursor + 5, 262, cursor + 5, 222)
    s.text(cursor - 6, 278, t["again"], size=14, anchor="end")
    return s.render()


# ---------------------------------------------------------------------------
# vscode-window (how-to page): the parts of VS Code used for the tasks.
# The texts are the English menus and files of VS Code, the same in both languages.

VSCODE = {"en": {"title": "VS Code with the Homework folder"},
          "bg": {"title": "VS Code с папката Homework"}}


def vscode_window(t):
    s = Svg(950, 560, t["title"])
    white, side, bar = "#ffffff", "#f7f6f3", "#ebe8e1"
    s.raw('<g transform="translate(30,0)">')      # room on the left for the number 4

    def fill(x, y, w, h, color, stroke=None, radius=0):
        line = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ""
        s.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}"{line}/>')

    def mark(x, y, n):
        s.raw(f'<circle cx="{x}" cy="{y}" r="12" fill="{COLORS["red"][1]}"/>')
        s.text(x, y + 5, str(n), size=14, weight=700, color="#ffffff", anchor="middle")

    # the window, the title bar with the menus and the command center
    fill(10, 10, 900, 540, white, COLORS["gray"][1], radius=8)
    fill(11, 11, 898, 30, bar, radius=7)
    s.text(24, 31, "File   Edit   Selection   View   Go   Run   Terminal   Help", size=12)
    fill(470, 17, 300, 18, white, COLORS["gray"][1], radius=5)
    s.text(620, 30, "Python-Data-Analysts-UniCredit-Homework", size=11, color=MUTED, anchor="middle")
    # the activity bar and its icons: Explorer, Search, Source Control, Run, Extensions
    fill(11, 41, 44, 479, bar)
    s.raw(f'<rect x="11" y="44" width="3" height="32" fill="{COLORS["blue"][1]}"/>')
    ink = f'fill="none" stroke="{MUTED}" stroke-width="1.8"'
    s.raw(f'<path d="M24,51 h11 l5,5 v15 h-16 z M29,51 v-3 h11 l5,5 v15 h-5" {ink}/>')
    s.raw(f'<circle cx="31" cy="98" r="6" {ink}/><path d="M35,103 L41,109" {ink}/>')
    s.raw(f'<circle cx="27" cy="134" r="3" {ink}/><circle cx="27" cy="152" r="3" {ink}/>'
          f'<circle cx="39" cy="140" r="3" {ink}/><path d="M27,137 v12 M39,143 q0,6 -12,6" {ink}/>')
    s.raw(f'<path d="M25,174 L39,182 L25,190 z" {ink}/>')
    s.raw(f'<path d="M23,212 h7 v7 h-7 z M23,221 h7 v7 h-7 z M32,221 h7 v7 h-7 z M34,208 h7 v7 h-7 z" {ink}/>')
    # the Explorer
    fill(55, 41, 280, 479, side)
    s.text(70, 62, "EXPLORER", size=11, weight=700, color=MUTED)
    s.text(66, 86, "v PYTHON-DATA-ANALYSTS-UNICREDIT-HOMEWORK", size=10, weight=700)
    tree = [(0, "> .venv"), (0, "> .vscode"), (0, "v 01-intro-syntax-types"), (1, "v practice"),
            (2, "task1-first-values.py"), (2, "task2-predict-types.py"), (2, "..."), (1, "homework.py"),
            (0, "> 02-conditions-and-loops"), (0, "> data"), (0, "check.py"), (0, "README.md"),
            (0, "requirements.txt")]
    for i, (level, name) in enumerate(tree):
        y = 110 + i * 22
        if name.startswith("task1"):
            fill(56, y - 15, 278, 21, COLORS["blue"][0])
        s.text(78 + level * 16, y, name, size=12.5)
    # the editor: the tab, the Run button, the code
    fill(335, 41, 574, 30, side)
    fill(335, 41, 170, 30, white)
    s.raw(f'<rect x="335" y="41" width="170" height="2" fill="{COLORS["blue"][1]}"/>')
    s.text(349, 61, "task1-first-values.py", size=12)
    s.raw(f'<path d="M846,49 L860,56 L846,63 z" fill="none" stroke="{COLORS["green"][1]}" stroke-width="2"/>')
    s.raw(f'<path d="M868,54 l4,4 l4,-4" {ink}/>')
    code = [("# == Part 1: the values of one row ==", MUTED), ("", INK),
            ("# ---- your code: part 1 ----", MUTED), ('loan_id = "L000001"', INK), ("currency = None", INK),
            ("outstanding = None", INK), ("# ---- end of your code ----", MUTED), ("", INK),
            ('check("loan_id", loan_id, "L000001")', INK)]
    fill(377, 147, 515, 64, COLORS["orange"][0])
    for i, (line, color) in enumerate(code):
        y = 98 + i * 21
        s.text(365, y, str(10 + i), size=12, mono=True, color=MUTED, anchor="end")
        s.text(385, y, line, size=12.5, mono=True, color=color)
    # the panel with the terminal
    s.raw(f'<path d="M335,300 H909" stroke="{COLORS["gray"][1]}" stroke-width="1.5"/>')
    s.text(349, 322, "PROBLEMS     OUTPUT     DEBUG CONSOLE", size=11, color=MUTED)
    s.text(605, 322, "TERMINAL", size=11, weight=700)
    s.raw(f'<rect x="605" y="328" width="60" height="2" fill="{COLORS["blue"][1]}"/>')
    s.text(752, 322, "cmd", size=12, color=MUTED)
    s.text(790, 323, "+", size=17, weight=700, color=MUTED)
    s.raw(f'<path d="M806,315 l4,4 l4,-4" {ink}/>')
    s.raw(f'<path d="M828,312 h14 M831,312 v-2 h8 v2 M830,314 l1,12 h8 l1,-12" {ink}/>')
    output = [("OK   loan_id", COLORS["green"][1]),
              ("FAIL currency: got None (NoneType), expected 'EUR' (str)", COLORS["red"][1]),
              ("...", INK), ("1 of 8 checks passed", INK), ("", INK),
              ("(.venv) C:\\Users\\you\\python-course\\Python-Data-Analysts-UniCredit-Homework>", INK)]
    for i, (line, color) in enumerate(output):
        s.text(349, 356 + i * 20, line, size=11.5, mono=True, color=color)
    # the status bar
    fill(11, 520, 898, 29, COLORS["blue"][0], radius=0)
    s.raw(f'<path d="M11,520 H909" stroke="{COLORS["blue"][1]}" stroke-width="1.5"/>')
    s.text(24, 539, "main", size=12)
    s.text(895, 539, "Python 3.13.9 (.venv)", size=12, anchor="end")
    # the numbers, explained under the picture
    mark(160, 57, 1)
    mark(826, 56, 2)
    mark(732, 318, 3)
    mark(-14, 143, 4)
    mark(740, 535, 5)
    s.raw('</g>')
    return s.render()


# ---------------------------------------------------------------------------
# map-filter: map changes every item, filter keeps some items

MAPF = {
    "en": {
        "title": "map and filter: one function, applied to every item",
        "map": "map: every item changes", "filter": "filter: only some items stay",
        "fmap": "d // 30", "ffilter": "d > 30 ?",
        "nmap": "5 items in, 5 items out", "nfilter": "5 items in, 2 items out",
        "no": "no",
        "cmap": "the same: [d // 30 for d in days]", "cfilter": "the same: [d for d in days if d > 30]",
        "smap": "SQL: SELECT expression", "sfilter": "SQL: WHERE",
    },
    "bg": {
        "title": "map и filter: една функция, приложена върху всеки елемент",
        "map": "map: всеки елемент се променя", "filter": "filter: остават само някои елементи",
        "fmap": "d // 30", "ffilter": "d > 30 ?",
        "nmap": "5 елемента влизат, 5 излизат", "nfilter": "5 елемента влизат, 2 излизат",
        "no": "не",
        "cmap": "същото: [d // 30 for d in days]", "cfilter": "същото: [d for d in days if d > 30]",
        "smap": "SQL: SELECT израз", "sfilter": "SQL: WHERE",
    },
}


def map_filter(t):
    days = [0, 35, 0, 120, 15]
    red = COLORS["red"][1]
    s = Svg(920, 400, t["title"])
    w, gap, yin, ybar, yout = 70, 10, 104, 176, 256
    for px, key, code, fn, color in ((20, "map", "map(lambda d: d // 30, days)", "fmap", "orange"),
                                     (480, "filter", "filter(lambda d: d > 30, days)", "ffilter", "violet")):
        s.text(px, 28, t[key], size=16, weight=700)
        s.text(px, 54, code, size=14, mono=True)
        s.text(px, 80, "days", size=12, mono=True, color=MUTED)
        x0 = px + 10
        s.rect(x0 - 6, ybar, 5 * w + 4 * gap + 12, 40, color, radius=6)
        s.text(x0 + (5 * w + 4 * gap) / 2, ybar + 26, t[fn], size=16, weight=700, mono=True, anchor="middle")
        for i, d in enumerate(days):
            x = x0 + i * (w + gap)
            cx = x + w / 2
            s.rect(x, yin, w, 44, "gray", radius=4)
            s.text(cx, yin + 28, str(d), size=16, mono=True, anchor="middle")
            s.arrow(cx, yin + 46, cx, ybar - 4)
            if key == "map":
                keep, out = True, str(d // 30)
            else:
                keep, out = d > 30, str(d)
            if keep:
                s.arrow(cx, ybar + 42, cx, yout - 4)
                s.rect(x, yout, w, 44, "green", radius=4)
                s.text(cx, yout + 28, out, size=16, mono=True, anchor="middle")
            else:
                s.text(cx, yout + 28, t["no"], size=14, weight=700, color=red, anchor="middle")
        s.text(px, yout + 76, t["n" + key], size=14, weight=700)
        s.text(px, yout + 100, t["c" + key], size=14, mono=True)
        s.text(px, yout + 124, t["s" + key], size=14, color=MUTED)
    s.raw(f'<path d="M460,16 L460,388" stroke="{COLORS["gray"][1]}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    return s.render()


DIAGRAMS = {"run-python": (run_python, RUN), "venv": (venv, VENV),
            "if-elif-else": (if_elif_else, IFS), "loop-simple": (loop_simple, LOOPS), "loop-flow": (loop_flow, LOOP),
            "list-indexing": (list_indexing, INDEX), "list-slicing": (list_slicing, SLICE), "set-operations": (set_operations, SETS),
            "map-filter": (map_filter, MAPF),
            "scope-legb": (scope_legb, LEGB),
            "table-rows": (table_rows, TABLE),
            "dict-lookup": (dict_lookup, LOOKUP),
            "class-objects": (class_objects, CLASSOBJ),
            "nomenclature": (nomenclature_diagram, NOMEN),
            "homework-repos": (homework_repos, REPOS),
            "terminal-prompt": (terminal_prompt, PROMPT),
            "vscode-window": (vscode_window, VSCODE)}

if __name__ == "__main__":
    for name, (draw, texts) in DIAGRAMS.items():
        for lang, folder in (("en", OUT), ("bg", OUT / "bg")):
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{name}.svg").write_text(draw(texts[lang]), encoding="utf-8")
            print("wrote", (folder / f"{name}.svg").relative_to(OUT.parents[2]))
