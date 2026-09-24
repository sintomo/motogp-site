"""公式API＋公式PDFから、指定年範囲の レース結果・年間順位 を正規化して era_Y0_Y1.json に出力
使い方: python3 era.py 2002 2009
"""
import json, os, re, sys, unicodedata
from collections import defaultdict, Counter
from api import c, year_data, rider
from pdfparse import parse
from pdfget import local

CLS = {"MotoGP™": "MotoGP", "MotoGP": "MotoGP", "500cc": "500cc", "350cc": "350cc", "250cc": "250cc", "125cc": "125cc",
       "Moto2™": "Moto2", "Moto2": "Moto2", "Moto3™": "Moto3", "Moto3": "Moto3", "50cc": "50cc", "80cc": "80cc",
       "MotoE™": "MotoE", "MotoE": "MotoE", "Sidecar": "Sidecar", "350cc Sidecar": "Sidecar", "500cc Sidecar": "Sidecar"}

def fold(s):
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)).lower()

SUFFIX = {"jr", "jr.", "sr", "ii", "iii"}
def key(name):
    t = [x for x in re.split(r"[\s]+", fold(name).replace("'", "").strip()) if x and x.strip(".") not in SUFFIX]
    if not t: return ""
    return t[-1].replace("-", "") + "|" + t[0][0]

def surname(name):
    t = [x for x in fold(name).split() if x.strip(".") not in SUFFIX]
    return t[-1].replace("-", "").replace("'", "") if t else ""

def proper(name):
    out = []
    for tk in name.split():
        if len(tk) > 1 and tk.upper() == tk:
            tk = "-".join(p[:1] + p[1:].lower() for p in tk.split("-"))
        elif re.match(r"^Mc[A-Z]{2,}$", tk):
            tk = "Mc" + tk[2].upper() + tk[3:].lower()
        out.append(tk)
    return " ".join(out)

SCALE_1993 = [25, 20, 16, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
def scale_points(year, pos, kind="RAC"):
    """PDFがなくポイント欄がない場合のみ使用（規則の配点表から算出）"""
    if not pos or kind != "RAC": return 0
    if year >= 1993: return SCALE_1993[pos - 1] if pos <= 15 else 0
    return None   # 1992年以前は未対応

def uuid_of(r):
    x = r["rider"]
    return x.get("riders_api_uuid") or x.get("riders_id") or x.get("id")

def build(y0, y1):
    races, standings, riders_seen = [], [], {}
    gindex = {}   # key -> uuid（全年）
    # まず全年のAPI名から索引
    data = {}
    for y in range(y0, y1 + 1):
        d = year_data(y)
        if d is None:
            print("未取得", y); continue
        data[y] = d
        for cname, v in d.items():
            for r in v["standings"]:
                u = uuid_of(r); riders_seen[u] = r["rider"]; gindex.setdefault(key(r["rider"]["full_name"]), u)
            for e, x, cl in v["races"]:
                for r in cl.get("classification") or []:
                    u = uuid_of(r); riders_seen[u] = r["rider"]; gindex.setdefault(key(r["rider"]["full_name"]), u)
    for y, d in data.items():
        for cname, v in d.items():
            cls = CLS.get(cname, cname)
            yindex = {}
            for r in v["standings"]:
                yindex.setdefault(key(r["rider"]["full_name"]), uuid_of(r))
            for e, x, cl in v["races"]:
                for r in cl.get("classification") or []:
                    yindex.setdefault(key(r["rider"]["full_name"]), uuid_of(r))
            # 同一イベント複数決勝 → 番号が大きい方（最終結果）を採用
            by_ev = defaultdict(list)
            for e, x, cl in v["races"]:
                by_ev[e["id"]].append((e, x, cl))
            rnd = 0
            evs = sorted(by_ev.values(), key=lambda L: L[0][0]["date_start"])
            for L in evs:
                spr = [t for t in L if t[1]["type"] == "SPR"]
                rac = [t for t in L if t[1]["type"] == "RAC"]
                rac.sort(key=lambda t: t[1].get("number") or 0)
                rnd += 1
                if any(t[1].get("number") == 1 for t in rac):
                    # 1イベント2レース制（MotoEなど）→ レース1・レース2 を別々に
                    r1 = [t for t in rac if t[1].get("number") == 1]
                    r2 = [t for t in rac if t[1].get("number") == 2]
                    plan = [("RAC", r1[-1])] + ([("RAC2", r2[-1])] if r2 else [])
                else:
                    # 赤旗中断で2パートの場合は番号の大きい方（最終結果）
                    plan = [("RAC", rac[-1])] if rac else []
                for kind, t in ([("SPR", spr[-1])] if spr else []) + plan:
                    e, x, cl = t
                    api = cl.get("classification") or []
                    pdfrows = []
                    if cl.get("file") and os.path.exists(local(cl["file"]) + ".txt"):
                        pdfrows = parse(open(local(cl["file"]) + ".txt", errors="ignore").read())
                    rows = []
                    if api:
                        # APIを主、PDFでチーム・ゼッケン・ポイントを補完
                        pby_pos = {p["pos"]: p for p in pdfrows if p["pos"]}
                        pby_sn = defaultdict(list)
                        for p in pdfrows: pby_sn[surname(p["name"])].append(p)
                        for r in api:
                            pos = r.get("position")
                            p = pby_pos.get(pos) if pos else None
                            if p and surname(p["name"])[:3] != surname(r["rider"]["full_name"])[:3]: p = None
                            if not p:
                                sn = surname(r["rider"]["full_name"])
                                cand = pby_sn.get(sn) or [q for k2, v2 in pby_sn.items() if k2[:3] == sn[:3] for q in v2]
                                p = cand[0] if len(cand) == 1 else None
                            st = r.get("status") or ""
                            rows.append(dict(pos=pos, uuid=uuid_of(r), name=r["rider"]["full_name"],
                                             nat=(r["rider"].get("country") or {}).get("iso", ""),
                                             number=(p or {}).get("number") or r["rider"].get("number"),
                                             team=(p or {}).get("team") or ((r.get("team") or {}).get("name") or ""),
                                             maker=(r.get("constructor") or {}).get("name") or (p or {}).get("moto", ""),
                                             points=(p["points"] if p else None) if (p and p["points"]) else (r.get("points") or 0),
                                             status="FIN" if pos else ({"NOTSTARTED": "DNS", "NOTFINISHFIRST": "DNF", "OUTSTND": "DNF"}.get(st, "DNF")),
                                             src="api+pdf" if p else "api"))
                        if not pdfrows:
                            for rr in rows:
                                if not rr["points"] and rr["pos"]:
                                    sp = scale_points(y, rr["pos"], x["type"])
                                    if sp: rr["points"] = sp; rr["src"] = "api+scale"
                    elif pdfrows:
                        for p in pdfrows:
                            k = key(p["name"])
                            u = yindex.get(k) or gindex.get(k)
                            rows.append(dict(pos=p["pos"], uuid=u, name=proper(p["name"]) if not u else riders_seen[u]["full_name"],
                                             nat=p["nation"], number=p["number"], team=p["team"], maker=p["moto"],
                                             points=p["points"], status=p["status"], src="pdf"))
                    races.append(dict(year=y, cls=cls, round=rnd, kind=kind, gp=e["short_name"], gp_name=e.get("name"),
                                      circuit=(e.get("circuit") or {}).get("name", ""), place=(e.get("circuit") or {}).get("place", ""),
                                      country=(e.get("country") or {}).get("iso", ""), date=e.get("date_end") or e.get("date_start"),
                                      file=cl.get("file"), rows=rows))
            for r in v["standings"]:
                standings.append(dict(year=y, cls=cls, pos=r.get("position"), uuid=uuid_of(r), name=r["rider"]["full_name"],
                                      nat=(r["rider"].get("country") or {}).get("iso", ""), points=r.get("points"),
                                      maker=(r.get("constructor") or {}).get("name", "")))
    out = dict(races=races, standings=standings,
               riders={u: dict(name=v["full_name"], nat=(v.get("country") or {}).get("iso", "")) for u, v in riders_seen.items()})
    json.dump(out, open(f"era_{y0}_{y1}.json", "w"), ensure_ascii=False)
    n = Counter((r["year"], r["cls"]) for r in races)
    print("races", len(races), "standings", len(standings), "riders", len(riders_seen))
    print("rows without data", [(r["year"], r["cls"], r["gp"]) for r in races if not r["rows"]])
    print("pdf rows unmatched", sum(1 for r in races for x in r["rows"] if not x["uuid"]))

if __name__ == "__main__":
    build(int(sys.argv[1]), int(sys.argv[2]))
