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
| Run, Edit, Reset, Present, OK, FAIL | buttons and output of the site and the tasks |
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

## Translated

| English | Bulgarian |
|---|---|
| value | стойност |
| variable | променлива |
| default value | стойност по подразбиране |
| condition | условие |
| comparison | сравнение |
| operator, operand | оператор, операнд |
| expression | израз |
| assignment | присвояване |
| function, method | функция, метод |
| parameter, argument | параметър, аргумент |
| object | обект |
| key, value (of a dictionary) | ключ, стойност |
| index, element | индекс, елемент |
| row, record | ред, запис |
| type | тип |
| to convert, conversion | преобразувам, преобразуване |
| missing value | липсваща стойност |
| module, library | модул, библиотека |
| error, bug | грешка, бъг |
| file, folder | файл, папка |
| report | отчет |
| dataset, data | набор от данни, данни |
| loan, client, portfolio | кредит, клиент, портфейл |
| exposure, outstanding amount | експозиция, непогасена сума |
| rating, rating scale | рейтинг, рейтингова скала |
| nomenclature | номенклатура |
| session | занятие |
| lecture | лекция |
| practice, practice task | упражнение, задача за упражнение |
| homework | домашно |
| task, check | задача, проверка |
| Check yourself | Проверете се |
| Answer | Отговор |
| Summary | Обобщение |
| Read more | Още за четене |
| Next session | Следващото занятие |
| Today you will learn to | Днес ще се научите да |
| academic hours | учебни часа |
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
| union, intersection, difference | обединение, сечение, разлика |
| shallow copy, deep copy | плитко копие, дълбоко копие |
| control flow statements | конструкции за управление |
| conditional expression | условен израз |
| keyword argument, positional argument | именуван аргумент, позиционен аргумент |
| return value, to return | върната стойност, връщам |
| to call, call | извиквам, извикване |
| pure function, side effect | чиста функция, страничен ефект |
| decorator | декоратор |
