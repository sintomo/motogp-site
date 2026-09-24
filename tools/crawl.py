"""MotoGP公式リザルトAPIの取得（キャッシュ付き）
使い方: python3 crawl.py 2002 2009   … 指定年範囲を取得
"""
import json, os, sys, time, hashlib, subprocess
B = "https://api.motogp.pulselive.com/motogp/v1"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE, exist_ok=True)

def get(path):
    fn = os.path.join(CACHE, hashlib.md5(path.encode()).hexdigest() + ".json")
    if os.path.exists(fn):
        with open(fn) as f: return json.load(f)
    for i in range(4):
        r = subprocess.run(["curl", "-sS", "--max-time", "40", B + path], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            with open(fn, "w") as f: json.dump(d, f)
            time.sleep(0.15)
            return d
        except Exception:
            time.sleep(2 + i * 3)
    print("FAIL", path, r.stdout[:200], r.stderr[:200], flush=True)
    return None

def season_ids():
    return {x["year"]: x["id"] for x in get("/results/seasons")}

def crawl(y0, y1):
    S = season_ids()
    riders = set()
    for y in range(y0, y1 + 1):
        s = S.get(y)
        if not s: continue
        cats = get(f"/results/categories?seasonUuid={s}") or []
        evs = get(f"/results/events?seasonUuid={s}&isFinished=true") or []
        evs = [e for e in evs if not e.get("test")]
        n = 0
        for c in cats:
            st = get(f"/results/standings?seasonUuid={s}&categoryUuid={c['id']}")
            for r in (st or {}).get("classification", []) or []:
                riders.add(r["rider"].get("riders_api_uuid") or r["rider"].get("riders_id"))
            for e in evs:
                ss = get(f"/results/sessions?eventUuid={e['id']}&categoryUuid={c['id']}") or []
                for x in ss:
                    if x.get("type") in ("RAC", "SPR"):
                        cl = get(f"/results/session/{x['id']}/classification?test=false")
                        n += 1
                        for r in (cl or {}).get("classification", []) or []:
                            riders.add(r["rider"].get("riders_api_uuid") or r["rider"].get("riders_id"))
        print(y, "cats", len(cats), "events", len(evs), "race sessions", n, flush=True)
    riders.discard(None)
    for i, u in enumerate(sorted(riders)):
        get(f"/riders/{u}")
    print("riders", len(riders), "done", flush=True)

if __name__ == "__main__":
    crawl(int(sys.argv[1]), int(sys.argv[2]))
