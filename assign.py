#!/usr/bin/env python3
"""Attach each green answer line to the question whose window contains it."""
import json
from collections import defaultdict

qs = json.load(open('raw_questions.json'))
raw = json.load(open('answers_raw.json'))          # [[page, y0, answer], ...]
raw.sort(key=lambda r: (r[0], r[1]))

def start(q):
    firsts = [b for b in q['blocks'] if b.get('first')]
    b = firsts[0] if firsts else (q['blocks'][0] if q['blocks'] else None)
    if b is None:
        return (q['page'], 0.0)
    return (b.get('page') or q['page'], b.get('y0') or 0.0)

starts = [start(q) for q in qs]
out = defaultdict(list)          # chapter -> list of (num, answer)
missing = []
for i, q in enumerate(qs):
    ch = q['chapter']
    lo = starts[i]
    # next question in the same chapter
    hi = None
    for j in range(i + 1, len(qs)):
        if qs[j]['chapter'] != ch:
            break
        hi = starts[j]
        break
    if hi is None:
        hi = (999, 0.0)
    hits = [r for r in raw if lo <= (r[0], r[1]) < hi]
    if hits:
        out[ch].append({'num': q['num'], 'a': hits[0][2]})
        extra = [h[2] for h in hits[1:]]
    else:
        out[ch].append({'num': q['num'], 'a': None})
        missing.append((ch + 1, q['num'], q['page']))

print('questions', len(qs), 'answered', sum(1 for v in out.values() for x in v if x['a']))
print('missing', len(missing))
for m in missing:
    q = [x for x in qs if x['chapter'] == m[0] - 1 and x['num'] == m[1]][0]
    kinds = [b.get('cls', 'line') for b in q['blocks']]
    print('  ', m, 'blocks', len(q['blocks']), kinds[:6])
# duplicates: same answer used twice?
used = defaultdict(int)
for ch, items in out.items():
    for it in items:
        if it['a']:
            used[(it['a'],)] += 1
json.dump(out, open('answers.json', 'w'), indent=1)
