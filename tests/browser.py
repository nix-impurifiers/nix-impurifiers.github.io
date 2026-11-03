#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import os
import json
import functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
PROJECTS=json.loads((ROOT/'content/projects.json').read_text())
PROJECT_COUNT=len(PROJECTS)
FILTERS=list(dict.fromkeys(project['category'] for project in PROJECTS))+['All']
server = None
BASE=os.environ.get('SITE_TEST_URL')
if not BASE:
    server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(SimpleHTTPRequestHandler,directory=str(ROOT/'dist')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    BASE=f'http://127.0.0.1:{server.server_port}' 
BROWSER=os.environ.get('CHROMIUM')
OUT=ROOT/'test-results'; OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(**({'executable_path':BROWSER} if BROWSER else {}),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    context=browser.new_context(viewport={'width':1440,'height':1050},color_scheme='light',permissions=['clipboard-read','clipboard-write'])
    page=context.new_page(); errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    response=page.goto(BASE+'/'); assert response.status==200
    page.wait_for_selector('html.js')
    assert page.locator('[data-project]:visible').count()==PROJECT_COUNT
    search_box = page.locator('#project-search').bounding_box()
    for label in FILTERS:
        page.get_by_role('button', name=label, exact=True).click()
        current = page.locator('#project-search').bounding_box()
        for dimension in ['x', 'width', 'height']:
            assert abs(current[dimension] - search_box[dimension]) < 0.001, (label, dimension, search_box, current)
    page.screenshot(path=str(OUT/'desktop-light.png'),full_page=True)
    page.locator('#project-search').fill('Zypper')
    assert page.locator('[data-project]:visible').count()==1
    assert 'rpm-impurifier' in page.locator('[data-project]:visible').inner_text()
    page.locator('#project-search').fill('dnf5')
    assert page.locator('[data-project]:visible').count()==1
    assert 'rpm-impurifier' in page.locator('[data-project]:visible').inner_text()
    page.locator('#project-search').fill('Nala')
    assert page.locator('[data-project]:visible').count()==1
    assert 'dpkg-impurifier' in page.locator('[data-project]:visible').inner_text()
    page.locator('#project-search').fill('no-such-frontend')
    assert page.locator('#no-projects').is_visible()
    page.locator('#reset-search').click()
    assert page.locator('[data-project]:visible').count()==PROJECT_COUNT
    page.get_by_role('button',name='Images & bundles',exact=True).click()
    assert page.locator('[data-project]:visible').count()==sum(project['category']=='Images & bundles' for project in PROJECTS)
    assert page.get_by_role('button',name='Images & bundles',exact=True).get_attribute('aria-pressed')=='true'
    page.get_by_role('button',name='All',exact=True).click()
    page.get_by_role('button',name='RPM',exact=True).click()
    assert 'makeOfflineRpm' in page.locator('#package-example').inner_text()
    assert page.locator('#example-docs').get_attribute('href')=='/rpm-impurifier/'
    page.get_by_role('button',name='Copy code example 1',exact=True).click()
    copied=page.evaluate('navigator.clipboard.readText()')
    assert copied==page.locator('#package-example').inner_text()
    page.get_by_role('button',name='DEB',exact=True).click()
    page.locator('[data-theme-toggle]').click(); page.locator('[data-theme-toggle]').click()
    assert page.locator('html').get_attribute('data-theme')=='dark'
    page.goto(BASE+'/rpm-impurifier/')
    assert page.locator('html').get_attribute('data-theme')=='dark'
    assert page.locator('h1').inner_text().startswith('rpm-impurifier')
    page.screenshot(path=str(OUT/'docs-dark.png'),full_page=False)
    page.goto(BASE+'/'); page.screenshot(path=str(OUT/'desktop-dark.png'),full_page=False)
    for slug in ['getting-started','testing','opkg-impurifier','portage-impurifier','bootc-impurifier','bitbake-impurifier','android-impurifier','termux-impurifier','dracut-impurifier','mkinitcpio-impurifier','impurifier']:
        response=page.goto(BASE+'/'+slug+'/'); assert response.status==200,slug
        assert page.locator('h1').count()==1,slug
    scaled=browser.new_context(viewport={'width':1920,'height':1080},device_scale_factor=2,color_scheme='light')
    sp=scaled.new_page(); sp.goto(BASE+'/'); sp.wait_for_selector('html.js')
    scaled_box=sp.locator('#project-search').bounding_box()
    for label in FILTERS:
        sp.get_by_role('button',name=label,exact=True).click()
        current=sp.locator('#project-search').bounding_box()
        for dimension in ['x','width','height']:
            assert abs(current[dimension]-scaled_box[dimension]) < 0.001, (label,dimension,scaled_box,current)
    sp.screenshot(path=str(OUT/'desktop-1080p-2x.png'),full_page=False)
    mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,color_scheme='light',is_mobile=True,has_touch=True)
    mp=mobile.new_page(); mp.on('pageerror',lambda error:errors.append(str(error)))
    for slug in ['','getting-started/','rpm-impurifier/','bitbake-impurifier/']:
        mp.goto(BASE+'/'+slug)
        assert mp.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth'),slug
    mp.goto(BASE+'/'); mp.screenshot(path=str(OUT/'mobile-light.png'),full_page=True)
    mobile_box = mp.locator('#project-search').bounding_box()
    for label in ['Profiles & environments', 'Native packages', 'All']:
        mp.get_by_role('button', name=label, exact=True).click()
        current = mp.locator('#project-search').bounding_box()
        for dimension in ['x', 'width', 'height']:
            assert abs(current[dimension] - mobile_box[dimension]) < 0.001, (label, dimension, mobile_box, current)
    mp.locator('#project-search').fill('apk')
    assert mp.locator('[data-project]:visible').count()==2
    mobile_matches=mp.locator('[data-project]:visible').all_inner_texts()
    assert all(any(name in row for row in mobile_matches) for name in ['apk-impurifier', 'android-impurifier'])
    nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
    np=nojs.new_page(); np.goto(BASE+'/')
    assert np.locator('[data-project]:visible').count()==PROJECT_COUNT
    assert not np.locator('#project-search').is_visible()
    assert np.get_by_role('link',name='dpkg-impurifier',exact=True).is_visible()
    np.get_by_role('link',name='dpkg-impurifier',exact=True).click()
    assert np.locator('h1').inner_text().startswith('dpkg-impurifier')
    assert not errors,errors
    browser.close()
if server: server.shutdown(); server.server_close()
print(f'Passed: desktop/mobile, all {PROJECT_COUNT} entries, search/filter/reset, examples, clipboard, persisted theme, guides and no-JavaScript navigation.')
