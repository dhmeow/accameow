#!/usr/bin/env python3
"""Extract the green 'The correct answer is ...' lines and attach each one to
the question that precedes it in the PDF. Writes answers.json keyed by chapter
index: {"0": [{"num": 1, "a": "B"}, {"num": 2, "a": "$8,290"}, ...]}
"""
import pymupdf, re, json
from collections import defaultdict

PDF = 'MA Complete Showhub.pdf'
PDF = 'MA Complete Studyhub Questions by MEOW.pdf'
d = pymupdf.open(PDF)
questions = json.load(open('raw_questions.json'))

def green_rects(page):
    out = []
    for it in page.get_drawings():
        if it['type'] == 'f' and it.get('fill'):
            c = it['fill']
            if abs(c[0] - 0.447) < 0.03 and c[1] > 0.95 and c[2] < 0.45:
                out.append(pymupdf.Rect(it['rect']))
    return out

HEAD = re.compile(r'(?i)^the\s+correct\s+answers?\s+(?:is|are)\s*:?\s*(.*)$')
LETTERS = re.compile(r'^\(?([A-D])\)?(?:\s*(?:,|and|&|/)\s*\(?([A-D])\)?)*\.?$')

def clean_answer(rest):
    rest = rest.strip()
    # cut at sentence end (but keep decimals like 3.69)
    m = re.match(r'^(.*?[^\d]\.)\s', rest + ' ')
    if m:
        rest = m.group(1)
    rest = rest.rstrip(' .;')
    if not rest:
        return None
    ls = re.findall(r'\b[A-D]\b', rest)
    if len(ls) >= 1 and re.fullmatch(r'[A-D\s,and&/()\.]+', rest):
        return ''.join(sorted(set(ls)))
    return rest[:60]

found = []
for pno in range(6, 221):
    page = d[pno]
    greens = green_rects(page)
    if not greens:
        continue
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            txt = ''.join(s['text'] for s in l['spans']).strip()
            if not txt:
                continue
            bb = pymupdf.Rect(l['bbox'])
            if bb.y0 < 80 or bb.y0 > 760:
                continue
            a = bb.get_area() or 1
            cov = min(1.0, sum((bb & g).get_area() for g in greens) / a)
            if cov < 0.45:
                continue
            m = HEAD.match(txt)
            if not m:
                continue
            ans = clean_answer(m.group(1))
            if ans:
                found.append((pno + 1, bb.y0, ans))

print('answer lines found:', len(found))
json.dump(found, open('answers_raw.json', 'w'))

pos = []
for i, q in enumerate(questions):
    lp, ly = q['page'], 0.0
    for b in q['blocks']:
        p = b.get('page') or q['page']
        y = b.get('y1') or 0
        if p > lp or (p == lp and y > ly):
            lp, ly = p, y
    pos.append((lp, ly))

order = sorted(range(len(questions)), key=lambda i: (pos[i][0], pos[i][1], i))
rank = {i: k for k, i in enumerate(order)}

assigned = {}
miss = []
for (ap, ay, ans) in found:
    best = None
    for idx in order:
        if pos[idx] <= (ap, ay):
            best = idx
    if best is None:
        miss.append((ap, ay, ans, 'nothing before it'))
        continue
    if best in assigned:
        k = rank[best]
        nxt = order[k + 1] if k + 1 < len(order) else None
        if nxt is not None and (ap, ay) >= pos[nxt]:
            best = nxt
        if best in assigned:
            miss.append((ap, ay, ans, 'collision q%d' % questions[best]['num']))
            continue
    assigned[best] = ans

by_ch = defaultdict(list)
for i, q in enumerate(questions):
    if i in assigned:
        by_ch[q['chapter']].append({'num': q['num'], 'a': assigned[i]})

missing = [(q['chapter'] + 1, q['num']) for i, q in enumerate(questions) if i not in assigned]
print('questions:', len(questions), 'answered:', len(assigned), 'missing:', len(missing))
print('missing:', missing)
print('unplaced:', len(miss))
for x in miss[:10]:
    print('  ', x)

# sanity: numeric answer attached to a question that shows A-D options
def has_options(q):
    for b in q['blocks']:
        if b['t'] == 'line' and re.match(r'^[A-D][\.\)]\s', b['text'].strip()):
            return True
    return False
sus = [(q['chapter'] + 1, q['num'], assigned[i]) for i, q in enumerate(questions)
       if i in assigned and has_options(q) and not re.fullmatch(r'[A-D]{1,4}', assigned[i])]
print('suspicious (options but non-letter answer):', len(sus), sus[:10])
letters = [a for a in assigned.values() if re.fullmatch(r'[A-D]{1,4}', a)]
print('letter answers:', len(letters), 'text answers:', len(assigned) - len(letters))
json.dump(by_ch, open('answers.json', 'w'), indent=1)
print('wrote answers.json')
