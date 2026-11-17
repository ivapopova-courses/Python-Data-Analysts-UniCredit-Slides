# Glossary - English to Bulgarian

The rule: **a programming term stays in English** when the Bulgarian word would hide
the English one the readers meet in documentation, error messages and code
(`list`, not "списък", when it means the Python type; `DataFrame`, not "таблица").
A term that is the same word in both languages is written in Bulgarian (функция,
обект, метод, оператор, модул). Everyday words are translated (стойност, условие,
грешка). The readers know SQL and SAS: their terms (JOIN, GROUP BY, DATA step,
PROC SORT) stay as they are.

Started on 2026-10-24 with the course structure; add the terms of each lecture when
it is written (lecture 1: added 2026-10-24; lectures 2 - 4: added 2026-10-25).

The words of every course site (session, lecture, homework, "Check yourself", the
buttons), a few basic programming words and the rule above in full are in the common
glossary of the course kit: `node_modules/@sciscend/course-kit/i18n/glossary-common.md`.
This file has the terms of this course; where the two differ, this file wins.

## Stays in English

Written in Latin letters, without quotes or backticks. Plural in English
("lists", "dictionaries"). Avoid a Bulgarian article where you can ("в този list",
"елементите на list"); where you cannot, add it with a hyphen: "list-ът",
"DataFrame-ът", "string-ът".

| Term | Note |
|---|---|
| list, tuple, set, dict / dictionary | the Python types; an ordinary list (of tasks, of names) is "списък" |
| string, strings | the type and its values: "стойност от тип string" |
| int, float, bool, None | the types, written as in code |
| f-string | |
| list comprehension, dict comprehension | |
| slice, slicing | |
| lambda | |
| scope | |
| docstring, type hints | |
| exception, traceback | "exception-ът"; an ordinary error is "грешка" (below) |
| virtual environment, venv, pip, package | "виртуална среда (virtual environment)" at first use, then "venv" |
| notebook, Jupyter, cell, kernel | "notebook-ът", "клетка" is also fine for cell |
| class, instance, attribute, property, dataclass | "class" for the Python keyword; "клас" is fine in plain text |
| NumPy, pandas, array, ndarray, broadcasting | |
| Series, DataFrame, index, column | the pandas objects; "колона" is fine for column in plain text |
| groupby, merge, join, pivot table | as in pandas / SQL |
| regular expression, regex, pattern, group | |
| repository, commit, push, pull, branch, merge, pull request | verbs: "направете commit", "качете с push" |
| SQL, SAS, DATA step, PROC | terms of the tools the readers know |
| statement | "statement-ът"; "statement по statement" (lecture 1) |
| bytecode, REPL, garbage collector | "bytecode-ът", "garbage collector-ът" |
| escape sequence, raw string | |
| dynamic typing, immutable | at first use with the Bulgarian: "динамично типизиране (dynamic typing)", "непроменими (immutable)" |
| truthy, falsy | |
| banker's rounding | "банкерското закръгляне (banker's rounding)" |
| iterable, iteration | "iterable"; iteration is "итерация" |
| pattern, guard, `match` / `case` | lecture 2: "pattern", "guard" |
| short-circuit evaluation | |
| mutable, hashable | at first use with the Bulgarian: "променяема (mutable)"; then either |
| named tuple, frozenset | |
| keyword-only, positional-only | the kinds of parameters |
| namespace, LEGB | "namespace" |
| closure, dispatch table | |
| higher-order function | "функция от по-висок ред (higher-order function)" at first use |
| Pylance, mypy, PEP | tools and documents |
| generator, generator expression | "generator-ът"; lecture 5 (2026-11-08) |
| linter, formatter, Ruff | "linter-ът", "formatter-ът" (how-to page, 2026-11-04) |
| match object, flag, lookaround, verbose pattern | lecture 7 (2026-11-15): "match обект"; "флаг (flag)" at first use |
| greedy, lazy | lecture 7: greedy ("лакоми"), lazy ("мързелив") at first use |
| named group, locale, BOM, mojibake | lecture 7: "именувана group" |
| loader, log, handler | lecture 8 (2026-11-16): "програма за зареждане (loader)" at first use, then "loader-ът"; "log-ът" |

## Translated

| English | Bulgarian |
|---|---|
| variable | променлива |
| default value | стойност по подразбиране |
| comparison | сравнение |
| expression | израз |
| assignment | присвояване |
| object | обект |
| key, value (of a dictionary) | ключ, стойност |
| row, record | ред, запис |
| type | тип |
| missing value | липсваща стойност |
| file, folder | файл, папка |
| report | отчет |
| dataset, data | набор от данни, данни |
| loan, client, portfolio | кредит, клиент, портфейл |
| exposure, outstanding amount | експозиция, непогасена сума |
| rating, rating scale | рейтинг, рейтингова скала |
| nomenclature | номенклатура |
| indentation, indented | отстъп, отместен навътре |
| interpreter, compiler, virtual machine | интерпретатор, компилатор, виртуална машина |
| implementation (CPython, PyPy) | реализация (implementation) |
| keyword (of Python) | ключова дума |
| augmented assignment | съкратено присвояване |
| floor division, modulo | целочислено деление, остатък от деление |
| rounding, to round | закръгляне, закръглям |
| workspace (VS Code) | работно пространство (workspace) |
| cell (notebook) | клетка |
| days past due | дни просрочие |
| loan card (homework 1) | карта на кредит |
| loop, loops | цикъл, цикли: "цикълът", "цикъла"; "`for` loop" is "цикъл `for`", "nested loops" is "вложени цикли" (Iva, 2026-10-25) |
| bucket (of days past due) | група |
| stage (IFRS 9) | етап |
| repayment schedule, annuity loan | погасителен план, анюитетен кредит |
| accumulator | акумулатор |
| to unpack, unpacking | разопаковам, разопаковане (unpacking) |
| sequence | поредица |
| the top N | първите N (lecture 5) |
| union, intersection, difference | обединение, сечение, разлика |
| shallow copy, deep copy | плитко копие, дълбоко копие |
| control flow statements | конструкции за управление |
| conditional expression | условен израз |
| keyword argument, positional argument | именуван аргумент, позиционен аргумент |
| return value, to return | върната стойност, връщам |
| to call, call | извиквам, извикване |
| pure function, side effect | чиста функция, страничен ефект |
| decorator | декоратор |
| case (upper / lower) | регистър (lecture 7, 2026-11-15) |
| quantifier | квантификатор |
| back-reference | обратна препратка |
| encoding | кодировка |
| check digit | контролна цифра |
| legal form | правна форма |
| maturity (of a loan) | падеж |
| EIK | ЕИК |
| reject file (of a loader) | файл с отхвърлените редове (lecture 8) |
| to raise (an exception) | предизвиквам (raise) at first use; "raise" alone in short cells |
| mode (of `open`) | режим |
| workbook, sheet (Excel) | работна книга (workbook), лист (sheet) at first use |
| grade (of the rating scale) | оценка |
