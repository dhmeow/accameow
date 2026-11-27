#!/usr/bin/env python3
"""Extract question text (green answers removed) from the MA Studyhub PDF.

Strategy
--------
* green highlight rectangles = answer paragraphs  -> dropped
* black grid lines / narrow green cells = tables    -> cropped as images (green kept)
* vector glyph art (formulas)                       -> cropped as images
* raster diagrams                                   -> cropped as images
* everything else                                   -> real text
"""
import pymupdf, re, json, base64, hashlib, os, sys
from collections import defaultdict

DOC = 'MA Complete Studyhub Questions by MEOW.pdf'
OUT = 'questions.json'
IMGDIR = 'assets'
os.makedirs(IMGDIR, exist_ok=True)

d = pymupdf.open(DOC)

CHAPTERS = [
    (7, 'Management Information'),
    (16, 'Materials'),
    (22, 'Managing Inventory'),
    (29, 'Labour'),
    (36, 'Overheads'),
    (48, 'Absorption and Marginal Costing'),
    (56, 'Process Costing, Joint Products and Further Processing'),
    (62, 'Cost Classification'),
    (76, 'Job, Batch and Service Costing'),
    (83, 'Alternative Cost Accounting Methods'),
    (88, 'Sampling Techniques and Expected Values'),
    (92, 'Forecasting Costs and Revenues'),
    (99, 'Time Series Analysis'),
    (104, 'Index Numbers'),
    (107, 'Spreadsheets'),
    (109, 'Compounding and Discounting'),
    (113, 'Investment Appraisal'),
    (123, 'Nature and Purpose of Budgeting'),
    (136, 'Fixed and Flexible Budgets, Budgetary Control, and Reporting'),
    (149, 'Behavioural Aspects of Budgeting'),
    (154, 'Presenting Information'),
    (161, 'Summarising and Analysing Data'),
    (168, 'Standard Costing and Variance Analysis'),
    (200, 'Introduction to Performance Management'),
    (205, 'Analysing Performance'),
    (210, 'Monitoring Performance, Cost Reductions, and Value Enhancement'),
]
CH_START = {p: i for i, (p, t) in enumerate(CHAPTERS)}

def chapter_of(page_no):  # page_no is 1-based pdf page
    idx = 0
    for i, (p, t) in enumerate(CHAPTERS):
        if page_no >= p:
            idx = i
    return idx

QPAT = re.compile(r'^(\d{1,3})[\.\)]\s+(\S.*)$')
OPTPAT = re.compile(r'^([A-D])[\.\)]\s*(.*)$')

def green_rects(page):
    out = []
    for it in page.get_drawings():
        if it['type'] == 'f' and it.get('fill'):
            c = it['fill']
            if abs(c[0] - 0.447) < 0.03 and c[1] > 0.95 and c[2] < 0.45:
                out.append(pymupdf.Rect(it['rect']))
    return out

def red_seps(page):
    out = []
    for it in page.get_drawings():
        r = pymupdf.Rect(it['rect'])
        if it['type'] == 's' and it.get('color') == (1.0, 0.0, 0.0) and r.height < 2 and r.width > 300:
            out.append(r.y0)
    return sorted(out)

def grid_zones(page):
    strokes = []
    for it in page.get_drawings():
        if it['type'] != 's':
            continue
        c = it.get('color')
        if not c or max(c) > 0.12:
            continue
        w = it.get('width') or 0
        if w > 1.5:
            continue
        strokes.append(pymupdf.Rect(it['rect']))
    # union-find on touching rects
    n = len(strokes)
    parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    for i in range(n):
        for j in range(i + 1, n):
            a, b = strokes[i], strokes[j]
            if a.intersects(b + (-3, -3, 3, 3)):
                union(i, j)
    comps = defaultdict(list)
    for i in range(n):
        comps[find(i)].append(strokes[i])
    zones = []
    for comp in comps.values():
        if len(comp) < 3:
            continue
        h = [r for r in comp if r.height < 1.6 and r.width > 30]
        v = [r for r in comp if r.width < 1.6 and r.height > 12]
        if len(h) < 2 or len(v) < 2:
            continue
        bb = pymupdf.Rect(comp[0])
        for r in comp[1:]:
            bb |= r
        if bb.width > 60 and bb.height > 16:
            zones.append(bb)
    return zones

def column_zones(lines):
    """Detect borderless tables: >=2 aligned text columns repeated over >=2 rows."""
    rows = []
    for l in sorted(lines, key=lambda x: (x['bb'].y0, x['bb'].x0)):
        if rows and abs(l['bb'].y0 - rows[-1]['y0']) <= 4:
            rows[-1]['lines'].append(l)
            rows[-1]['y1'] = max(rows[-1]['y1'], l['bb'].y1)
        else:
            rows.append({'y0': l['bb'].y0, 'y1': l['bb'].y1, 'lines': [l]})
    for r in rows:
        r['lines'].sort(key=lambda l: l['bb'].x0)
        clusters = []
        for l in r['lines']:
            if clusters and l['bb'].x0 - clusters[-1][1] < 12:
                clusters[-1][1] = max(clusters[-1][1], l['bb'].x1)
                clusters[-1][2].append(l)
            else:
                clusters.append([l['bb'].x0, l['bb'].x1, [l]])
        r['clusters'] = clusters
        r['anchor'] = clusters[0][0]
    zones = []
    i = 0
    while i < len(rows):
        if len(rows[i]['clusters']) < 2:
            i += 1
            continue
        j = i
        run = [rows[i]]
        while j + 1 < len(rows) and len(rows[j + 1]['clusters']) >= 2 and \
                rows[j + 1]['y0'] - rows[j]['y1'] < 14:
            j += 1
            run.append(rows[j])
        if len(run) >= 2:
            # consistent columns?
            cols_ok = 0
            for c in run[0]['clusters'][1:]:
                x = c[0]
                hits = 0
                for r2 in run[1:]:
                    if any(abs(cl[0] - x) < 10 for cl in r2['clusters']):
                        hits += 1
                if hits >= len(run) - 1:
                    cols_ok += 1
            if cols_ok >= 1:
                z = pymupdf.Rect(run[0]['clusters'][0][0], run[0]['y0'],
                                 max(cl[1] for cl in run[0]['clusters']), run[-1]['y1'])
                for r2 in run:
                    z |= pymupdf.Rect(r2['clusters'][0][0], r2['y0'],
                                      max(cl[1] for cl in r2['clusters']), r2['y1'])
                # header rows above that share a column
                k = i - 1
                while k >= 0 and z.y0 - rows[k]['y1'] < 30:
                    if any(abs(cl[0] - c[0]) < 10 for cl in rows[k]['clusters'] for c in run[0]['clusters'][1:]):
                        z |= pymupdf.Rect(rows[k]['clusters'][0][0], rows[k]['y0'],
                                          max(cl[1] for cl in rows[k]['clusters']), rows[k]['y1'])
                    k -= 1
                zones.append(z)
                i = j + 1
                continue
        i += 1
    return zones

def formula_zones(page):
    fills = []
    for it in page.get_drawings():
        if it['type'] != 'f':
            continue
        c = it.get('fill')
        if not c or max(c) > 0.12:
            continue
        r = pymupdf.Rect(it['rect'])
        if r.get_area() < 900 and r.width < 34 and r.height < 34:
            fills.append(r)
    if len(fills) < 4:
        return []
    fills.sort(key=lambda r: (r.y0, r.x0))
    zones = []
    used = [False] * len(fills)
    for i in range(len(fills)):
        if used[i]:
            continue
        grp = [fills[i]]
        used[i] = True
        changed = True
        while changed:
            changed = False
            gb = grp[0]
            for r in grp[1:]:
                gb |= r
            gb = pymupdf.Rect(gb.x0 - 6, gb.y0 - 6, gb.x1 + 6, gb.y1 + 6)
            for j in range(len(fills)):
                if used[j]:
                    continue
                if fills[j].intersects(gb):
                    grp.append(fills[j])
                    used[j] = True
                    changed = True
        if len(grp) < 4:
            continue
        bb = pymupdf.Rect(grp[0])
        for r in grp[1:]:
            bb |= r
        if bb.width > 20 and bb.height > 6:
            zones.append(pymupdf.Rect(bb.x0 - 2, bb.y0 - 2, bb.x1 + 2, bb.y1 + 2))
    return zones

_crop_cache = {}
def crop(page, rect, pad=2):
    rect = pymupdf.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)
    rect &= page.rect
    rect = pymupdf.Rect(round(rect.x0, 1), round(rect.y0, 1), round(rect.x1, 1), round(rect.y1, 1))
    key = (page.number, tuple(rect))
    if key in _crop_cache:
        return _crop_cache[key]
    pix = page.get_pixmap(clip=rect, matrix=pymupdf.Matrix(2.1, 2.1), alpha=False)
    data = pix.tobytes('png')
    name = hashlib.md5(data).hexdigest()[:16] + '.png'
    path = os.path.join(IMGDIR, name)
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(data)
    _crop_cache[key] = name
    return name

def _pix_bytes(xref):
    pix = pymupdf.Pixmap(d, xref)
    if pix.colorspace is None or pix.colorspace.n not in (1, 3):
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    return pix

def compose_image_grid(xrefs, cols=2, cell_w=290, gap=16, margin=14):
    """Lay several rasters out in a clean grid (A/B on top, C/D below).

    Some pages stack their option rasters on top of each other, so the later
    image's white background hides the earlier graph.  Re-drawing them side by
    side keeps every option fully visible.
    """
    cells = []
    for xref in xrefs:
        pix = _pix_bytes(xref)
        cells.append((pix, pix.width / max(1, pix.height)))
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    row_h = [max(cell_w / ar for _, ar in row) for row in rows]
    width = margin * 2 + cols * cell_w + (cols - 1) * gap
    height = margin * 2 + sum(row_h) + (len(rows) - 1) * gap
    out = pymupdf.open()
    p = out.new_page(width=width, height=height)
    y = margin
    for row, rh in zip(rows, row_h):
        x = margin
        for pix, ar in row:
            h = cell_w / ar
            p.insert_image(pymupdf.Rect(x, y, x + cell_w, y + h), stream=pix.tobytes('png'))
            x += cell_w + gap
        y += rh + gap
    pixout = p.get_pixmap(matrix=pymupdf.Matrix(2.1, 2.1), alpha=False)
    # the source rasters carry a pale green edge line; keep the grid clean
    s = bytearray(pixout.samples)
    for i in range(0, len(s), pixout.n):
        r, g, b = s[i], s[i + 1], s[i + 2]
        if g > r + 12 and g > b + 12 and r > 120:
            s[i] = s[i + 1] = s[i + 2] = 255
    pixout = pymupdf.Pixmap(pixout.colorspace, pixout.width, pixout.height, bytes(s), pixout.alpha)
    data = pixout.tobytes('png')
    name = hashlib.md5(data).hexdigest()[:16] + '.png'
    with open(os.path.join(IMGDIR, name), 'wb') as f:
        f.write(data)
    return name, width, height

def overlap_groups(rects, thresh=0.15):
    """Group rects that sit on top of each other (occluding rasters)."""
    n = len(rects)
    parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for i in range(n):
        for j in range(i + 1, n):
            inter = (rects[i] & rects[j]).get_area()
            if inter > thresh * min(rects[i].get_area(), rects[j].get_area()):
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[rj] = ri
    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(rects[i])
    return list(groups.values())

def line_text(line):
    return ''.join(s['text'] for s in line['spans'])

def page_lines(page):
    lines = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            txt = line_text(l)
            if not txt.strip():
                continue
            bb = pymupdf.Rect(l['bbox'])
            if bb.y0 < 82 or bb.y0 > 752:
                continue
            size = max(s['size'] for s in l['spans'])
            bold = any('Bold' in s['font'] or 'Black' in s['font'] or 'Semi' in s['font'] for s in l['spans'])
            lines.append({'bb': bb, 'text': txt.strip(), 'size': size, 'bold': bold})
    return lines

def looks_like_stem(pending):
    texts = [p['text'].strip() for p in pending if p['kind'] == 'text']
    if not texts:
        return True
    first = texts[0]
    if OPTPAT.match(first) or (first and first[0].islower()):
        return False
    if len(first) < 25 and not first.rstrip().endswith(('.', ':', '?')):
        return False
    return True

def coverage(r, greens):
    if not greens:
        return 0.0
    a = r.get_area()
    if a <= 0:
        return 0.0
    s = 0.0
    for g in greens:
        s += (r & g).get_area()
    return min(1.0, s / a)

# ---------------------------------------------------------------- extraction
questions = []      # flat list
cur = None
expected = 1
missed = []
pending = []        # elements waiting for the next question start
warnings = []

def new_question(num, chapter, page):
    q = {'num': num, 'chapter': chapter, 'page': page, 'blocks': [], 'seen_answer': False}
    questions.append(q)
    return q

def add_block(kind, **kw):
    global cur
    if cur is None:
        return
    kw['t'] = kind
    kw.setdefault('page', cur['page'])
    kw.setdefault('y0', 0)
    kw.setdefault('y1', 0)
    cur['blocks'].append(kw)

def flush_pending_as_blocks(prefix=None):
    """Append pending elements at the start of the current question."""
    global pending
    if not pending:
        return
    for el in pending:
        if el['kind'] == 'text':
            add_block('line', text=el['text'], x=el['x'], size=el['size'], bold=el['bold'], y0=el['y0'], y1=el['y1'], page=el.get('page', 0))
        else:
            add_block('fig', src=el['src'], w=el['w'], h=el['h'], cls=el.get('cls', 'fig'), y0=el['y0'], y1=el['y1'], page=el.get('page', 0))
    pending = []

def close_question():
    global cur
    cur = None

for pno in range(len(d)):
    page = d[pno]
    page_no = pno + 1
    if page_no < 7 or page_no > 221:
        continue
    chap = chapter_of(page_no)
    greens = green_rects(page)
    seps = red_seps(page)
    lines = page_lines(page)
    # drop chapter headings & other oversized display text
    lines = [l for l in lines if l['size'] < 20 and 'Updated 23/10/25' not in l['text']]
    for l in lines:
        l['cov'] = coverage(l['bb'], greens)
    gzones = grid_zones(page)
    czones = column_zones([l for l in lines if l['cov'] < 0.45])
    fzones = formula_zones(page)
    imgs = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] == 1:
            r = pymupdf.Rect(b['bbox'])
            if r.y0 > 80 and r.y1 < 760 and r.get_area() > 400:
                imgs.append(r)

    # ---- rasters stacked on top of each other: rebuild as a visible grid
    # (the later image's white background hides the earlier option graphs)
    grid_elems = []
    if len(imgs) > 1 and any(len(g) > 1 for g in overlap_groups(imgs)):
        infos = page.get_image_info(xrefs=True)
        rows = []
        for r in sorted(imgs, key=lambda q: q.y0):
            if rows and r.y0 - rows[-1][0].y0 < 30:
                rows[-1].append(r)
            else:
                rows.append([r])
        ordered = [r for row in rows for r in sorted(row, key=lambda q: q.x0)]
        xrefs = []
        for r in ordered:
            best = min(infos, key=lambda i: abs(pymupdf.Rect(i['bbox']).x0 - r.x0) +
                                            abs(pymupdf.Rect(i['bbox']).y0 - r.y0))
            xrefs.append(best['xref'])
        name, gw, gh = compose_image_grid(xrefs)
        bb = pymupdf.Rect(ordered[0])
        for r in ordered[1:]:
            bb |= r
        grid_elems.append({'kind': 'fig', 'y0': bb.y0, 'y1': bb.y1, 'x': bb.x0,
                           'src': name, 'w': gw, 'h': gh, 'cls': 'image', 'page': page_no})
        imgs = []

    # ---- answer detection
    answer_lines = [l for l in lines if l['cov'] >= 0.45 and l['bb'].width > 100]

    # answer y-bands = clusters of answer lines (gap < 12pt)
    bands = []
    for l in sorted(answer_lines, key=lambda x: x['bb'].y0):
        if bands and l['bb'].y0 - bands[-1][1] < 14:
            bands[-1][1] = max(bands[-1][1], l['bb'].y1)
            bands[-1][0] = min(bands[-1][0], l['bb'].y0)
        else:
            bands.append([l['bb'].y0, l['bb'].y1])

    # green answer cells inside tables also close a question
    cells = [g for g in greens if g.width <= 95]
    close_bands = [list(b) for b in bands]
    for c in cells:
        close_bands.append([c.y0, c.y1])
    close_bands.sort()
    merged_close = []
    for a, b in close_bands:
        if merged_close and a - merged_close[-1][1] < 14:
            merged_close[-1][1] = max(merged_close[-1][1], b)
        else:
            merged_close.append([a, b])
    close_bands = merged_close

    def in_band(y0, y1):
        for a, b in bands:
            if y0 >= a - 2 and y1 <= b + 2:
                return True
        return False

    # ---- crop zones (tables, formulas, diagrams)
    zones = []
    for z in gzones:
        zones.append(('table', z))
    for z in czones:
        zones.append(('table', z))
    for z in fzones:
        if in_band(z.y0, z.y1):
            continue
        zones.append(('formula', z))
    for r in imgs:
        zones.append(('image', r))

    # narrow green cells (true/false tables) -> crop their rows
    cell_rows = []
    for c in sorted(cells, key=lambda r: r.y0):
        if in_band(c.y0, c.y1):
            continue
        placed = False
        for row in cell_rows:
            if abs(c.y0 - row['y0']) < 12 or 0 <= c.y0 - row['y1'] < 26:
                row['rect'] |= c
                row['y0'] = min(row['y0'], c.y0)
                row['y1'] = max(row['y1'], c.y1)
                placed = True
                break
        if not placed:
            cell_rows.append({'rect': pymupdf.Rect(c), 'y0': c.y0, 'y1': c.y1})
    for row in cell_rows:
        z = pymupdf.Rect(row['rect'])
        # extend to text on the same rows
        for l in lines:
            if l['bb'].y1 > z.y0 - 2 and l['bb'].y0 < z.y1 + 2 and l['cov'] < 0.45:
                z |= l['bb']
        # header row above
        for l in lines:
            if l['bb'].y1 <= z.y0 and z.y0 - l['bb'].y1 < 30 and re.search(r'\b(True|False|Tru|Fals)\b', l['text']):
                z |= l['bb']
        z = pymupdf.Rect(45, z.y0 - 3, 560, z.y1 + 3)
        zones.append(('table', z))

    # merge overlapping zones
    merged = []
    for kind, z in sorted(zones, key=lambda k: k[1].y0):
        if kind == 'table':
            for m in merged:
                if m[1].intersects(z) and m[0] == 'table':
                    m[1] |= z
                    break
            else:
                merged.append([kind, pymupdf.Rect(z)])
        else:
            merged.append([kind, pymupdf.Rect(z)])
    zones = merged

    # ---- graphics: group neighbouring crops (2x2 graph grids) into ONE figure
    # a page often holds four option graphs; cropping each separately clips the
    # option letters / axis labels, so union them into one clean picture.
    gfx = [(k, pymupdf.Rect(z)) for k, z in zones if k in ('image', 'formula')]
    zones = [(k, z) for k, z in zones if k not in ('image', 'formula')]
    gfx.sort(key=lambda kz: (round(kz[1].y0), kz[1].x0))
    groups = []
    for k, z in gfx:
        groups.append({'rect': pymupdf.Rect(z)})

    def _gap(a, b):
        vgap = max(0.0, max(a.y0, b.y0) - min(a.y1, b.y1))
        hgap = max(0.0, max(a.x0, b.x0) - min(a.x1, b.x1))
        return vgap, hgap

    changed = True
    while changed:
        changed = False
        out = []
        for g in groups:
            for o in out:
                vgap, hgap = _gap(o['rect'], g['rect'])
                if vgap < 18 and hgap < 24:
                    o['rect'] |= g['rect']
                    changed = True
                    break
            else:
                out.append(g)
        groups = out

    for g in groups:
        z = pymupdf.Rect(g['rect'])
        pad = 15
        x0, x1 = z.x0 - pad, z.x1 + pad
        if z.width >= 120:
            x0, x1 = 40, 590  # full text column: keeps A/B/C/D + axis labels
        zone = pymupdf.Rect(max(36, x0), max(82, z.y0 - pad),
                            min(592, x1), min(752, z.y1 + pad))
        zones.append(('image', zone))

    # never let an enlarged graphic swallow a question header or sentence line
    guard = [l for l in lines if l['cov'] < 0.45 and (l['bold'] or len(l['text']) > 26)]
    # green answer paragraphs must never appear inside a crop
    hidden = [g for g in greens if g.height > 3]
    fixed = []
    for kind, z in zones:
        if kind in ('image', 'formula'):
            z = pymupdf.Rect(z)
            for gr in hidden:
                if not gr.intersects(z):
                    continue
                if gr.y0 + gr.height / 2 < (z.y0 + z.y1) / 2:
                    z.y0 = max(z.y0, gr.y1 + 3)
                else:
                    z.y1 = min(z.y1, gr.y0 - 3)
            for l in guard:
                bb = l['bb']
                if bb.y1 <= z.y0 or bb.y0 >= z.y1:
                    continue
                if bb.x1 <= z.x0 or bb.x0 >= z.x1:
                    continue
                if bb.y0 + bb.height / 2 < (z.y0 + z.y1) / 2:
                    z.y0 = max(z.y0, bb.y1 + 2)
                else:
                    z.y1 = min(z.y1, bb.y0 - 2)
            if z.height < 12:
                continue
        fixed.append((kind, z))
    zones = fixed

    # ---- build page elements in reading order
    elems = []
    used_lines = set()
    for kind, z in zones:
        # skip zones that are inside an answer band
        if in_band(z.y0, z.y1):
            continue
        inside = []
        for i, l in enumerate(lines):
            if i in used_lines or l['cov'] >= 0.45:
                continue
            if (l['bb'] & z).get_area() > 0.6 * l['bb'].get_area():
                inside.append(i)
        if not inside and kind != 'image':
            continue
        for i in inside:
            used_lines.add(i)
        name = crop(page, z)
        elems.append({'kind': 'fig', 'y0': z.y0, 'y1': z.y1, 'x': z.x0, 'src': name,
                      'w': z.width, 'h': z.height, 'cls': kind, 'page': page_no})

    for i, l in enumerate(lines):
        if i in used_lines or l['cov'] >= 0.45:
            continue
        elems.append({'kind': 'text', 'y0': l['bb'].y0, 'y1': l['bb'].y1, 'x': l['bb'].x0, 'text': l['text'],
                      'size': l['size'], 'bold': l['bold'], 'page': page_no})

    elems.extend(grid_elems)
    elems.sort(key=lambda e: (round(e['y0'], 1), e['x']))

    # ---- chapter boundary
    if page_no in CH_START:
        close_question()
        pending = []
        expected = 1

    # ---- walk elements, splitting questions
    band_idx = 0
    prev_fig = False
    stem_mode = bool(cur is not None and cur['seen_answer'])
    for el in elems:
        while band_idx < len(close_bands) and el['y0'] > close_bands[band_idx][1] + 1:
            if cur is not None:
                cur['seen_answer'] = True
            stem_mode = True
            band_idx += 1
        if el['kind'] == 'text':
            txt = el['text']
            kill = globals().get('_kill', False)
            if re.match(r'(?i)^(the correct answer|correct answer|answer\s*[:\-]|tutorial note|explanation\b|working\b)', txt.strip()):
                globals()['_kill'] = True
                continue
            if kill and not el['bold'] and not QPAT.match(txt):
                continue
            globals()['_kill'] = False
            m = QPAT.match(txt)
            num = int(m.group(1)) if m else -1
            is_q = bool(m) and el['bold'] and (el['x'] < 100 or prev_fig)
            if m and el['bold'] and not is_q:
                missed.append((page_no, num, expected, round(el['x'], 1), txt[:70]))
            if is_q:
                expected = num + 1
                prev_fig = False
                txt = re.sub(r'^(\d{1,3})[\.\)]\s+\1[\.\)]\s+', r'\1. ', txt)
                el['text'] = txt
                if pending and cur is not None and not cur['seen_answer'] and not looks_like_stem(pending):
                    # continuation across pages: pending belongs to the open question
                    for p in pending:
                        if p['kind'] == 'text':
                            add_block('line', text=p['text'], x=p['x'], size=p['size'], bold=p['bold'], y0=p['y0'], y1=p['y1'], page=p.get('page', page_no))
                        else:
                            add_block('fig', src=p['src'], w=p['w'], h=p['h'], cls=p.get('cls', 'fig'), y0=p['y0'], y1=p['y1'], page=p.get('page', page_no))
                    pending = []
                    close_question()
                    cur = new_question(num, chap, page_no)
                    add_block('line', text=txt, x=el['x'], size=el['size'], bold=el['bold'], first=True)
                else:
                    cur = new_question(num, chap, page_no)
                    flush_pending_as_blocks()
                    add_block('line', text=txt, x=el['x'], size=el['size'], bold=el['bold'], first=True, y0=el['y0'], y1=el['y1'], page=page_no)
                stem_mode = False
                continue
            prev_fig = False
            if cur is None or stem_mode:
                pending.append(el)
            else:
                add_block('line', text=txt, x=el['x'], size=el['size'], bold=el['bold'], y0=el['y0'], y1=el['y1'], page=page_no)
        else:
            prev_fig = True
            if cur is None or stem_mode:
                pending.append(el)
            else:
                add_block('fig', src=el['src'], w=el['w'], h=el['h'], cls=el['cls'], y0=el['y0'], y1=el['y1'], page=page_no)

    # answers that sit below the last element on this page still close the question
    if cur is not None and band_idx < len(close_bands):
        cur['seen_answer'] = True

# ---------------------------------------------------------------- fragments
# A question fragment = consecutive blocks on one page.  If a fragment shows
# column / table layout we cannot trust as plain text, it is replaced by one
# clean image of that region (the user's own rule for unclear questions).

def finalize():
    for q in questions:
        blocks = q['blocks']
        frags = []
        for b in blocks:
            if frags and b.get('first'):
                frags.append({'page': b['page'], 'y0': b['y0'], 'y1': b['y1'], 'b': [b]})
            elif frags and b['page'] == frags[-1]['page'] and b['y0'] - frags[-1]['y1'] < 30:
                frags[-1]['b'].append(b)
                frags[-1]['y1'] = max(frags[-1]['y1'], b['y1'])
            else:
                frags.append({'page': b['page'], 'y0': b['y0'], 'y1': b['y1'], 'b': [b]})
        out = []
        for f in frags:
            text_blocks = [b for b in f['b'] if b['t'] == 'line']
            stray = [b for b in text_blocks
                     if b['x'] > 101 and not b.get('first')
                     and not re.match(r'^[A-D][\.\)]\s', b['text'].strip())
                     and not re.match(r'^\(?\d{1,2}[\.\)]\s', b['text'].strip())]
            if len(stray) >= 2:
                z = pymupdf.Rect(45, f['y0'] - 2, 560, f['y1'] + 2)
                name = crop(d[f['page'] - 1], z)
                out.append({'t': 'fig', 'src': name, 'w': z.width, 'h': z.height,
                            'cls': 'block', 'page': f['page'], 'y0': f['y0'], 'y1': f['y1']})
                continue
            for b in f['b']:
                if b['t'] == 'line' and (b in stray or
                        (len(b['text']) <= 8 and re.fullmatch(r'[A-Za-z]+', b['text'].strip()))):
                    continue
                out.append(b)
        q['blocks'] = out

finalize()
json.dump(questions, open('raw_questions.json', 'w'), indent=1)
print('questions:', len(questions))
print('images:', len(os.listdir(IMGDIR)))
from collections import Counter
print(Counter(q['chapter'] for q in questions))
print('MISSED MARKERS', len(missed))
for x in missed[:60]:
    print('  missed', x)
