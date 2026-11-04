#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the generated site's navigation, local anchors and project coverage."""
from html.parser import HTMLParser
import json
import hashlib
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=set(); self.links=[]; self.assets=[]; self.headings=0; self.lang=None
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate id: {attrs["id"]}'
            self.ids.add(attrs['id'])
        if tag=='a' and attrs.get('href'): self.links.append(attrs['href'])
        if tag in ('script','img') and attrs.get('src'): self.assets.append(attrs['src'])
        if tag=='link' and attrs.get('href'): self.assets.append(attrs['href'])
        if tag=='h1': self.headings+=1
        if tag=='html': self.lang=attrs.get('lang')

pages={}
for path in DIST.rglob('*.html'):
    doc=Document(); doc.feed(path.read_text()); pages[path]=doc
    assert doc.headings==1, f'{path}: expected one h1, got {doc.headings}'
    assert doc.lang=='en', path
    assert 'content' in doc.ids, path
for path, doc in pages.items():
    for ref in doc.links+doc.assets:
        url=urlsplit(ref)
        assert url.scheme.lower() not in ['javascript','file'], f'{path}: unsafe URL {ref}'
        if url.scheme or url.netloc: continue
        target=(DIST/unquote(url.path.lstrip('/'))) if url.path.startswith('/') else (path.parent/unquote(url.path))
        if not url.path: target=path
        if target.is_dir(): target=target/'index.html'
        assert target.exists(), f'{path}: missing target {ref}'
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f'{path}: missing anchor {ref}'
    for ref in doc.assets:
        if ref.endswith(('.css', '.js')):
            match = re.fullmatch(r'/assets/site\.([0-9a-f]{12})\.(css|js)', ref)
            assert match, f'{path}: stylesheet/script URL must be content-versioned: {ref}'
            assert hashlib.sha256((DIST/ref.lstrip('/')).read_bytes()).hexdigest().startswith(match[1]), ref
    assert all(not urlsplit(ref).netloc for ref in doc.assets), f'{path}: third-party asset dependency'
projects=json.loads((ROOT/'content/projects.json').read_text())
assert projects and len({p['name'] for p in projects})==len(projects)
for project in projects:
    assert DIST/project['name']/'index.html' in pages, project['name']
assert len(pages)==3*len(projects)+6
for project in projects:
    name=project['name']
    for suffix in ['guide/index.html', 'features/index.html', 'system.json', 'source-review.json']:
        assert (DIST/name/suffix).exists(), (name,suffix)
    record=json.loads((DIST/name/'system.json').read_text())
    assert record['reviewBasis']=='project-readme'
assert (DIST/'compare/index.html').exists()
assert (DIST/'model-contract.json').exists()
assert len(json.loads((DIST/'source-review.json').read_text()))==len(projects)
print(f'Passed: {len(pages)} pages, {len(projects)} project guides, internal links/anchors, unique headings, local assets.')
