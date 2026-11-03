# nix-impurifiers website

The directory and documentation for [nix-impurifiers](https://github.com/nix-impurifiers).
Public site: **https://nix-impurifiers.github.io/**.

The theme follows the text-led layout and system typography of
[nix-purifiers](https://nix-purifiers.github.io/), with warm paper, charcoal and
bronze colors. It supports the operating system's theme and a persisted manual
choice, responsive layouts, keyboard navigation and JavaScript-free reading.
No external fonts, images, analytics or client-side dependencies are required.

## Build

Requires Python 3.11 or later. The static build uses one pinned dependency:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python build.py
python tests/check_site.py
python -m http.server --directory dist
```

`dist/` contains the complete site: the directory, getting-started and testing
guides, all project READMEs and shared engine documentation. It can be hosted by
any static web server. Browser interactions use plain JavaScript; all
navigation and documentation remain usable without it.

## Refresh documentation

`content/projects.json` records project descriptions, families and exact source
revisions. `content/projects/` contains README snapshots at those revisions.
Relative source links are rewritten to the pinned GitHub revision during the
build. No project source is fetched during an ordinary build.

To update all README snapshots using an authenticated GitHub CLI:

```sh
python scripts/update_docs.py
python build.py
python tests/check_site.py
```

Review the updated snapshots and revision manifest before committing. Edit
`content/getting-started.md` and `content/testing.md` for the standalone guides.

## Browser checks

The browser suite starts and stops its own local static server. It covers
search, family filters, empty/reset behavior, code examples, clipboard copy,
theme persistence, mobile overflow, documentation routes and reading with
JavaScript disabled.

```sh
python -m pip install playwright==1.64.0
python -m playwright install chromium
python tests/browser.py
```

Set `CHROMIUM` to use an existing Chromium executable, or `SITE_TEST_URL` to
check an already running instance. Screenshots are written to ignored
`test-results/`. GitHub Actions builds, checks and publishes Pages on pushes to
`main`; pull requests run the same checks without deployment.

`.openai/hosting.json` identifies a separate owner-private Sites preview. It is
not needed for the public GitHub Pages deployment or local static hosting.

Original website code is MIT licensed. Project README snapshots retain their
source attribution; referenced upstream software retains its own license.
