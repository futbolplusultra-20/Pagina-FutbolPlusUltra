# FutbolPlusUltra · web estática

Archivos: `index.html`, `noticia.html`, `news.json` (tus noticias a mano), `auto.json` (lo genera el script), `assets/`.

## Sección Noticias
Muestra publicaciones y videos juntos, ordenados por fecha, con filtros Todo / Publicaciones / Videos.
- `news.json`: noticias que escribes tú (con página de detalle si llevan `body`). Campos: `id`, `type` (post|video), `source` (x|instagram|youtube|tiktok), `category`, `title`, `highlight`, `date`, `ts` (AAAA-MM-DD), `image`, `url`, `summary`, `body`, `sources`.
- `auto.json`: lo rellena `python scripts/update_feed.py` con tus videos de YouTube (RSS público) y, si configuras el token, tus publicaciones y Reels de Instagram.
- Las tarjetas de ejemplo (`demo`) se borran de `news.json`.

## Probar
Súbela a Netlify, Cloudflare Pages o GitHub Pages. Con doble clic no cargan los JSON; en local usa `python -m http.server`.

## Instagram
Cuenta profesional + app en developers.facebook.com + token. Define IG_USER_ID e IG_TOKEN. El token caduca (~60 días) y hay que renovarlo.

## X
Sin API de pago no se puede leer. Añade tus publicaciones de X a `news.json` a mano.
