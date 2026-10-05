"""Regenerate aggregate policy evidence from private, pinned local inputs.

No policy is selected and no dictionary is emitted. See README for input pins.
"""
import argparse
import collections
import gc
import hashlib
import itertools
import json
import sqlite3
from pathlib import Path
from readers import normalize, read_binary, read_mrd, read_morph_json, require


def signatures(db, name, kind):
    out = collections.defaultdict(list)
    for lid, key, n in db.execute(f'SELECT lid,{kind},n FROM {name}_lemmas'):
        out[key].append((lid, n))
    return out


def id_feasibility(db):
    old = signatures(db, 'old', 'ordered')
    new = signatures(db, 'new', 'ordered')
    matched = [v[0] for k, v in old.items() if len(v) == 1 and len(new.get(k, [])) == 1]
    old_count, old_forms = db.execute('SELECT count(*),sum(n) FROM old_lemmas').fetchone()
    new_count, new_forms = db.execute('SELECT count(*),sum(n) FROM new_lemmas').fetchone()
    no_semantic = db.execute('SELECT count(*) FROM old_lemmas o WHERE NOT EXISTS '
                            '(SELECT 1 FROM new_lemmas n WHERE n.semantic=o.semantic)').fetchone()[0]
    # Use a set rather than an unindexed correlated spelling query.
    spellings = {r[0] for r in db.execute('SELECT lemma FROM new_lemmas')}
    no_spelling = sum(r[0] not in spellings for r in db.execute('SELECT lemma FROM old_lemmas'))
    ids = sum(n for _, n in matched)
    return dict(unique_exact_ordered_paradigms=len(matched),
                preservable_ids_in_exact_ordered_paradigms=ids,
                old_paradigms_no_semantic_match=no_semantic,
                old_paradigms_no_lemma_spelling=no_spelling,
                unresolved_old_slots=old_count-len(matched),
                new_records_to_append=new_count-len(matched),
                total_slots_if_preserving_all_old_slots=old_count+new_count-len(matched),
                retired_old_ids=old_forms-ids, retention_forms_total=new_forms+old_forms-ids)


def gender_option(db):
    old = signatures(db, 'old', 'semantic')
    changed = matched = 0
    old_ids = set()
    rows = db.execute('SELECT lid,surface,tags FROM new ORDER BY lid,tid')
    for lid, group in itertools.groupby(rows, lambda r:r[0]):
        row = [(word, set(tags)) for _, word, tags in group]
        if not any({1,48} <= tags for _, tags in row):
            continue
        changed += 1
        collapsed = [(w, sorted((t-{1,48})|{27}) if {1,48} <= t else sorted(t)) for w,t in row]
        key = hashlib.sha256(json.dumps(collapsed, ensure_ascii=False, separators=(',',':')).encode()).hexdigest()
        if key in old:
            matched += 1
            old_ids.update(lid for lid, _ in old[key])
    return dict(new_paradigms_with_joint_male_female_tags=changed,
                new_paradigms_matching_old_after_collapse=matched,
                distinct_old_paradigms_matched=len(old_ids))


def stable_verification(binary, variants):
    original, _ = read_binary(binary)
    report = {}
    for policy, path in variants:
        rows, _ = read_binary(path, allow_empty=True)
        require(len(rows) >= len(original), 'stable resource omits old slots')
        same = empty = changed = 0
        for old, new in zip(original, rows):
            if old == new: same += 1
            elif not new: empty += 1
            else: changed += 1
        report[policy] = dict(unchanged_old_paradigms=same, empty_old_slots=empty,
                              changed_nonempty_old_slots=changed, slots=len(rows),
                              forms=sum(map(len, rows)))
        del rows
        gc.collect()
    return report


def removal_history(db, stages):
    lost = {r[0] for r in db.execute('SELECT surface FROM old EXCEPT SELECT surface FROM new')}
    remaining = lost.copy()
    timeline = []
    for stage, path in stages:
        path = Path(path)
        source = read_morph_json(path) if path.suffix == '.json' else read_mrd(path)
        present = set()
        for lemma in source.lemmas:
            if lemma.stem.startswith('-'): continue
            for ending in source.models[lemma.model]:
                word = normalize(ending.prefix+lemma.stem+ending.suffix)
                if word in lost: present.add(word)
        removed = remaining-present
        timeline.append(dict(stage=stage, file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                             lost_from_published_present=len(present), removed_since_previous=len(removed)))
        remaining = present
    # Publish aggregate categories only, without source-derived lexical samples.
    contracted = sum(word.endswith('ьи') for word in lost)
    return dict(timeline=timeline, categories={'contracted_-ьи': contracted,
                                              'other_lost_surfaces': len(lost)-contracted})



def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--database', required=True)
    p.add_argument('--output-dir', required=True)
    p.add_argument('--binary', required=True)
    p.add_argument('--retain-legacy', required=True)
    p.add_argument('--tombstone', required=True)
    p.add_argument('--history-dir', required=True)
    a = p.parse_args()
    out = Path(a.output_dir);out.mkdir(exist_ok=False)
    db = sqlite3.connect(f'file:{a.database}?mode=ro', uri=True)
    def save(name, value):
        (out/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
        print(name, flush=True)
    save('id-feasibility.json', id_feasibility(db))
    save('gender-option.json', gender_option(db))
    save('stable-verification.json', stable_verification(a.binary, [('retain-legacy', a.retain_legacy), ('tombstone', a.tombstone)]))
    history = Path(a.history_dir)
    save('removal-history.json', removal_history(db, [(stage, history/name) for stage,name in [
        ('initial','initial-upstream.mrd'),('pre-think','pre-think.mrd'),('post-think','post-think.mrd'),
        ('pre-json','historical.mrd'),('post-pack','post-pack.json')]]))
    inputs = [Path(a.binary),Path(a.retain_legacy),Path(a.tombstone)]
    save('policy-inputs.json', {str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs})

if __name__ == '__main__':
    main()
