# Collect candidate clips from Mixkit and Coverr per shot; write JSON + thumbnails.
import json, re, sys, os, urllib.request, urllib.parse, html, concurrent.futures as cf
OUT = sys.argv[1]
UA = {"User-Agent": "Mozilla/5.0"}
def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()
SHOTS = {
 "s1_window": {"mixkit": ["rain", "window", "raindrops"], "coverr": ["rain window night", "raindrops window", "rainy window city lights"]},
 "s2_busstop": {"mixkit": ["night-city", "street", "man-walking"], "coverr": ["bus stop rain", "man walking rain night", "rainy night street", "man in the rain"]},
 "s3_puddle": {"mixkit": ["puddle", "drops", "water-drops"], "coverr": ["puddle rain", "raindrops puddle", "rain drops water surface"]},
 "s4_umbrella": {"mixkit": ["umbrella"], "coverr": ["umbrella rain", "umbrella night", "two people umbrella"]},
 "s5_tea": {"mixkit": ["tea", "cup", "hot-drink"], "coverr": ["tea cup", "pouring tea", "hands holding mug", "cup of tea rain"]},
 "s6_phone": {"mixkit": ["smartphone", "phone"], "coverr": ["phone on table", "phone ringing", "phone notification"]},
 "s7_door": {"mixkit": ["door"], "coverr": ["door opening", "open door light", "front door rain"]},
 "x_city": {"mixkit": ["city-at-night"], "coverr": ["manchester", "rainy city night", "red brick building rain"]},
 "x_overlay": {"mixkit": ["rain-drops"], "coverr": ["rain black background", "rain overlay"]},
}
def mixkit(tag):
    items = []
    for url in (f"https://mixkit.co/free-stock-video/{tag}/", f"https://mixkit.co/free-stock-video/discover/{tag}/"):
        try:
            h = get(url).decode("utf-8", "ignore")
        except Exception as e:
            continue
        # item blocks: link slug + id
        for m in re.finditer(r'href="/free-stock-video/([a-z0-9-]+)-(\d+)/"', h):
            slug, vid = m.group(1), m.group(2)
            items.append({"src": "mixkit", "id": vid, "title": slug.replace("-", " "),
                          "page": f"https://mixkit.co/free-stock-video/{slug}-{vid}/",
                          "thumb": f"https://assets.mixkit.co/videos/{vid}/{vid}-thumb-360-0.jpg",
                          "preview": f"https://assets.mixkit.co/videos/{vid}/{vid}-360.mp4"})
        if items: break
    return items
def coverr(q):
    try:
        h = get("https://coverr.co/s?q=" + urllib.parse.quote(q)).decode("utf-8", "ignore")
    except Exception:
        return []
    items = []
    for m in re.finditer(r'"poster":"(https://cdn\.coverr\.co/videos/([^/]+)/thumbnail\?width=1920)"', h):
        slug = m.group(2)
        items.append({"src": "coverr", "id": slug, "title": slug.replace("coverr-", "").replace("-", " "),
                      "page": f"https://coverr.co/videos/{slug}",
                      "thumb": f"https://cdn.coverr.co/videos/{slug}/thumbnail?width=640",
                      "preview": f"https://cdn.coverr.co/videos/{slug}/360p.mp4",
                      "full": f"https://cdn.coverr.co/videos/{slug}/1080p.mp4"})
    return items
res = {}
for shot, q in SHOTS.items():
    seen, lst = set(), []
    for t in q["mixkit"]:
        for it in mixkit(t):
            k = it["src"] + it["id"]
            if k not in seen: seen.add(k); lst.append(it)
    for t in q["coverr"]:
        for it in coverr(t):
            k = it["src"] + it["id"]
            if k not in seen: seen.add(k); lst.append(it)
    res[shot] = lst
    print(shot, len(lst), flush=True)
json.dump(res, open(os.path.join(OUT, "candidates.json"), "w"), indent=1)
# thumbnails
os.makedirs(os.path.join(OUT, "thumbs"), exist_ok=True)
jobs = []
for shot, lst in res.items():
    for i, it in enumerate(lst):
        fn = os.path.join(OUT, "thumbs", f"{shot}__{it['src']}__{re.sub(r'[^A-Za-z0-9_-]', '_', it['id'])[:60]}.jpg")
        it["thumb_file"] = fn
        jobs.append((it["thumb"], fn))
def dl(a):
    u, fn = a
    if os.path.exists(fn): return
    try: open(fn, "wb").write(get(u, 30))
    except Exception as e: pass
with cf.ThreadPoolExecutor(12) as ex: list(ex.map(dl, jobs))
json.dump(res, open(os.path.join(OUT, "candidates.json"), "w"), indent=1)
print("done")
