#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Refresh documentation snapshots from public project main commits using gh."""
import base64
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def api(path): return json.loads(subprocess.check_output(['gh','api',path],text=True))
def snapshot(name):
    revision=api(f'repos/nix-impurifiers/{name}/commits/main')['sha']
    data=api(f'repos/nix-impurifiers/{name}/contents/README.md?ref={revision}')
    return revision,base64.b64decode(data['content']).decode()
projects=json.loads((ROOT/'content/projects.json').read_text())
for project in projects:
    revision,text=snapshot(project['name'])
    (ROOT/'content/projects'/f'{project["name"]}.md').write_text(text)
    project['revision']=revision
    print(project['name'],revision[:7])
(ROOT/'content/projects.json').write_text(json.dumps(projects,indent=2)+'\n')
revision,text=snapshot('impurifier')
(ROOT/'content/engine.md').write_text(text)
(ROOT/'content/engine.json').write_text(json.dumps({'revision':revision})+'\n')
