#!/usr/bin/env python3
"""Build the single-file study site from raw_questions.json + assets/."""
import json, re, os, base64, html
from collections import defaultdict

RAW = json.load(open('raw_questions.json'))

CHAPTERS = [
    'Management Information', 'Materials', 'Managing Inventory', 'Labour', 'Overheads',
    'Absorption and Marginal Costing', 'Process Costing, Joint Products and Further Processing',
    'Cost Classification', 'Job, Batch and Service Costing', 'Alternative Cost Accounting Methods',
    'Sampling Techniques and Expected Values', 'Forecasting Costs and Revenues',
    'Time Series Analysis', 'Index Numbers', 'Spreadsheets', 'Compounding and Discounting',
    'Investment Appraisal', 'Nature and Purpose of Budgeting',
    'Fixed and Flexible Budgets, Budgetary Control, and Reporting',
    'Behavioural Aspects of Budgeting', 'Presenting Information', 'Summarising and Analysing Data',
    'Standard Costing and Variance Analysis', 'Introduction to Performance Management',
    'Analysing Performance', 'Monitoring Performance, Cost Reductions, and Value Enhancement',
]

OPT = re.compile(r'^([A-D])[\.\)]\s*(.*)$')
ITEM = re.compile(r'^\(?(\d{1,2})[\.\)]\s*(.*)$')

def esc(t):
    return html.escape(t, quote=False)

def join_lines(lines):
    """Merge hard-wrapped PDF lines into paragraphs."""
    paras, cur = [], []
    for ln in lines:
        t = ln.strip()
        if not t:
            continue
        if cur:
            prev = cur[-1]
            if re.search(r'[\.\:\?\!]$', prev) and re.match(r'[A-Z0-9“"(]', t):
                paras.append(cur)
                cur = [t]
            else:
                cur.append(t)
        else:
            cur = [t]
    if cur:
        paras.append(cur)
    out = []
    for p in paras:
        s = ' '.join(p)
        s = re.sub(r'\s+', ' ', s).strip()
        s = re.sub(r'\s+([,.;:])', r'\1', s)
        out.append(s)
    return out

def build_blocks(q):
    blocks = q['blocks']
    title = None
    chunks = []          # ('p', text) ('opt', label, text) ('item', num, text) ('fig', src)
    cur = None
    just_title = False

    def flush():
        nonlocal cur
        if not cur:
            return
        if cur['type'] == 'p':
            for s in join_lines(cur['lines']):
                chunks.append(('p', s))
        else:
            text = ' '.join(cur['lines'])
            text = re.sub(r'\s+', ' ', text).strip()
            chunks.append((cur['type'], cur['label'], text))
        cur = None

    for b in blocks:
        if b['t'] == 'fig':
            flush()
            chunks.append(('fig', b['src'], b.get('cls', 'fig'), b.get('w', 0)))
            continue
        txt = b['text'].strip()
        x = b['x']
        if b.get('first') and title is None:
            flush()
            m = re.match(r'^(\d{1,3})[\.\)]\s*(.*)$', txt)
            title = m.group(2) if m else txt
            just_title = True
            continue
        # continuation of a two-line bold question heading
        if just_title and b.get('bold') and x < 100 and not OPT.match(txt):
            title = (title + ' ' + txt).strip()
            just_title = False
            continue
        just_title = False
        m = OPT.match(txt)
        if m and x < 105:
            flush()
            cur = {'type': 'opt', 'label': m.group(1), 'x': x, 'lines': [m.group(2)]}
            continue
        m = ITEM.match(txt)
        if m and 70 < x < 105:
            flush()
            cur = {'type': 'item', 'label': m.group(1), 'x': x, 'lines': [m.group(2)]}
            continue
        if cur and cur['type'] in ('opt', 'item') and x > cur['x'] + 6:
            cur['lines'].append(txt)
        elif cur and cur['type'] == 'p':
            cur['lines'].append(txt)
        else:
            flush()
            cur = {'type': 'p', 'label': None, 'x': x, 'lines': [txt]}
    flush()
    return title, chunks

def inner(chunks):
    parts = []
    items = 0
    for c in chunks:
        if c[0] == 'p':
            parts.append(f'<p>{esc(c[1])}</p>')
        elif c[0] == 'opt':
            parts.append(
                f'<div class="opt"><span class="opt-k">{esc(c[1])}</span>'
                f'<span class="opt-v">{esc(c[2])}</span></div>')
        elif c[0] == 'item':
            parts.append(
                f'<div class="numitem"><span class="numitem-k">{esc(c[1])}</span>'
                f'<span>{esc(c[2])}</span></div>')
        elif c[0] == 'fig':
            cls = c[2]
            w = c[3] if len(c) > 3 else 0
            maxw = max(240, min(640, round(w * 2.0))) if w else 620
            parts.append(
                f'<figure class="fig fig-{esc(cls)}" style="max-width:{maxw}px">'
                f'<img data-src="{esc(c[1])}" alt="Question table or diagram"></figure>')
    return '\n'.join(parts)

# ------------------------------------------------------------------ assemble
by_chapter = defaultdict(list)
for q in RAW:
    by_chapter[q['chapter']].append(q)

ANSWERS = {}
if os.path.exists('answers.json'):
    ANSWERS = {int(k): {x['num']: x['a'] for x in v if x['a']}
               for k, v in json.load(open('answers.json')).items()}

chapters = []
for ci, name in enumerate(CHAPTERS):
    qs = sorted(by_chapter.get(ci, []), key=lambda q: q['page'])
    items = []
    for q in qs:
        title, chunks = build_blocks(q)
        if not title:
            first_p = next((c[1] for c in chunks if c[0] == 'p'), '')
            title = (first_p[:150] + '…') if len(first_p) > 150 else first_p
            if first_p:
                chunks = list(chunks)
                try:
                    chunks.remove(('p', first_p))
                except ValueError:
                    pass
        items.append({
            'num': q['num'],
            'page': q['page'],
            'title': title or '',
            'body': inner(chunks),
            'empty': not chunks,
            'hasfig': any(c[0] == 'fig' for c in chunks),
            'ans': ANSWERS.get(ci, {}).get(q['num'], ''),
        })
    chapters.append({'n': ci + 1, 'title': name, 'items': items})

total = sum(len(c['items']) for c in chapters)
empty = sum(1 for c in chapters for it in c['items'] if it['empty'])
noimg = [it for c in chapters for it in c['items'] if not it['hasfig'] and not it['body']]
print('chapters', len(chapters), 'questions', total, 'empty', empty)

# image map (only the crops the page actually references)
used_srcs = set()
for ch in chapters:
    for it in ch['items']:
        for m in re.finditer(r'data-src="([^"]+)"', it['body']):
            used_srcs.add(m.group(1))

data_uris = {}
for f in os.listdir('assets'):
    if f.endswith('.png') and f in used_srcs:
        with open(os.path.join('assets', f), 'rb') as fh:
            data_uris[f] = 'data:image/png;base64,' + base64.b64encode(fh.read()).decode()

# ------------------------------------------------------------------ template
CSS = r'''
:root{
  --red:#e01b2e; --red-2:#ff3347; --ink:#0a0a0b; --ink-2:#151517;
  --paper:#ffffff; --muted:#6b6b72; --line:#e8e8ec;
  --max:820px; --ease:cubic-bezier(.22,.61,.36,1);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;color:var(--ink);
  background:
    radial-gradient(900px 520px at 6% -10%,rgba(224,27,46,.16),transparent 62%),
    radial-gradient(760px 540px at 102% 2%,rgba(255,120,160,.18),transparent 60%),
    radial-gradient(760px 640px at 44% 108%,rgba(96,124,255,.12),transparent 62%),
    linear-gradient(180deg,#f8f9fc,#eceef4 58%,#f5f6f9);
  background-attachment:fixed;
  font-family:'Roboto',system-ui,-apple-system,'Segoe UI',sans-serif;
  -webkit-font-smoothing:antialiased;font-size:16px;line-height:1.62}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block}

/* ---------- home ---------- */
.home{position:relative;min-height:100vh;background:var(--ink);color:#f4f4f5;overflow:hidden}
.aura{position:absolute;inset:-20%;pointer-events:none;filter:blur(10px)}
.aura span{position:absolute;display:block;border-radius:50%;filter:blur(90px);opacity:.55;
  animation:drift 26s var(--ease) infinite alternate}
.aura span:nth-child(1){width:52vw;height:52vw;background:#7a0a17;top:-12%;left:-8%}
.aura span:nth-child(2){width:38vw;height:38vw;background:#30040a;top:30%;right:-10%;animation-delay:-8s}
.aura span:nth-child(3){width:30vw;height:30vw;background:#b3102a;bottom:-18%;left:28%;opacity:.32;animation-delay:-15s}
@keyframes drift{from{transform:translate3d(0,0,0) scale(1)}
  to{transform:translate3d(4%,6%,0) scale(1.12)}}
.grain{position:absolute;inset:0;pointer-events:none;opacity:.16;
  background-image:radial-gradient(rgba(255,255,255,.14) 1px,transparent 1px);
  background-size:3px 3px;mix-blend-mode:overlay}

.wrap{position:relative;z-index:2;max-width:1080px;margin:0 auto;padding:0 24px}

.hero{padding:96px 0 40px;display:flex;flex-direction:column;gap:26px}
.kicker{display:inline-flex;align-items:center;gap:10px;font-size:12px;letter-spacing:.24em;
  text-transform:uppercase;color:#f0a7ad;font-weight:500}
.kicker::before{content:"";width:28px;height:1px;background:var(--red)}
.hero h1{margin:0;font-weight:700;letter-spacing:-.03em;line-height:.98;
  font-size:clamp(46px,8.4vw,104px)}
.hero h1 .out{color:transparent;-webkit-text-stroke:1.5px rgba(255,255,255,.45)}
.hero h1 em{font-style:normal;color:var(--red-2)}
.hero .sub{max-width:560px;color:#b9b9c0;font-size:17px;line-height:1.65;margin:0}
.credit{display:flex;align-items:center;gap:14px;margin-top:4px;flex-wrap:wrap}
.credit .label{font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:#8b8b93}
.credit .name{font-size:clamp(22px,3.4vw,34px);font-weight:700;letter-spacing:.06em;
  color:#fff}
.credit .name b{color:var(--red-2);font-weight:700}
.cta{display:flex;gap:12px;flex-wrap:wrap;margin-top:6px}
.btn{display:inline-flex;align-items:center;gap:10px;padding:14px 22px;border-radius:999px;
  font-size:14px;font-weight:500;letter-spacing:.01em;border:1px solid transparent;
  transition:transform .35s var(--ease),background .35s var(--ease),border-color .35s var(--ease),
    box-shadow .35s var(--ease),color .35s var(--ease)}
.btn svg{width:16px;height:16px;flex:none}
.btn-primary{background:var(--red);color:#fff;box-shadow:0 12px 40px -14px rgba(224,27,46,.9)}
.btn-primary:hover{background:var(--red-2);transform:translateY(-2px)}
.btn-ghost{border-color:rgba(255,255,255,.18);color:#ececf0;background:rgba(255,255,255,.02)}
.btn-ghost:hover{border-color:rgba(255,255,255,.4);transform:translateY(-2px)}

.chapters{padding:36px 0 90px}
.chapters-head{display:flex;align-items:baseline;justify-content:space-between;gap:20px;
  border-top:1px solid rgba(255,255,255,.12);padding-top:28px;margin-bottom:22px}
.chapters-head h2{margin:0;font-size:13px;letter-spacing:.22em;text-transform:uppercase;
  color:#9a9aa2;font-weight:500}
.chapters-head .count{font-size:13px;color:#6f6f78}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
.card{position:relative;display:flex;flex-direction:column;gap:12px;padding:20px;
  min-height:150px;
  border:1px solid rgba(255,255,255,.1);border-radius:16px;background:
    linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.012));
  transition:transform .4s var(--ease),border-color .4s var(--ease),background .4s var(--ease)}
.card::after{content:"";position:absolute;inset:0;border-radius:16px;pointer-events:none;
  background:radial-gradient(120px 80px at 100% 0,rgba(224,27,46,.35),transparent 70%);
  opacity:0;transition:opacity .4s var(--ease)}
.card:hover{transform:translateY(-4px);border-color:rgba(224,27,46,.55)}
.card:hover::after{opacity:1}
.card .top{display:flex;align-items:center;justify-content:space-between}
.card .no{font-size:12px;font-weight:700;letter-spacing:.16em;color:var(--red-2)}
.card .qn{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#77777f}
.card h3{margin:0;font-size:16px;font-weight:500;line-height:1.4;letter-spacing:-.01em;
  color:#f0f0f2}
.card .arrow{margin-top:auto;display:flex;align-items:center;gap:8px;font-size:11px;
  letter-spacing:.12em;text-transform:uppercase;color:#8a8a92;
  transition:color .35s var(--ease),gap .35s var(--ease)}
.card .arrow svg{width:13px;height:13px;flex:none}
.card:hover .arrow{color:#fff;gap:12px}

footer.site{padding:30px 0 42px;border-top:1px solid rgba(255,255,255,.1);
  display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;
  font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#71717a}
footer.site b{color:#e6e6ea;letter-spacing:.2em}

/* ---------- chapter pages ---------- */
.page{display:none;background:transparent}
.page.active{display:block}
.bar{position:sticky;top:0;z-index:20;
  background:rgba(255,255,255,.55);backdrop-filter:blur(26px) saturate(180%);
  -webkit-backdrop-filter:blur(26px) saturate(180%);
  border-bottom:1px solid rgba(255,255,255,.75);
  box-shadow:0 14px 32px -28px rgba(16,18,30,.6)}
.bar-in{max-width:var(--max);margin:0 auto;padding:14px 24px;display:flex;align-items:center;
  justify-content:space-between;gap:16px}
.back{display:inline-flex;align-items:center;gap:8px;font-size:12px;letter-spacing:.14em;
  text-transform:uppercase;color:#4b4b52;transition:color .3s var(--ease),gap .3s var(--ease)}
.back:hover{color:var(--red);gap:11px}
.back svg{width:14px;height:14px}
.bar .meta{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#9a9aa1}

.chapter{max-width:var(--max);margin:0 auto;padding:36px 24px 90px}
.chapter header{position:relative;overflow:hidden;border:1px solid rgba(255,255,255,.8);
  border-radius:26px;padding:26px 28px;margin-bottom:16px;
  background:linear-gradient(180deg,rgba(255,255,255,.72),rgba(255,255,255,.44));
  backdrop-filter:blur(26px) saturate(180%);
  -webkit-backdrop-filter:blur(26px) saturate(180%);
  box-shadow:0 1px 0 rgba(255,255,255,.9) inset,0 24px 50px -36px rgba(16,18,30,.65)}
.chapter .no{font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--red);
  text-transform:uppercase}
.chapter h1{margin:12px 0 0;font-size:clamp(28px,4.6vw,42px);line-height:1.12;
  letter-spacing:-.025em;font-weight:700}
.chapter .lede{margin:14px 0 0;color:var(--muted);font-size:14px}

.q{padding:24px 26px;margin-bottom:12px;border:1px solid rgba(255,255,255,.78);
  border-radius:22px;
  background:linear-gradient(180deg,rgba(255,255,255,.56),rgba(255,255,255,.36));
  backdrop-filter:blur(26px) saturate(180%);
  -webkit-backdrop-filter:blur(26px) saturate(180%);
  box-shadow:0 1px 0 rgba(255,255,255,.9) inset,0 18px 40px -32px rgba(16,18,30,.6);
  transition:background .4s var(--ease),box-shadow .4s var(--ease),transform .4s var(--ease)}
.q:hover{background:linear-gradient(180deg,rgba(255,255,255,.75),rgba(255,255,255,.5));
  transform:translateY(-2px);
  box-shadow:0 1px 0 rgba(255,255,255,.95) inset,0 26px 50px -32px rgba(16,18,30,.55)}
.q:last-child,.q:last-of-type{margin-bottom:0}
.q-head{display:flex;gap:16px;align-items:baseline}
.q-no{flex:none;font-size:13px;font-weight:700;letter-spacing:.08em;color:var(--red);
  padding-top:3px;min-width:32px}
.q-title{margin:0;font-size:17.5px;line-height:1.5;font-weight:500;letter-spacing:-.005em}
.q-body{margin-top:14px;padding-left:48px}
.q-body p{margin:0 0 12px;color:#25252a}
.q-body p:last-child{margin-bottom:0}
.opt{display:flex;gap:12px;padding:9px 0;border-top:1px dashed #eee}
.opt:first-of-type{border-top:0}
.opt-k{flex:none;width:22px;height:22px;border-radius:50%;border:1px solid #d9d9df;
  display:grid;place-items:center;font-size:11px;font-weight:700;color:#3a3a41;
  margin-top:2px;background:#fafafb}
.opt-v{color:#25252a}
.numitem{display:flex;gap:10px;padding:4px 0}
.numitem-k{flex:none;min-width:18px;font-weight:500;color:#6a6a72;font-variant-numeric:tabular-nums}
figure.fig{margin:18px auto 10px;border:1px solid rgba(255,255,255,.9);border-radius:16px;
  overflow:hidden;display:flex;justify-content:center;
  background:rgba(255,255,255,.85);padding:10px;
  box-shadow:0 1px 0 rgba(255,255,255,.9) inset,0 16px 32px -26px rgba(16,18,30,.75)}
figure.fig img{width:100%;height:auto;border-radius:9px}
figure.fig-table,figure.fig-block{border-color:rgba(255,255,255,.95)}
.q-meta{color:#a3a3aa;font-size:11px;letter-spacing:.12em;text-transform:uppercase;
  padding-left:48px;margin-top:16px}
.q.bare .q-head{display:none}
.q.bare .q-body{padding-left:0}
.q.bare .q-meta{padding-left:0}

/* ---------- fancy layers ---------- */
.home::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:1;
  background:radial-gradient(620px circle at var(--mx,50%) var(--my,0%),rgba(224,27,46,.16),transparent 65%)}

.topbar{position:relative;z-index:3;padding:22px 0 0}
.topbar-in{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.brand{display:inline-flex;align-items:center;gap:10px;font-size:12px;font-weight:700;
  letter-spacing:.26em;text-transform:uppercase;color:#f2f2f4;white-space:nowrap}
.brand .dot{width:8px;height:8px;border-radius:50%;background:var(--red-2);
  box-shadow:0 0 0 4px rgba(224,27,46,.18),0 0 18px 2px rgba(255,51,71,.55);
  animation:pulse 2.6s var(--ease) infinite}
@keyframes pulse{0%,100%{transform:scale(1);opacity:.9}50%{transform:scale(1.28);opacity:1}}
.brand-sub{color:#6f6f78;font-weight:400;letter-spacing:.2em}
.brand-txt{font-size:10px;letter-spacing:.28em;color:#9a9aa2;font-weight:500}
.brand-name{font-size:clamp(15px,1.8vw,19px);letter-spacing:.32em;font-weight:700;
  background:linear-gradient(100deg,#fff,#ff9aa5 38%,#e01b2e 58%,#fff 82%);
  background-size:250% 100%;-webkit-background-clip:text;background-clip:text;
  color:transparent;-webkit-text-fill-color:transparent;
  animation:sheen 9s linear infinite;
  filter:drop-shadow(0 6px 18px rgba(224,27,46,.45))}
.pill{display:inline-flex;align-items:center;gap:8px;padding:8px 14px;border-radius:999px;
  border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.03);
  font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;color:#9a9aa2;
  white-space:nowrap;
  transition:border-color .35s var(--ease),color .35s var(--ease)}
.pill b{color:#fff;letter-spacing:.2em}
.pill:hover{border-color:rgba(224,27,46,.5);color:#dcdce0}

.hero{padding:58px 0 40px}
.credit .name{display:inline-flex;gap:.02em;letter-spacing:.02em}
.credit .name b{display:inline-block;color:#fff;font-weight:700;
  animation:float 5s var(--ease) infinite}
.credit .name b:nth-child(1){color:var(--red-2)}
.credit .name b:nth-child(2){animation-delay:.14s}
.credit .name b:nth-child(3){animation-delay:.28s}
.credit .name b:nth-child(4){color:var(--red-2);animation-delay:.42s}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}

.stats{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
.stat{flex:1 1 120px;min-width:118px;padding:14px 16px;border-radius:14px;
  border:1px solid rgba(255,255,255,.1);
  background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,.012))}
.stat b{display:block;font-size:26px;font-weight:700;letter-spacing:-.02em;color:#fff;line-height:1.15}
.stat span{display:block;margin-top:6px;font-size:10.5px;letter-spacing:.18em;
  text-transform:uppercase;color:#85858d}

.marquee{position:relative;z-index:2;margin:34px -24px 0;overflow:hidden;
  border-top:1px solid rgba(255,255,255,.1);border-bottom:1px solid rgba(255,255,255,.1);
  background:rgba(255,255,255,.02);
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent);
  mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)}
.marquee-track{display:flex;width:max-content;animation:slide 52s linear infinite}
.marquee:hover .marquee-track{animation-play-state:paused}
.marquee span{display:inline-flex;align-items:center;gap:12px;padding:12px 20px;
  font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#8d8d95;white-space:nowrap}
.marquee span::after{content:"";width:4px;height:4px;border-radius:50%;background:rgba(224,27,46,.85)}
@keyframes slide{from{transform:translate3d(0,0,0)}to{transform:translate3d(-50%,0,0)}}

.card{overflow:hidden;animation:cardIn .7s var(--ease) backwards;
  animation-delay:calc(var(--i,0) * 28ms)}
@keyframes cardIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
.card .wm{position:absolute;right:8px;bottom:2px;font-size:82px;font-weight:700;line-height:1;
  letter-spacing:-.07em;color:rgba(255,255,255,.045);pointer-events:none}
.card .shade{position:absolute;inset:0;border-radius:16px;pointer-events:none;
  background:linear-gradient(115deg,transparent 32%,rgba(255,255,255,.09) 48%,transparent 64%);
  transform:translateX(-120%);transition:transform .95s var(--ease)}
.card:hover .shade{transform:translateX(120%)}

footer.site{display:block;padding:44px 0 56px;text-align:center;border-top:0}
.credits-big{display:flex;flex-direction:column;align-items:center;gap:10px;padding:36px 20px;
  border:1px solid rgba(255,255,255,.1);border-radius:22px;
  background:radial-gradient(120% 160% at 50% 0,rgba(224,27,46,.17),transparent 62%),
    linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01))}
.credits-big .cb-label{font-size:10.5px;letter-spacing:.32em;text-transform:uppercase;color:#8a8a92}
.credits-big .cb-name{font-size:clamp(40px,9vw,78px);font-weight:700;letter-spacing:.16em;
  line-height:1;background:linear-gradient(180deg,#fff 32%,#e01b2e);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 14px 44px rgba(224,27,46,.4))}
.credits-big .cb-note{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#6f6f78}
.foot-row{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;
  margin-top:22px;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#6a6a72}

.progress{position:fixed;top:0;left:0;height:2px;width:0;z-index:60;
  background:linear-gradient(90deg,var(--red),var(--red-2));
  box-shadow:0 0 14px rgba(224,27,46,.55)}
.totop{position:fixed;right:22px;bottom:24px;z-index:50;width:46px;height:46px;border-radius:50%;
  border:1px solid rgba(255,255,255,.85);background:rgba(255,255,255,.6);
  backdrop-filter:blur(22px) saturate(180%);
  -webkit-backdrop-filter:blur(22px) saturate(180%);
  color:#3a3a41;display:grid;place-items:center;
  cursor:pointer;box-shadow:0 1px 0 rgba(255,255,255,.9) inset,0 14px 32px -18px rgba(16,18,30,.5);
  opacity:0;pointer-events:none;transform:translateY(10px);
  transition:opacity .35s var(--ease),transform .35s var(--ease),border-color .35s,color .35s}
.totop.on{opacity:1;pointer-events:auto;transform:none}
.totop:hover{border-color:var(--red);color:var(--red)}
.totop svg{width:16px;height:16px}

.q{position:relative}
.q::before{content:"";position:absolute;left:0;top:26px;bottom:26px;width:3px;
  border-radius:2px;background:var(--red);opacity:0;transform:scaleY(.35);
  transform-origin:top;transition:opacity .4s var(--ease),transform .4s var(--ease)}
.q:hover::before{opacity:.9;transform:none}

/* ---------- answer key (end of each chapter) ---------- */
.key{margin:46px 0 6px;border-radius:18px;overflow:hidden;position:relative;
  border:1px solid rgba(224,27,46,.26);
  background:radial-gradient(120% 190% at 10% 0,rgba(224,27,46,.22),transparent 58%),
    linear-gradient(180deg,#141417,#0a0a0c);
  box-shadow:0 26px 60px -38px rgba(224,27,46,.6)}
.key::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:18px;
  background:linear-gradient(115deg,transparent 36%,rgba(255,255,255,.05) 50%,transparent 64%);
  transform:translateX(-110%);transition:transform 1s var(--ease)}
.key:hover::after{transform:translateX(110%)}
.key-sum{display:flex;align-items:center;gap:14px;padding:18px 20px;cursor:pointer;
  list-style:none;color:#f4f4f6;user-select:none;position:relative;z-index:1}
.key-sum::-webkit-details-marker{display:none}
.key-sum:focus-visible{outline:2px solid var(--red-2);outline-offset:-2px}
.key-ic{flex:none;width:36px;height:36px;border-radius:11px;display:grid;place-items:center;
  border:1px solid rgba(255,51,71,.42);background:rgba(224,27,46,.15);color:var(--red-2)}
.key-ic svg{width:17px;height:17px}
.key-txt{display:flex;flex-direction:column;gap:3px;min-width:0}
.key-txt b{font-size:12px;letter-spacing:.22em;text-transform:uppercase}
.key-txt i{font-style:normal;font-size:11px;letter-spacing:.1em;color:#8c8c94}
.key-chev{margin-left:auto;flex:none;color:#9a9aa2;
  transition:transform .38s var(--ease),color .38s var(--ease)}
.key-chev svg{width:16px;height:16px;display:block}
.key[open] .key-chev{transform:rotate(180deg);color:var(--red-2)}
.key[open] .key-txt b{color:#fff}
.key-body{padding:2px 20px 20px;position:relative;z-index:1;
  animation:keyIn .45s var(--ease)}
@keyframes keyIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.key-grid{display:flex;flex-wrap:wrap;gap:8px}
.kchip{display:flex;align-items:baseline;gap:8px;min-width:74px;white-space:nowrap;
  padding:9px 11px;border-radius:11px;
  border:1px solid rgba(255,255,255,.09);background:rgba(255,255,255,.035);
  transition:border-color .3s var(--ease),background .3s var(--ease),transform .3s var(--ease)}
.kchip:hover{border-color:rgba(255,51,71,.55);background:rgba(224,27,46,.14);
  transform:translateY(-2px)}
.kchip b{font-size:10.5px;font-weight:500;color:#87878f;font-variant-numeric:tabular-nums;
  min-width:1.2em}
.kchip i{font-style:normal;font-size:13.5px;font-weight:700;color:#fff;letter-spacing:.02em}
.kchip.kdash i{color:#6f6f78;font-weight:400}
.key-note{margin:14px 0 0;font-size:11px;line-height:1.65;color:#7c7c84}

/* ---------- home flourish ---------- */
.home::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:1;
  background-image:radial-gradient(rgba(255,255,255,.12) 1px,transparent 1px);
  background-size:34px 34px;
  -webkit-mask-image:radial-gradient(130% 85% at 50% 0,#000 6%,transparent 68%);
  mask-image:radial-gradient(130% 85% at 50% 0,#000 6%,transparent 68%)}
.hero h1 em{background:linear-gradient(100deg,#ff3347,#ff8e9a,#e01b2e,#ff3347);
  background-size:300% 100%;-webkit-background-clip:text;background-clip:text;
  color:transparent;-webkit-text-fill-color:transparent;
  animation:sheen 9s linear infinite}
@keyframes sheen{from{background-position:0% 50%}to{background-position:300% 50%}}
.kicker{transition:color .4s var(--ease)}
.hero:hover .kicker{color:#e6e6ea}

/* ---------- iOS glass pass ---------- */
.home .card{backdrop-filter:blur(26px) saturate(160%);
  -webkit-backdrop-filter:blur(26px) saturate(160%);
  background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(255,255,255,.02));
  border-color:rgba(255,255,255,.17);
  box-shadow:0 1px 0 rgba(255,255,255,.2) inset,0 24px 52px -34px rgba(0,0,0,.95)}
.home .card:hover{background:linear-gradient(180deg,rgba(255,255,255,.13),rgba(255,255,255,.04))}
.stat,.pill,.btn-ghost,.credits-big{backdrop-filter:blur(24px) saturate(160%);
  -webkit-backdrop-filter:blur(24px) saturate(160%);
  border-color:rgba(255,255,255,.2);
  box-shadow:0 1px 0 rgba(255,255,255,.22) inset,0 20px 44px -32px rgba(0,0,0,.9)}
.key{backdrop-filter:blur(26px) saturate(160%);
  -webkit-backdrop-filter:blur(26px) saturate(160%)}
.opt{transition:background .3s var(--ease),border-radius .3s var(--ease)}
.q-body .opt:hover{background:rgba(255,255,255,.6)}

/* motion */
.fade{opacity:0;transform:translateY(14px);transition:opacity .7s var(--ease),
  transform .7s var(--ease)}
.fade.in{opacity:1;transform:none}
body.paging .view{animation:viewIn .45s var(--ease)}
@keyframes viewIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important}
  .fade{opacity:1;transform:none}
}
@media (max-width:640px){
  .hero{padding:52px 0 28px}
  .topbar{padding:16px 0 0}
  .brand{font-size:11px;letter-spacing:.2em}
  .brand-sub,.brand-txt{display:none}
  .brand-name{font-size:15px;letter-spacing:.28em}
  .pill{font-size:9.5px;letter-spacing:.14em;padding:7px 11px}
  .q-body{padding-left:0}
  .q-meta{padding-left:0}
  .opt{padding:8px 0}
  .chapter{padding:22px 16px 70px}
  .chapter header{padding:20px;border-radius:20px}
  .q{padding:20px 16px;border-radius:18px}
  figure.fig{max-width:100%!important;padding:7px;border-radius:14px}
}
'''

JS = r'''
const data = JSON.parse(document.getElementById('site-data').textContent);
const imgs = data.imgs;
const chapters = data.chapters;

function img(src){ return imgs[src] || ''; }

function fillImages(root){
  root.querySelectorAll('img[data-src]').forEach(el=>{
    const k = el.getAttribute('data-src');
    if (imgs[k]) el.src = imgs[k];
  });
}

function answerKey(ch){
  const rows = ch.items.map(q=>{
    const a = q.ans || '';
    return `<span class="kchip${a?'':' kdash'}" title="Question ${q.num}"><b>${q.num}</b><i>${a || '–'}</i></span>`;
  }).join('');
  return `
    <details class="key">
      <summary class="key-sum">
        <span class="key-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></span>
        <span class="key-txt"><b>Answer key</b><i>${ch.items.length} question${ch.items.length===1?'':'s'} · options only</i></span>
        <span class="key-chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="2"><path d="M6 9l6 6 6-6"/></svg></span>
      </summary>
      <div class="key-body">
        <div class="key-grid">${rows}</div>
        <p class="key-note">Chapter ${String(ch.n).padStart(2,'0')} · answers only, no explanations.
          A dash means that question's answer is highlighted inside its own table.</p>
      </div>
    </details>`;
}

function buildChapter(ch){
  const sec = document.createElement('section');
  sec.className = 'page view';
  sec.id = 'ch' + ch.n;
  sec.innerHTML = `
    <div class="bar"><div class="bar-in">
      <a class="back" href="#home"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>All chapters</a>
      <span class="meta">Chapter ${ch.n} of ${chapters.length}</span>
    </div></div>
    <div class="chapter">
      <header>
        <div class="no">Chapter ${String(ch.n).padStart(2,'0')}</div>
        <h1>${ch.title}</h1>
        <p class="lede">${ch.items.length} question${ch.items.length===1?'':'s'}</p>
      </header>
                  ${ch.items.map((q,i)=>`
        <article class="q fade${q.title?'':' bare'}">
          <div class="q-head"><span class="q-no">${q.num}</span>
            ${q.title?`<h2 class="q-title">${q.title}</h2>`:''}</div>
          <div class="q-body">${q.body}</div>
          <div class="q-meta">PDF page ${q.page}</div>
        </article>`).join('')}
      ${answerKey(ch)}
    </div>`;
  return sec;
}

const root = document.getElementById('views');
const home = document.getElementById('home');
chapters.forEach(ch=>root.appendChild(buildChapter(ch)));
root.querySelectorAll('img[data-src]').forEach(el=>{
  el.src = imgs[el.getAttribute('data-src')] || '';
});

const io = new IntersectionObserver(es=>{
  es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} });
},{rootMargin:'0px 0px -8% 0px'});
function observeAll(){ document.querySelectorAll('.q.fade').forEach(el=>io.observe(el)); }
observeAll();

function show(){
  const h = location.hash.replace('#','');
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  if (h && h!=='home' && document.getElementById(h)) {
    home.style.display='none';
    const page = document.getElementById(h);
    page.classList.add('active');
    document.body.classList.remove('paging');
    void document.body.offsetWidth;
    document.body.classList.add('paging');
    window.scrollTo(0,0);
    page.querySelectorAll('.fade').forEach(el=>el.classList.add('in'));
  } else {
    home.style.display='block';
    window.scrollTo(0,0);
  }
}
window.addEventListener('hashchange', show);
show();

/* cursor glow on the home screen */
const homeEl = document.getElementById('home');
window.addEventListener('pointermove', e=>{
  if (homeEl.style.display === 'none' || !homeEl.offsetParent) return;
  homeEl.style.setProperty('--mx', e.clientX + 'px');
  homeEl.style.setProperty('--my', e.clientY + 'px');
}, {passive:true});

/* reading progress + back to top */
const bar = document.querySelector('.progress');
const toTop = document.querySelector('.totop');
function onScroll(){
  const el = document.documentElement;
  const max = el.scrollHeight - el.clientHeight;
  const onHome = home.style.display !== 'none';
  if (bar) bar.style.width = onHome ? '0%' : (max > 0 ? (el.scrollTop / max * 100) + '%' : '0%');
  if (toTop) toTop.classList.toggle('on', !onHome && el.scrollTop > 420);
}
window.addEventListener('scroll', onScroll, {passive:true});
if (toTop) toTop.addEventListener('click', ()=>window.scrollTo({top:0, behavior:'smooth'}));
const _show = show;
show = function(){ _show(); onScroll(); };
show();
'''

def page_html(ch):
    return ''

# build chapter markup server-side? No - generated in JS from JSON for size.
site_data = {
    'chapters': [{'n': c['n'], 'title': c['title'], 'items': c['items']} for c in chapters],
    'imgs': data_uris,
}

cards = '\n'.join(
    f'''<a class="card" href="#ch{c['n']}" style="--i:{i}">
      <span class="shade"></span>
      <span class="wm">{c['n']:02d}</span>
      <div class="top"><span class="no">{c['n']:02d}</span>
        <span class="qn">{len(c['items'])} Q</span></div>
      <h3>{esc(c['title'])}</h3>
      <div class="arrow">Open chapter <svg viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg></div>
    </a>''' for i, c in enumerate(chapters))

ticker_items = ''.join(
    f'<span>{c["n"]:02d} · {esc(c["title"].split(",")[0][:34])}</span>' for c in chapters)
ticker = ticker_items * 2

html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ACCA MA — Complete Studyhub Questions by MEOW</title>
<meta name="description" content="All ACCA MA Studyhub questions, chapter by chapter, with a collapsible answer key at the end of every chapter.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<div id="home" class="home">
  <div class="aura"><span></span><span></span><span></span></div>
  <div class="grain"></div>
  <div class="wrap">
    <div class="topbar">
      <div class="topbar-in">
        <a class="brand" href="#home" aria-label="All credits to MEOW">
          <span class="dot"></span>
          <span class="brand-txt">All credits to</span>
          <span class="brand-name">MEOW</span></a>
        <span class="pill"><b>{len(chapters)}</b>&nbsp;chapters&nbsp;·&nbsp;<b>{total}</b>&nbsp;questions</span>
      </div>
    </div>
    <div class="hero">
      <div class="kicker">ACCA Management Accounting · Studyhub</div>
      <h1>Complete<br><em>Questions</em><br><span class="out">Chapter Wise</span></h1>
      <p class="sub">Every question from the book, chapter by chapter. Answers and explanations
        stay hidden while you attempt each one honestly — every chapter ends with a collapsible
        answer key. Tables and diagrams are kept exactly as printed.</p>
      <div class="credit">
        <span class="label">All credits to</span>
        <span class="name"><b>M</b><b>E</b><b>O</b><b>W</b></span>
      </div>
      <div class="stats">
        <div class="stat"><b>{len(chapters)}</b><span>Chapters</span></div>
        <div class="stat"><b>{total}</b><span>Questions</span></div>
        <div class="stat"><b>{len(chapters)}</b><span>Answer keys</span></div>
      </div>
      <div class="cta">
        <a class="btn btn-primary" href="#ch1">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5V6a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/></svg>
          Start with Chapter 1
        </a>
        <a class="btn btn-ghost" href="https://drive.google.com/file/d/1TzUup2zFMrTLTt87kQVqq6yKfIyuokWG/view?usp=sharing"
           target="_blank" rel="noopener">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/>
            <path d="M14 3v5h5M9 13h6M9 17h4"/></svg>
          Studyhub Questions PDF Link
        </a>
      </div>
    </div>

    <div class="marquee" id="chapters"><div class="marquee-track">{ticker}</div></div>

    <div class="chapters">
      <div class="chapters-head">
        <h2>Chapters</h2>
        <span class="count">{len(chapters)} chapters · {total} questions</span>
      </div>
      <div class="grid">
{cards}
      </div>
    </div>

    <footer class="site">
      <div class="credits-big">
        <span class="cb-label">All credits to</span>
        <span class="cb-name">MEOW</span>
        <span class="cb-note">Compiled &amp; shared by MEOW</span>
      </div>
      <div class="foot-row">
        <span>ACCA MA · Studyhub Questions</span>
        <span>Answers hidden · Chapter wise</span>
      </div>
    </footer>
  </div>
</div>

<div class="progress"></div>
<button class="totop" aria-label="Back to top">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M12 19V5M6 11l6-6 6 6"/></svg>
</button>

<div id="views"></div>

<script id="site-data" type="application/json">{json.dumps(site_data, separators=(',', ':'))}</script>
<script>{JS}</script>
</body>
</html>
'''

with open('index.html', 'w') as f:
    f.write(html_doc)
print('written index.html', round(os.path.getsize('index.html') / 1e6, 2), 'MB')
