# CYBER//CHALLENGE — Static Website

This is a standalone static implementation of the supplied cyberpunk study-challenge specification.

## Run

Open `index.html` in a modern browser, or serve the folder with a local static server.

## Resource links

All six live Proton Drive links are configured in:

`assets/js/config.js`

The subjects are mapped as follows:

- MA → Question Practice / Notes
- FA → Question Practice / Notes
- LAW → Question Practice / Notes

## Page flow

`index.html` → boot → challenge → `selection.html` → `ma.html` / `fa.html` / `law.html`

`index.html` → NO → `game-over.html`

## Notes

- Static HTML/CSS/JS; no build step required.
- Shared interface components are implemented as reusable CSS/JS patterns.
- Reduced-motion behavior is included.
- Portrait phones receive the landscape orientation gate.
- External resources use a short secure-connection transition before redirecting.
