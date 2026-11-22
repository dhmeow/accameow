# Question formatting review

This is a **manual-review list**, not a claim that every listed question is broken. The flags are based on the extracted question data and identify likely context/explanation contamination or long table-like content that should be checked against the PDF.

**Where to edit:** `js/questions.js`. Search for the exact `id` shown below (for example, `ch1-q8`). Each question object contains `context`, `question`, `options` or `matrixRows`, `explanation`, `answerText`, and `sourcePage`. Keep the answer key intact when editing.

## Questions to inspect

| Chapter | Question | PDF page | Question ID | Review flag |
|---:|---:|---:|---|---|
| 1 | 8 | 10 | `ch1-q8` | Tutorial note appears in the context field; check whether it belongs in the explanation instead. |
| 1 | 17 | 13 | `ch1-q17` | Long context (802 characters); inspect line breaks and table/paragraph formatting. |
| 2 | 7 | 19 | `ch2-q7` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (1015 characters); inspect line breaks and table/paragraph formatting. |
| 2 | 8 | 19 | `ch2-q8` | Long context (700 characters); inspect line breaks and table/paragraph formatting. |
| 3 | 10 | 25 | `ch3-q10` | Long context (826 characters); inspect line breaks and table/paragraph formatting. |
| 3 | 12 | 27 | `ch3-q12` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (725 characters); inspect line breaks and table/paragraph formatting. |
| 4 | 3 | 29 | `ch4-q3` | Worked answer/explanation appears before the question; verify context/explanation split. |
| 4 | 5 | 30 | `ch4-q5` | Worked answer/explanation appears before the question; verify context/explanation split. |
| 4 | 6 | 31 | `ch4-q6` | Long context (531 characters); inspect line breaks and table/paragraph formatting. |
| 4 | 9 | 32 | `ch4-q9` | Tutorial note appears in the context field; check whether it belongs in the explanation instead. |
| 4 | 14 | 34 | `ch4-q14` | Worked answer/explanation appears before the question; verify context/explanation split. |
| 5 | 2 | 37 | `ch5-q2` | Long context (550 characters); inspect line breaks and table/paragraph formatting. |
| 5 | 6 | 40 | `ch5-q6` | Long context (654 characters); inspect line breaks and table/paragraph formatting. |
| 5 | 9 | 41 | `ch5-q9` | Long context (799 characters); inspect line breaks and table/paragraph formatting. |
| 5 | 10 | 43 | `ch5-q10` | Long context (1156 characters); inspect line breaks and table/paragraph formatting. |
| 5 | 16 | 46 | `ch5-q16` | Long context (686 characters); inspect line breaks and table/paragraph formatting. |
| 6 | 4 | 49 | `ch6-q4` | Long context (548 characters); inspect line breaks and table/paragraph formatting. |
| 6 | 6 | 51 | `ch6-q6` | Worked answer/explanation appears before the question; verify context/explanation split.<br>Long context (640 characters); inspect line breaks and table/paragraph formatting. |
| 6 | 7 | 51 | `ch6-q7` | Long context (839 characters); inspect line breaks and table/paragraph formatting. |
| 6 | 8 | 52 | `ch6-q8` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (825 characters); inspect line breaks and table/paragraph formatting. |
| 6 | 9 | 53 | `ch6-q9` | Long context (1083 characters); inspect line breaks and table/paragraph formatting. |
| 7 | 4 | 57 | `ch7-q4` | Long context (570 characters); inspect line breaks and table/paragraph formatting. |
| 7 | 5 | 58 | `ch7-q5` | Long context (676 characters); inspect line breaks and table/paragraph formatting. |
| 7 | 6 | 59 | `ch7-q6` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (953 characters); inspect line breaks and table/paragraph formatting. |
| 8 | 7 | 66 | `ch8-q7` | Long context (579 characters); inspect line breaks and table/paragraph formatting. |
| 8 | 9 | 67 | `ch8-q9` | Long context (550 characters); inspect line breaks and table/paragraph formatting. |
| 8 | 12 | 69 | `ch8-q12` | Long context (537 characters); inspect line breaks and table/paragraph formatting. |
| 8 | 20 | 72 | `ch8-q20` | Long context (635 characters); inspect line breaks and table/paragraph formatting. |
| 8 | 25 | 75 | `ch8-q25` | Long context (554 characters); inspect line breaks and table/paragraph formatting. |
| 9 | 4 | 77 | `ch9-q4` | Long context (533 characters); inspect line breaks and table/paragraph formatting. |
| 12 | 9 | 96 | `ch12-q9` | Tutorial note appears in the context field; check whether it belongs in the explanation instead. |
| 12 | 14 | 97 | `ch12-q14` | Long context (631 characters); inspect line breaks and table/paragraph formatting. |
| 14 | 3 | 105 | `ch14-q3` | Long context (791 characters); inspect line breaks and table/paragraph formatting. |
| 14 | 4 | 106 | `ch14-q4` | Long context (632 characters); inspect line breaks and table/paragraph formatting. |
| 17 | 2 | 113 | `ch17-q2` | Long context (587 characters); inspect line breaks and table/paragraph formatting. |
| 17 | 3 | 114 | `ch17-q3` | Long context (587 characters); inspect line breaks and table/paragraph formatting. |
| 17 | 10 | 118 | `ch17-q10` | Long context (642 characters); inspect line breaks and table/paragraph formatting. |
| 17 | 11 | 118 | `ch17-q11` | Long context (579 characters); inspect line breaks and table/paragraph formatting. |
| 17 | 12 | 119 | `ch17-q12` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (616 characters); inspect line breaks and table/paragraph formatting. |
| 18 | 3 | 124 | `ch18-q3` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (814 characters); inspect line breaks and table/paragraph formatting. |
| 18 | 13 | 129 | `ch18-q13` | Long context (617 characters); inspect line breaks and table/paragraph formatting. |
| 18 | 14 | 130 | `ch18-q14` | Long context (613 characters); inspect line breaks and table/paragraph formatting. |
| 18 | 18 | 132 | `ch18-q18` | Long context (551 characters); inspect line breaks and table/paragraph formatting. |
| 18 | 19 | 133 | `ch18-q19` | Long context (593 characters); inspect line breaks and table/paragraph formatting. |
| 18 | 22 | 135 | `ch18-q22` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (562 characters); inspect line breaks and table/paragraph formatting. |
| 19 | 14 | 141 | `ch19-q14` | Long context (902 characters); inspect line breaks and table/paragraph formatting. |
| 19 | 17 | 143 | `ch19-q17` | Long context (614 characters); inspect line breaks and table/paragraph formatting. |
| 19 | 20 | 145 | `ch19-q20` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (697 characters); inspect line breaks and table/paragraph formatting. |
| 19 | 21 | 146 | `ch19-q21` | Long context (723 characters); inspect line breaks and table/paragraph formatting. |
| 19 | 23 | 147 | `ch19-q23` | Long context (613 characters); inspect line breaks and table/paragraph formatting. |
| 20 | 6 | 151 | `ch20-q6` | Long context (563 characters); inspect line breaks and table/paragraph formatting. |
| 21 | 7 | 158 | `ch21-q7` | Long context (616 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 9 | 172 | `ch23-q9` | Long context (570 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 20 | 179 | `ch23-q20` | Long context (568 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 33 | 185 | `ch23-q33` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (644 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 39 | 188 | `ch23-q39` | Long context (683 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 40 | 190 | `ch23-q40` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Worked answer/explanation appears before the question; verify context/explanation split.<br>Long context (1032 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 41 | 191 | `ch23-q41` | Long context (750 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 42 | 192 | `ch23-q42` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (630 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 43 | 192 | `ch23-q43` | Long context (688 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 44 | 194 | `ch23-q44` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (924 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 47 | 196 | `ch23-q47` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (800 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 48 | 197 | `ch23-q48` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (903 characters); inspect line breaks and table/paragraph formatting. |
| 23 | 49 | 198 | `ch23-q49` | Long context (1288 characters); inspect line breaks and table/paragraph formatting. |
| 24 | 3 | 201 | `ch24-q3` | Long context (551 characters); inspect line breaks and table/paragraph formatting. |
| 24 | 6 | 202 | `ch24-q6` | Long context (676 characters); inspect line breaks and table/paragraph formatting. |
| 25 | 8 | 207 | `ch25-q8` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (800 characters); inspect line breaks and table/paragraph formatting. |
| 25 | 9 | 208 | `ch25-q9` | Tutorial note appears in the context field; check whether it belongs in the explanation instead. |
| 26 | 16 | 217 | `ch26-q16` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (1060 characters); inspect line breaks and table/paragraph formatting. |
| 26 | 17 | 218 | `ch26-q17` | Tutorial note appears in the context field; check whether it belongs in the explanation instead.<br>Long context (582 characters); inspect line breaks and table/paragraph formatting. |

## How to fix each flag

- **Tutorial note in context:** move only the tutorial-note sentence(s) from `context` into `explanation` if the PDF shows they are feedback for the preceding question. Check the page before moving; do not remove source wording.
- **Worked answer in context:** compare the question order on the cited PDF page. Put scenario data in `context`, the actual prompt in `question`, and solution workings in `explanation`.
- **Long context / possible table:** preserve all rows and values. If the extracted context contains a table, represent it as structured rows in the question object and render it as a table in `app.js`; do not flatten columns into a single paragraph.
- **Missing matrix rows / numeric answer:** populate `matrixRows` or `answerText` from the green-highlighted correct answer in the PDF.

## Exact code locations

- Question bank: `js/questions.js` (search by `id`).
- Question layout/rendering: `js/app.js`, function `renderQuiz()`.
- Global theme and visual styling: `css/style.css` (dark glass override block is at the end).
- Home page markup: `js/app.js`, function `renderHome()`.

**Total flagged for manual review: 70**. The report intentionally includes long contexts as a review flag even when the data may be correct, because table formatting cannot be reliably judged from plain-text extraction alone.