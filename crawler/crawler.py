import os, json, hashlib
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from .extract import html_to_text

BASE_URL = os.getenv("BASE_URL", "https://www.informatik-solutions.ch")
OUT_DIR = os.path.join("data", "pages_raw")
CHUNKS_PATH = os.path.join("data", "chunks.jsonl")
ALLOW_DOMAINS = {urlparse(BASE_URL).netloc}

def fetch(url):
    with httpx.Client(timeout=20, follow_redirects=True, headers={"User-Agent":"site-bot/1.0"}) as c:
        r = c.get(url)
        r.raise_for_status()
        return r.text

def discover(start):
    seen, q = set([start]), [start]
    urls = []
    while q:
        u = q.pop(0)
        try:
            html = fetch(u)
        except Exception:
            continue
        urls.append(u)
        soup = BeautifulSoup(html, "lxml")
        for a in soup.find_all("a", href=True):
            href = urljoin(u, a["href"])
            pr = urlparse(href)
            if pr.netloc in ALLOW_DOMAINS and pr.scheme in {"http","https"}:
                if any(x in pr.path.lower() for x in ["/wp-admin","/feed"]):
                    continue
                if href not in seen:
                    seen.add(href)
                    q.append(href)
    return list(dict.fromkeys(urls))

def chunk(text, url, title, size=700, overlap=120):
    words = text.split()
    i = 0
    while i < len(words):
        part = " ".join(words[i:i+size])
        yield {
            "id": hashlib.md5(f"{url}-{i}".encode()).hexdigest(),
            "url": url,
            "title": title,
            "content": part,
        }
        i += size - overlap

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    urls = discover(BASE_URL)
    print(f"Gefundene URLs: {len(urls)}")
    with open(CHUNKS_PATH, "w", encoding="utf-8") as out:
        for u in urls:
            try:
                html = fetch(u)
                parsed = html_to_text(html)
                for ch in chunk(parsed["markdown"], u, parsed["title"]):
                    out.write(json.dumps(ch, ensure_ascii=False) + "\n")
            except Exception as e:
                print("Fehler:", u, e)

if __name__ == "__main__":
    main()
