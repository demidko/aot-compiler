import sqlite3,tempfile,unittest,struct
from pathlib import Path
from write_prefix import paradigms,write_prefix
from order_comparison import ordered,jhash

class WriterTest(unittest.TestCase):
    def database(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);p=Path(tmp.name)/'data.sqlite';d=sqlite3.connect(p)
        for name,keys in [('old',['A','B','D','D']),('new',['B','A','D','C'])]:
            d.execute(f'CREATE TABLE {name}(lid INT,tid INT,surface TEXT,tags BLOB)')
            d.execute(f'CREATE TABLE {name}_lemmas(lid INT,ordered TEXT)')
            for lid,key in enumerate(keys):
                d.execute(f'INSERT INTO {name}_lemmas VALUES(?,?)',(lid,key))
                d.execute(f'INSERT INTO {name} VALUES(?,?,?,?)',(lid,0,{'A':'дом','B':'кот','C':'лес','D':'луг'}[key],bytes([19])))
        d.commit();self.addCleanup(d.close);return p,d

    def test_unique_matching_preserves_slots_and_appends_ambiguous(self):
        _,db=self.database();rows=list(paradigms(db,'new','tombstone'))
        self.assertEqual([i for i,_ in rows],list(range(6)))
        self.assertEqual([r[0][2] if r else None for _,r in rows],['дом','кот',None,None,'луг','лес'])
        rows=list(paradigms(db,'new','retain-legacy'))
        self.assertEqual([r[0][2] for _,r in rows],['дом','кот','луг','луг','луг','лес'])

    def test_prefix_blocks_and_no_overwrite(self):
        p,_=self.database();out=p.with_suffix('.bin');info=write_prefix(p,'old',out)
        self.assertEqual(info['lemmas'],4);self.assertEqual(info['strings'],3)
        raw=out.read_bytes();self.assertEqual(raw[:10],struct.pack('>ii',1,2)+bytes([19,100]))
        with self.assertRaises(ValueError):write_prefix(p,'old',out)

    def test_result_order_comes_from_reference_list(self):
        b=struct.pack('>iii',2,5,1);ref=(b,{jhash('дом'):0})
        rows=[('дом','один',b'',b'\x13',1,0),('дом','два',b'',b'\x13',5,0)]
        self.assertEqual(ordered('дом',rows,ref),[('два',b'\x13'),('один',b'\x13')])
        self.assertEqual(jhash('Aa'),jhash('BB'))

if __name__=='__main__':unittest.main()
