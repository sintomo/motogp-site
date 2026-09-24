"""決勝リザルトPDF（公式）を取得して text 化。使い方: python3 pdfget.py 2002 2009"""
import os, sys, subprocess, time, hashlib
from api import c, season
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf")
os.makedirs(D, exist_ok=True)

def local(url):
    return os.path.join(D, hashlib.md5(url.encode()).hexdigest())

def fetch(url):
    p = local(url)
    if os.path.exists(p + ".txt"): return p + ".txt"
    for i in range(3):
        subprocess.run(["curl", "-sS", "-L", "--max-time", "60", "-o", p + ".pdf", url])
        r = subprocess.run(["pdftotext", "-layout", p + ".pdf", p + ".txt"], capture_output=True)
        if r.returncode == 0:
            os.remove(p + ".pdf"); time.sleep(0.2); return p + ".txt"
        time.sleep(3)
    print("FAIL", url, flush=True)

def urls(y):
    s = season(y)
    cats = c(f"/results/categories?seasonUuid={s}") or []
    evs = [e for e in (c(f"/results/events?seasonUuid={s}&isFinished=true") or []) if not e.get("test")]
    for cat in cats:
        for e in evs:
            for x in c(f"/results/sessions?eventUuid={e['id']}&categoryUuid={cat['id']}") or []:
                if x.get("type") in ("RAC", "SPR"):
                    cl = c(f"/results/session/{x['id']}/classification?test=false") or {}
                    if cl.get("file") and (not MISSING_ONLY or not cl.get("classification")): yield cl["file"]

MISSING_ONLY = "--missing" in sys.argv
if __name__ == "__main__":
    for y in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
        n = 0
        for u in urls(y):
            fetch(u); n += 1
        print(y, "pdf", n, flush=True)
