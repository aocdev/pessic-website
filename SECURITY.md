# Security Policy

## Supported Versions

Only the version of the website currently published is supported.

## Scope

The Pessic website is a **static site**: HTML, CSS and a small script, with no server code, no forms, no cookies, no analytics and no third-party code, fonts or images. It is built by `tools/build.py` from the templates in `src/` and the texts in `i18n/`.

Potential security concerns include:

- **Script injection** through texts in `i18n/*.json` (values may contain inline HTML, so a translation could add markup) or the generated pages
- **Download links** in `js/main.js` pointing to the wrong place, or files that do not match the release (each Pessic release publishes `SHA256SUMS.txt` and signed build attestations)
- **The build scripts** (`tools/`), which read the app's `MANUAL.md` and write the pages

Vulnerabilities in the **Pessic app** itself belong in the [app's security policy](https://github.com/aocdev/pessic/security/policy).

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT open a public issue**
2. Use [GitHub Security Advisories](https://github.com/aocdev/pessic-website/security/advisories/new) to report it privately
3. Include:
   - Description of the vulnerability
   - Steps to reproduce (the page and the browser)
   - Potential impact
   - Suggested fix (if any)

You should receive an acknowledgment within **48 hours** and a resolution plan within **7 days**.

## Disclosure Policy

- Vulnerabilities will be fixed and the site republished
- A security advisory will be published after the fix is available
- Credit will be given to the reporter (unless anonymity is requested)
