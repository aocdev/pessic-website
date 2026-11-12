# Contributing to the Pessic website

First off, thank you for considering contributing! This repository is the website of [Pessic](https://github.com/aocdev/pessic), the desktop monthly budget app. Contributions to the app itself go to [its repository](https://github.com/aocdev/pessic/blob/main/CONTRIBUTING.md).

## Code of Conduct

This project adheres to the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior via [GitHub Issues](https://github.com/aocdev/pessic-website/issues).

## How Can I Contribute?

- **Report a problem**: a broken link, a layout that fails on your phone, a typo. Open an [issue](https://github.com/aocdev/pessic-website/issues).
- **Improve the texts**: clearer explanations, better Catalan, a missing question in the FAQ.
- **Translate the site**: see [Translations](#translations) below.
- **Propose new content**: open an issue first so we can agree on it.

## Development Setup

### Prerequisites

- **Python 3.10+** (standard library only) to build the pages
- **A browser**
- For new screenshots only: **Java 21+** and the [app's source](https://github.com/aocdev/pessic) next to this folder

### Getting Started

```bash
git clone https://github.com/aocdev/pessic-website.git
git clone https://github.com/aocdev/pessic.git        # the manual comes from its MANUAL.md
cd pessic-website
python3 tools/build.py                                # builds index.html and manual.html
python3 tools/check.py                                # checks tags, files and anchors
python3 -m http.server 8000                           # then open http://localhost:8000
```

```
pessic-website/
  src/            # page templates: HTML with {{key}} placeholders, no text
  i18n/           # texts, one JSON file per language (ca.json is the default)
  css/ js/        # styles and the small script
  assets/         # icon and screenshots
  tools/          # build.py, check.py, screenshots/
  index.html      # generated, committed (it is what the hosting serves)
  manual.html     # generated from the app's MANUAL.md, committed
```

### How the Pages Are Built

`index.html` and `manual.html` are **generated**: never edit them by hand. Change `src/`, `i18n/` or the app's `MANUAL.md`, run `python3 tools/build.py` and commit the generated pages together with your change. CI rebuilds them and fails if the committed pages are out of date.

In the templates:

- `{{key}}` inserts a text from `i18n/<language>.json` (it may contain inline HTML)
- `{{@key}}` inserts a text inside an attribute (`alt`, `aria-label`…), escaped
- `{{=name}}` is filled in by the build (language, paths, the language switcher…)

The build fails if a template or `js/main.js` asks for a key that `ca.json` does not have, or if `ca.json` has a key nothing uses.

### Translations

1. Copy `i18n/ca.json` to `i18n/<code>.json` (for example `es.json`) and set `_language.code` and `_language.name`
2. Translate the values. Keep the HTML tags and the `{placeholders}` in the `js.*` texts
3. Run `python3 tools/build.py`: the page is written to `<code>/index.html` and a language switcher appears

Missing keys fall back to Catalan, with a warning, so a partial translation still works. A translated manual is a `MANUAL.<code>.md` in the app's repository.

### Screenshots

The screenshots come from the real app, with an **invented profile** ("Marta"):

```bash
tools/screenshots/take.sh
```

**Never take screenshots of a real budget**, not even blurred or "anonymised". The script uses a temporary database and a fixed date, so it never touches your own Pessic data.

## Guidelines

- **No external dependencies**: no frameworks, CDNs, web fonts, analytics or trackers
- **No text in `src/` or `js/main.js`**: every visible text goes in `i18n/ca.json`
- **Accessible**: keyboard navigation, `alt` texts, enough contrast in light and dark mode
- **Responsive**: check a phone-sized window (about 390 px wide)
- **Honest**: describe what the app really does today

## Branching and Commits

We use [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow) and [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/), as in the app:

```
feat/short-description      # New section or feature
fix/short-description       # Fix
docs/short-description      # Texts and documentation
i18n/short-description      # Translations
```

| Type | Description |
|------|-------------|
| `feat` | A new section, page or behaviour |
| `fix` | A fix (layout, link, script) |
| `docs` | Texts on the site or documentation (README, CONTRIBUTING) |
| `style` | Visual changes (CSS) with no new content |
| `refactor` | Restructuring templates or tools with no visible change |
| `build` | Changes to `tools/` |
| `ci` | Changes to the workflows |
| `chore` | Other changes (screenshots, assets) |

Scopes (optional): `landing`, `manual`, `i18n`, `downloads`, `screenshots`, `tools`.

```
feat(landing): add a section about the payroll account
fix(downloads): highlight the right card on ARM Linux
i18n: add Spanish translation
chore(screenshots): retake them for Pessic 1.1
```

## Pull Request Process

1. **Create an issue first** for new content or sections
2. **Branch from `main`**
3. **Build and check**: `python3 tools/build.py && python3 tools/check.py`
4. **Commit the generated pages** together with your change
5. **Check it in a browser**: desktop and phone width, light and dark mode

## Getting Help

- **Questions**: [Discussions in the app's repository](https://github.com/aocdev/pessic/discussions)
- **Website problems**: [GitHub Issues](https://github.com/aocdev/pessic-website/issues)

Thank you for contributing!
