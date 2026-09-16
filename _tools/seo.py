"""Technical SEO for the public site: hreflang, canonical, social meta, JSON-LD, robots.txt, sitemap.xml.

Idempotent. Run from the repo root after adding or changing a page: python3 _tools/seo.py
A new page must be added to PAGES, otherwise it has no hreflang and is missing from the sitemap.
"""
import json, re, subprocess, sys, pathlib

ROOT = "https://swissnaturalizationtest.ch/"
LANGS = ["en", "fr", "de", "it"]
PAGES = ["landing.html", "transparency.html", "engineering.html", "press-kit.html",
         "privacy-policy.html", "terms.html", "account-deletion.html",
         "press/24-heures.html", "press/badener-tagblatt.html", "press/corriere-del-ticino.html",
         "press/leman-bleu.html", "press/tsri.html", "press/watson.html"]
HASH_PAGES = {"transparency.html", "privacy-policy.html", "terms.html", "account-deletion.html"}
MARK = "<!-- seo:start -->"
APPLE = "https://apps.apple.com/app/id6769993041"
PLAY = "https://play.google.com/store/apps/details?id=ch.vincedev.swisscitizenship"


def lang_url(base, l):
    return base if l == "en" else f"{base}?lang={l}"


def head_block(page, html):
    base = ROOT + page
    out = [MARK]
    for l in LANGS:
        out.append(f'<link rel="alternate" hreflang="{l}" href="{lang_url(base, l)}">')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{base}">')
    # Canonical follows the ?lang= variant, so each language is indexed on its own URL.
    out.append('<script>(function(){var q=null;try{q=new URLSearchParams(location.search).get("lang");}catch(e){}'
               f'var c=document.createElement("link");c.rel="canonical";c.href="{base}"'
               '+(q==="fr"||q==="de"||q==="it"?"?lang="+q:"");document.head.appendChild(c);})();</script>')
    if 'property="og:url"' not in html:
        out.append(f'<meta property="og:url" content="{base}">')
    if 'property="og:type"' not in html:
        out.append('<meta property="og:type" content="website">')
    if 'property="og:site_name"' not in html:
        out.append('<meta property="og:site_name" content="Swiss Naturalization Test">')
    if 'name="twitter:card"' not in html:
        card = "summary_large_image" if 'property="og:image"' in html else "summary"
        out.append(f'<meta name="twitter:card" content="{card}">')
    if page == "landing.html":
        desc = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebSite", "@id": ROOT + "#website", "name": "Swiss Naturalization Test",
             "url": base, "inLanguage": LANGS},
            {"@type": "MobileApplication", "@id": ROOT + "#app", "name": "Swiss Naturalization Test",
             "url": base, "description": desc, "applicationCategory": "EducationalApplication",
             "operatingSystem": "iOS, Android", "inLanguage": LANGS, "countriesSupported": "CH",
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CHF"},
             "downloadUrl": [APPLE, PLAY], "sameAs": [APPLE, PLAY],
             "author": {"@type": "Person", "name": "Vincenzo Casini"}}]}
        out.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>")
    out.append("<!-- seo:end -->")
    return "\n".join(out) + "\n"


LS_OLD = 'apply(saved||(LANGS.indexOf(nl)>=0?nl:"en"));'
LS_NEW = ('var q=null;try{q=new URLSearchParams(location.search).get("lang");}catch(e){}\n'
          '  apply((LANGS.indexOf(q)>=0?q:null)||saved||(LANGS.indexOf(nl)>=0?nl:"en"));')
HASH_OLD = 'if(L.indexOf(h)<0){var s=null;'
HASH_NEW = ('var q=null;try{q=new URLSearchParams(location.search).get("lang");}catch(e){}\n'
            '  if(L.indexOf(h)<0&&L.indexOf(q)>=0){location.hash=q;}else if(L.indexOf(h)<0){var s=null;')

for page in PAGES:
    p = pathlib.Path(page)
    html = p.read_text(encoding="utf-8")
    if MARK in html:
        html = re.sub(r"<!-- seo:start -->.*?<!-- seo:end -->\n", "", html, flags=re.S)
    html = html.replace("</head>", head_block(page, html) + "</head>", 1)
    if page in HASH_PAGES:
        if HASH_NEW not in html:
            assert html.count(HASH_OLD) == 1, page
            html = html.replace(HASH_OLD, HASH_NEW)
    else:
        if LS_NEW not in html:
            assert html.count(LS_OLD) == 1, page
            html = html.replace(LS_OLD, LS_NEW)
    if page == "landing.html":
        # Images in the three hidden language blocks were all downloaded on every visit.
        # The English block (default, and what crawlers render) stays eager for a fast first paint;
        # screenshots have no intrinsic size in the markup, so lazy-loading them would shift the layout.
        cut = html.index('<div class="langblock" id="lb-fr"')
        html = html[:cut] + re.sub(r"<img(?![^>]*\bloading=)(?![^>]*screenshots/)", '<img loading="lazy"', html[cut:])
    p.write_text(html, encoding="utf-8")
    print("patched", page)

# robots.txt
pathlib.Path("robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {ROOT}sitemap.xml\n")

# sitemap.xml with hreflang alternates; lastmod = last commit touching the page
rows = ['<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for page in PAGES:
    base = ROOT + page
    lastmod = subprocess.run(["git", "log", "-1", "--format=%cs", "--", page],
                             capture_output=True, text=True).stdout.strip()
    alts = [f'    <xhtml:link rel="alternate" hreflang="{l}" href="{lang_url(base, l)}"/>' for l in LANGS]
    alts.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{base}"/>')
    for l in LANGS:
        rows.append("  <url>")
        rows.append(f"    <loc>{lang_url(base, l)}</loc>")
        if lastmod:
            rows.append(f"    <lastmod>{lastmod}</lastmod>")
        rows.extend(alts)
        rows.append("  </url>")
rows.append("</urlset>")
pathlib.Path("sitemap.xml").write_text("\n".join(rows) + "\n")
print("robots.txt, sitemap.xml written")
