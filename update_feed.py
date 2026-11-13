"""Genera auto.json con tus últimos videos de YouTube y publicaciones/Reels de Instagram.
Solo librería estándar. Instagram es opcional: define IG_USER_ID e IG_TOKEN.
Guarda también el texto completo de cada publicación para su página de noticia."""
import json, os, urllib.request, urllib.parse, xml.etree.ElementTree as ET

def split_text(text):
    """Devuelve (titulo, resto de párrafos) sin líneas que solo tengan #hashtags o @menciones."""
    lines = [l.strip() for l in (text or "").split("\n")]
    lines = [l for l in lines if l]
    if not lines:
        return "", []
    rest = [l for l in lines[1:] if not all(w[0] in "#@" for w in l.split())]
    return lines[0], rest

def extra(rest):
    return {"summary": rest[0][:160], "body": [{"p": rest}]} if rest else {}

out = []
# --- YouTube (RSS público) ---
CH = "UC3G_ykLv-EAS0w-AkCmrnIQ"
NS = {"a": "http://www.w3.org/2005/Atom", "y": "http://www.youtube.com/xml/schemas/2015", "m": "http://search.yahoo.com/mrss/"}
try:
    root = ET.fromstring(urllib.request.urlopen(f"https://www.youtube.com/feeds/videos.xml?channel_id={CH}", timeout=20).read())
    for e in root.findall("a:entry", NS)[:8]:
        v = e.find("y:videoId", NS).text; d = e.find("a:published", NS).text
        desc = e.find("m:group/m:description", NS)
        _, rest = split_text(desc.text if desc is not None else "")
        it = {"id": "yt-" + v, "type": "video", "source": "youtube", "category": "Video",
              "title": e.find("a:title", NS).text, "date": d[:10], "ts": d[:10],
              "url": f"https://www.youtube.com/shorts/{v}", "thumb": f"https://i.ytimg.com/vi/{v}/hqdefault.jpg"}
        it.update(extra([l for l in rest if "http" not in l]))
        out.append(it)
except Exception as ex:
    print("YouTube falló:", ex)
# --- Instagram (Graph API) ---
uid, tok = os.getenv("IG_USER_ID"), os.getenv("IG_TOKEN")
if uid and tok:
    try:
        q = urllib.parse.urlencode({"fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp", "limit": 25, "access_token": tok})
        data = json.load(urllib.request.urlopen(f"https://graph.facebook.com/v27.0/{uid}/media?{q}", timeout=20))
        os.makedirs("assets/auto", exist_ok=True)
        for m in data.get("data", []):
            if m["media_type"] == "VIDEO":  # los Reels/videos de Instagram se ignoran: los videos salen solo de YouTube
                continue
            if sum(1 for o in out if o["source"] == "instagram") >= 8:
                break
            vid = False
            src = m.get("media_url")
            local = ""
            if src:  # las URLs de Instagram caducan: se guarda copia local
                local = f"assets/auto/{m['id']}.jpg"
                urllib.request.urlretrieve(src, local)
            title, rest = split_text(m.get("caption") or "Publicación de Instagram")
            it = {"id": "ig-" + m["id"], "type": "video" if vid else "post", "source": "instagram",
                  "category": "Reel" if vid else "Instagram", "title": title[:120], "date": m["timestamp"][:10],
                  "ts": m["timestamp"][:10], "url": m["permalink"], "image": local}
            it.update(extra(rest))
            out.append(it)
    except Exception as ex:
        print("Instagram falló:", ex)
json.dump(out, open("auto.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(len(out), "elementos guardados en auto.json")
