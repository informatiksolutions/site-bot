# Site-Bot fuer informatik-solutions.ch (Open Source)

## Schnellstart (lokal)
```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Crawlen
python crawler/crawler.py

# 2) Embeddings + Indizes
python index/build_embeddings.py
python index/index_faiss.py
python index/index_typesense.py

# 3) API starten
uvicorn api.server:app --reload --port 8000
```

## Widget einbinden (WordPress)
Lade `web/widget.js` und `web/styles.css` nach `wp-content/uploads/sitebot/` (oder Child-Theme). 
Füge kurz vor `</body>` ein:
```html
<link rel="stylesheet" href="/wp-content/uploads/sitebot/styles.css" />
<script>window.SITEBOT_API='https://YOUR-API-DOMAIN';</script>
<script src="/wp-content/uploads/sitebot/widget.js" defer></script>
```

Alternativ per `functions.php` (Child-Theme) einhaengen – siehe Anleitung in der ZIP-README.
