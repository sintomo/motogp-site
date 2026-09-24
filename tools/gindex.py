"""キャッシュ全体から ライダー名→API uuid 索引と、uuid→ライダー詳細 を作る"""
import json, os, glob
from era import key
from api import CACHE
def build():
    idx, info = {}, {}
    for f in glob.glob(os.path.join(CACHE, "*.json")):
        try: d = json.load(open(f))
        except Exception: continue
        if isinstance(d, dict) and isinstance(d.get("classification"), list):
            for r in d["classification"]:
                x = r.get("rider") or {}
                u = x.get("riders_api_uuid") or x.get("riders_id") or x.get("id")
                if u and x.get("full_name"):
                    idx.setdefault(key(x["full_name"]), set()).add(u)
        elif isinstance(d, dict) and "birth_date" in d and d.get("id"):
            info[d["id"]] = d
    return idx, info
