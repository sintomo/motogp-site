"""英語版Wikipedia シーズン記事（wikitext）の 参戦者表・年間順位表 を解析"""
import re

def sections(text):
    lines = text.splitlines()
    heads = []
    for i, l in enumerate(lines):
        m = re.match(r"^(=+)\s*(.*?)\s*\1\s*$", l)
        if m: heads.append((len(m.group(1)), m.group(2), i))
    out = []
    for k, (lv, t, i) in enumerate(heads):
        end = next((j for (lv2, t2, j) in heads[k + 1:] if lv2 <= lv), len(lines))
        parent = next((t2 for (lv2, t2, j) in reversed(heads[:k]) if lv2 < lv), "")
        out.append(dict(level=lv, title=t, parent=parent, body="\n".join(lines[i + 1:end])))
    return out

def _has(t, c):
    return re.search(r"(^|[^0-9])" + re.escape(c), t) is not None

def find(text, cls, kind):
    c = cls.lower().replace(" ", "")
    for s in sections(text):
        t, p = s["title"].lower().replace(" ", ""), s["parent"].lower().replace(" ", "")
        if not _has(t, c) and not ((kind in ("part", "stand") and ("particip" in p or "rider" in p or "manufactur" in p))):
            continue
        if kind == "part" and _has(t, c) and "particip" in t: return s["body"]
        if kind == "part" and "particip" in p and _has(t, c): return s["body"]
        if kind == "stand" and _has(t, c) and "standing" in t and "manufactur" not in t and "constructor" not in t and "team" not in t: return s["body"]
        if kind == "stand" and "rider" in p and "standing" in p and _has(t, c): return s["body"]
        if kind == "manu" and _has(t, c) and ("manufactur" in t or "constructor" in t): return s["body"]
        if kind == "manu" and ("manufactur" in p or "constructor" in p) and _has(t, c): return s["body"]
    return ""

LINK = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]")
def clean(v):
    v = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", v)
    v = re.sub(r"\{\{flagicon\|[^}]*\}\}|\{\{flag\|[^}]*\}\}", "", v)
    v = re.sub(r"\{\{(?:sortname|nowrap)\|([^}|]*)\|?([^}]*)\}\}", lambda m: (m.group(1) + " " + m.group(2)).strip(), v)
    v = LINK.sub(r"\1", v)
    v = re.sub(r"<br\s*/?>", " ", v).replace("nowrap|", "")
    v = re.sub(r"<[^>]+>", "", v)
    v = v.replace("'''", "").replace("''", "").replace("&nbsp;", " ")
    v = re.sub(r"\{\{[^}]*\}\}", "", v)
    return re.sub(r"\s+", " ", v).strip()

def flag(v):
    m = re.search(r"\{\{flag(?:icon)?\|([^}|]*)", v)
    return m.group(1).strip() if m else ""

def cell_attrs(raw):
    """'rowspan=3 style=..| value' → (rowspan, value)"""
    rs = 1
    if "|" in raw and not raw.strip().startswith("[[") and not raw.strip().startswith("{{"):
        # 属性部分と値部分を分ける（リンク内の | は除外）
        depth, cut = 0, -1
        for i, ch in enumerate(raw):
            if raw[i:i + 2] in ("[[", "{{"): depth += 1
            if raw[i:i + 2] in ("]]", "}}"): depth -= 1
            if ch == "|" and depth == 0:
                cut = i; break
        if cut >= 0 and re.search(r"(rowspan|style|align|colspan|bgcolor|class)\s*=", raw[:cut]):
            m = re.search(r"rowspan\s*=\s*\"?(\d+)", raw[:cut])
            if m: rs = int(m.group(1))
            raw = raw[cut + 1:]
    return rs, raw

def rows_of(table):
    """wikitable → 行のリスト（各行はセル文字列のリスト。! と | 両方）"""
    out, cur = [], None
    for l in table.splitlines():
        s = l.strip()
        if s.startswith("{|"): continue
        if s.startswith("|-") or s.startswith("|}"):
            if cur is not None: out.append(cur)
            cur = [] if s.startswith("|-") else None
            continue
        if cur is None: cur = []
        if s.startswith("!") or (s.startswith("|") and not s.startswith("|+")):
            body = s[1:]
            parts = re.split(r"\|\||!!", body)
            cur.extend(parts)
    if cur: out.append(cur)
    return out

def tables(body):
    """本文中の wikitable を（入れ子外側を無視して）順に取り出す"""
    res, stack = [], []
    lines = body.splitlines()
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith("{|"): stack.append(i)
        elif s.startswith("|}") and stack:
            st = stack.pop()
            if 'wikitable' in lines[st]:
                res.append("\n".join(lines[st:i + 1]))
    return res

def rounds_set(v, n):
    v = clean(v).lower().replace("–", "-").replace("—", "-")
    if not v or v.startswith("all"): return set(range(1, n + 1))
    out = set()
    for part in re.split(r"[,;]\s*", v):
        m = re.match(r"(\d+)\s*-\s*(\d+)", part)
        if m: out |= set(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.strip().isdigit(): out.add(int(part.strip()))
    return out

def participants(text, cls, nrounds):
    body = find(text, cls, "part")
    res = []
    for t in tables(body):
        rows = rows_of(t)
        head = [clean(cell_attrs(c)[1]).lower() for c in rows[0]] if rows else []
        if "rider" not in " ".join(head): continue
        idx = {k: next((i for i, h in enumerate(head) if k in h), None) for k in ("team", "constructor", "motorcycle", "no", "rider", "round")}
        carry = {}
        ncol = len(head)
        for r in rows[1:]:
            cells, it, col = [None] * ncol, iter(r), 0
            vals = list(r)
            # rowspan の繰り越しを埋める
            out, vi = [], 0
            for ci in range(ncol):
                if ci in carry and carry[ci][0] > 0:
                    out.append(carry[ci][1]); carry[ci] = (carry[ci][0] - 1, carry[ci][1])
                elif vi < len(vals):
                    rs, v = cell_attrs(vals[vi]); vi += 1
                    out.append(v)
                    if rs > 1: carry[ci] = (rs - 1, v)
                else:
                    out.append("")
            g = lambda k: out[idx[k]] if idx[k] is not None and idx[k] < len(out) else ""
            rider = clean(g("rider"))
            if not rider: continue
            no = clean(g("no"))
            res.append(dict(team=clean(g("team")), constructor=clean(g("constructor")), motorcycle=clean(g("motorcycle")),
                            number=int(no) if no.isdigit() else None, rider=rider, nat=flag(g("rider")),
                            rounds=rounds_set(g("round"), nrounds)))
    return res

RES_TOKENS = {"ret": "DNF", "dns": "DNS", "nc": "DNF", "dsq": "DSQ", "dnq": "DNQ", "exc": "EXC", "dnf": "DNF", "wd": None, "dnp": None, "": None, "-": None, "c": None}
def standings(text, cls):
    """複数の表に分かれている場合は列をつなげる"""
    body = find(text, cls, "stand")
    parts = []
    for t in tables(body):
        r = _stand_table(t)
        if r and r[1] and all(len(x) == 3 for x in r[1]): parts.append(r)
    if not parts:
        for t in tables(body):
            r = _stand_table(t)
            if r: return r
        return [], []
    if len(parts) == 1: return parts[0]
    codes, byname, order = [], {}, []
    for rows, cds in parts:
        off = len(codes); codes += cds
        for r in rows:
            k = r["rider"]
            if k not in byname:
                byname[k] = dict(r, cells=[""] * off); order.append(k)
            b = byname[k]
            b["cells"] = b["cells"] + [""] * (off - len(b["cells"])) + r["cells"][:len(cds)] + [""] * (len(cds) - len(r["cells"]))
            if r.get("pos"): b["pos"] = r["pos"]; b["pts"] = r["pts"]
    return [byname[k] for k in order], codes

def _stand_table(t):
    for _ in [0]:
        rows = rows_of(t)
        if not rows: continue
        head = rows[0]
        hl = [clean(cell_attrs(c)[1]) for c in head]
        if not any("rider" in h.lower() for h in hl): continue
        # レース列 = Rider/Bike と Pts の間
        ri = next(i for i, h in enumerate(hl) if "rider" in h.lower())
        pis = [i for i, h in enumerate(hl) if h.lower().startswith("pt") or h.lower() == "points"]
        if not pis: continue
        pi = max(pis)
        bi = next((i for i, h in enumerate(hl) if h.lower() in ("bike", "motorcycle", "manufacturer", "constructor", "machine")), None)
        cand = [i for i in range(ri + 1, pi) if re.fullmatch(r"[A-Z]{3}", re.sub(r"[^A-Z]", "", hl[i])[:3] or "") and hl[i].lower() not in ("team", "bike", "machine")]
        first = cand[0] if cand else (bi if bi is not None else ri) + 1
        codes = [re.sub(r"[^A-Z]", "", clean(h))[:3] for h in hl[first:pi]]
        out = []
        ncol = len(hl)
        carry = {}
        for r in rows[1:]:
            vals, vi = [], 0
            for ci in range(ncol):
                if ci in carry and carry[ci][0] > 0:
                    vals.append(carry[ci][1]); carry[ci] = (carry[ci][0] - 1, carry[ci][1])
                elif vi < len(r):
                    rs, v = cell_attrs(r[vi]); vi += 1
                    vals.append(v)
                    if rs > 1: carry[ci] = (rs - 1, v)
                else:
                    vals.append("")
            if len(vals) < pi: continue
            pos = clean(vals[0])
            rider = clean(vals[ri])
            if not rider or rider.lower() in ("rider", "pos", "pos."): continue
            out.append(dict(pos=int(pos) if pos.isdigit() else None, rider=rider, nat=flag(vals[ri]),
                            bike=clean(vals[bi]) if bi is not None else "",
                            cells=[clean(v) for v in vals[first:pi]], pts=clean(vals[pi]) if pi < len(vals) else ""))
        return out, codes
    return None

def manufacturers(text, cls):
    body = find(text, cls, "manu")
    for t in tables(body):
        rows = rows_of(t)
        if len(rows) < 2: continue
        for r in rows[1:]:
            vals = [clean(cell_attrs(v)[1]) for v in r]
            if vals and vals[0] == "1":
                return vals[1]
    return ""

def header_links(text, cls):
    """年間順位表の見出し行のリンク先（各GP記事タイトル）を順に返す"""
    body = find(text, cls, "stand")
    for t in tables(body):
        rows = rows_of(t)
        if not rows: continue
        hl = [clean(cell_attrs(c)[1]) for c in rows[0]]
        if not any("rider" in h.lower() for h in hl): continue
        out = []
        for c in rows[0]:
            m = re.search(r"\[\[([^\]|]*(?:Grand Prix|TT)[^\]|]*)\|", c)
            if m: out.append(m.group(1).strip())
        return out
    return []

def infobox_podium(text, cls):
    """各GP記事の Infobox から (1位,2位,3位) のライダー名と国"""
    n = cls.replace("cc", "")
    out = []
    for k in ("First", "Second", "Third"):
        m = re.search(r"\|[ \t]*" + k + r"_Rider_" + n + r"[ \t]*=[ \t]*(.*)", text)
        cm = re.search(r"\|[ \t]*" + k + r"_Rider_" + n + r"_Country[ \t]*=[ \t]*(.*)", text)
        out.append((clean(m.group(1)) if m else "", clean(cm.group(1)) if cm else ""))
    return out

def calendar_winners(text):
    """シーズン記事の日程表（クラス別優勝者の列）→ [{class: (rider, flag)}] を開催順に"""
    for s in sections(text):
        if "calendar" not in s["title"].lower() and "grands prix" not in s["title"].lower() and "results" not in s["title"].lower():
            continue
        for t in tables(s["body"]):
            rows = rows_of(t)
            if not rows: continue
            hl = [clean(cell_attrs(c)[1]).lower() for c in rows[0]]
            cols = {}
            for i, h in enumerate(hl):
                m = re.match(r"(\d+)\s*cc\s*winner", h.replace(" ", " "))
                if m and "sidecar" not in h: cols[i] = m.group(1) + "cc"
            if not cols: continue
            out = []
            for r in rows[1:]:
                vals = []
                for v in r:
                    m = re.search(r"colspan\s*=\s*\"?(\d+)", v.split("|")[0]) if "|" in v else None
                    vals += [cell_attrs(v)[1]] * (int(m.group(1)) if m else 1)
                if len(vals) < max(cols) + 1: continue
                d_ = {c: (clean(vals[i]), flag(vals[i])) for i, c in cols.items()}
                gi = next((j for j, h in enumerate(hl) if "grand prix" in h or h in ("race", "event")), None)
                d_["_gp"] = clean(vals[gi]) if gi is not None and gi < len(vals) else ""
                out.append(d_)
            return out
    return []
