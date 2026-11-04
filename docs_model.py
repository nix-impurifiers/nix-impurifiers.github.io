# SPDX-License-Identifier: MIT
"""Check documentation metadata and detect drift from its source snapshots.

Source excerpts locate where summaries came from. These checks do not test
backend behavior; backend integration and VM suites do that.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTRACT = json.loads((ROOT / 'content/model-contract.json').read_text())
STATES = {'known', 'unknown', 'not-applicable'}


def validate_fact(fact, definition, source, *, example=False):
    assert isinstance(fact, dict) and fact.get('state') in STATES, 'invalid fact state'
    if fact['state'] != 'known':
        assert set(fact) == {'state', 'reason'}, 'unknown/inapplicable facts cannot carry values'
        assert isinstance(fact['reason'], str) and fact['reason'].strip(), 'reason required'
        return
    expected = {'state', 'value', 'source_excerpts'} | ({'language'} if example else set())
    assert set(fact) == expected, 'unexpected or missing fact fields'
    value = fact['value']
    kind = definition['type']
    assert (kind == 'boolean' and type(value) is bool
            or kind == 'enum' and value in definition['values']
            or kind == 'text' and isinstance(value, str) and value.strip()), 'invalid fact value'
    assert isinstance(fact['source_excerpts'], list) and fact['source_excerpts'], 'source_excerpts required'
    assert all(isinstance(quote, str) and quote.strip() and quote in source
               for quote in fact['source_excerpts']), 'source_excerpts not found in reviewed README'
    if example:
        assert isinstance(fact['language'], str) and re.fullmatch(r'[A-Za-z0-9_+-]*', fact['language'])
        assert value in source, 'example must preserve source text'


def validate_record(project, record, source):
    assert set(record) == {'version', 'repository', 'reviewedRevision', 'readmeSha256', 'reviewBasis', 'facts', 'example'}
    assert record['version'] == CONTRACT['version']
    assert record['repository'] == 'nix-impurifiers/' + project['name']
    assert re.fullmatch(r'[0-9a-f]{40}', record['reviewedRevision']), 'invalid reviewed revision'
    assert record['reviewBasis'] == 'project-readme'
    assert record['readmeSha256'] == hashlib.sha256(source.encode()).hexdigest(), 'README changed: review the documentation record before publication'
    assert set(record['facts']) == set(CONTRACT['facts']), 'every contract field must be addressed'
    for key, definition in CONTRACT['facts'].items():
        validate_fact(record['facts'][key], definition, source)
        if key == 'validation' and record['facts'][key]['state'] == 'known':
            assert record['facts'][key]['value'] in record['facts'][key]['source_excerpts'], 'validation scope must be a verbatim source excerpt'
    validate_fact(record['example'], {'type': 'text'}, source, example=True)
    return record


def load_records(projects):
    directory = ROOT / 'content/models'
    assert {p.stem for p in directory.glob('*.json')} == {p['name'] for p in projects}, 'catalog/model coverage differs'
    records = {}
    for project in projects:
        name = project['name']
        source = (ROOT / 'content/projects' / f'{name}.md').read_text()
        try:
            records[name] = validate_record(project, json.loads((directory / f'{name}.json').read_text()), source)
        except AssertionError as error:
            raise AssertionError(f'{name}: {error}') from error
    return records


def fact_label(key, fact):
    if fact['state'] == 'unknown':
        return 'Unknown'
    if fact['state'] == 'not-applicable':
        return 'Not applicable'
    if key == 'target_nix':
        return CONTRACT['facts'][key]['labels'][fact['value']]
    if key == 'bundled_client':
        return 'Optional supplied static client' if fact['value'] else 'Not offered'
    return fact['value']


def source_review(project, record):
    return {'repository': record['repository'], 'reviewedRevision': record['reviewedRevision'],
            'snapshotRevision': project['revision'], 'readmeSha256': record['readmeSha256'],
            'reviewBasis': record['reviewBasis'],
            'status': 'matched' if record['reviewedRevision'] == project['revision'] else 'readme-unchanged'}
