# SPDX-License-Identifier: MIT
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from docs_model import load_records, validate_record, source_review


class DocumentationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects=json.loads((ROOT/'content/projects.json').read_text())
        cls.records=load_records(cls.projects)

    def fixture(self):
        project=self.projects[0]
        return project,copy.deepcopy(self.records[project['name']]),(ROOT/'content/projects'/f'{project["name"]}.md').read_text()

    def test_every_project_has_an_explicit_record(self):
        self.assertEqual(set(self.records),{p['name'] for p in self.projects})

    def test_changed_readme_requires_review(self):
        project,record,source=self.fixture()
        with self.assertRaisesRegex(AssertionError,'README changed'):
            validate_record(project,record,source+'\nNew behavior.\n')

    def test_unknown_requires_reason_and_cannot_claim_false(self):
        project,record,source=self.fixture()
        record['facts']['bundled_client']={'state':'unknown','reason':'Not reviewed.'}
        validate_record(project,record,source)
        record['facts']['bundled_client']['value']=False
        with self.assertRaises(AssertionError):validate_record(project,record,source)
        record['facts']['bundled_client']={'state':'unknown','reason':''}
        with self.assertRaises(AssertionError):validate_record(project,record,source)

    def test_missing_fact_and_unsupported_enum_are_rejected(self):
        project,record,source=self.fixture()
        del record['facts']['target_nix']
        with self.assertRaises(AssertionError):validate_record(project,record,source)
        project,record,source=self.fixture()
        record['facts']['target_nix']['value']='inferred-from-family'
        with self.assertRaises(AssertionError):validate_record(project,record,source)

    def test_evidence_must_exist_and_example_must_remain_source_text(self):
        project,record,source=self.fixture()
        record['facts']['target_nix']['evidence']=['Unreviewed assertion.']
        with self.assertRaises(AssertionError):validate_record(project,record,source)
        project,record,source=self.fixture()
        record['example']['value']='invented command'
        with self.assertRaises(AssertionError):validate_record(project,record,source)

    def test_validation_scope_cannot_expand_its_evidence(self):
        project,record,source=self.fixture()
        record['facts']['validation']['value']='Every operating system is supported.'
        with self.assertRaisesRegex(AssertionError,'verbatim'):
            validate_record(project,record,source)

    def test_identical_readme_with_newer_source_keeps_review_identity(self):
        project,record,source=self.fixture()
        project=dict(project,revision='f'*40)
        validate_record(project,record,source)
        status=source_review(project,record)
        self.assertEqual(status['status'],'readme-unchanged')
        self.assertEqual(status['reviewedRevision'],record['reviewedRevision'])


if __name__=='__main__':unittest.main()
