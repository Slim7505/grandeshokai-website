#!/usr/bin/env python3
"""Checks run after build.py (locally and in CI). Exit 1 on any failure.

- every internal href/src resolves to a file in dist/
- every page has <title>, meta description, canonical, hreflang for every language, one <h1>
- every <img> has a non-empty alt
- html lang attribute matches the folder
"""
import json, pathlib, re, sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / "dist"
site = json.loads((ROOT / "content/site.json").read_text(encoding="utf-8"))
langs = site["languages"]


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.imgs, self.h1, self.title = [], [], 0, False
        self.meta_desc = self.canonical = False
        self.hreflang = set()
        self.lang = None

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("img", "script") and a.get("src"):
            self.links.append(a["src"])
        if tag == "img":
            self.imgs.append(a.get("alt"))
        if tag == "link":
            if a.get("rel") == "stylesheet" or a.get("rel") == "icon":
                self.links.append(a.get("href", ""))
            if a.get("rel") == "canonical":
                self.canonical = True
            if a.get("rel") == "alternate" and a.get("hreflang"):
                self.hreflang.add(a["hreflang"])
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.meta_desc = True
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.title = True


def resolve(page, href):
    href = href.split("#")[0].split("?")[0]
    if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
        return True
    if href.startswith("/"):
        target = DIST / href.lstrip("/")
    else:
        target = (page.parent / href).resolve()
    if target.is_dir() or href.endswith("/"):
        target = target / "index.html"
    return target.exists()


errors = []
pages = sorted(DIST.rglob("*.html"))
for page in pages:
    p = P()
    p.feed(page.read_text(encoding="utf-8"))
    rel = page.relative_to(DIST)
    top = rel.parts[0] if len(rel.parts) > 1 else None
    for href in p.links:
        if not resolve(page, href):
            errors.append(f"{rel}: broken link {href}")
    for alt in p.imgs:
        if not alt:
            errors.append(f"{rel}: <img> without alt")
    if top in langs:
        if p.lang != top:
            errors.append(f"{rel}: html lang={p.lang} expected {top}")
        if p.h1 != 1:
            errors.append(f"{rel}: {p.h1} <h1> (expected 1)")
        if not (p.title and p.meta_desc and p.canonical):
            errors.append(f"{rel}: missing title/description/canonical")
        if not set(langs) <= p.hreflang:
            errors.append(f"{rel}: hreflang {sorted(p.hreflang)} missing some of {langs}")

print(f"checked {len(pages)} pages")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print("OK")
