# grandeshokai.com — Grande Shokai Co., Ltd.

The corporate website for グランデ商会株式会社 (Grande Shokai Co., Ltd.) in Japanese and English.

## How the site is built

The site is a static build. There is no server, database or tracking.

| Path | What it holds |
|---|---|
| `content/site.json` | Facts shared by both languages: domain, email, phone, the page list and image sizes |
| `content/ja.json`, `content/en.json` | Every visible word, one file per language. Both files must have the same keys, and the build stops if one is missing |
| `templates/` | Jinja2 templates |
| `assets/` | CSS, JavaScript and WebP images |
| `build.py` | Writes the finished site to `dist/` |
| `check.py` | Fails the build on broken links, missing SEO tags, a missing `alt` or a wrong `lang` attribute |

To work on the site locally:

```bash
pip install jinja2==3.1.6
python build.py && python check.py
python -m http.server -d dist 8000   # then open http://localhost:8000/ja/
```

Pushing to `main` deploys the site through GitHub Actions (`.github/workflows/pages.yml`).

## Where the content came from

Everything was restored from the Wayback Machine captures of grandeshokai.com, taken between 2018 and 2022.

- **Company facts:** address, officers and capital are as published in 2018.
- **Contact email:** the archived site used a form and did not show an email address, so `info@grandeshokai.com` in `content/site.json` must be confirmed before launch.
- **Product claims:** the archive's medical claims (for example "prevents cancer", "treats malaria" or "lowers cholesterol") were left out to stay within Japan's 薬機法 and 景品表示法. Specifications, origins and applications were kept.
- **Senna:** it is labelled as a pharmaceutical raw material. In Japan, senna leaves and pods count as 医薬品成分 (pharmaceutical ingredients).
- **Brand logos:** partner and brand logos are not used. Brand names appear as plain text.

## Going live

1. In GitHub, go to **Settings → Pages → Source** and choose **GitHub Actions**. Then go to **Settings → General** and set the default branch to `main`.
2. At the domain's DNS provider, add these records:
   - `A` records on `@` pointing to `185.199.108.153`, `185.199.109.153`, `185.199.110.153` and `185.199.111.153`
   - `AAAA` records on `@` pointing to `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153` and `2606:50c0:8003::153`
   - a `CNAME` record on `www` pointing to `slim7505.github.io`
3. Go to **Settings → Pages**, set the custom domain to `grandeshokai.com` and tick **Enforce HTTPS**.
