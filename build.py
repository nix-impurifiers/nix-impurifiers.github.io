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
from docs_model import CONTRACT, load_records, fact_label, source_review

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
PROJECTS = json.loads((ROOT / "content/projects.json").read_text())
MODELS = load_records(PROJECTS)
ORIGIN = "https://github.com/nix-impurifiers"
ESC = html.escape
ASSET_URLS = {
    name: f"/assets/{Path(name).stem}.{hashlib.sha256((ROOT/'assets'/name).read_bytes()).hexdigest()[:12]}{Path(name).suffix}"
    for name in ['site.css', 'site.js']
}
assert PROJECTS and len({p['name'] for p in PROJECTS}) == len(PROJECTS)

THEME = """<script>try{var t=localStorage.getItem('impurifiers-theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t}catch(e){}</script>"""

def page(title, description, body, *, docs=False):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="description" content="{ESC(description, quote=True)}">
<title>{ESC(title)}{' · nix-impurifiers' if title != 'nix-impurifiers' else ''}</title>
{THEME}<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{ASSET_URLS['site.css']}"><script src="{ASSET_URLS['site.js']}" defer></script></head>
<body><a class="skip" href="#content">Skip to content</a>
<header class="site-header"><div class="shell"><a class="brand" href="/">nix-impurifiers</a>
<nav class="site-nav" aria-label="Main navigation"><a href="/#impurifiers">Directory</a><a href="/getting-started/">Get started</a><a href="/compare/">Compare</a><a class="source-link" href="{ORIGIN}">GitHub ↗</a><button type="button" class="theme-toggle js-only" data-theme-toggle aria-label="Change color theme">Theme: system</button></nav></div></header>
<main id="content" class="shell{' docs' if docs else ''}">{body}</main>
<footer class="site-footer"><div class="shell">Nix-built software and artifacts. Native consumer workflows.
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


def document(slug, text, description, *, revision=None, repository=None, navigation=""):
    repository = repository or slug
    renderer = markdown.Markdown(extensions=['fenced_code','tables','toc','sane_lists'], extension_configs={'toc':{'permalink':True,'toc_depth':'2-3'}})
    body = renderer.convert(text)
    if revision:
        links = RewriteLinks(repository, revision); links.feed(body); body = ''.join(links.parts)
    toc = f'<nav class="doc-toc" aria-label="On this page">{renderer.toc}</nav>' if renderer.toc_tokens else ''
    # Put the document heading before its contents list.
    heading = re.match(r'(<h1\b.*?</h1>)', body, re.S)
    first = heading[1] if heading else ''
    rest = body[len(first):]
    meta = f'<p class="doc-meta">Documentation from <a href="{ORIGIN}/{repository}/blob/{revision}/README.md">the project README at {revision[:7]} ↗</a>. See the repository for the latest changes.</p>' if revision else ''
    title = re.sub('<[^>]+>', '', first).strip().replace('&para;', '').strip() if first else slug
    breadcrumb = f'<a href="/{repository}/">{repository}</a> / Full guide' if repository != slug else ESC(slug)
    content = f'<p class="breadcrumbs"><a href="/">nix-impurifiers</a> / {breadcrumb}</p>{navigation}<article class="doc-body">{first}{toc}{rest}</article>{meta}'
    directory=OUT/slug; directory.mkdir(parents=True)
    (directory/'index.html').write_text(page(html.unescape(title), description, content, docs=True))


def project_navigation(name, active):
    items = [('overview', f'/{name}/', 'Overview'), ('guide', f'/{name}/guide/', 'Full guide'), ('features', f'/{name}/features/', 'Feature matrix')]
    links = ''.join(f'<a href="{url}"' + (' aria-current="page"' if key == active else '') + f'>{label}</a>' for key, url, label in items)
    return f'<nav class="documentation-navigation" aria-label="Project documentation">{links}<a class="project-source" href="{ORIGIN}/{name}">Source ↗</a></nav>'


def rendered(text, name, revision):
    body = markdown.markdown(text, extensions=['fenced_code', 'tables', 'sane_lists'])
    links = RewriteLinks(name, revision); links.feed(body)
    return ''.join(links.parts)


def fact_content(key, fact, name, revision):
    if fact['state'] != 'known':
        return f'<strong>{fact_label(key, fact)}.</strong> {ESC(fact["reason"])}'
    if key == 'validation':
        return rendered(fact['value'], name, revision)
    return ESC(fact_label(key, fact))


def project_pages(project, record):
    name = project['name']; revision = record['reviewedRevision']
    source = (ROOT/'content/projects'/f'{name}.md').read_text()
    runtime = record['facts']['target_nix']; bundle = record['facts']['bundled_client']
    example = record['example']
    introduction = f'<p class="section-intro">{ESC(project["description"])}</p>'
    if example['state'] == 'known':
        example_html = f'<pre><code class="language-{ESC(example["language"],quote=True)}">{ESC(example["value"])}</code></pre><p class="code-note">See the full guide for prerequisites, installation and the surrounding configuration.</p>'
    else:
        example_html = f'<p>{ESC(example["reason"])}</p>'
    runtime_note = {'mode-dependent': 'This backend supports Nix-backed and native-payload paths. Nix-backed operation needs a usable Nix store/client and its native prerequisites; native modes have their own file-layout and ABI contract. Choose the constructor in the full guide.', 'required': 'Nix itself is this backend’s native manager. This is not a promise of a new Nix installer.', 'not-added': 'The backend does not add a target Nix client, daemon or database integration. The consumer, payload architecture, interpreter ABI and external libraries still need to match.'}.get(runtime.get('value'), '')
    parts = {
        'output': f'<dl class="artifact-summary"><div><dt>Consumer tools</dt><dd>{ESC(project["frontends"])}</dd></div><div><dt>Family</dt><dd>{ESC(project["category"])}</dd></div></dl>',
        'build': f'<p><a href="/{name}/guide/">Open the full guide →</a> · <a href="/getting-started/">General build setup</a></p>{example_html}',
        'runtime': f'<p><strong>{fact_content("target_nix", runtime, name, revision)}</strong></p><p>{ESC(runtime_note)}</p><p><strong>Bundled client:</strong> {fact_content("bundled_client", bundle, name, revision)}</p>',
        'validation': fact_content('validation', record['facts']['validation'], name, revision) + f'<p class="code-note"><a href="/{name}/guide/">Read the full guide’s requirements and limits</a>.</p>'
    }
    sections = ''.join(f'<section class="overview-section" aria-labelledby="overview-{section["id"]}"><h2 id="overview-{section["id"]}">{ESC(section["title"])}</h2>{parts[section["id"]]}</section>' for section in CONTRACT['sections'])
    renderer = markdown.Markdown(extensions=['toc', 'fenced_code', 'tables']); renderer.convert(source)
    def anchors(tokens):
        for token in tokens:
            yield token
            yield from anchors(token.get('children', []))
    old_links = ''.join(f'<li id="{ESC(t["id"],quote=True)}" data-guide-target="/{name}/guide/#{ESC(t["id"],quote=True)}"><a href="/{name}/guide/#{ESC(t["id"],quote=True)}">{ESC(re.sub("<[^>]+>", "", t["name"]))}</a></li>' for t in anchors(renderer.toc_tokens))
    legacy = f'<details class="legacy-guide"><summary>Full guide sections</summary><ul>{old_links}</ul></details>'
    review = f'<p class="doc-meta"><a href="{ORIGIN}/{name}/tree/{revision}">Source revision {revision[:7]} ↗</a></p>'
    body = f'<p class="breadcrumbs"><a href="/">nix-impurifiers</a> / {name}</p>{project_navigation(name,"overview")}<article class="doc-body"><h1>{name}</h1>{introduction}{sections}{legacy}</article>{review}'
    target = OUT/name; target.mkdir(parents=True)
    (target/'index.html').write_text(page(name, project['description'], body, docs=True))
    document(name+'/guide', source, project['description']+' Full guide.', revision=project['revision'], repository=name, navigation=project_navigation(name,'guide'))
    rows=[]
    for key, definition in CONTRACT['facts'].items():
        fact=record['facts'][key]
        rows.append(f'<tr><th scope="row">{ESC(definition["title"])}</th><td>{fact_content(key,fact,name,revision)}</td></tr>')
    matrix = f'<p class="breadcrumbs"><a href="/">nix-impurifiers</a> / <a href="/{name}/">{name}</a></p>{project_navigation(name,"features")}<article class="doc-body"><h1>{name} feature matrix</h1><p>Runtime requirements, optional integrations and validation scope.</p><table><thead><tr><th>Feature</th><th>Behavior and requirements</th></tr></thead><tbody>{"".join(rows)}</tbody></table><p><a href="/compare/">Compare all impurifiers →</a></p></article>{review}'
    (target/'features').mkdir(); (target/'features/index.html').write_text(page(name+' feature matrix', 'Runtime requirements and validation scope.', matrix, docs=True))
    (target/'system.json').write_text(json.dumps(record,indent=2)+'\n')
    (target/'source-review.json').write_text(json.dumps(source_review(project,record),indent=2)+'\n')


def comparison_page():
    rows=[]
    for p in sorted(PROJECTS,key=lambda p:p['name']):
        facts=MODELS[p['name']]['facts']
        rows.append(f'<tr><th scope="row"><a href="/{p["name"]}/">{p["name"]}</a></th><td>{ESC(p["description"])}</td><td>{ESC(fact_label("target_nix",facts["target_nix"]))}</td><td>{ESC(fact_label("bundled_client",facts["bundled_client"]))}</td><td><a href="/{p["name"]}/features/">Details and limits</a></td></tr>')
    text=f'<section class="comparison doc-body"><p class="eyebrow">Runtime requirements</p><h1>Compare impurifiers</h1><p>Compare artifact formats and runtime requirements. Open each feature matrix for details and limits.</p><p><strong>Depends on payload mode:</strong> the project offers Nix-backed and native-payload paths. <strong>No Nix runtime added:</strong> compatible native consumer tools and payload libraries are still required.</p><table><thead><tr><th>Impurifier</th><th>Artifact</th><th>Target-side Nix integration</th><th>Bundled Nix client</th><th>Details</th></tr></thead><tbody>{"".join(rows)}</tbody></table></section>'
    target=OUT/'compare'; target.mkdir(); (target/'index.html').write_text(page('Compare impurifiers','Compare runtime requirements and native artifact formats.',text,docs=True))


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
    return f'''<section class="hero"><p class="eyebrow">Nix builds. Native consumers.</p><h1>Nix-built software.<br><span>Your native tools.</span></h1><p class="lead">Turn Nix-built software and prepared payloads into native packages, images, language artifacts and boot components. Keep the consumer’s own installation and runtime model.</p><p class="hero-links"><a href="/getting-started/">Get started →</a><a href="#impurifiers">Find your impurifier ↓</a></p></section>
<section class="section" aria-labelledby="how-heading"><h2 id="how-heading">Keep the familiar part.</h2><p>Native tools consume the artifact. Nix produces its payload and metadata. Choose native-owned files, a Nix-backed application or a target-specific bundle, according to the consumer’s ownership and runtime model.</p><div class="flow" aria-label="A typical impurifier package flow"><div class="flow-step"><strong>01 / Nix-built payload</strong><p>Build compatible software or prepare its files with Nix.</p></div><span class="flow-arrow" aria-hidden="true">→</span><div class="flow-step"><strong>02 / Native artifact</strong><p>Emit a package, recipe, profile or image for the target manager.</p></div><span class="flow-arrow" aria-hidden="true">→</span><div class="flow-step"><strong>03 / Native consumer</strong><p>Install or consume through native tools, with the payload and runtime model suited to the target.</p></div></div>
<div class="example-head"><span class="example-label">An offline application</span><div class="example-tabs js-only" role="group" aria-label="Package example"><button type="button" data-example="dpkg" aria-pressed="true">DEB</button><button type="button" data-example="rpm" aria-pressed="false">RPM</button><button type="button" data-example="pacman" aria-pressed="false">ALPM</button></div></div><pre><code id="package-example" class="language-nix">{ESC(examples['dpkg'])}\n</code></pre>{templates}<p class="code-note">A library fragment for your flake. <a id="example-docs" href="/dpkg-impurifier/">Read the dpkg guide →</a></p></section>
<section id="impurifiers" class="section" aria-labelledby="directory-heading"><h2 id="directory-heading">Find your impurifier.</h2><p class="section-intro">Choose by package manager or artifact ecosystem. Start with a common overview, compare the documented runtime contract, then open the complete guide for native setup and limits.</p><div class="toolbar js-only"><label class="sr-only" for="project-search">Search impurifiers and frontends</label><input id="project-search" type="search" placeholder="Search by manager, frontend or format…" autocomplete="off" spellcheck="false" aria-controls="project-directory"><span id="project-count" class="count" role="status" aria-live="polite">{len(PROJECTS)} impurifiers</span></div><fieldset class="filters js-only"><legend class="sr-only">Filter by package-manager family</legend>{filters}</fieldset><div id="project-directory">{''.join(groups)}</div><p id="no-projects" class="empty-state" hidden>No matching impurifier. <button id="reset-search" type="button">Clear search and filters</button></p></section>
<section class="section" aria-labelledby="transport-heading"><h2 id="transport-heading">Choose the runtime contract.</h2><p>Not every artifact needs Nix on the target. Native-owned closures and prepared payloads use the consumer’s own runtime; Nix-backed modes manage a Nix store and profile. <a href="/compare/">Compare the documented modes →</a></p><p>For Nix-backed transports:</p><div class="transport"><div><h3>Net</h3><p>A small artifact carries the descriptor and integration. The target resolves the closure through its configured Nix substituters.</p></div><div><h3>Offline</h3><p>The artifact carries a local closure cache. Import uses that cache with remote substitution and remote builders disabled.</p></div></div><p class="aside-note">Selected adapters also offer native payloads with no target-side Nix. Nix-backed packages may use an external client or optionally bundle a static one. Providing a complete Nix installation through an impure package remains deferred installer work.</p></section>
<section class="section" aria-labelledby="testing-heading"><h2 id="testing-heading">Transactions tested in VMs.</h2><p>Validation follows the consumer: native package transactions, interpreter execution, container/image lifecycles, early boots and Kubernetes release operations. Each overview names its documented scope; a passing fixture does not establish every platform or mode.</p><ul class="checks"><li>Native ownership and meaningful runtime dependencies.</li><li>Failed activation followed by an actual offline recovery.</li><li>Retention while installed; release after removal and pruning.</li></ul><p><a href="/testing/">Read the coverage and its limits →</a></p></section>
<section class="section" aria-labelledby="family-heading"><h2 id="family-heading">The other direction.</h2><p><a href="https://nix-purifiers.github.io/">nix-purifiers</a> brings a build tool’s dependencies into Nix. Impurifiers bring Nix-built applications into native package-manager workflows.</p><p>Nix-backed adapters use the <a href="/impurifier/">shared impurifier engine</a>. Original project code is MIT licensed; upstream software retains its own license.</p></section>'''


def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(); shutil.copytree(ROOT/'assets', OUT/'assets')
    for name, url in ASSET_URLS.items():
        (OUT/'assets'/name).rename(OUT/url.lstrip('/'))
    (OUT/'index.html').write_text(page('nix-impurifiers',f'Nix-built applications, installed through native tools. Explore {len(PROJECTS)} impurifiers, native VM coverage, and project documentation.',homepage()))
    for p in PROJECTS:
        project_pages(p, MODELS[p['name']])
    comparison_page()
    (OUT/'model-contract.json').write_text(json.dumps(CONTRACT, indent=2)+'\n')
    (OUT/'catalog.json').write_text(json.dumps({'version': CONTRACT['version'], 'contract': '/model-contract.json', 'projects': [dict(p, model=MODELS[p['name']]) for p in PROJECTS]}, indent=2)+'\n')
    (OUT/'source-review.json').write_text(json.dumps([source_review(p, MODELS[p['name']]) for p in PROJECTS], indent=2)+'\n')
    revision=json.loads((ROOT/'content/engine.json').read_text())['revision']
    document('impurifier',(ROOT/'content/engine.md').read_text(),'The shared transactional Nix profile engine for impurifiers.',revision=revision)
    for slug in ['getting-started','testing']:
        document(slug,(ROOT/'content'/f'{slug}.md').read_text(), 'Guides for native package-manager integration with Nix.')
    (OUT/'404.html').write_text(page('Page not found','Find your impurifier.', '<section class="hero"><p class="eyebrow">404</p><h1>This page is missing.</h1><p><a href="/#impurifiers">Browse the impurifier directory →</a></p></section>'))
    (OUT/'.nojekyll').touch()
    print(f'Built {len(list(OUT.rglob("*.html")))} HTML pages with {len(PROJECTS)} project guides and the shared engine.')

if __name__ == '__main__': main()
