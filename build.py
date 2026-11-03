#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the static directory and pinned project documentation, without network access."""
import html
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit
import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
PROJECTS = json.loads((ROOT / "content/projects.json").read_text())
ORIGIN = "https://github.com/nix-impurifiers"
ESC = html.escape
ASSET_URLS = {
    name: f"/assets/{Path(name).stem}.{hashlib.sha256((ROOT/'assets'/name).read_bytes()).hexdigest()[:12]}{Path(name).suffix}"
    for name in ['site.css', 'site.js']
}
assert len(PROJECTS) == 40 and len({p['name'] for p in PROJECTS}) == 40

THEME = """<script>try{var t=localStorage.getItem('impurifiers-theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t}catch(e){}</script>"""

def page(title, description, body, *, docs=False):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="description" content="{ESC(description, quote=True)}">
<title>{ESC(title)}{' · nix-impurifiers' if title != 'nix-impurifiers' else ''}</title>
{THEME}<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{ASSET_URLS['site.css']}"><script src="{ASSET_URLS['site.js']}" defer></script></head>
<body><a class="skip" href="#content">Skip to content</a>
<header class="site-header"><div class="shell"><a class="brand" href="/">nix-impurifiers</a>
<nav class="site-nav" aria-label="Main navigation"><a href="/#impurifiers">Directory</a><a href="/getting-started/">Get started</a><a class="source-link" href="{ORIGIN}">GitHub ↗</a><button type="button" class="theme-toggle js-only" data-theme-toggle aria-label="Change color theme">Theme: system</button></nav></div></header>
<main id="content" class="shell{' docs' if docs else ''}">{body}</main>
<footer class="site-footer"><div class="shell">Nix-built applications. Native package-manager intent.
<p class="footer-links"><a href="{ORIGIN}/nix-impurifiers.github.io">Website source ↗</a><a href="/impurifier/">Shared engine</a><a href="https://nix-purifiers.github.io/">nix-purifiers ↗</a><span>Original code: MIT</span></p></div></footer></body></html>'''

class RewriteLinks(HTMLParser):
    def __init__(self, name, revision):
        super().__init__(convert_charrefs=False)
        self.name, self.revision, self.parts = name, revision, []
    def handle_starttag(self, tag, attrs):
        rewritten = []
        for key, value in attrs:
            if key in ('href','src') and value:
                url = urlsplit(value)
                if not url.scheme and not value.startswith(('#','/')):
                    value = f'{ORIGIN}/{self.name}/blob/{self.revision}/{value.removeprefix("./")}'
                elif key == 'href' and url.netloc == 'github.com':
                    match = re.fullmatch(r'/nix-impurifiers/([^/]+)/?(?:blob/[^/]+/README\.md)?', url.path)
                    names = {p['name'] for p in PROJECTS} | {'impurifier'}
                    if match and match[1] in names:
                        value = '/' + match[1] + '/' + (('#'+url.fragment) if url.fragment else '')
            rewritten.append(key if value is None else f'{key}="{ESC(value, quote=True)}"')
        self.parts.append('<'+tag+(' '+ ' '.join(rewritten) if rewritten else '')+'>')
    def handle_endtag(self, tag): self.parts.append('</'+tag+'>')
    def handle_data(self, data): self.parts.append(data)
    def handle_entityref(self, name): self.parts.append('&'+name+';')
    def handle_charref(self, name): self.parts.append('&#'+name+';')
    def handle_comment(self, data): self.parts.append('<!--'+data+'-->')


def document(slug, text, description, *, revision=None):
    renderer = markdown.Markdown(extensions=['fenced_code','tables','toc','sane_lists'], extension_configs={'toc':{'permalink':True,'toc_depth':'2-3'}})
    body = renderer.convert(text)
    if revision:
        links = RewriteLinks(slug, revision); links.feed(body); body = ''.join(links.parts)
    toc = f'<nav class="doc-toc" aria-label="On this page">{renderer.toc}</nav>' if renderer.toc_tokens else ''
    # Put the document heading before its contents list.
    heading = re.match(r'(<h1\b.*?</h1>)', body, re.S)
    first = heading[1] if heading else ''
    rest = body[len(first):]
    meta = f'<p class="doc-meta">Documentation from <a href="{ORIGIN}/{slug}/blob/{revision}/README.md">the project README at {revision[:7]} ↗</a>. See the repository for the latest changes.</p>' if revision else ''
    title = re.sub('<[^>]+>', '', first).strip().replace('&para;', '').strip() if first else slug
    content = f'<p class="breadcrumbs"><a href="/">nix-impurifiers</a> / {ESC(slug)}</p><article class="doc-body">{first}{toc}{rest}</article>{meta}'
    directory=OUT/slug; directory.mkdir(parents=True)
    (directory/'index.html').write_text(page(html.unescape(title), description, content, docs=True))


def homepage():
    groups = []
    categories = list(dict.fromkeys(p['category'] for p in PROJECTS))
    for category in categories:
        rows=[]
        for p in sorted((p for p in PROJECTS if p['category']==category),key=lambda p:p['name']):
            terms=' '.join([p['name'],p['description'],p['frontends'],p['category'],p.get('aliases','')]).lower()
            rows.append(f'''<li class="project-row" data-project data-category="{ESC(category,quote=True)}" data-search="{ESC(terms,quote=True)}"><a href="/{p['name']}/">{p['name']}</a><div class="description">{ESC(p['description'])}<span class="frontends">{ESC(p['frontends'])}</span></div></li>''')
        groups.append(f'<section class="catalog-group" aria-label="{ESC(category,quote=True)}"><h3>{ESC(category)}</h3><ul class="project-list">'+''.join(rows)+'</ul></section>')
    filters='<button type="button" data-filter="all" aria-pressed="true">All</button>'+''.join(f'<button type="button" data-filter="{ESC(c,quote=True)}" aria-pressed="false">{ESC(c)}</button>' for c in categories)
    examples={
        'dpkg': 'let\n  adapter = inputs.dpkg-impurifier.lib.dpkg-impurifier {\n    inherit pkgs;\n  };\nin adapter.makeOfflineDeb { pkg = pkgs.hello; }',
        'rpm': 'let\n  adapter = inputs.rpm-impurifier.lib.rpm-impurifier {\n    inherit pkgs;\n  };\nin adapter.makeOfflineRpm { pkg = pkgs.hello; }',
        'pacman': 'let\n  adapter = inputs.pacman-impurifier.lib.pacman-impurifier {\n    inherit pkgs;\n  };\nin adapter.makeOfflinePackage { pkg = pkgs.hello; }',
    }
    templates=''.join(f'<template id="example-{key}">{ESC(value)}</template>' for key,value in examples.items())
    return f'''<section class="hero"><p class="eyebrow">Native packages, Nix closures</p><h1>Nix-built software.<br><span>Your package manager.</span></h1><p class="lead">Install Nix-built applications through the tools your system already uses. Impurifiers connect native package-manager intent with Nix application closures.</p><p class="hero-links"><a href="/getting-started/">Get started →</a><a href="#impurifiers">Find your impurifier ↓</a></p></section>
<section class="section" aria-labelledby="how-heading"><h2 id="how-heading">Keep the familiar part.</h2><p>Your package manager handles the native transaction. Nix supplies the application. A shared engine connects the installed intent to a GC-rooted profile.</p><div class="flow" aria-label="A typical impurifier package flow"><div class="flow-step"><strong>01 / Nix closure</strong><p>Build an application and its dependencies with Nix.</p></div><span class="flow-arrow" aria-hidden="true">→</span><div class="flow-step"><strong>02 / Native artifact</strong><p>Emit a package, recipe, profile or image for the target manager.</p></div><span class="flow-arrow" aria-hidden="true">→</span><div class="flow-step"><strong>03 / Application</strong><p>Install through native tools. Retain the needed Nix store paths.</p></div></div>
<div class="example-head"><span class="example-label">An offline application</span><div class="example-tabs js-only" role="group" aria-label="Package example"><button type="button" data-example="dpkg" aria-pressed="true">DEB</button><button type="button" data-example="rpm" aria-pressed="false">RPM</button><button type="button" data-example="pacman" aria-pressed="false">ALPM</button></div></div><pre><code id="package-example" class="language-nix">{ESC(examples['dpkg'])}\n</code></pre>{templates}<p class="code-note">A library fragment for your flake. <a id="example-docs" href="/dpkg-impurifier/">Read the dpkg guide →</a></p></section>
<section id="impurifiers" class="section" aria-labelledby="directory-heading"><h2 id="directory-heading">Find your impurifier.</h2><p class="section-intro">Choose by package manager, not by distribution. Each guide describes its native dependencies, integration and tested limits.</p><div class="toolbar js-only"><label class="sr-only" for="project-search">Search impurifiers and frontends</label><input id="project-search" type="search" placeholder="Search by manager, frontend or format…" autocomplete="off" spellcheck="false" aria-controls="project-directory"><span id="project-count" class="count" role="status" aria-live="polite">40 impurifiers</span></div><fieldset class="filters js-only"><legend class="sr-only">Filter by package-manager family</legend>{filters}</fieldset><div id="project-directory">{''.join(groups)}</div><p id="no-projects" class="empty-state" hidden>No matching impurifier. <button id="reset-search" type="button">Clear search and filters</button></p></section>
<section class="section" aria-labelledby="transport-heading"><h2 id="transport-heading">Two ways to carry the closure.</h2><div class="transport"><div><h3>Net</h3><p>A small artifact carries the descriptor and integration. The target resolves the closure through its configured Nix substituters.</p></div><div><h3>Offline</h3><p>The artifact carries a local closure cache. Import uses that cache with remote substitution and remote builders disabled.</p></div></div><p class="aside-note">Bring a working Nix runtime. Providing Nix through an impure native package is deferred installer work. Individual adapters document their transport and activation rules.</p></section>
<section class="section" aria-labelledby="testing-heading"><h2 id="testing-heading">Transactions tested in VMs.</h2><p>Native tools and real package databases exercise more than archive creation: failure, offline recovery, upgrades, configuration and garbage collection.</p><ul class="checks"><li>Native ownership and meaningful runtime dependencies.</li><li>Failed activation followed by an actual offline recovery.</li><li>Retention while installed; release after removal and pruning.</li></ul><p><a href="/testing/">Read the coverage and its limits →</a></p></section>
<section class="section" aria-labelledby="family-heading"><h2 id="family-heading">The other direction.</h2><p><a href="https://nix-purifiers.github.io/">nix-purifiers</a> brings a build tool’s dependencies into Nix. Impurifiers bring Nix-built applications into native package-manager workflows.</p><p>These adapters share the <a href="/impurifier/">impurifier engine</a>. Original project code is MIT licensed; upstream software retains its own license.</p></section>'''


def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(); shutil.copytree(ROOT/'assets', OUT/'assets')
    for name, url in ASSET_URLS.items():
        (OUT/'assets'/name).rename(OUT/url.lstrip('/'))
    (OUT/'index.html').write_text(page('nix-impurifiers','Nix-built applications, installed through native package managers. Explore 40 impurifiers, native VM coverage, and project documentation.',homepage()))
    for p in PROJECTS:
        document(p['name'],(ROOT/'content/projects'/f"{p['name']}.md").read_text(),p['description']+'. '+p['frontends']+'.',revision=p['revision'])
    revision=json.loads((ROOT/'content/engine.json').read_text())['revision']
    document('impurifier',(ROOT/'content/engine.md').read_text(),'The shared transactional Nix profile engine for impurifiers.',revision=revision)
    for slug in ['getting-started','testing']:
        document(slug,(ROOT/'content'/f'{slug}.md').read_text(), 'Guides for native package-manager integration with Nix.')
    (OUT/'404.html').write_text(page('Page not found','Find your impurifier.', '<section class="hero"><p class="eyebrow">404</p><h1>This page is missing.</h1><p><a href="/#impurifiers">Browse the impurifier directory →</a></p></section>'))
    (OUT/'.nojekyll').touch()
    print(f'Built {len(list(OUT.rglob("*.html")))} HTML pages with 40 project guides and the shared engine.')

if __name__ == '__main__': main()
