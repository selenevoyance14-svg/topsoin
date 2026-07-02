#!/usr/bin/env python3
"""
Ajoute un bloc de maillage interne "À lire aussi" à TOUS les articles du journal.

- Catégorie de chaque article : lue dans les scripts générateurs (slug→category),
  avec repli sur le kicker si absente.
- Insère 4 liens vers d'autres articles de la MÊME catégorie, juste avant la
  mention de transparence (.disclosure).
- Idempotent : le bloc est délimité par des marqueurs et remplacé à chaque run.
- Ajoute au besoin le style .related dans journal/_style.css.

Usage : python3 scripts/add-maillage.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "journal"
SCRIPTS = ROOT / "scripts"

START = "<!--maillage-start-->"
END = "<!--maillage-end-->"

KICKER_MAP = {
    "GUIDE LINGERIE": "lingerie", "TENDANCE": "lingerie", "RÉFLEXION": "lingerie",
    "GUIDE NUIT": "nuit", "NUIT & LOUNGEWEAR": "nuit",
    "RITUEL SOINS": "soins", "SOINS INTIMES": "soins", "GUIDE BIEN-ÊTRE INTIME": "soins",
    "SENSUALITÉ": "sensualite", "RITUEL COUPLE": "sensualite",
    "ÉROTISME": "erotisme", "JEUX DE COUPLE": "erotisme",
    "IDÉES CADEAUX": "cadeaux", "COFFRETS": "cadeaux", "COFFRETS & CADEAUX": "cadeaux",
}


def build_slug_category():
    """Parcourt les scripts générateurs et associe chaque slug à sa category."""
    mapping = {}
    for name in ["build-journal.py", "add-articles.py", "add-articles-batch2.py", "add-comparatifs.py"]:
        p = SCRIPTS / name
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        # Paires (slug, category) : la category suit le slug dans chaque dict.
        for m in re.finditer(r'"slug":\s*"([^"]+)"(.*?)"category":\s*"([^"]+)"', text, re.DOTALL):
            slug, between, cat = m.group(1), m.group(2), m.group(3)
            # Évite de traverser plusieurs dicts : pas d'autre "slug" entre les deux.
            if '"slug"' not in between:
                mapping[slug] = cat
    return mapping


CSS_RULE = """
.related{margin:48px 0 0;padding:22px 24px;background:var(--paper);border:1px solid var(--line);border-radius:10px}
.related-title{color:var(--accent);margin-bottom:12px;display:block}
.related ul{margin:0;padding-left:20px}
.related li{margin-bottom:8px;font-size:16px}
.related a{color:var(--accent);text-decoration:underline;text-underline-offset:3px}
"""


def ensure_css():
    css_path = JOURNAL / "_style.css"
    css = css_path.read_text(encoding="utf-8")
    if ".related{" not in css:
        css_path.write_text(css.rstrip() + "\n" + CSS_RULE, encoding="utf-8")
        print("✓ _style.css : styles .related ajoutés")


def get_meta(html):
    kicker = re.search(r'class="kicker">([^<]*)</div>', html)
    title = re.search(r'<h1 class="serif">([^<]*)</h1>', html)
    return (kicker.group(1).strip() if kicker else ""), (title.group(1).strip() if title else "")


def render_block(items):
    lis = "".join(f'    <li><a href="/journal/{s}.html">{t}</a></li>\n' for s, t in items)
    return (f"{START}\n"
            f'<div class="related">\n'
            f'  <div class="related-title smallcaps">À lire aussi</div>\n'
            f"  <ul>\n{lis}  </ul>\n"
            f"</div>\n{END}")


def main():
    ensure_css()
    slug_cat = build_slug_category()

    files = [f for f in JOURNAL.glob("*.html") if f.name != "index.html"]
    meta = {}   # slug -> (category, title)
    for f in files:
        slug = f.stem
        html = f.read_text(encoding="utf-8")
        kicker, title = get_meta(html)
        cat = slug_cat.get(slug) or KICKER_MAP.get(kicker, "lingerie")
        meta[slug] = (cat, title)

    # Index par catégorie (ordre stable alphabétique).
    by_cat = {}
    for slug in sorted(meta):
        cat = meta[slug][0]
        by_cat.setdefault(cat, []).append(slug)

    updated = 0
    for f in files:
        slug = f.stem
        cat, _ = meta[slug]
        siblings = by_cat.get(cat, [])
        if len(siblings) < 2:
            continue
        j = siblings.index(slug)
        related = [siblings[(j + k) % len(siblings)] for k in range(1, len(siblings))]
        related = related[:4]
        items = [(s, meta[s][1]) for s in related]
        block = render_block(items)

        html = f.read_text(encoding="utf-8")
        if START in html and END in html:
            html = re.sub(re.escape(START) + r".*?" + re.escape(END), block, html, flags=re.DOTALL)
        else:
            html = html.replace('  <div class="disclosure">', block + "\n\n  <div class=\"disclosure\">", 1)
        f.write_text(html, encoding="utf-8")
        updated += 1

    print(f"✅ Maillage inséré/mis à jour sur {updated} articles.")
    for cat, slugs in sorted(by_cat.items()):
        print(f"   {cat}: {len(slugs)} articles")


if __name__ == "__main__":
    main()
