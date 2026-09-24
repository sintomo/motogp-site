"""キャッシュ済み公式データの読み出し（ネット接続しない）"""
import json, os, hashlib
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

def c(path):
    fn = os.path.join(CACHE, hashlib.md5(path.encode()).hexdigest() + ".json")
    if not os.path.exists(fn): return None
    with open(fn) as f: return json.load(f)

def season(y):
    S = {x["year"]: x["id"] for x in c("/results/seasons")}
    return S.get(y)

def year_data(y):
    """{class_name: {'standings': [...], 'races': [(event, session, classification_json)]}}"""
    s = season(y)
    cats = c(f"/results/categories?seasonUuid={s}") or []
    evs = [e for e in (c(f"/results/events?seasonUuid={s}&isFinished=true") or []) if not e.get("test")]
    evs.sort(key=lambda e: e["date_start"])
    out = {}
    for cat in cats:
        st = c(f"/results/standings?seasonUuid={s}&categoryUuid={cat['id']}")
        races = []
        for e in evs:
            ss = c(f"/results/sessions?eventUuid={e['id']}&categoryUuid={cat['id']}")
            if ss is None:
                return None  # 未取得
            for x in ss:
                if x.get("type") in ("RAC", "SPR"):
                    cl = c(f"/results/session/{x['id']}/classification?test=false")
                    if cl is None: return None
                    races.append((e, x, cl))
        out[cat["name"]] = {"standings": (st or {}).get("classification") or [], "races": races}
    return out

def rider(uuid):
    return c(f"/riders/{uuid}")
