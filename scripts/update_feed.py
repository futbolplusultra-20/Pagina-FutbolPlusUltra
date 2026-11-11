"""Genera auto.json con tus últimos videos de YouTube y publicaciones/Reels de Instagram.
Solo librería estándar. Uso:  python scripts/update_feed.py
Instagram es opcional: define IG_USER_ID e IG_TOKEN (API de Instagram de Meta, cuenta profesional).
Sin red no se ha podido probar; revisa los campos con la documentación de Meta."""
import json, os, urllib.request, urllib.parse, xml.etree.ElementTree as ET
out = []
# --- YouTube (RSS público) ---
CH = "UC3G_ykLv-EAS0w-AkCmrnIQ"
NS = {"a": "http://www.w3.org/2005/Atom", "y": "http://www.youtube.com/xml/schemas/2015"}
try:
    root = ET.fromstring(urllib.request.urlopen(f"https://www.youtube.com/feeds/videos.xml?channel_id={CH}", timeout=20).read())
    for e in root.findall("a:entry", NS)[:8]:
        v = e.find("y:videoId", NS).text; d = e.find("a:published", NS).text
        out.append({"id": "yt-" + v, "type": "video", "source": "youtube", "category": "Video",
                    "title": e.find("a:title", NS).text, "date": d[:10], "ts": d[:10],
                    "url": f"https://www.youtube.com/shorts/{v}", "thumb": f"https://i.ytimg.com/vi/{v}/hqdefault.jpg"})
except Exception as ex:
    print("YouTube falló:", ex)
# --- Instagram (Graph API) ---
uid, tok = os.getenv("IG_USER_ID"), os.getenv("IG_TOKEN")
if uid and tok:
    try:
        q = urllib.parse.urlencode({"fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp", "limit": 8, "access_token": tok})
        data = json.load(urllib.request.urlopen(f"https://graph.facebook.com/v21.0/{uid}/media?{q}", timeout=20))
        os.makedirs("assets/auto", exist_ok=True)
        for m in data.get("data", []):
            vid = m["media_type"] == "VIDEO"
            src = m.get("thumbnail_url") if vid else m.get("media_url")
            local = ""
            if src:  # las URLs de Instagram caducan: se guarda copia local
                local = f"assets/auto/{m['id']}.jpg"
                urllib.request.urlretrieve(src, local)
            cap = (m.get("caption") or "Publicación de Instagram").strip().split("\n")[0][:90]
            out.append({"id": "ig-" + m["id"], "type": "video" if vid else "post", "source": "instagram",
                        "category": "Reel" if vid else "Instagram", "title": cap, "date": m["timestamp"][:10],
                        "ts": m["timestamp"][:10], "url": m["permalink"], "image": local})
    except Exception as ex:
        print("Instagram falló:", ex)
json.dump(out, open("auto.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(len(out), "elementos guardados en auto.json")
