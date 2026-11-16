#!/usr/bin/env python3
"""Static multilingual site builder.

content/site.json  : site-wide facts (domain, languages, pages, company data)
content/<lang>.json: every visible string for that language
templates/*.html   : Jinja2 templates (base.html + one per page)
assets/            : copied as-is to dist/assets

Output: dist/<lang>/<page>/index.html (+ dist/index.html language chooser),
sitemap.xml with hreflang alternates, robots.txt, 404.html, CNAME.
"""
import json, shutil, sys, datetime, pathlib
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / "dist"


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def page_path(lang, slug):
    return f"/{lang}/" if slug == "home" else f"/{lang}/{slug}/"


def main():
    site = load("content/site.json")
    langs = site["languages"]
    strings = {l: load(f"content/{l}.json") for l in langs}
    # every language must carry the same keys as the default language
    def keys(d, pre=""):
        out = set()
        for k, v in d.items():
            out.add(pre + k)
            if isinstance(v, dict):
                out |= keys(v, pre + k + ".")
        return out
    base_keys = keys(strings[langs[0]])
    for l in langs[1:]:
        missing = base_keys - keys(strings[l])
        if missing:
            sys.exit(f"[{l}] missing keys: {sorted(missing)[:20]}")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "assets", DIST / "assets")

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      undefined=StrictUndefined, autoescape=True,
                      trim_blocks=True, lstrip_blocks=True)
    base_url = site["base_url"].rstrip("/")
    year = datetime.date.today().year
    urls = []
    for slug in site["pages"]:
        for lang in langs:
            alt = {l: base_url + page_path(l, slug) for l in langs}
            ctx = dict(site=site, t=strings[lang], lang=lang, langs=langs,
                       slug=slug, alt=alt, canonical=alt[lang],
                       path=lambda s, l=lang: page_path(l, s),
                       year=year, base_url=base_url)
            html = env.get_template(f"{slug}.html").render(**ctx)
            out = DIST / page_path(lang, slug).strip("/") / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8")
        urls.append(slug)

    # language chooser at / (redirects by browser language, links for crawlers)
    root = env.get_template("root.html").render(site=site, langs=langs, strings=strings,
                                                base_url=base_url,
                                                alt={l: base_url + page_path(l, "home") for l in langs})
    (DIST / "index.html").write_text(root, encoding="utf-8")
    nf = env.get_template("404.html").render(site=site, langs=langs, strings=strings)
    (DIST / "404.html").write_text(nf, encoding="utf-8")

    # sitemap with hreflang alternates
    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for slug in urls:
        for lang in langs:
            sm.append(f"  <url><loc>{base_url}{page_path(lang, slug)}</loc><lastmod>{today}</lastmod>")
            for l in langs:
                sm.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{base_url}{page_path(l, slug)}"/>')
            sm.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{base_url}{page_path(langs[0], slug)}"/>')
            sm.append("  </url>")
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n", encoding="utf-8")
    if site.get("cname"):
        (DIST / "CNAME").write_text(site["cname"] + "\n", encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"built {len(urls)} pages x {len(langs)} languages -> {DIST}")


if __name__ == "__main__":
    main()
