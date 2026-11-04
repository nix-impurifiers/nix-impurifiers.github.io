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
# Or refresh selected guides and the shared engine:
python scripts/update_docs.py opkg-impurifier xbps-impurifier
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

## Structured project documentation

Each backend has an overview, full guide and documentation matrix, with a
cross-project comparison at `/compare/`. This adopts the useful organization of
the sibling [nix-purifiers documentation system](https://github.com/nix-purifiers/nix-purifiers.github.io/tree/e323c4e7749b7fb66fc8cd413ade4a399d02fe55/docs-site),
while retaining this site's palette, catalog and consumer-specific terminology.

`content/model-contract.json` owns the common overview sections and fact
vocabulary. Every catalog entry has an explicit `content/models/<name>.json`;
there are no family defaults for behavior. Records currently describe reviewed
README contracts: target-side Nix integration, optional bundled clients and a
verbatim validation-scope excerpt. They are documentation metadata, not an
implementation conformance model or a new operational test harness.

Facts use `known`, `unknown` or `not-applicable`. Known facts require literal
README evidence; unknown/inapplicable facts require reasons and cannot carry
values. Unknown is not converted to false. Source examples remain unchanged;
records without a fenced example explicitly point to the full guide.

To refresh a guide:

1. Run `scripts/update_docs.py` for the selected backend.
2. Review runtime/mode statements, scope and the example against the pinned
   README. Edit the explicit record and evidence when they change.
3. Update `reviewedRevision` and `readmeSha256` after that review. Do not use a
   regex or package-manager family to infer a new capability.
4. Run `python -m unittest discover -s tests -p 'test_*.py'`, `python build.py`,
   `python tests/check_site.py` and the browser suite.

A changed README hash blocks publication until its record is reviewed. A newer
commit with identical README content can retain the earlier review identity;
`source-review.json` reports `readme-unchanged`. Source review covers README
content, not every implementation file. Backend native/VM tests remain the
implementation evidence.

The build exports `catalog.json`, a global `source-review.json`, and per-project
`system.json`/`source-review.json`. The full README remains at `/<name>/guide/`,
preserving its headings and complete prose. Old overview fragments redirect to
those guide headings with JavaScript; without it, Full guide sections retains
the corresponding links.
