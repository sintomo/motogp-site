"""2001年以前用：公式API＋公式PDF（URL推定）＋英語版Wikipedia（年間順位表・参戦者表）で era_Y0_Y1.json を作る
使い方: python3 era2.py 1990 2001
出典の優先順位：①公式API決勝結果 ②公式リザルトPDF ③Wikipedia年間順位表（ポイント獲得者の着順のみ）
"""
import json, os, re, sys, subprocess, unicodedata
from collections import defaultdict, Counter
from api import c, season
from pdfparse import parse
from pdfget import local
from era import CLS, key, surname, proper, uuid_of, fold
import wparse as W

UA = "motogp-daizen-personal-site/1.0"
WIKI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki")

def wiki(y):
    p = os.path.join(WIKI, f"{y}.txt")
    if not os.path.exists(p):
        subprocess.run(["curl", "-sS", "-A", UA, "-o", p,
                        f"https://en.wikipedia.org/w/index.php?title={y}_Grand_Prix_motorcycle_racing_season&action=raw"])
    return open(p, encoding="utf-8").read()

def pdf_rows(url):
    p = local(url)
    if os.path.exists(p + ".txt"):
        return parse(open(p + ".txt", errors="ignore").read())
    if os.path.exists(p + ".404"):
        return []
    r = subprocess.run(["curl", "-sS", "-L", "--max-time", "60", "-o", p + ".pdf", "-w", "%{http_code}", url], capture_output=True, text=True)
    if r.stdout.strip() != "200":
        open(p + ".404", "w").close()
        if os.path.exists(p + ".pdf"): os.remove(p + ".pdf")
        return []
    q = subprocess.run(["pdftotext", "-layout", p + ".pdf", p + ".txt"], capture_output=True)
    os.remove(p + ".pdf")
    if q.returncode != 0: return []
    return parse(open(p + ".txt", errors="ignore").read())

SCALES = {"a": [25, 20, 16, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
          "b": [20, 15, 12, 10, 8, 6, 4, 3, 2, 1],
          "c": [20, 17, 15, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
          "d": [15, 12, 10, 8, 6, 5, 4, 3, 2, 1]}
def scale(y):
    if y >= 1993: return SCALES["a"]
    if y == 1992: return SCALES["b"]
    if y >= 1988: return SCALES["c"]
    if y >= 1969: return SCALES["d"]
    if y >= 1950: return [8, 6, 4, 3, 2, 1]
    return [10, 8, 7, 6, 5]

ALIAS_CODE = {"ESP": {"SPA"}, "GER": {"GER", "WGER"}, "YUG": {"JUG", "YUG"}, "SMR": {"RSM"}, "RSM": {"RSM"},
              "VDM": {"VDU", "VDM"}, "BRA": {"BRA", "RIO"}, "RIO": {"RIO", "BRA"}, "FIM": {"FIM"}, "EUR": {"EUR", "CAT"}, "ITA": {"ITA", "NAT"}, "AND": {"AND", "POR"}, "BAW": {"BAW"}, "MAN": {"TT"}, "HOL": {"NED"}, "DDR": {"EGER"}, "ULS": {"ULST"}, "NAC": {"NAT"},
              "CZE": {"CZE", "TCH"}, "GBR": {"GBR", "TT"}, "SPA": {"SPA"}}

def align(codes, evs):
    """年間順位表の列コード → イベントID（まず順番通り、失敗したら順不同で）"""
    out, p = {}, 0
    for ci, code in enumerate(codes):
        al = ALIAS_CODE.get(code, {code})
        for k in range(p, len(evs)):
            if evs[k]["short_name"] in al:
                out[evs[k]["id"]] = ci; p = k + 1; break
    if len(out) == len(codes): return out
    out, used = {}, set()
    for ci, code in enumerate(codes):
        al = ALIAS_CODE.get(code, {code})
        for e in evs:
            if e["id"] not in used and e["short_name"] in al:
                out[e["id"]] = ci; used.add(e["id"]); break
    return out
COUNTRY = {"united states": "US", "usa": "US", "italy": "IT", "ita": "IT", "spain": "ES", "esp": "ES", "japan": "JP", "jpn": "JP",
           "france": "FR", "fra": "FR", "germany": "DE", "ger": "DE", "brd": "DE", "west germany": "DE", "frg": "DE",
           "united kingdom": "GB", "great britain": "GB", "gbr": "GB", "uk": "GB", "australia": "AU", "aus": "AU",
           "netherlands": "NL", "ned": "NL", "switzerland": "CH", "sui": "CH", "belgium": "BE", "bel": "BE", "austria": "AT",
           "aut": "AT", "sweden": "SE", "swe": "SE", "finland": "FI", "fin": "FI", "brazil": "BR", "bra": "BR", "argentina": "AR",
           "arg": "AR", "venezuela": "VE", "ven": "VE", "san marino": "SM", "smr": "SM", "czech republic": "CZ", "cze": "CZ",
           "czechoslovakia": "CS", "tch": "CS", "hungary": "HU", "hun": "HU", "south africa": "ZA", "rsa": "ZA",
           "new zealand": "NZ", "nzl": "NZ", "ireland": "IE", "irl": "IE", "denmark": "DK", "den": "DK", "norway": "NO",
           "nor": "NO", "yugoslavia": "YU", "yug": "YU", "canada": "CA", "can": "CA", "malaysia": "MY", "mas": "MY",
           "indonesia": "ID", "ina": "ID", "portugal": "PT", "por": "PT", "colombia": "CO", "col": "CO", "slovenia": "SI",
           "slo": "SI", "slovakia": "SK", "svk": "SK", "poland": "PL", "pol": "PL", "chile": "CL", "chi": "CL", "mexico": "MX",
           "mex": "MX", "east germany": "DD", "gdr": "DD", "ddr": "DD", "soviet union": "SU", "urs": "SU", "luxembourg": "LU",
           "lux": "LU", "croatia": "HR", "cro": "HR", "greece": "GR", "gre": "GR", "thailand": "TH", "tha": "TH", "china": "CN",
           "chn": "CN", "russia": "RU", "rus": "RU", "rhodesia": "RH", "rho": "RH", "uruguay": "UY", "uru": "UY",
           "liechtenstein": "LI", "lie": "LI", "monaco": "MC", "mon": "MC", "estonia": "EE", "est": "EE", "ukraine": "UA",
           "ukr": "UA", "israel": "IL", "isr": "IL", "turkey": "TR", "tur": "TR", "philippines": "PH", "phi": "PH",
           "socialist federal republic of yugoslavia": "YU", "england": "GB", "scotland": "GB", "wales": "GB",
           "northern ireland": "GB", "iceland": "IS", "isl": "IS", "peru": "PE", "per": "PE", "cuba": "CU", "cub": "CU",
           "korea": "KR", "kor": "KR", "nld": "NL", "deu": "DE", "uk": "GB", "che": "CH", "aut": "AT", "swe": "SE", "fin": "FI", "gbr": "GB", "south korea": "KR", "qatar": "QA", "qat": "QA", "india": "IN", "ind": "IN"}
def iso(n):
    return COUNTRY.get((n or "").strip().lower(), "")

def article_podium(title, cls):
    d = os.path.join(WIKI, "art"); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, re.sub(r"[^A-Za-z0-9]+", "_", title) + ".txt")
    if not os.path.exists(p):
        import urllib.parse, time
        subprocess.run(["curl", "-sS", "-A", UA, "-o", p,
                        "https://en.wikipedia.org/w/index.php?title=" + urllib.parse.quote(title.replace(" ", "_")) + "&action=raw"])
        time.sleep(1)
    return W.infobox_podium(open(p, encoding="utf-8", errors="ignore").read(), cls)

GP_WORDS = [("east german", {"EGER", "DDR"}), ("west german", {"WGER", "GER"}), ("german", {"WGER", "GER"}), ("french", {"FRA"}),
    ("austrian", {"AUT"}), ("nations", {"NAT"}), ("italian", {"NAT", "ITA"}), ("isle of man", {"TT"}), ("dutch", {"NED"}),
    ("belgian", {"BEL"}), ("swedish", {"SWE"}), ("finnish", {"FIN"}), ("czech", {"TCH", "CZE"}), ("yugoslav", {"JUG", "YUG"}),
    ("spanish", {"SPA"}), ("ulster", {"ULST"}), ("venezuela", {"VEN"}), ("british", {"GBR"}), ("san marino", {"RSM"}),
    ("argentin", {"ARG"}), ("japan", {"JPN"}), ("swiss", {"SWI"}), ("hungar", {"HUN"}), ("portug", {"POR"}), ("brazil", {"BRA", "RIO"}),
    ("rio", {"RIO", "BRA"}), ("south africa", {"RSA"}), ("australia", {"AUS"}), ("malaysia", {"MAL"}), ("united states", {"USA"}),
    ("baden", {"BAW"}), ("europe", {"EUR", "CAT"}), ("drg", {"EGER"}), ("imola", {"IMO"}), ("catalan", {"CAT"}), ("madrid", {"MAD"}), ("pacific", {"PAC"}),
    ("valencia", {"VAL"}), ("indonesia", {"INA"}), ("canad", {"CAN"}), ("fim", {"FIM"}), ("vitesse", {"VDU"}), ("le mans", {"VDU"}),
    ("expo", {"POR"}), ("qatar", {"QAT"}), ("chinese", {"CHN"}), ("turkish", {"TUR"}), ("salzburg", {"AUT"})]
def gp_codes(name):
    n = (name or "").lower()
    for w, codes in GP_WORDS:
        if w in n: return codes
    return set()

NOTE_RE = re.compile(r"cancel|\brace\b|^no |abandon|not held|postpon|source|^none$|=", re.I)

TOK = {"ret": "DNF", "nc": "DNF", "dnf": "DNF", "dns": "DNS", "dsq": "DSQ", "dq": "DSQ", "exc": "EXC", "dnq": "DNQ"}

def build(y0, y1):
    races, standings, riders_seen, gindex = [], [], {}, {}
    stats = Counter()
    for y in range(y0, y1 + 1):
        s = season(y)
        if not s: continue
        cats = c(f"/results/categories?seasonUuid={s}") or []
        evs = sorted([e for e in (c(f"/results/events?seasonUuid={s}&isFinished=true") or []) if not e.get("test")], key=lambda e: e["date_start"])
        wt = wiki(y)
        # 各GP記事タイトル（500cc年間順位表の見出しリンク）→ イベント
        art_of, p = {}, 0
        big = "500cc" if y < 2002 else "MotoGP"
        _, bcodes = W.standings(wt, big)
        links = W.header_links(wt, big)
        if len(links) == len(bcodes):
            m = align(bcodes, evs)
            art_of = {eid: links[ci] for eid, ci in m.items()}
        cw = [r for r in W.calendar_winners(wt)
              if any(v[0] and not NOTE_RE.search(v[0]) for k, v in r.items() if k != "_gp")]
        win_of = {}
        used = set()
        for r in cw:
            codes = gp_codes(r.get("_gp", ""))
            ev = next((e for e in evs if e["id"] not in used and e["short_name"] in codes), None)
            if ev: win_of[ev["id"]] = r; used.add(ev["id"])
        if len(win_of) < len(cw) and len(cw) == len(evs):
            win_of = {e["id"]: cw[i] for i, e in enumerate(evs)}   # 名前で対応できない場合は順番で
        for cat in cats:
            cls = CLS.get(cat["name"], cat["name"])
            st = (c(f"/results/standings?seasonUuid={s}&categoryUuid={cat['id']}") or {}).get("classification") or []
            for r in st:
                u = uuid_of(r); riders_seen[u] = r["rider"]
                standings.append(dict(year=y, cls=cls, pos=r.get("position"), uuid=u, name=r["rider"]["full_name"],
                                      nat=(r["rider"].get("country") or {}).get("iso", ""), points=r.get("points"),
                                      maker=(r.get("constructor") or {}).get("name", "")))
            wrows, wcodes = W.standings(wt, cls)
            if not st and wrows:
                # 公式の年間順位データなし → Wikipedia の年間順位表（最終順位・ポイント）
                for wr in wrows:
                    if wr["pos"] and re.match(r"^\d+(\.\d)?$", wr["pts"] or ""):
                        standings.append(dict(year=y, cls=cls, pos=wr["pos"], uuid=None, name=wr["rider"], nat=iso(wr["nat"]),
                                              points=float(wr["pts"]), maker=(wr.get("bike") or "").split(" ")[0], src="wiki"))
            ok_codes = all(len(x) >= 3 for x in wcodes) and len(wcodes) >= 5
            if not ok_codes: wrows, wcodes = [], []
            # Wikipedia列 → イベント の対応（順番に照合）
            col_of = align(wcodes, evs)
            if wcodes and len(col_of) != len(wcodes):
                print("列対応に失敗", y, cls, wcodes, [e["short_name"] for e in evs]); col_of = {}
            yindex = {key(r["rider"]["full_name"]): uuid_of(r) for r in st}
            rnd = 0
            for e in evs:
                ss = [x for x in (c(f"/results/sessions?eventUuid={e['id']}&categoryUuid={cat['id']}") or []) if x.get("type") == "RAC"]
                ss.sort(key=lambda x: x.get("number") or 0)
                cl = c(f"/results/session/{ss[-1]['id']}/classification?test=false") if ss else None
                api = (cl or {}).get("classification") or []
                url = (cl or {}).get("file") or (f"https://resources.motogp.com/files/results/{y}/{cat['name'].replace('™','')}/{e['short_name']}/RAC/classification.pdf" if y >= 1998 else "")
                prow = pdf_rows(url) if url else []
                rows, src = [], ""
                sc = scale(y)
                if api:
                    pby_pos = {q["pos"]: q for q in prow if q["pos"]}
                    for r in api:
                        u = uuid_of(r); riders_seen[u] = r["rider"]
                        pos = r.get("position")
                        q = pby_pos.get(pos) if pos else None
                        if q and surname(q["name"])[:3] != surname(r["rider"]["full_name"])[:3]: q = None
                        if not q:
                            cand = [z for z in prow if surname(z["name"])[:3] == surname(r["rider"]["full_name"])[:3]]
                            q = cand[0] if len(cand) == 1 else None
                        stt = r.get("status") or ""
                        pts = (q["points"] if q and q["points"] else None)
                        if pts is None and pos and sc: pts = sc[pos - 1] if pos <= len(sc) else 0
                        rows.append(dict(pos=pos, uuid=u, name=r["rider"]["full_name"], nat=(r["rider"].get("country") or {}).get("iso", ""),
                                         number=(q or {}).get("number"), team=(q or {}).get("team", ""),
                                         maker=(r.get("constructor") or {}).get("name") or (q or {}).get("moto", ""),
                                         points=pts or 0, status="FIN" if pos else {"NOTSTARTED": "DNS"}.get(stt, "DNF")))
                    src = "api+pdf" if prow else "api"
                elif prow:
                    for q in prow:
                        k = key(q["name"]); u = yindex.get(k)
                        pts = q["points"]
                        if not pts and q["pos"] and sc and not any(z["points"] for z in prow): pts = sc[q["pos"] - 1] if q["pos"] <= len(sc) else 0
                        rows.append(dict(pos=q["pos"], uuid=u, name=riders_seen[u]["full_name"] if u in riders_seen else proper(q["name"]),
                                         nat=q["nation"], number=q["number"], team=q["team"], maker=q["moto"], points=pts, status=q["status"]))
                    src = "pdf"
                elif e["id"] in col_of:
                    ci = col_of[e["id"]]
                    for wr in wrows:
                        v = wr["cells"][ci] if ci < len(wr["cells"]) else ""
                        v = v.strip()
                        if not v: continue
                        m = re.match(r"^(\d+)", v)
                        if m:
                            pos = int(m.group(1)); stt = "FIN"
                        else:
                            stt = TOK.get(v.lower().split()[0] if v else "", None)
                            if not stt: continue
                            pos = None
                        k = key(wr["rider"]); u = yindex.get(k)
                        pts = (sc[pos - 1] if (sc and pos and pos <= len(sc)) else 0)
                        rows.append(dict(pos=pos, uuid=u, name=riders_seen[u]["full_name"] if u in riders_seen else wr["rider"],
                                         nat=(riders_seen[u].get("country") or {}).get("iso", "") if u in riders_seen else iso(wr["nat"]),
                                         number=None, team="", maker=wr.get("bike", "").split(" ")[0] if wr.get("bike") else "",
                                         points=pts, status=stt))
                    rows.sort(key=lambda r: (r["pos"] is None, r["pos"] or 0))
                    src = "wiki"
                if not rows and e["id"] in art_of and (ss or any(n and not NOTE_RE.search(n) for n, _ in article_podium(art_of[e["id"]], cls))):
                    for i, (nm, ctry) in enumerate(article_podium(art_of[e["id"]], cls)):
                        if not nm or NOTE_RE.search(nm): continue
                        u = yindex.get(key(nm)) or gindex.get(key(nm))
                        rows.append(dict(pos=i + 1, uuid=u, name=riders_seen[u]["full_name"] if u in riders_seen else nm,
                                         nat=(riders_seen[u].get("country") or {}).get("iso", "") if u in riders_seen else iso(ctry),
                                         number=None, team="", maker="", points=(sc[i] if sc else 0), status="FIN"))
                    if rows: src = "podium"
                wname = (win_of.get(e["id"], {}).get(cls) or ("", ""))[0]
                if not rows and wname and (ss or y < 1990) and not re.search(r"\brace\b|^no |cancel", wname.lower()):
                    nm, ctry = win_of[e["id"]][cls]
                    u = yindex.get(key(nm))
                    rows.append(dict(pos=1, uuid=u, name=riders_seen[u]["full_name"] if u in riders_seen else nm,
                                     nat=(riders_seen[u].get("country") or {}).get("iso", "") if u in riders_seen else iso(ctry),
                                     number=None, team="", maker="", points=(sc[0] if sc else 0), status="FIN"))
                    src = "winner"
                raced = bool(ss) or bool(rows)
                if not raced: continue
                rnd += 1
                stats[src or "none"] += 1
                races.append(dict(year=y, cls=cls, round=rnd, kind="RAC", gp=e["short_name"], gp_name=e.get("name"),
                                  circuit=(e.get("circuit") or {}).get("name", ""), place="", country=(e.get("country") or {}).get("iso", ""),
                                  date=e.get("date_end") or e.get("date_start"), file=url if prow else "", src=src, rows=rows))
    # 参戦者表（Wikipedia）でチーム名・ゼッケンを補完
    filled = 0
    byyc = defaultdict(list)
    for r in races: byyc[(r["year"], r["cls"])].append(r)
    for (y, cls), rs in byyc.items():
        parts = W.participants(wiki(y), cls, len(rs))
        pk = defaultdict(list)
        for pp in parts: pk[key(pp["rider"])].append(pp)
        for r in rs:
            for row in r["rows"]:
                if row.get("team") and row.get("number"): continue
                cand = [pp for pp in pk.get(key(row["name"]), []) if r["round"] in pp["rounds"]] or pk.get(key(row["name"]), [])
                if len(cand) >= 1:
                    pp = cand[0]
                    if not row.get("team") and pp["team"]: row["team"] = pp["team"]; row["team_src"] = "wiki"; filled += 1
                    if not row.get("number") and pp["number"]: row["number"] = pp["number"]
                    if not row.get("maker") and pp["constructor"]: row["maker"] = pp["constructor"]
    print("チーム名をWikipedia参戦者表で補完", filled)
    json.dump(dict(races=races, standings=standings,
                   riders={u: dict(name=v["full_name"], nat=(v.get("country") or {}).get("iso", "")) for u, v in riders_seen.items()}),
              open(f"era_{y0}_{y1}.json", "w"), ensure_ascii=False)
    print("races", len(races), "standings", len(standings), dict(stats))
    print("no data", [(r["year"], r["cls"], r["gp"]) for r in races if not r["rows"]])

if __name__ == "__main__":
    build(int(sys.argv[1]), int(sys.argv[2]))
