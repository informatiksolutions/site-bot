from bs4 import BeautifulSoup
from markdownify import markdownify
from readability import Document

def html_to_text(html: str) -> dict:
    doc = Document(html)
    title = (doc.short_title() or "").strip()
    content_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(content_html, "lxml")
    # Entferne Navigation/Fusszeilen
    for sel in ["header", "nav", "footer", ".site-header", ".site-footer", ".menu", ".sidebar"]:
        for el in soup.select(sel):
            el.decompose()
    text_md = markdownify(str(soup))
    return {"title": title, "markdown": text_md}
