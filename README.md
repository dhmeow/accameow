# CYBER//CHALLENGE — GitHub + Vercel

## IMPORTANT

All files in this version are intentionally in the repository root.

Do NOT put the CSS/JS files inside `assets/` unless you also restore the corresponding paths in the HTML.

### Root files

- `index.html`
- `selection.html`
- `ma.html`
- `fa.html`
- `law.html`
- `game-over.html`
- `cyberpunk.css`
- `effects.js`
- `config.js`
- `app.js`
- `page.js`

## Vercel

Import the GitHub repository into Vercel.

For this plain static HTML project:

- Framework Preset: `Other`
- Build Command: leave empty
- Output Directory: leave empty
- Install Command: leave empty

Vercel should serve `index.html` from the repository root.

## GitHub

Upload/replace the files so your repository root looks like this:

```text
YOUR-REPO/
├── index.html
├── selection.html
├── ma.html
├── fa.html
├── law.html
├── game-over.html
├── cyberpunk.css
├── effects.js
├── config.js
├── app.js
├── page.js
└── README.md
```

After committing the changes, redeploy on Vercel.

## Links

The six Proton Drive resource links are already configured in `config.js`.
