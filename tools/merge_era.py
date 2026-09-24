"""era_Y0_Y1.json → data/*.csv へ反映（races / results / entries / riders / seasons / manufacturers）
使い方: python3 merge_era.py 2002 2009
"""
import csv, json, sys
from collections import Counter, defaultdict
from resolve import Resolver, R
from gindex import build
from era import key, fold
from maps import nat_ja, gp_ja, maker_ja, NEW_MAKERS
from ja_names import JA

y0, y1 = int(sys.argv[1]), int(sys.argv[2])
JAF = {fold(k): v for k, v in JA.items()}

def read(fn):
    try:
        with open(R + fn, encoding='utf-8-sig') as f: return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

def write(fn, rows, fields):
    with open(R + fn, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(rows)

def num(v):
    if v in (None, ""): return ""
    f = float(v)
    return str(int(f)) if f == int(f) else str(f)

d = json.load(open(f'era_{y0}_{y1}.json'))
idx, info = build()
RS = Resolver()
makers = read('manufacturers.csv'); mk = {m['name_ja'] for m in makers}
for row in NEW_MAKERS:
    if row[0] not in mk:
        makers.append(dict(zip(['name_ja', 'id', 'country', 'color', 'note'], row))); mk.add(row[0])

SAME_NAME = {"julian miralles": [(2000, "979e8c74-59a7-4110-91e6-cd0e8c2a2c00"), (0, "65707356-ac89-47ac-8e97-f27d8d2e0640")]}
def rid_of(name, uuid, nat, year=None):
    if not uuid and fold(name) in SAME_NAME and year:
        uuid = next(u for y0, u in SAME_NAME[fold(name)] if year >= y0)
    if not uuid:
        c = idx.get(key(name))
        if c and len(c) == 1: uuid = list(c)[0]
        elif c and year:
            # 同名複数（親子など）→ その年に14〜50歳だった人
            ok = [u for u in c if (info.get(u) or {}).get('birth_date') and 14 <= year - int(info[u]['birth_date'][:4]) <= 50]
            if len(ok) == 1: uuid = ok[0]
    return RS.get(name, uuid, nat), uuid

from maps import maker_or_raw
AUTO_MAKERS = []
def mk_of(s):
    m = maker_or_raw(s)
    if not m: return ""
    if m not in mk:
        import re as _r
        mid = _r.sub(r'[^a-z0-9]+', '-', fold(m)).strip('-') or 'maker'
        while mid in {x['id'] for x in makers}: mid += '-x'
        makers.append(dict(name_ja=m, id=mid, country='—', color='#999999', note='公式リザルト／英語版Wikipediaの表記「' + m + '」'))
        mk.add(m); AUTO_MAKERS.append(m)
    return m

CANCELLED = {(2008, '250cc', 'INP'): '中止（ハリケーン・アイクの影響による悪天候）',
             (2011, 'MotoGP', 'MAL'): '中止（2周目のマルコ・シモンチェリの事故による）',
             (2018, 'MotoGP', 'GBR'): '中止（大雨・路面の排水不良）', (2018, 'Moto2', 'GBR'): '中止（大雨・路面の排水不良）',
             (2018, 'Moto3', 'GBR'): '中止（大雨・路面の排水不良）'}
races, results, problems = [], [], []
agg = defaultdict(lambda: dict(team=Counter(), maker=Counter(), number=Counter(), pts=0.0, uuid=None))
for r in d['races']:
    if (r['year'], r['cls'], r['gp']) in CANCELLED:
        r['rows'] = []
    rows = r['rows']
    if r['kind'] == 'SPR' and not rows:
        continue   # 行われなかったスプリント
    win = None
    for x in rows:
        rid, u = rid_of(x['name'], x['uuid'], x['nat'], r['year'])
        x['rid'] = rid
        if x['status'] == 'FIN' and x['pos'] == 1: win = rid
        m = mk_of(x['maker'])
        if not m and x['maker']: problems.append(('maker?', r['year'], r['cls'], r['gp'], x['name'], x['maker']))
        results.append(dict(year=r['year'], **{'class': r['cls']}, round=r['round'], session=r['kind'], pos=x['pos'] or '',
                            rider_id=rid, number=x['number'] or '', team=x['team'], maker=m, points=num(x['points']) if x['points'] else '',
                            result=x['status']))
        if r['kind'] in ('RAC', 'RAC2'):
            a = agg[(r['year'], r['cls'], rid)]
            if x['team']: a['team'][x['team']] += 1
            if m: a['maker'][m] += 1
            if x['number']: a['number'][x['number']] += 1
            a['pts'] += float(x['points'] or 0); a['uuid'] = a['uuid'] or u
    races.append(dict(year=r['year'], **{'class': r['cls']}, round=r['round'], session=r['kind'], gp_code=r['gp'],
                      gp_name_ja=gp_ja(r['gp'], r['gp_name'], r['year']), circuit=r['circuit'], date=r['date'] or '',
                      winner_id=win or '', status='確認済' if (rows or (r['year'], r['cls'], r['gp']) in CANCELLED) else '要確認',
                      note=({'wiki': '公式リザルトに結果データがないため、ポイント獲得者などの着順のみ掲載（出典：英語版Wikipedia 年間順位表）',
                             'podium': '公式リザルトに結果データがないため、上位3名のみ掲載（出典：英語版Wikipedia 各GP記事）',
                             'winner': '公式リザルトに結果データがないため、優勝者のみ掲載（出典：英語版Wikipedia シーズン記事の日程表）'}.get(r.get('src'), '')
                            if rows else CANCELLED.get((r['year'], r['cls'], r['gp']), '公式リザルトに結果データなし（未収録）')),
                      source=r.get('file') or ''))

# ---- 年間順位 ----
st = defaultdict(dict)
for s in d['standings']:
    rid, u = rid_of(s['name'], s['uuid'], s['nat'], s['year'])
    st[(s['year'], s['cls'])][rid] = (s['pos'], s['points'], mk_of(s['maker']))
    agg[(s['year'], s['cls'], rid)]['uuid'] = agg[(s['year'], s['cls'], rid)]['uuid'] or u
calc, nocalc = [], []
for (y, c) in {(k[0], k[1]) for k in agg}:
    if st.get((y, c)): continue
    # 公式の年間順位データなし → 決勝ポイント合計から算出
    partial = any((r.get('src') in ('wiki', 'podium', 'winner') or not r['rows']) and r['kind'] != 'SPR'
                  for r in d['races'] if r['year'] == y and r['cls'] == c)
    if partial:
        # 公式の年間順位なし＋レース結果も一部のみ → 順位は付けない
        nocalc.append((y, c)); st[(y, c)] = {}; continue
    calc.append((y, c))
    pts = {k[2]: v['pts'] for k, v in agg.items() if k[0] == y and k[1] == c and v['pts'] > 0}
    wins = Counter(x['rider_id'] for x in results if x['year'] == y and x['class'] == c and x['pos'] == 1 and x['session'] == 'RAC')
    order = sorted(pts, key=lambda k: (-pts[k], -wins[k]))
    st[(y, c)] = {k: (i + 1, pts[k], '') for i, k in enumerate(order)}

unresolved = set()
# ---- ハーフポイントの検出（公式の年間順位と決勝ポイント合計の差が、1レースの半分で説明できる場合） ----
for (y, c), dct in st.items():
    if (y, c) in calc or (y, c) in nocalc: continue
    xs = [x for x in results if x['year'] == y and x['class'] == c]
    tot = defaultdict(float)
    for x in xs: tot[x['rider_id']] += float(x['points'] or 0)
    diff = {k: float(v[1] or 0) - tot[k] for k, v in dct.items() if abs(float(v[1] or 0) - tot[k]) > 0.01}
    diff.update({k: -t for k, t in tot.items() if k not in dct and t > 0})
    if not diff: continue
    byr = defaultdict(list)
    for x in xs: byr[(x['round'], x['session'])].append(x)
    tot_abs = sum(abs(v) for v in diff.values())
    best = None
    for rk, lst in byr.items():
        pts = {x['rider_id']: float(x['points'] or 0) for x in lst}
        rest = sum(abs(diff.get(k, 0) + pts.get(k, 0) / 2) for k in set(diff) | {k for k, v in pts.items() if v > 0})
        if best is None or rest < best[0]: best = (rest, rk)
    for rk, lst in byr.items():
        pts = {x['rider_id']: float(x['points'] or 0) for x in lst}
        exact = all(abs(-pts.get(k, 0) / 2 - v) < 0.01 for k, v in diff.items()) and all(k in diff for k, v in pts.items() if v > 0)
        # ほぼ説明できる（差の合計が7割以上減る、かつ半端な0.5点を含む）場合もハーフポイントとみなす
        halfish = any(abs(v * 2 - round(v * 2)) < 0.01 and abs(v - round(v)) > 0.01 for v in diff.values())
        if exact or (best and best[1] == rk and halfish and best[0] < tot_abs * 0.6):
            for x in lst:
                if x['points']: x['points'] = num(float(x['points']) / 2)
            for r in races:
                if (r['year'], r['class'], r['round'], r['session']) == (y, c, rk[0], rk[1]):
                    r['note'] = (r['note'] + ' ' if r['note'] else '') + 'レース距離不足のためハーフポイント'
            problems.append(('ハーフポイント適用', y, c, rk))
            # agg も補正
            for x in lst:
                if (y, c, x['rider_id']) in agg and x['points'] and rk[1] in ('RAC', 'RAC2'):
                    agg[(y, c, x['rider_id'])]['pts'] -= float(x['points'])
            break
    else:
        problems.append(('年間順位と決勝ポイント合計の差（未解決）', y, c, diff)); unresolved.add((y, c))

# ---- 参戦一覧 ----
old = read('entries.csv')
keep = [e for e in old if not (y0 <= int(e['year']) <= y1 and e['class'] in {r['cls'] for r in d['races']})]
prev = {(int(e['year']), e['class'], e['rider_id']): e for e in old}
ents = []
for (y, c, rid), a in agg.items():
    s = st.get((y, c), {}).get(rid)
    p = prev.get((y, c, rid), {})
    m = (a['maker'].most_common(1)[0][0] if a['maker'] else '') or (s[2] if s else '') or p.get('maker', '')
    ents.append(dict(year=y, **{'class': c}, rider_id=rid, team_id=p.get('team_id', ''),
                     entry_name=p.get('entry_name') or (a['team'].most_common(1)[0][0] if a['team'] else ''),
                     maker=m or '不明', machine=p.get('machine', ''),
                     number=a['number'].most_common(1)[0][0] if a['number'] else '',
                     rank=s[0] if s else '', points=num(s[1]) if s and s[1] else '',
                     status='確認済' if m else '要確認'))
    if p and p.get('maker') and m and p['maker'] != m:
        problems.append(('maker差', y, c, rid, p['maker'], m))
# 年間順位に載っているのに決勝結果に出てこない人（結果未収録レースのみ出走など）
for (y, c), dct in st.items():
    for rid, s in dct.items():
        if (y, c, rid) not in agg:
            p = prev.get((y, c, rid), {})
            ents.append(dict(year=y, **{'class': c}, rider_id=rid, team_id=p.get('team_id', ''), entry_name=p.get('entry_name', ''),
                             maker=s[2] or p.get('maker') or '不明', machine=p.get('machine', ''), number='', rank=s[0],
                             points=num(s[1]) if s[1] else '', status='確認済' if (s[2] or p.get('maker')) else '要確認'))
lost = [k for k in prev if y0 <= k[0] <= y1 and k[1] in {r['cls'] for r in d['races']} and (k[0], k[1], k[2]) not in {(e['year'], e['class'], e['rider_id']) for e in ents}]
nodata = {(r['year'], r['cls']) for r in d['races'] if not r['rows'] and r['kind'] != 'SPR' and (r['year'], r['cls'], r['gp']) not in CANCELLED}
for k in lost:
    if (k[0], k[1]) in nodata:
        problems.append(('旧行を維持（結果未収録レースのみ）', k)); ents.append(prev[k])
    else:
        problems.append(('旧行を削除（公式の決勝結果に出走記録なし）', k, prev[k].get('entry_name'), prev[k].get('points')))
CO = {'MotoGP': 0, '500cc': 1, 'Moto2': 2, '250cc': 3, '350cc': 4, 'Moto3': 5, '125cc': 6, '80cc': 7, '50cc': 8}
allent = keep + ents
allent.sort(key=lambda e: (int(e['year']), CO.get(e['class'], 9), int(e['rank']) if str(e['rank']).strip() else 999, e['rider_id']))
write('entries.csv', allent, ['year', 'class', 'rider_id', 'team_id', 'entry_name', 'maker', 'machine', 'number', 'rank', 'points', 'status'])

# ---- races / results ----
rf = ['year', 'class', 'round', 'session', 'gp_code', 'gp_name_ja', 'circuit', 'date', 'winner_id', 'status', 'note', 'source']
xf = ['year', 'class', 'round', 'session', 'pos', 'rider_id', 'number', 'team', 'maker', 'points', 'result']
cls_set = {r['cls'] for r in d['races']}
inr = lambda e: y0 <= int(e['year']) <= y1 and e['class'] in cls_set
allr = [x for x in read('races.csv') if not inr(x)] + races
allx = [x for x in read('results.csv') if not inr(x)] + results
allr.sort(key=lambda r: (int(r['year']), CO.get(r['class'], 9), int(r['round']), r['session'] != 'SPR'))
write('races.csv', allr, rf)
write('results.csv', allx, xf)

# ---- ライダー ----
uuid_of_rid = {}
for (y, c, rid), a in agg.items():
    if a['uuid']: uuid_of_rid.setdefault(rid, a['uuid'])
for rid, u in RS.by_api.items():
    pass
for u, rid in RS.by_api.items():
    uuid_of_rid.setdefault(rid, u)
riders = RS.riders
byid = {r['id']: r for r in riders}
for rid, v in RS.new.items():
    ja = JAF.get(fold(v['name_en']))
    if not ja: problems.append(('日本語名なし', v['name_en']))
    riders.append(dict(id=rid, name_ja=ja or v['name_en'], name_en=v['name_en'], nationality=v['nat'], birth_year='', profile='',
                       status='記憶', birth_date='', birthplace='', api_id=''))
    byid[rid] = riders[-1]
for rid, u in uuid_of_rid.items():
    r = byid.get(rid)
    if not r: continue
    r['api_id'] = r.get('api_id') or u
    i = info.get(u)
    if not i: continue
    bd = i.get('birth_date') or ''
    if bd:
        if r.get('birth_year') and r['birth_year'] != bd[:4]:
            problems.append(('生年差', rid, r['birth_year'], bd))
        r['birth_date'] = bd; r['birth_year'] = bd[:4]
    if i.get('birth_city'):
        r['birthplace'] = i['birth_city'].strip()
    ctry = (i.get('country') or {}).get('iso')
    if ctry and not r.get('nationality'):
        r['nationality'] = nat_ja(ctry)
    if rid in RS.new:
        r['status'] = '確認済'
write('riders.csv', riders, ['id', 'name_ja', 'name_en', 'nationality', 'birth_year', 'birth_date', 'birthplace', 'profile', 'status', 'api_id'])
write('manufacturers.csv', makers, ['name_ja', 'id', 'country', 'color', 'note'])

# ---- シーズン概要（開催戦数・2位） ----
seasons = read('seasons.csv')
sk = {(int(s['year']), s['class']): s for s in seasons}
for (y, c), dct in st.items():
    rounds = len({(r['round']) for r in races if r['year'] == y and r['class'] == c and r['session'] == 'RAC' and not r['note'].startswith('中止')})
    r2 = next((k for k, v in dct.items() if v[0] == 2), '')
    s = sk.get((y, c))
    if s:
        if s.get('runner_up_id') and r2 and s['runner_up_id'] != r2: problems.append(('2位差', y, c, s['runner_up_id'], r2))
        if s.get('rounds') and int(s['rounds']) != rounds: problems.append(('戦数差', y, c, s['rounds'], rounds))
        s['rounds'] = rounds or s.get('rounds')
        s['runner_up_id'] = s.get('runner_up_id') or r2
    else:
        seasons.append(dict(year=y, **{'class': c}, rounds=rounds, runner_up_id=r2, constructor_champion='',
                            summary=('年間順位は公式の各レース結果のポイントから集計（公式の年間順位データが未収録のため）。' if (y, c) in calc else
                                     '公式の年間順位データがなく、レース結果も一部のみのため、年間順位は未掲載。' if (y, c) in nocalc else ''),
                            rule_changes='', status='確認済'))
NOTE_U = '年間順位・ポイントは公式発表の値（公式データがない年は英語版Wikipediaの年間順位表）。結果が部分的なレースがあるため、または後日の裁定などにより、一部選手は各レース結果のポイント合計と一致しない。'
for s_ in seasons:
    if (int(s_['year']), s_['class']) in unresolved and '一致しない' not in (s_.get('summary') or ''):
        s_['summary'] = ((s_.get('summary') or '') + ' ' + NOTE_U).strip()
seasons.sort(key=lambda s: (int(s['year']), CO.get(s['class'], 9)))
write('seasons.csv', seasons, list(read('seasons.csv')[0].keys()) if read('seasons.csv') else ['year', 'class', 'rounds', 'runner_up_id', 'constructor_champion', 'summary', 'rule_changes', 'status'])

# ---- 王者照合（rider_id 未設定なら、名前が一致する場合に設定） ----
chs = read('champions.csv')
en_of = {r['id']: r['name_en'] for r in riders}
ch_changed = 0
for ch in chs:
    k = (int(ch['year']), ch['class'])
    if k in st:
        w = next((r for r, v in st[k].items() if v[0] == 1), None)
        if ch.get('rider_id') and ch['rider_id'] != w: problems.append(('王者差', k, ch['rider_id'], w))
        if not ch.get('rider_id') and w:
            ja = next((r['name_ja'] for r in riders if r['id'] == w), '')
            if fold(ch['rider_name']).replace('・', '') == fold(ja).replace('・', '') or fold(en_of.get(w, '')).split()[-1] in fold(ch['rider_name']):
                ch['rider_id'] = w; ch_changed += 1
            else:
                problems.append(('王者rider_id未設定（名前不一致）', k, ch['rider_name'], w, ja))
if ch_changed:
    write('champions.csv', chs, list(chs[0].keys()))
    problems.append(('王者にrider_idを設定', ch_changed))

print('順位なし', nocalc)
print('auto makers', len(AUTO_MAKERS), AUTO_MAKERS[:80])
print('races', len(races), 'results', len(results), 'entries(era)', len(ents), 'new riders', len(RS.new), 'calc standings', sorted(calc))
for p in problems: print(*p)
