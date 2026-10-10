import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from compare import historical
from readers import FormatError, expand, read_gram_json, read_morph_json, read_mrd


class HistoricalTest(unittest.TestCase):
    def inputs(self, old_ending='AA', new_ending='AA', old_common='',
               new_common='', unused_old=None, unused_new=None, stem='ДОМ'):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        models = ['%*' + old_ending]
        if unused_old:
            models.append('%*' + unused_old)
        (root / 'input.mrd').write_text(
            f'{len(models)}\n' + '\n'.join(models) +
            f'\n1\n255;\n0\n0\n1\n{stem} 0 0 -1 {old_common or "-"} -\n',
            encoding='utf-8')
        models = [dict(endings=[dict(flexia='', gramcode=new_ending)])]
        if unused_new:
            models.append(dict(endings=[dict(flexia='', gramcode=unused_new)]))
        morph = dict(flexia_models=models,
                     lemmas=[dict(l=stem, f=0, a=0, s=-1, t=new_common)],
                     accent_models=[[255]], sessions=[], prefix_sets=[])
        (root / 'input.json').write_text(json.dumps(morph), encoding='utf-8')
        (root / 'gram.json').write_text(json.dumps(dict(gramcodes={
            'AA': dict(p='N', g=['sg']), 'AC': dict(p='', g=['anim'])
        })), encoding='utf-8')
        return SimpleNamespace(mrd=root / 'input.mrd', morph=root / 'input.json',
                               gram=root / 'gram.json')

    def test_known_codes_validate_and_keep_matching_raw_digests(self):
        args = self.inputs(old_common='AC', new_common='AC')
        report = historical(args)
        self.assertEqual(report['semantic_import_status'], 'validated')
        self.assertEqual(report['old_raw_expansion'], report['new_raw_expansion'])
        self.assertEqual(report['old_raw_expansion']['forms'], 1)
        for source in ('old', 'new'):
            self.assertEqual(report['semantic_validation'][source],
                             dict(missing_ending_codes=[], missing_common_codes=[]))
        tags = read_gram_json(args.gram)
        self.assertEqual(list(expand(read_mrd(args.mrd), tags)),
                         list(expand(read_morph_json(args.morph), tags)))

    def test_matching_unknown_common_codes_block_semantics_only(self):
        args = self.inputs(old_common='ZZ', new_common='ZZ')
        report = historical(args)
        self.assertEqual(report['semantic_import_status'], 'blocked')
        self.assertEqual(report['old_raw_expansion'], report['new_raw_expansion'])
        self.assertEqual(report['missing_ending_codes'], [])
        for source in ('old', 'new'):
            self.assertEqual(report['semantic_validation'][source]['missing_common_codes'],
                             [dict(code='ZZ', using_lemmas=1)])
        for reader, path in ((read_mrd, args.mrd), (read_morph_json, args.morph)):
            with self.assertRaisesRegex(FormatError, 'unknown common code ZZ'):
                list(expand(reader(path), read_gram_json(args.gram)))

    def test_unknown_common_code_in_either_source_blocks(self):
        for source in ('old', 'new'):
            with self.subTest(source=source):
                report = historical(self.inputs(**{source + '_common': 'ZZ'}))
                self.assertEqual(report['semantic_import_status'], 'blocked')
                self.assertEqual(report['semantic_validation'][source]['missing_common_codes'],
                                 [dict(code='ZZ', using_lemmas=1)])
                other = 'new' if source == 'old' else 'old'
                self.assertEqual(report['semantic_validation'][other]['missing_common_codes'], [])

    def test_unknown_ending_code_in_either_source_blocks(self):
        for source in ('old', 'new'):
            with self.subTest(source=source):
                report = historical(self.inputs(**{source + '_ending': 'ZZ'}))
                self.assertEqual(report['semantic_import_status'], 'blocked')
                self.assertEqual(report['semantic_validation'][source]['missing_ending_codes'],
                                 [dict(model=0, code='ZZ', using_lemmas=1)])
                self.assertEqual(report['missing_ending_codes'],
                                 report['semantic_validation']['old']['missing_ending_codes'])

    def test_unknown_code_in_unused_models_blocks_in_both_sources(self):
        args = self.inputs(unused_old='ZZ', unused_new='YY')
        report = historical(args)
        self.assertEqual(report['semantic_import_status'], 'blocked')
        self.assertEqual(report['old_raw_expansion'], report['new_raw_expansion'])
        for source, code in (('old', 'ZZ'), ('new', 'YY')):
            self.assertEqual(report['semantic_validation'][source]['missing_ending_codes'],
                             [dict(model=1, code=code, using_lemmas=0)])

    def test_common_codes_on_meta_entries_are_validated(self):
        report = historical(self.inputs(stem='-МЕТА', old_common='ZZ', new_common='YY'))
        self.assertEqual(report['semantic_import_status'], 'blocked')
        for source, code in (('old', 'ZZ'), ('new', 'YY')):
            self.assertEqual(report['semantic_validation'][source]['missing_common_codes'],
                             [dict(code=code, using_lemmas=1)])

    def test_absent_common_codes_are_not_missing(self):
        report = historical(self.inputs())
        self.assertEqual(report['semantic_import_status'], 'validated')
        for source in ('old', 'new'):
            self.assertEqual(report['semantic_validation'][source]['missing_common_codes'], [])

    def test_missing_common_counts_are_aggregated_and_sorted(self):
        args = self.inputs(new_common='ZZ')
        morph = json.loads(args.morph.read_text())
        morph['lemmas'] += [dict(l='КОТ', f=0, a=0, s=-1, t='YY'),
                            dict(l='ЛЕС', f=0, a=0, s=-1, t='ZZ')]
        args.morph.write_text(json.dumps(morph), encoding='utf-8')
        report = historical(args)
        self.assertEqual(report['semantic_validation']['new']['missing_common_codes'],
                         [dict(code='YY', using_lemmas=1), dict(code='ZZ', using_lemmas=2)])
        self.assertEqual(report, historical(args))

    def test_cli_writes_blocked_report_with_raw_evidence(self):
        args = self.inputs(old_common='ZZ', new_common='ZZ')
        output = args.mrd.parent / 'report.json'
        result = subprocess.run([
            sys.executable, str(Path(__file__).with_name('compare.py')), 'historical',
            '--mrd', str(args.mrd), '--morph', str(args.morph),
            '--gram', str(args.gram), '--output', str(output)
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(output.read_text())
        self.assertEqual(report['semantic_import_status'], 'blocked')
        self.assertEqual(report['old_raw_expansion'], report['new_raw_expansion'])
        self.assertEqual(set(report['inputs']), {'mrd', 'morph', 'gram'})

    def test_valid_code_resolution_does_not_claim_raw_equivalence(self):
        report = historical(self.inputs(new_common='AC'))
        self.assertEqual(report['semantic_import_status'], 'validated')
        self.assertNotEqual(report['old_raw_expansion'], report['new_raw_expansion'])


if __name__ == '__main__':
    unittest.main()
