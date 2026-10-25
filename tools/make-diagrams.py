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
        "title": "Indexes and slices of a list",
        "pos": "index from the start", "neg": "index from the end",
        "slice": "loans[1:4] - from index 1 up to 4, without 4",
        "examples": "Examples:",
        "every2": "loans[::2]  -> every 2nd", "reversed": "loans[::-1] -> reversed", "copy": "loans[:]    -> a copy",
    },
    "bg": {
        "title": "Индекси и срезове на списък",
        "pos": "индекс от началото", "neg": "индекс от края",
        "slice": "loans[1:4] - от индекс 1 до 4, без 4",
        "examples": "Примери:",
        "every2": "loans[::2]  -> всеки 2-ри", "reversed": "loans[::-1] -> обърнат", "copy": "loans[:]    -> копие",
    },
}


def list_indexing(t):
    green = COLORS["green"][1]
    blue = COLORS["blue"][1]
    orange = COLORS["orange"][1]
    s = Svg(920, 330, t["title"])
    items = ["L01", "L02", "L03", "L04", "L05", "L06"]
    x0, w, y = 190, 105, 82
    s.text(20, 30, "loans = [\"L01\", \"L02\", \"L03\", \"L04\", \"L05\", \"L06\"]", size=15, mono=True)
    s.text(x0 - 14, y - 12, t["pos"], size=12, color=green, anchor="end")
    s.text(x0 - 14, y + 92, t["neg"], size=12, color=blue, anchor="end")
    for i, item in enumerate(items):
        x = x0 + i * w
        s.rect(x, y, w, 56, "orange" if 1 <= i <= 3 else "gray", radius=4)
        s.text(x + w / 2, y + 35, f'"{item}"', size=16, mono=True, anchor="middle")
        s.text(x + w / 2, y - 12, str(i), size=16, weight=700, mono=True, color=green, anchor="middle")
        s.text(x + w / 2, y + 92, str(i - len(items)), size=16, weight=700, mono=True, color=blue, anchor="middle")
    # the slice bracket
    s.poly([(x0 + w + 4, 180), (x0 + w + 4, 190), (x0 + 4 * w - 4, 190), (x0 + 4 * w - 4, 180)], color=orange,
           head=False)
    s.text(x0 + 2.5 * w, 210, t["slice"], size=14, weight=700, color=orange, anchor="middle")
    s.text(20, 238, t["examples"], size=13, weight=700, color=MUTED)
    s.lines(20, 262, [('loans[0]    -> "L01"', {"mono": True}), ('loans[-1]   -> "L06"', {"mono": True}),
                      ('loans[2]    -> "L03"', {"mono": True})], size=14, gap=21)
    s.lines(330, 262, [('loans[1:4]  -> ["L02", "L03", "L04"]', {"mono": True}),
                       ('loans[:2]   -> ["L01", "L02"]', {"mono": True}),
                       ('loans[-2:]  -> ["L05", "L06"]', {"mono": True})], size=14, gap=21)
    s.lines(700, 262, [(t["every2"], {"mono": True}), (t["reversed"], {"mono": True}),
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


DIAGRAMS = {"run-python": (run_python, RUN), "venv": (venv, VENV),
            "if-elif-else": (if_elif_else, IFS), "loop-flow": (loop_flow, LOOP),
            "list-indexing": (list_indexing, INDEX), "set-operations": (set_operations, SETS),
            "scope-legb": (scope_legb, LEGB),
            "table-rows": (table_rows, TABLE),
            "dict-lookup": (dict_lookup, LOOKUP),
            "class-objects": (class_objects, CLASSOBJ),
            "nomenclature": (nomenclature_diagram, NOMEN)}

if __name__ == "__main__":
    for name, (draw, texts) in DIAGRAMS.items():
        for lang, folder in (("en", OUT), ("bg", OUT / "bg")):
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{name}.svg").write_text(draw(texts[lang]), encoding="utf-8")
            print("wrote", (folder / f"{name}.svg").relative_to(OUT.parents[2]))
