import json
import tempfile
import unittest
from pathlib import Path
from readers import *

class ReadersTest(unittest.TestCase):
    def file(self,text):
        d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup)
        p=Path(d.name)/'input';p.write_text(text,encoding='utf8');return p

    def source(self,**kw):
        d=dict(flexia_models=[dict(endings=[dict(flexia='А',gramcode='AA'),dict(flexia='Ы',gramcode='AB',prefix='ПРЕ')])],
               lemmas=[dict(l='ЗОРКА',f=0,a=0,s=0,t='AC')],accent_models=[[255,255]],sessions=[{}],prefix_sets=[])
        d.update(kw);return d

    def test_full_lemma_is_not_stem(self):
        s=read_morph_json(self.file(json.dumps(self.source())))
        self.assertEqual(s.lemmas[0].stem,'ЗОРК')
        self.assertEqual(list(expand(s,{'AA':(19,),'AB':(19,0),'AC':(20,)})),[[('зорка',(19,20)),('презоркы',(19,0,20))]])

    def test_empty_suffix_and_stem(self):
        d=self.source(flexia_models=[dict(endings=[dict(flexia='',gramcode='AA')])],lemmas=[dict(l='ДОМ',f=0,a=0,s=0)])
        self.assertEqual(read_morph_json(self.file(json.dumps(d))).lemmas[0].stem,'ДОМ')
        d=self.source(lemmas=[dict(l='А',f=0,a=0,s=0)])
        self.assertEqual(read_morph_json(self.file(json.dumps(d))).lemmas[0].stem,'')

    def test_unknown_tags_and_fields_fail(self):
        for d in [dict(gramcodes={'AA':{'p':'NEW','g':[]}}),dict(gramcodes={'AA':{'p':'N','g':['NEW']}})]:
            with self.assertRaises(FormatError):read_gram_json(self.file(json.dumps(d)))
        with self.assertRaises(FormatError):read_morph_json(self.file(json.dumps(self.source(extra=[]))))

    def test_duplicate_json_key_fails(self):
        with self.assertRaises(FormatError):load_json(self.file('{"x":1,"x":2}'))

    def test_bad_ending_and_index_fail(self):
        for lemma in [dict(l='ДОМ',f=0,a=0,s=0),dict(l='А',f=-1,a=0,s=0),dict(l='А',f=0,a=9,s=0)]:
            with self.assertRaises(FormatError):read_morph_json(self.file(json.dumps(self.source(lemmas=[lemma]))))

    def test_prefix_policy_explicit(self):
        d=self.source(prefix_sets=[['ПСЕВДО']],lemmas=[dict(l='ЗОРКА',f=0,a=0,s=0,p=0)])
        s=read_morph_json(self.file(json.dumps(d)))
        with self.assertRaisesRegex(FormatError,'prefix-set'):list(expand(s,{'AA':(19,),'AB':(19,)}))
        self.assertEqual(len(list(expand(s,{'AA':(19,),'AB':(19,)},prefix_policy='legacy-ignore'))),1)

    def test_common_gender_is_not_rewritten(self):
        tags=read_gram_json(self.file(json.dumps(dict(gramcodes={'AA':dict(p='N',g=['mas-fem']),'AB':dict(p='N',g=['mas','fem'])}))))
        self.assertEqual(tags['AA'],(19,27));self.assertEqual(tags['AB'],(19,1,48))

    def test_order_duplicates_and_normalization(self):
        s=Source([[Ending('Ё','AA'),Ending('Ё','AA')]], [Lemma('ВС',0,0,0)],[[255]],[],[])
        self.assertEqual(list(expand(s,{'AA':(19,1,19)})),[[('все',(19,1)),('все',(19,1))]])
        with self.assertRaises(FormatError):normalize('LATIN')

    def test_empty_pos_preserves_legacy_marker(self):
        tags=read_gram_json(self.file(json.dumps(dict(gramcodes={'AA':dict(p='',g=['anim'])}))))
        self.assertEqual(tags['AA'],(30,36))

    def test_binary_counts_and_ordinals(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'tiny.gz'
            def block(n,b):return struct.pack('>ii',n,len(b))+b
            data=block(1,bytes([19,1,100]))+block(1,'дом'.encode('cp1251')+b'd')+block(1,struct.pack('>iii',1,0,0))+block(0,b'')
            with gzip.open(p,'wb') as f:f.write(data)
            self.assertEqual(read_binary(p)[0],[[('дом',(19,1))]])
            with gzip.open(p,'wb') as f:f.write(data+b'junk')
            with self.assertRaises(FormatError):read_binary(p)

    def test_tab_duplicate_requires_explicit_policy(self):
        p=self.file('AA X С ед\nAA X С мн\n')
        with self.assertRaises(FormatError):read_tab(p)
        self.assertEqual(read_tab(p,duplicate_policy='legacy-last-wins')['AA'],(19,0))

    def test_mrd_and_json_synthetic_equivalence(self):
        mrd=self.file('1\n%А*AA%Ы*AB*ПРЕ\n1\n255;255;\n1\nu;start;end\n0\n1\nЗОРК 0 0 0 AC -\n')
        js=self.file(json.dumps(self.source(sessions=[dict(user='u',start='start',last_save='end')])))
        self.assertEqual(read_mrd(mrd),read_morph_json(js))

    def test_mrd_truncation(self):
        with self.assertRaises(FormatError):read_mrd(self.file('2\n%А*AA\n'))

    def test_unknown_code_even_in_unused_model(self):
        s=Source([[Ending('А','XX')]],[],[],[],[])
        with self.assertRaises(FormatError):list(expand(s,{}))

if __name__=='__main__':unittest.main()
