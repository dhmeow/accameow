# MA Study Resources — All Credits to MEOW

A responsive, static study-question website built from the supplied **MA Complete Studyhub Questions by MEOW.pdf**.

## Features

- Polished white interface with an iOS-inspired glass treatment.
- Home page with a clear **All Credits to MEOW** credit lockup.
- All 26 chapters, with chapter search.
- One question displayed at a time, with a progress bar at the top.
- A separate Home control in the quiz header.
- Confirm, Skip and Next Question controls.
- Green feedback for correct answers and red feedback for an incorrect selection, while revealing the correct answer in green.
- Supports single-choice, select-two, numeric-entry and statement/table questions.
- The original PDF's three graph-choice illustrations are included as cropped image assets.
- No profile page, login, account, database or backend.

## Run locally

Open `index.html` in a modern browser. The project is plain HTML, CSS and JavaScript and does not require a build step.

For a local development server, you can also run:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Deploy to GitHub + Vercel

1. Create a GitHub repository and upload the contents of this folder (keep `index.html`, `css/`, `js/` and `assets/` in the root structure).
2. In Vercel, import the GitHub repository.
3. Choose **Other** as the framework preset, leave the build command empty, and set the output directory to `.`.
4. Deploy. No environment variables are required.

## Updating question data

The chapter list and question bank are in `js/questions.js`. The app reads `window.MA_STUDY_DATA` from this file. Each question includes its source PDF page number, answer key and, where present, the explanation from the source.

## Source notes

- The questions and answer keys are based on the PDF supplied for this project.
- One unnumbered Chapter 5 table item is shown as Question 8 because it appears between the PDF's Questions 7 and 9.
- Questions that are absent from the supplied PDF have not been invented. The source itself skips some printed question numbers.
- Some table-based questions have been converted into row-by-row answer controls so the highlighted answer can be checked clearly on mobile and desktop.
- The site is a practice companion and does not include the dropdown-style MTQs that the PDF author notes are not included in the source.
