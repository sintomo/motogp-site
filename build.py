# -*- coding: utf-8 -*-
"""
MotoGP大全 ビルドスクリプト（Python標準ライブラリのみ）

  python build.py          データをチェックして docs/ にサイトを作成
  python build.py --check  データのチェックのみ（ファイルは作らない）

入力：data/*.csv（Excelで編集）、content/*.html（文章ページ）、templates/base.html、static/
出力：docs/（GitHub Pages で公開するフォルダー。手で編集しない）
"""
import csv
import html
import os
import re
import shutil
import sys
from collections import defaultdict
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
CONTENT = os.path.join(BASE, "content")
OUT = os.path.join(BASE, "docs")

# ------------------------------------------------------------
# サイト設定（ここを編集）
# ------------------------------------------------------------
SITE = {
    "name": "MotoGP大全",
    "tagline": "1949年のWGP開幕から2027年の850cc新時代まで。シーズン・ライダー・チーム・メーカー、規則・技術・名勝負を網羅。",
    "footnote": "公開情報に基づく個人用まとめ。正式な規則はFIM／Dorna公式文書を参照。",
}
# (ID, メニュー表示名, 出力パス)  ※並び順＝メニューの順
NAV = [
    ("top", "概要", "index.html"),
    ("seasons", "シーズン", "seasons/index.html"),
    ("riders", "ライダー", "riders/index.html"),
    ("teams", "チーム", "teams/index.html"),
    ("makers", "メーカー", "makers/index.html"),
    ("champions", "王者・記録", "champions.html"),
    ("eras", "時代史", "eras.html"),
    ("rules", "規則", "rules.html"),
    ("tech", "技術", "tech.html"),
    ("machines", "マシン図鑑", "machines.html"),
    ("battles", "名勝負", "battles.html"),
    ("japan", "日本とGP", "japan.html"),
    ("circuits", "サーキット", "circuits.html"),
    ("sources", "出典", "sources.html"),
]
# content/ の文章ページ（ファイル名 → NAV の ID）
CONTENT_PAGES = {"index": "top", "eras": "eras", "rules": "rules", "tech": "tech", "machines": "machines",
                 "champions": "champions", "battles": "battles", "japan": "japan", "circuits": "circuits",
                 "sources": "sources"}
STATUS = {"確認済", "記憶", "要確認", ""}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errors, warnings = [], []


def err(src, msg):
    errors.append(f"[エラー] {src}: {msg}")


def warn(src, msg):
    warnings.append(f"[注意]   {src}: {msg}")


# ------------------------------------------------------------
# CSV 読み込み（Excelの「CSV UTF-8」推奨。Shift-JIS保存でも読める）
# ------------------------------------------------------------
def load(name, required=()):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        err(name, "ファイルがありません")
        return []
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp932"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        err(name, "文字コードを読み取れません（CSV UTF-8 で保存し直してください）")
        return []
    rows = []
    reader = csv.DictReader(text.splitlines())
    missing = [c for c in required if c not in (reader.fieldnames or [])]
    if missing:
        err(name, "列がありません: " + ", ".join(missing))
        return []
    for i, r in enumerate(reader, start=2):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        if not any(r.values()):
            continue  # 空行は無視
        r["_src"] = f"{name} {i}行目"
        for c in required:
            if not r.get(c):
                err(r["_src"], f"「{c}」が空です")
        if "status" in r and r["status"] not in STATUS:
            err(r["_src"], f"status は 確認済／記憶／要確認 のいずれか（今: {r['status']}）")
        rows.append(r)
    return rows


def as_int(r, col, allow_blank=False):
    v = r.get(col, "")
    if v == "" and allow_blank:
        return None
    try:
        return int(float(v))
    except ValueError:
        err(r["_src"], f"「{col}」は数字で入力（今: {v}）")
        return None


# ------------------------------------------------------------
# データ読み込みとチェック
# ------------------------------------------------------------
classes = load("classes.csv", ["code", "group", "order"])
riders = load("riders.csv", ["id", "name_ja"])
teams = load("teams.csv", ["id", "name_ja"])
makers = load("manufacturers.csv", ["name_ja", "id"])
champions = load("champions.csv", ["year", "class", "rider_name"])
seasons = load("seasons.csv", ["year", "class"])
entries = load("entries.csv", ["year", "class", "rider_id", "team_id", "maker"])
timeline = load("timeline.csv", ["year", "category", "text"])
class_bars = load("class_bars.csv", ["label", "from", "to", "color", "text"])
machines = load("machines.csv", ["name", "class"])
battles = load("battles.csv", ["year", "race"])
japanese = load("japanese.csv", ["name"])
circuits = load("circuits.csv", ["name"])
legends = load("legends.csv", ["name"])
sources = load("sources.csv", ["title"])


def index_by(rows, key, label):
    out = {}
    for r in rows:
        k = r.get(key, "")
        if k in out:
            err(r["_src"], f"{label}「{k}」が重複しています")
        out[k] = r
    return out


CLS = index_by(classes, "code", "クラス")
for c in classes:
    c["order"] = as_int(c, "order") or 99
RID = index_by(riders, "id", "ライダーID")
TID = index_by(teams, "id", "チームID")
MK = index_by(makers, "name_ja", "メーカー名")
index_by(makers, "id", "メーカーID")
for r in riders + teams + makers:
    if r.get("id") and not ID_RE.match(r["id"]):
        err(r["_src"], f"ID「{r['id']}」は半角小文字・数字・ハイフンのみ（例: marc-marquez）")
for r in riders:
    as_int(r, "birth_year", True)


def check_class(r):
    if r.get("class") and r["class"] not in CLS:
        err(r["_src"], f"クラス「{r['class']}」が classes.csv にありません")


seen = set()
for r in champions:
    r["year"] = as_int(r, "year")
    check_class(r)
    if r.get("rider_id") and r["rider_id"] not in RID:
        err(r["_src"], f"rider_id「{r['rider_id']}」が riders.csv にありません")
    k = (r["year"], r["class"])
    if k in seen:
        err(r["_src"], f"{r['year']}年 {r['class']} の王者が2人います")
    seen.add(k)
    if r.get("maker") and r["maker"] not in MK:
        pass  # 未登録メーカーはリンクなしで表示（エラーにしない）

seen = set()
for r in seasons:
    r["year"] = as_int(r, "year")
    check_class(r)
    as_int(r, "rounds", True)
    if r.get("runner_up_id") and r["runner_up_id"] not in RID:
        err(r["_src"], f"runner_up_id「{r['runner_up_id']}」が riders.csv にありません")
    if r.get("constructor_champion") and r["constructor_champion"] not in MK:
        warn(r["_src"], f"メーカー「{r['constructor_champion']}」が manufacturers.csv にありません")
    k = (r["year"], r["class"])
    if k in seen:
        err(r["_src"], f"{r['year']}年 {r['class']} が重複しています")
    seen.add(k)

seen = set()
for r in entries:
    r["year"] = as_int(r, "year")
    check_class(r)
    r["rank_i"] = as_int(r, "rank", True)
    if r["rider_id"] not in RID:
        err(r["_src"], f"rider_id「{r['rider_id']}」が riders.csv にありません")
    if r["team_id"] not in TID:
        err(r["_src"], f"team_id「{r['team_id']}」が teams.csv にありません")
    if r["maker"] not in MK:
        err(r["_src"], f"メーカー「{r['maker']}」が manufacturers.csv にありません")
    k = (r["year"], r["class"], r["rider_id"])
    if k in seen:
        warn(r["_src"], f"{r['year']}年 {r['class']} に同じライダーが複数行（代役・移籍なら問題なし）")
    seen.add(k)

for r in timeline + battles:
    r["year_i"] = as_int(r, "year")
for r in class_bars:
    as_int(r, "from"); as_int(r, "to")

used_riders = {r.get("rider_id") for r in champions} | {r["rider_id"] for r in entries} | {r.get("runner_up_id") for r in seasons}
for r in riders:
    if r["id"] not in used_riders:
        warn(r["_src"], f"ライダー「{r['id']}」はどこからも参照されていません")


def report():
    for m in errors + warnings:
        print(m)
    print(f"\nチェック結果: エラー {len(errors)} 件 / 注意 {len(warnings)} 件")


if errors:
    report()
    print("エラーを直してから再実行してください。サイトは作成していません。")
    sys.exit(1)
if "--check" in sys.argv:
    report()
    sys.exit(0)

# ------------------------------------------------------------
# HTML 部品
# ------------------------------------------------------------
E = html.escape
TEMPLATE = open(os.path.join(BASE, "templates", "base.html"), encoding="utf-8").read()
written = []


def yr(y):
    return f'<span class="yr">{y}</span>'


def badge(status):
    if status == "要確認":
        return ' <span class="chk">要確認</span>'
    if status == "記憶":
        return ' <span class="chk chk-soft" title="出典と未照合">未照合</span>'
    return ""


def a(root, path, text):
    return f'<a href="{root}{path}">{text}</a>'


def rider_link(root, rid, fallback=""):
    r = RID.get(rid)
    return a(root, f"riders/{rid}.html", E(r["name_ja"])) if r else E(fallback)


def team_link(root, tid):
    t = TID.get(tid)
    return a(root, f"teams/{tid}.html", E(t["name_ja"])) if t else E(tid)


def maker_link(root, name):
    m = MK.get(name)
    dot = f'<span class="dot" style="background:{m["color"] if m and m.get("color") else "#999"}"></span>'
    return dot + (a(root, f"makers/{m['id']}.html", E(name)) if m else E(name))


def season_link(root, y):
    return a(root, f"seasons/{y}.html", str(y)) if y in SEASON_YEARS else str(y)


def yr_link(root, y):
    """年号チップ。シーズンページがあればリンクにする"""
    return a(root, f"seasons/{y}.html", yr(y)) if y in SEASON_YEARS else yr(y)


def rank_txt(e):
    """年間順位（ポイントがあれば併記）"""
    if not e.get("rank_i"):
        return "—"
    return f'{e["rank_i"]}位' + (f'（{e["points"]}点）' if e.get("points") else "")


def table(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tbl {cls}"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def chips(target, values, first="すべて", all_value=True):
    btns = []
    if all_value:
        btns.append(f'<button type="button" data-value="" aria-pressed="true">{first}</button>')
    for i, (v, label) in enumerate(values):
        pressed = "true" if (not all_value and i == 0) else "false"
        btns.append(f'<button type="button" data-value="{E(v)}" aria-pressed="{pressed}">{E(label)}</button>')
    return f'<div class="chips" role="group" data-filter="{target}">{"".join(btns)}</div>'


def nav_html(root, current):
    cur = ' aria-current="page"'
    return "".join(f'<a href="{root}{p}"{cur if i == current else ""}>{l}</a>' for i, l, p in NAV)


def write(path, title, body, nav_id, desc=""):
    depth = path.count("/")
    root = "../" * depth
    body = body.replace("{{root}}", root)
    page = (TEMPLATE.replace("{{title}}", E(title))
            .replace("{{description}}", E(desc or SITE["tagline"]))
            .replace("{{site_name}}", SITE["name"])
            .replace("{{tagline}}", SITE["tagline"])
            .replace("{{footnote}}", SITE["footnote"])
            .replace("{{updated}}", date.today().isoformat())
            .replace("{{nav}}", nav_html(root, nav_id))
            .replace("{{root}}", root)
            .replace("{{content}}", body))
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    written.append(path)


def ptitle(t):
    return f"{t}｜{SITE['name']}"


# ------------------------------------------------------------
# 集計
# ------------------------------------------------------------
CH_BY = defaultdict(list)          # (year) -> champions
for c in champions:
    CH_BY[c["year"]].append(c)
SEASON_ROWS = defaultdict(list)
for s in seasons:
    SEASON_ROWS[s["year"]].append(s)
ENT_BY_YEAR = defaultdict(list)
ENT_BY_RIDER = defaultdict(list)
ENT_BY_TEAM = defaultdict(list)
ENT_BY_MAKER = defaultdict(list)
for e in entries:
    ENT_BY_YEAR[e["year"]].append(e)
    ENT_BY_RIDER[e["rider_id"]].append(e)
    ENT_BY_TEAM[e["team_id"]].append(e)
    ENT_BY_MAKER[e["maker"]].append(e)
SEASON_YEARS = sorted(set(CH_BY) | set(SEASON_ROWS) | set(ENT_BY_YEAR))
TITLES = defaultdict(list)
for c in champions:
    if c.get("rider_id"):
        TITLES[c["rider_id"]].append(c)
RUNNER = defaultdict(list)
for s in seasons:
    if s.get("runner_up_id"):
        RUNNER[s["runner_up_id"]].append(s)
cls_order = lambda code: CLS.get(code, {}).get("order", 99)

# ------------------------------------------------------------
# 埋め込みブロック（content/*.html の <!--@名前--> を置換）
# ------------------------------------------------------------
def blk_classbars():
    y0, span = 1949, 2027 - 1949
    rows = defaultdict(list)
    order = []
    for b in class_bars:
        if b["label"] not in rows:
            order.append(b["label"])
        rows[b["label"]].append(b)
    out = []
    for lab in order:
        segs = "".join(
            f'<div class="sg" style="left:{(int(s["from"]) - y0) / span * 100:.2f}%;width:{(int(s["to"]) - int(s["from"])) / span * 100:.2f}%;background:{s["color"]}">{E(s["text"])}</div>'
            for s in rows[lab])
        out.append(f'<div class="br"><div class="l">{E(lab)}</div><div class="trk">{segs}</div></div>')
    return "".join(out)


def blk_classaxis():
    return "".join(f'<span style="left:{(y - 1949) / 78 * 100:.2f}%">{y}</span>' for y in (1949, 1970, 1990, 2010, 2027))


BIG = ' class="big"'


def blk_timeline():
    cats = []
    for t in timeline:
        if t["category"] not in cats:
            cats.append(t["category"])
    items = "".join(
        f'<li data-cat="{E(t["category"])}"{BIG if t.get("major") else ""}>{yr_link("{{root}}", t["year_i"])} {E(t["text"])}<span class="cat">{E(t["category"])}</span></li>'
        for t in sorted(timeline, key=lambda x: x["year_i"] or 0))
    return chips("tl", [(c, c) for c in cats]) + f'<ul class="tl" id="tl">{items}</ul>'


def blk_machines():
    cats = []
    for m in machines:
        if m["class"] not in cats:
            cats.append(m["class"])
    cards = "".join(
        f'<article class="mc" data-cat="{E(m["class"])}"><div class="top"><b>{E(m["name"])}</b><span class="cls">{E(m["class"])}</span></div>'
        f'<div class="spec">{E(m.get("years", ""))}｜{E(m.get("engine", ""))}</div><p>{m.get("note", "")}</p></article>'
        for m in machines)
    return chips("mg", [(c, c) for c in cats]) + f'<div class="grid" id="mg">{cards}</div>'


def blk_champions():
    groups = []
    for c in sorted(classes, key=lambda x: x["order"]):
        if c["group"] not in [g[0] for g in groups]:
            groups.append((c["group"], []))
        [g for g in groups if g[0] == c["group"]][0][1].append(c)
    out = [chips("ch", [(g, g) for g, _ in groups], all_value=False), '<div id="ch">']
    for g, cl in groups:
        codes = {c["code"] for c in cl}
        rows = sorted([c for c in champions if c["class"] in codes], key=lambda x: x["year"])
        note = next((c["note"] for c in cl if c.get("note")), "")
        body = [[yr_link("{{root}}", r["year"]),
                 rider_link("{{root}}", r.get("rider_id"), r["rider_name"]) + badge(r.get("status", "")),
                 E(r.get("nationality", "")), maker_link("{{root}}", r.get("maker", "")),
                 E(r["class"]) if len(codes) > 1 else ""] for r in rows]
        head = ["年", "ライダー", "国籍", "メーカー"] + (["クラス"] if len(codes) > 1 else [])
        if len(codes) == 1:
            body = [b[:4] for b in body]
        out.append(f'<div data-cat="{E(g)}"><h4>{E(g)}（{len(rows)}件）</h4>{table(head, body)}<p class="note">{E(note)}</p></div>')
    out.append("</div>")
    return "".join(out)


def source_li(s):
    t = a("", s["url"], E(s["title"])) if s.get("url") else E(s["title"])
    u = f'<span class="cat">{E(s["used_for"])}</span>' if s.get("used_for") else ""
    return f"<li>{t}{u}</li>"


def cards(rows, fn):
    return "".join(fn(r) for r in rows)


BLOCKS = {
    "classbars": blk_classbars,
    "classaxis": blk_classaxis,
    "timeline": blk_timeline,
    "machines": blk_machines,
    "champions": blk_champions,
    "legends": lambda: cards(legends, lambda r: f'<article class="mc"><div class="top"><b>{E(r["name"])}</b></div><div class="spec">{E(r.get("era", ""))}｜{E(r.get("titles", ""))}</div><p>{r.get("note", "")}</p></article>'),
    "battles": lambda: cards(sorted(battles, key=lambda x: x["year_i"] or 0), lambda b: f'<div class="battle">{yr(b["year_i"])}<div><b>{E(b["race"])}</b><div class="who">{E(b.get("who", ""))}</div><p>{b.get("note", "")}</p></div></div>'),
    "japanese": lambda: cards(japanese, lambda r: f'<article class="mc"><div class="top"><b>{E(r["name"])}</b><span class="cls">{E(r.get("era", ""))}</span></div><p>{r.get("note", "")}</p></article>'),
    "circuits": lambda: cards(circuits, lambda r: f'<article class="mc"><div class="top"><b>{E(r["name"])}</b></div><div class="spec">{E(r.get("info", ""))}</div><p>{r.get("note", "")}</p></article>'),
    "sources": lambda: cards(sources, source_li),
}

# ------------------------------------------------------------
# 出力
# ------------------------------------------------------------
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
shutil.copytree(os.path.join(BASE, "static"), os.path.join(OUT, "assets"))
open(os.path.join(OUT, ".nojekyll"), "w").close()

# 文章ページ
nav_title = {i: l for i, l, p in NAV}
nav_path = {i: p for i, l, p in NAV}
for name, nid in CONTENT_PAGES.items():
    src = open(os.path.join(CONTENT, name + ".html"), encoding="utf-8").read()
    for key, fn in BLOCKS.items():
        if f"<!--@{key}-->" in src:
            src = src.replace(f"<!--@{key}-->", fn())
    left = re.findall(r"<!--@(\w+)-->", src)
    if left:
        print(f"[注意]   content/{name}.html: 不明な埋め込み {left}")
    write(nav_path[nid], SITE["name"] if nid == "top" else ptitle(nav_title[nid]), f'<section class="page">{src}</section>', nid)

# ---------- シーズン ----------
rows = []
for y in reversed(SEASON_YEARS):
    top = sorted(CH_BY.get(y, []), key=lambda c: cls_order(c["class"]))
    prem = next((c for c in top if c["class"] in ("MotoGP", "500cc")), None)
    rows.append([a("{{root}}", f"seasons/{y}.html", yr(y)),
                 (rider_link("{{root}}", prem.get("rider_id"), prem["rider_name"]) + f'（{E(prem["class"])}）') if prem else "—",
                 f"{len(top)}クラス" if top else "—",
                 "◯" if ENT_BY_YEAR.get(y) else ""])
decades = sorted({(y // 10) * 10 for y in SEASON_YEARS}, reverse=True)
body = (f'<h1>シーズン</h1><p class="sub">1949年から現在までの各シーズン。MotoGP時代（2002年〜）から順次、参戦チーム・ライダーを追加中。</p>'
        + '<p class="jump">' + " ".join(f'<a href="#d{d}">{d}年代</a>' for d in decades) + '</p>')
by_dec = defaultdict(list)
for r, y in zip(rows, reversed(SEASON_YEARS)):
    by_dec[(y // 10) * 10].append(r)
for d in decades:
    body += f'<h3 id="d{d}">{d}年代</h3>' + table(["年", "最高峰王者", "王者掲載クラス", "参戦一覧"], by_dec[d])
write("seasons/index.html", ptitle("シーズン"), f'<section class="page">{body}</section>', "seasons")

for i, y in enumerate(SEASON_YEARS):
    b = [f'<p class="crumb">{a("{{root}}", "seasons/index.html", "シーズン")} ＞ {y}年</p><h1>{y}年シーズン</h1>']
    # クラス別の概要
    srows = sorted(SEASON_ROWS.get(y, []), key=lambda s: cls_order(s["class"]))
    for s in srows:
        champ = next((c for c in CH_BY.get(y, []) if c["class"] == s["class"]), None)
        facts = [("クラス", E(s["class"])),
                 ("開催戦数", f'{s["rounds"]}戦' if s.get("rounds") else "—"),
                 ("王者", rider_link("{{root}}", champ.get("rider_id"), champ["rider_name"]) + f'（{maker_link("{{root}}", champ.get("maker", ""))}）' if champ else "—"),
                 ("ランキング2位", rider_link("{{root}}", s.get("runner_up_id")) if s.get("runner_up_id") else "—"),
                 ("メーカー王者", maker_link("{{root}}", s["constructor_champion"]) if s.get("constructor_champion") else "—")]
        dl = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in facts)
        b.append(f'<h3>{E(s["class"])}クラス{badge(s.get("status", ""))}</h3><dl class="facts">{dl}</dl>')
        if s.get("summary"):
            b.append(f'<p class="prose">{E(s["summary"])}</p>')
        if s.get("rule_changes"):
            b.append(f'<p class="prose"><b>主な規則変更：</b>{E(s["rule_changes"])}（詳細は{a("{{root}}", "rules.html", "規則")}）</p>')
    # 参戦チーム・ライダー
    ents = ENT_BY_YEAR.get(y, [])
    for code in sorted({e["class"] for e in ents}, key=cls_order):
        ce = [e for e in ents if e["class"] == code]
        by_team = defaultdict(list)
        order = []
        for e in ce:
            if e["team_id"] not in by_team:
                order.append(e["team_id"])
            by_team[e["team_id"]].append(e)
        trs = []
        for tid in order:
            es = by_team[tid]
            trs.append([team_link("{{root}}", tid) + f'<div class="note">{E(es[0].get("entry_name", ""))}</div>',
                        maker_link("{{root}}", es[0]["maker"]) + (badge("要確認") if any(x.get("status") == "要確認" for x in es) else "") + (f'<div class="note">{E(es[0].get("machine", ""))}</div>' if es[0].get("machine") else ""),
                        "<br>".join(rider_link("{{root}}", e["rider_id"]) + (f' <span class="note">#{E(e["number"])}</span>' if e.get("number") else "") for e in es),
                        "<br>".join(rank_txt(e) for e in es)])
        b.append(f'<h3>{E(code)} 参戦チーム・ライダー</h3>' + table(["チーム", "メーカー", "ライダー", "年間順位"], trs)
                 + '<p class="note">年間順位は判明分のみ。空欄は未入力。「要確認」の行はメーカー・車両の特定が不確か。</p>')
    # 全クラス王者
    ch = sorted(CH_BY.get(y, []), key=lambda c: cls_order(c["class"]))
    if ch:
        b.append("<h3>この年の各クラス王者</h3>" + table(["クラス", "ライダー", "国籍", "メーカー"],
                 [[E(c["class"]), rider_link("{{root}}", c.get("rider_id"), c["rider_name"]) + badge(c.get("status", "")),
                   E(c.get("nationality", "")), maker_link("{{root}}", c.get("maker", ""))] for c in ch]))
    if not srows and not ents:
        b.append('<p class="note">このシーズンの詳細（参戦チーム・ライダー、概要）は未入力。</p>')
    prev = SEASON_YEARS[i - 1] if i > 0 else None
    nxt = SEASON_YEARS[i + 1] if i < len(SEASON_YEARS) - 1 else None
    b.append('<nav class="pager"><span>' + (a("{{root}}", f"seasons/{prev}.html", f"← {prev}年") if prev else "")
             + '</span><span>' + (a("{{root}}", f"seasons/{nxt}.html", f"{nxt}年 →") if nxt else "") + "</span></nav>")
    write(f"seasons/{y}.html", ptitle(f"{y}年シーズン"), f'<section class="page">{"".join(b)}</section>', "seasons")

# ---------- ライダー ----------
def years_of(rid):
    ys = [e["year"] for e in ENT_BY_RIDER.get(rid, [])] + [c["year"] for c in TITLES.get(rid, [])]
    return (min(ys), max(ys)) if ys else (None, None)


rows = []
for r in sorted(riders, key=lambda x: x["name_ja"]):
    y0, y1 = years_of(r["id"])
    rows.append((r, f'<tr data-text="{E(r["name_ja"] + " " + r.get("name_en", "") + " " + r.get("nationality", ""))}"><td>{rider_link("{{root}}", r["id"])}<div class="note">{E(r.get("name_en", ""))}</div></td>'
                    f'<td>{E(r.get("nationality", ""))}</td><td class="n">{len(TITLES.get(r["id"], [])) or ""}</td><td class="n">{f"{y0}–{y1}" if y0 else ""}</td></tr>'))
body = ('<h1>ライダー</h1><p class="sub">登録ライダーの一覧。名前・英字・国籍で絞り込み可。王者の数は全クラス合計（登録分）。</p>'
        '<input type="search" class="search" placeholder="名前・国籍で検索（例：マルケス、Rossi、日本）" data-search="rl" aria-label="ライダー検索">'
        f'<div class="tbl"><table><thead><tr><th>ライダー</th><th>国籍</th><th>タイトル</th><th>記録のある年</th></tr></thead><tbody id="rl">{"".join(x[1] for x in rows)}</tbody></table></div>'
        f'<p class="note">{len(riders)}人を登録。過去の王者は順次追加。</p>')
write("riders/index.html", ptitle("ライダー"), f'<section class="page">{body}</section>', "riders")

for r in riders:
    rid = r["id"]
    b = [f'<p class="crumb">{a("{{root}}", "riders/index.html", "ライダー")} ＞ {E(r["name_ja"])}</p>',
         f'<h1>{E(r["name_ja"])}{badge(r.get("status", ""))}</h1><p class="sub">{E(r.get("name_en", ""))}</p>']
    facts = [("国籍", E(r.get("nationality", "")) or "—"), ("生年", f'{r["birth_year"]}年' if r.get("birth_year") else "—"),
             ("世界タイトル", f'{len(TITLES.get(rid, []))}回（登録分）')]
    # 参戦記録からの自動集計（クラス別）
    for code in sorted({e["class"] for e in ENT_BY_RIDER.get(rid, [])}, key=cls_order):
        ce = [e for e in ENT_BY_RIDER[rid] if e["class"] == code]
        ys = sorted({e["year"] for e in ce})
        ranked = [e for e in ce if e["rank_i"]]
        best = min(ranked, key=lambda e: (e["rank_i"], e["year"])) if ranked else None
        pts = [int(float(e["points"])) for e in ce if e.get("points")]
        facts.append((f"{code} 参戦", f"{ys[0]}〜{ys[-1]}年（{len(ys)}シーズン）"))
        if best:
            facts.append((f"{code} 最高位", f'{best["rank_i"]}位（{best["year"]}年）'))
        if pts:
            facts.append((f"{code} 通算ポイント", f"{sum(pts)}点" + ("（一部年のみ）" if len(pts) < len(ce) else "")))
    b.append('<dl class="facts">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in facts) + "</dl>")
    if r.get("profile"):
        b.append(f'<p class="prose">{r["profile"]}</p>')
    t = sorted(TITLES.get(rid, []), key=lambda c: c["year"])
    if t:
        b.append("<h3>世界タイトル</h3>" + table(["年", "クラス", "メーカー"], [[yr_link("{{root}}", c["year"]), E(c["class"]), maker_link("{{root}}", c.get("maker", ""))] for c in t]))
    ru = sorted(RUNNER.get(rid, []), key=lambda s: s["year"])
    if ru:
        b.append("<h3>ランキング2位</h3><p>" + "、".join(a("{{root}}", f'seasons/{s["year"]}.html', f'{s["year"]}年') + f'（{E(s["class"])}）' for s in ru) + "</p>")
    es = sorted(ENT_BY_RIDER.get(rid, []), key=lambda e: e["year"])
    if es:
        b.append("<h3>所属の移り変わり</h3>" + table(["年", "クラス", "チーム", "メーカー", "年間順位"],
                 [[a("{{root}}", f'seasons/{e["year"]}.html', yr(e["year"])), E(e["class"]), team_link("{{root}}", e["team_id"]),
                   maker_link("{{root}}", e["maker"]), rank_txt(e)] for e in es]))
    else:
        b.append('<p class="note">参戦記録は未入力。</p>')
    write(f"riders/{rid}.html", ptitle(r["name_ja"]), f'<section class="page">{"".join(b)}</section>', "riders")

# ---------- チーム ----------
rows = []
for t in sorted(teams, key=lambda x: x["name_ja"]):
    ys = sorted({e["year"] for e in ENT_BY_TEAM.get(t["id"], [])})
    rows.append([team_link("{{root}}", t["id"]), E(t.get("country", "")), f"{ys[0]}–{ys[-1]}" if ys else "—", E(t.get("note", ""))])
write("teams/index.html", ptitle("チーム"), '<section class="page"><h1>チーム</h1><p class="sub">登録チームの一覧。スポンサー名が変わっても同じチームとして管理（各年の正式名はチームページに表示）。</p>'
      + table(["チーム", "国", "記録のある年", "概要"], rows) + "</section>", "teams")
for t in teams:
    es = sorted(ENT_BY_TEAM.get(t["id"], []), key=lambda e: (-e["year"], e["class"]))
    b = [f'<p class="crumb">{a("{{root}}", "teams/index.html", "チーム")} ＞ {E(t["name_ja"])}</p><h1>{E(t["name_ja"])}{badge(t.get("status", ""))}</h1>',
         f'<p class="sub">{E(t.get("country", ""))}　{E(t.get("note", ""))}</p>']
    by = defaultdict(list)
    for e in es:
        by[(e["year"], e["class"])].append(e)
    trs = [[a("{{root}}", f"seasons/{y}.html", yr(y)), E(c), E(v[0].get("entry_name", "")), maker_link("{{root}}", v[0]["maker"]),
            "<br>".join(rider_link("{{root}}", e["rider_id"]) + (f' {rank_txt(e)}' if e["rank_i"] else "") for e in v)] for (y, c), v in by.items()]
    b.append("<h3>年別の体制</h3>" + (table(["年", "クラス", "エントリー名", "メーカー", "ライダー（年間順位）"], trs) if trs else '<p class="note">未入力。</p>'))
    write(f"teams/{t['id']}.html", ptitle(t["name_ja"]), f'<section class="page">{"".join(b)}</section>', "teams")

# ---------- メーカー ----------
rows = []
for m in makers:
    n = [c for c in champions if c.get("maker") == m["name_ja"]]
    rows.append([maker_link("{{root}}", m["name_ja"]), E(m.get("country", "")), f'<span class="n">{len(n)}</span>', E(m.get("note", ""))])
write("makers/index.html", ptitle("メーカー"), '<section class="page"><h1>メーカー</h1><p class="sub">ライダーズタイトル数は全クラス合計（登録分）。</p>'
      + table(["メーカー", "国", "ライダーズタイトル", "概要"], rows) + "</section>", "makers")
for m in makers:
    name = m["name_ja"]
    b = [f'<p class="crumb">{a("{{root}}", "makers/index.html", "メーカー")} ＞ {E(name)}</p><h1>{E(name)}</h1>',
         f'<p class="sub">{E(m.get("country", ""))}　{E(m.get("note", ""))}</p>']
    ch = sorted([c for c in champions if c.get("maker") == name], key=lambda c: c["year"])
    cc = defaultdict(int)
    for c in ch:
        cc[c["class"]] += 1
    cons = sorted([s for s in seasons if s.get("constructor_champion") == name], key=lambda s: s["year"])
    facts = [("ライダーズタイトル", f"{len(ch)}回（" + "、".join(f"{k} {v}" for k, v in sorted(cc.items(), key=lambda x: cls_order(x[0]))) + "）" if ch else "—"),
             ("メーカータイトル（登録分）", "、".join(a("{{root}}", f'seasons/{s["year"]}.html', str(s["year"])) for s in cons) or "—")]
    b.append('<dl class="facts">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in facts) + "</dl>")
    if ch:
        b.append("<h3>歴代王者</h3>" + table(["年", "クラス", "ライダー"], [[a("{{root}}", f'seasons/{c["year"]}.html', yr(c["year"])), E(c["class"]), rider_link("{{root}}", c.get("rider_id"), c["rider_name"])] for c in ch]))
    ms = [x for x in machines if x.get("maker") == name]
    if ms:
        b.append('<h3>主なマシン</h3><div class="grid">' + "".join(f'<article class="mc"><div class="top"><b>{E(x["name"])}</b><span class="cls">{E(x["class"])}</span></div><div class="spec">{E(x.get("years", ""))}｜{E(x.get("engine", ""))}</div><p>{x.get("note", "")}</p></article>' for x in ms) + "</div>")
    es = ENT_BY_MAKER.get(name, [])
    if es:
        by = defaultdict(set)
        for e in es:
            by[e["year"]].add(e["team_id"])
        b.append("<h3>参戦チーム（登録分）</h3>" + table(["年", "チーム"], [[a("{{root}}", f"seasons/{y}.html", yr(y)), "、".join(team_link("{{root}}", t) for t in sorted(v))] for y, v in sorted(by.items(), reverse=True)]))
    write(f"makers/{m['id']}.html", ptitle(name), f'<section class="page">{"".join(b)}</section>', "makers")

report()
print(f"\n完了: {len(written)} ページを docs/ に作成しました。docs/index.html を開いて確認してください。")
