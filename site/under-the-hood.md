---
title: Animations
---

# Animations

Step-by-step animations that show what Python does **under the hood**: what a
variable really is, and in which order an expression is calculated.

Each animation has several **scenarios** (tabs at the top). A link below opens
one scenario in a new tab.

- **Next step:** Right arrow or `Space`. **Back:** Left arrow. **Start:** `Home`.
  **Auto-play:** `P`.
- `file.html#3` opens scenario 3, `file.html#3.5` opens scenario 3 at step 5.
- Scenarios marked **advanced** go deeper.

::: info English and Bulgarian
Every animation is in English and in Bulgarian. The **EN / BG** button at the top
of an animation switches the language and keeps the current step.
:::

## Session 1 - Introduction, syntax, data types and variables

**[Names and objects](animations/namesAndObjects.html){target="_blank"}** -
a variable is a name bound to an object; assignment, a new value, two names for one
object, `x = x + 1`, dynamic typing, `is` and `==`.
[1. A name and an object](animations/namesAndObjects.html#1){target="_blank"},
[2. A new value](animations/namesAndObjects.html#2){target="_blank"},
[3. Two names, one object](animations/namesAndObjects.html#3){target="_blank"},
[4. `x = x + 1`](animations/namesAndObjects.html#4){target="_blank"},
[5. Types belong to objects](animations/namesAndObjects.html#5){target="_blank"},
[6. Several names at once](animations/namesAndObjects.html#6){target="_blank"},
[7. `is` and `==` (advanced)](animations/namesAndObjects.html#7){target="_blank"}

**[How an expression is evaluated](animations/expressionEvaluation.html){target="_blank"}** -
the order of operations, step by step, with the table of priorities.
[1. Precedence](animations/expressionEvaluation.html#1){target="_blank"},
[2. Brackets](animations/expressionEvaluation.html#2){target="_blank"},
[3. `**` and minus](animations/expressionEvaluation.html#3){target="_blank"},
[4. `//` and `%`](animations/expressionEvaluation.html#4){target="_blank"},
[5. Chained comparisons](animations/expressionEvaluation.html#5){target="_blank"},
[6. `and` / `or`](animations/expressionEvaluation.html#6){target="_blank"},
[7. Mixed types](animations/expressionEvaluation.html#7){target="_blank"}

## Session 2 - Conditional statements and loops

**[Loops step by step](animations/loopTrace.html){target="_blank"}** -
the variables, the test and the output of `if` / `elif` / `else`, `for`, `while`,
`break` and `continue`, one line at a time.
[1. `for` with an accumulator](animations/loopTrace.html#1){target="_blank"},
[2. Decisions in a loop](animations/loopTrace.html#2){target="_blank"},
[3. `while`: repay a loan](animations/loopTrace.html#3){target="_blank"},
[4. `break`: stop at the first](animations/loopTrace.html#4){target="_blank"},
[5. `continue`: skip a record](animations/loopTrace.html#5){target="_blank"},
[6. `for` - `else` (advanced)](animations/loopTrace.html#6){target="_blank"}

## Session 3 - Lists (basics), tuples and sets

**[Lists and references](animations/listsAndReferences.html){target="_blank"}** -
a list changes in place; two names for one list; copies; `sort()` and `sorted()`;
tuples that cannot change.
[1. A list changes in place](animations/listsAndReferences.html#1){target="_blank"},
[2. Two names, one list](animations/listsAndReferences.html#2){target="_blank"},
[3. A copy](animations/listsAndReferences.html#3){target="_blank"},
[4. `sort()` and `sorted()`](animations/listsAndReferences.html#4){target="_blank"},
[5. A tuple cannot change](animations/listsAndReferences.html#5){target="_blank"},
[6. A list inside a tuple (advanced)](animations/listsAndReferences.html#6){target="_blank"}

## Session 4 - Functions

**[Function calls step by step](animations/functionCalls.html){target="_blank"}** -
each call gets a frame with its local names; `return`; local and global names; calls
in calls; a list passed to a function.
[1. A call and a return](animations/functionCalls.html#1){target="_blank"},
[2. Local and global](animations/functionCalls.html#2){target="_blank"},
[3. `UnboundLocalError`](animations/functionCalls.html#3){target="_blank"},
[4. A function calls a function](animations/functionCalls.html#4){target="_blank"},
[5. A list passed to a function](animations/functionCalls.html#5){target="_blank"},
[6. A list as a default value (advanced)](animations/functionCalls.html#6){target="_blank"}

## Session 6 - Dictionaries

**[Grouping by hand](animations/groupingByHand.html){target="_blank"}** -
a dictionary as a lookup table, and as the result of a `GROUP BY` that grows row by
row: a lookup with a default, counting with `get`, sums with `defaultdict`, groups of
rows in lists, and a join by key.
[1. A lookup](animations/groupingByHand.html#1){target="_blank"},
[2. Count with `get`](animations/groupingByHand.html#2){target="_blank"},
[3. Sum with `defaultdict`](animations/groupingByHand.html#3){target="_blank"},
[4. Group into lists](animations/groupingByHand.html#4){target="_blank"},
[5. The join by key](animations/groupingByHand.html#5){target="_blank"}
