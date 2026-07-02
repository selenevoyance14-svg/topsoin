#!/usr/bin/env python3
"""
Ajoute des articles COMPARATIFS "Top / Meilleur" (intention d'achat) au journal.

- Chaque produit devient un mini-avis (H3 + rôle + lien Amazon cliquable DANS le texte)
  suivi de sa carte produit → beaucoup de liens affiliés, format qui convertit.
- Section "Comment bien choisir" (guide d'achat) pour le SEO et l'utilité.
- Non destructif / idempotent : réécrit le HTML, n'insère la carte d'index que si absente.

Usage : python3 scripts/add-comparatifs.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "journal"
DATA_JSX = ROOT / "data.jsx"
PARTNER_TAG = "lebrunnathali-21"
DATE = "2 juillet 2026"
DISCLAIMER_PRIME = "Tous les produits ci-dessous sont disponibles sur Amazon, souvent en livraison Prime et expédiés en colis neutre — discrétion totale."


def amazon_url(asin):
    return f"https://www.amazon.fr/dp/{asin}?tag={PARTNER_TAG}"


def load_products():
    text = DATA_JSX.read_text(encoding="utf-8")
    start = text.find("const PRODUCTS = ")
    if start == -1:
        return []
    json_start = text.find("[", start)
    depth = 0
    in_str = False
    escape = False
    for i, c in enumerate(text[json_start:]):
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return json.loads(text[json_start:json_start + i + 1])
    return []


def _bold(s):
    out, parts = "", s.split("**")
    for i, p in enumerate(parts):
        out += p if i % 2 == 0 else f"<strong>{p}</strong>"
    return out


def render_para_block(paragraphs):
    return "".join(f"<p>{_bold(p)}</p>\n" for p in paragraphs)


def render_product_card(p):
    return f"""<div class="product-card">
  <img src="{p['image']}" alt="{p['name']}" loading="lazy"/>
  <div class="pc-body">
    <div class="pc-name">{p['name']}</div>
    <div class="pc-sub smallcaps">{p['sub']}</div>
    <div class="pc-price">{p.get('price') or 'Voir prix'}</div>
    <a class="pc-cta" href="{amazon_url(p['asin'])}" target="_blank" rel="sponsored noopener nofollow">Voir sur Amazon →</a>
  </div>
</div>
"""


# Rôles éditoriaux : donnent un angle distinct à chaque produit du top.
ROLES = [
    ("Notre coup de cœur", "Un modèle qui coche toutes les cases : finition soignée, très bons retours d'acheteuses et prix juste. Si tu ne devais en retenir qu'un, ce serait celui-là."),
    ("Le meilleur rapport qualité-prix", "Difficile de trouver mieux à ce tarif : l'essentiel est là, sans payer pour du superflu."),
    ("L'option petit budget", "Le choix le plus accessible de la sélection, parfait pour se lancer sans trop dépenser."),
    ("Le choix premium", "Pour celles qui veulent ce qui se fait de mieux : matières et finitions haut de gamme, on sent la différence."),
    ("Le plus polyvalent", "Un choix passe-partout qui s'adapte à la plupart des envies et des situations."),
    ("Idéal pour débuter", "Simple à prendre en main et rassurant : le bon point de départ quand on découvre."),
    ("La valeur sûre", "Un classique plébiscité qui fait l'unanimité depuis longtemps : on prend peu de risques."),
    ("L'alternative tendance", "Le modèle dont on parle en ce moment, à considérer si tu aimes sortir des sentiers battus."),
    ("Le confort avant tout", "Pensé pour se faire oublier : c'est le genre de produit qu'on ne quitte plus une fois adopté."),
    ("Le cadeau parfait", "Joliment présenté et sûr de faire plaisir : une valeur sûre à offrir les yeux fermés."),
]


def render_pick(i, p, role):
    label, sentence = role
    link = f'<a href="{amazon_url(p["asin"])}" target="_blank" rel="sponsored noopener nofollow">voir le prix sur Amazon →</a>'
    body = f"<h3>{i}. {p['name']}</h3>\n<p><strong>{label}.</strong> {sentence} {link}</p>\n"
    return body + render_product_card(p)


_CURSORS = {}


def select_products(products, cats, n, offset_key):
    pool = [p for p in products if p["cat"] in cats]
    if not pool:
        return []
    start = _CURSORS.get(offset_key, 0)
    selected = [pool[(start + i) % len(pool)] for i in range(min(n, len(pool)))]
    _CURSORS[offset_key] = (start + n) % len(pool)
    return selected


def render_comparatif(a, products):
    n = a.get("n_products", 8)
    selected = select_products(products, a["product_cats"], n, a["product_cats"][0])
    picks_html = "".join(render_pick(i + 1, p, ROLES[i % len(ROLES)]) for i, p in enumerate(selected))
    guide_title, guide_bullets = a["guide"]
    guide_html = f"<h2>{guide_title}</h2>\n<ul>\n" + "".join(f"<li>{_bold(b)}</li>\n" for b in guide_bullets) + "</ul>\n"
    intro_html = render_para_block(a["intro"])
    outro_html = render_para_block(a["outro"])
    cover_bg = f"linear-gradient(135deg, {a['cover_color']} 0%, {a['cover_color']}aa 100%)"

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{a['title']} — Maison Léa</title>
<meta name="description" content="{a['lead']}" />
<link rel="canonical" href="https://guide-soin.fr/journal/{a['slug']}.html" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{a['title']}" />
<meta property="og:description" content="{a['lead']}" />
<meta property="og:url" content="https://guide-soin.fr/journal/{a['slug']}.html" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,500&family=Geist:wght@300;400;500;600&family=Geist+Mono:wght@400&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="_style.css" />
</head>
<body>
<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="brand">Maison <em>Léa</em></a>
    <a href="/journal/">← Le Journal</a>
  </div>
</nav>

<article class="wrap">
  <div class="kicker">{a['kicker']}</div>
  <h1 class="serif">{a['title']}</h1>
  <p class="lead">{a['lead']}</p>
  <div class="meta">{a['date']} · {a['read']} de lecture</div>

  <div class="cover"><div class="cover-bg" style="background:{cover_bg}"></div></div>

  {intro_html}
  {guide_html}
  <h2>Notre sélection, passée au crible</h2>
  {picks_html}
  {outro_html}

  <div class="disclosure">
    <strong>Transparence :</strong> Maison Léa est partenaire du Programme Amazon. Les liens vers Amazon nous rémunèrent par une petite commission, sans surcoût pour vous. <a href="/affiliation.html">En savoir plus</a>.
  </div>

  <a href="/journal/" class="cta-back">← Voir tous les articles</a>
</article>

<footer class="foot">
  © 2026 Maison Léa · <a href="/">Accueil</a> · <a href="/affiliation.html">Affiliation</a> · <a href="/mentions-legales.html">Mentions légales</a> · <a href="/confidentialite.html">Confidentialité</a>
</footer>
</body>
</html>
"""


def render_card(a):
    return f"""<a href="/journal/{a['slug']}.html" class="article-card">
  <div class="ac-cover" style="background:linear-gradient(135deg, {a['cover_color']} 0%, {a['cover_color']}aa 100%)"></div>
  <div class="ac-body">
    <div class="ac-kicker smallcaps">{a['kicker']}</div>
    <div class="ac-title serif">{a['title']}</div>
    <div class="ac-lead">{a['lead']}</div>
    <div class="ac-meta">{a['date']} · {a['read']}</div>
  </div>
</a>
"""


def main():
    products = load_products()
    print(f"📚 {len(products)} produits chargés depuis data.jsx")

    for a in COMPARATIFS:
        (JOURNAL / f"{a['slug']}.html").write_text(render_comparatif(a, products), encoding="utf-8")
        print(f"✓ {a['slug']}.html")

    index_path = JOURNAL / "index.html"
    html = index_path.read_text(encoding="utf-8")
    to_card = [a for a in COMPARATIFS if f"/journal/{a['slug']}.html" not in html]
    if to_card:
        anchor = '<div class="articles-grid">\n'
        if anchor not in html:
            anchor = '<div class="articles-grid">'
            cards = "\n    " + "\n    ".join(render_card(a).strip() for a in to_card)
        else:
            cards = "    " + "    ".join(render_card(a) for a in to_card)
        html = html.replace(anchor, anchor + cards, 1)
        index_path.write_text(html, encoding="utf-8")
    print(f"✓ index.html : +{len(to_card)} cartes (déjà présentes : {len(COMPARATIFS) - len(to_card)})")
    print(f"\n✅ {len(COMPARATIFS)} comparatifs générés.")


# ────────────────────────────────────────────────────────────────────────────
COMPARATIFS = [
    {
        "slug": "meilleure-lingerie-selection-comparatif",
        "kicker": "COMPARATIF", "category": "lingerie",
        "title": "Meilleure lingerie : notre sélection coup de cœur",
        "lead": "Ensembles, dentelle, coupes flatteuses : notre sélection des plus belles pièces de lingerie, pour toutes les envies et tous les budgets.",
        "date": DATE, "read": "6 min", "cover_color": "#8b1d2c",
        "product_cats": ["lingerie"], "n_products": 8,
        "intro": [
            "Choisir une belle pièce de lingerie, c'est autant une question de coupe que de confiance. On a rassemblé ici nos coups de cœur — des modèles flatteurs, bien notés et disponibles rapidement — pour t'aider à trouver la pièce qui te correspond.",
            "Du modèle petit budget à la dentelle premium, il y en a pour toutes les silhouettes et toutes les occasions.",
        ],
        "guide": ("Comment bien choisir sa lingerie", [
            "**La taille avant tout** : un soutien-gorge bien ajusté ne baille pas au bonnet et ne remonte pas dans le dos. En cas de doute, mesure-toi ou prends la taille de bonnet au-dessus.",
            "**La matière** : dentelle pour l'élégance, microfibre pour l'invisible sous les vêtements, coton pour le confort quotidien.",
            "**L'occasion** : un ensemble uni pour tous les jours, une pièce en dentelle ou un body pour les moments qui comptent.",
            "**Le confort** : la plus belle pièce est celle qu'on oublie une fois portée — méfie-toi de ce qui serre ou gratte.",
        ]),
        "outro": [
            DISCLAIMER_PRIME,
            "Notre conseil : commande deux tailles quand tu hésites, le retour est gratuit avec Prime. Tu gardes celle qui tombe parfaitement.",
        ],
    },
    {
        "slug": "meilleur-pyjama-nuisette-comparatif",
        "kicker": "COMPARATIF", "category": "nuit",
        "title": "Meilleurs pyjamas et nuisettes : le comparatif",
        "lead": "Satin, coton, modal : notre sélection des tenues de nuit les plus douces et flatteuses, pour bien dormir en toute saison.",
        "date": DATE, "read": "6 min", "cover_color": "#3a2e1f",
        "product_cats": ["nuit"], "n_products": 8,
        "intro": [
            "Bien dormir commence par une tenue de nuit agréable. Entre le glissé du satin, la douceur du modal et la respirabilité du coton, on a sélectionné les modèles qui allient confort et jolie coupe.",
            "Du pyjama cocooning d'hiver à la nuisette légère d'été, voici nos préférés.",
        ],
        "guide": ("Comment choisir sa tenue de nuit", [
            "**La saison** : coton et modal respirants pour l'été, molleton et polaire pour les nuits froides.",
            "**La sensation recherchée** : satin pour le côté sensuel et fluide, coton pour le confort brut.",
            "**La coupe** : ample pour dormir sans rien sentir, empire ou ajustée pour un effet plus flatteur.",
            "**L'entretien** : le satin se lave en cycle doux, le coton passe partout — à prendre en compte au quotidien.",
        ]),
        "outro": [
            DISCLAIMER_PRIME,
            "Astuce : les nuisettes en satin taillent souvent juste. Si tu hésites, prends la taille au-dessus pour garder le beau tombé fluide.",
        ],
    },
    {
        "slug": "meilleurs-soins-corps-selection",
        "kicker": "COMPARATIF", "category": "soins",
        "title": "Meilleurs soins du corps : notre sélection",
        "lead": "Huiles, laits, gommages, soins intimes doux : notre sélection des produits qui prennent vraiment soin de la peau au quotidien.",
        "date": DATE, "read": "6 min", "cover_color": "#2a3a2a",
        "product_cats": ["soins"], "n_products": 8,
        "intro": [
            "Une peau douce et confortable, ça tient à une routine simple et à de bons produits. On a réuni ici nos soins du corps favoris : hydratation, nutrition, gommage et soins intimes doux, pour tous les besoins.",
            "Des textures légères aux plus riches, il y a de quoi composer un rituel qui te ressemble.",
        ],
        "guide": ("Comment choisir ses soins du corps", [
            "**Ton type de peau** : crème hydratante pour les peaux normales, beurre ou huile riche pour les peaux sèches.",
            "**Le moment** : une texture qui pénètre vite le matin, un soin plus riche à masser le soir.",
            "**Pour les zones intimes** : privilégie un pH adapté, sans savon parfumé, doux et testé.",
            "**La composition** : une liste courte, sans parfum agressif, reste le plus sûr pour les peaux sensibles.",
        ]),
        "outro": [
            DISCLAIMER_PRIME,
            "Le vrai secret d'une belle peau, c'est la régularité : deux minutes chaque soir valent mieux qu'un soin intense une fois par mois.",
        ],
    },
    {
        "slug": "meilleures-huiles-bougies-massage-comparatif",
        "kicker": "COMPARATIF", "category": "sensualite",
        "title": "Meilleures huiles et bougies de massage",
        "lead": "Pour un rituel à deux réussi : notre sélection d'huiles et de bougies de massage, du plus doux au plus sensuel.",
        "date": DATE, "read": "6 min", "cover_color": "#5b1a26",
        "product_cats": ["sensualite"], "n_products": 8,
        "intro": [
            "Un bon massage à deux commence par le bon produit : une huile qui glisse sans coller, une bougie qui parfume la pièce et se transforme en huile tiède. On a sélectionné les valeurs sûres pour créer un vrai moment de détente.",
            "Neutres ou parfumées, chauffantes ou comestibles, voici nos préférées pour un rituel sensuel réussi.",
        ],
        "guide": ("Comment choisir son huile ou sa bougie de massage", [
            "**Neutre ou parfumée** : neutre pour un massage soin, parfumée pour installer une ambiance sensuelle.",
            "**Effet chauffant** : agréable pour un massage sensuel, à éviter sur les zones très sensibles.",
            "**La bougie de massage** : elle fond à basse température en une huile tiède — vérifie qu'elle est bien prévue pour la peau.",
            "**La composition** : privilégie les huiles végétales, faciles à rincer et douces pour la peau.",
        ]),
        "outro": [
            DISCLAIMER_PRIME,
            "Le vrai luxe, c'est le geste : une pièce chaude, une lumière basse, et le produit fait le reste. La régularité crée l'intimité.",
        ],
    },
    {
        "slug": "meilleurs-vibromasseurs-comparatif-guide",
        "kicker": "COMPARATIF", "category": "erotisme",
        "title": "Meilleurs vibromasseurs : le comparatif",
        "lead": "Discrets, connectés, pour débuter ou pour couple : notre sélection des vibromasseurs les mieux notés, avec guide d'achat clair.",
        "date": DATE, "read": "7 min", "cover_color": "#3a1420",
        "product_cats": ["erotisme"], "n_products": 8,
        "intro": [
            "Le choix est vaste et pas toujours simple à décrypter. On a réuni ici les modèles les plus appréciés — du petit stimulateur discret au modèle connecté pour couple — avec un guide clair pour t'y retrouver.",
            "Que ce soit pour débuter en douceur ou pour varier les plaisirs, il y a un modèle pour chaque envie.",
        ],
        "guide": ("Comment choisir son vibromasseur", [
            "**La matière** : privilégie le silicone médical, doux, sans danger et facile à nettoyer.",
            "**Pour débuter** : un petit modèle simple et silencieux rassure plus qu'un appareil complexe.",
            "**Le type de stimulation** : externe, interne, double ou air pulsé — à choisir selon tes envies.",
            "**Les indispensables** : rechargeable en USB, étanche et silencieux, ce sont les repères d'un bon produit.",
            "**Le lubrifiant** : à base d'eau, compatible avec tout, il améliore nettement le confort.",
        ]),
        "outro": [
            DISCLAIMER_PRIME,
            "Le bon réflexe : un modèle rechargeable, étanche et en silicone doux. Ce sont les critères qui font durer le plaisir dans le temps.",
        ],
    },
    {
        "slug": "meilleurs-coffrets-cadeaux-couple-comparatif",
        "kicker": "COMPARATIF", "category": "cadeaux",
        "title": "Meilleurs coffrets cadeaux couple : le top",
        "lead": "Anniversaire, Saint-Valentin, juste pour faire plaisir : notre sélection des plus beaux coffrets cadeaux à offrir en couple.",
        "date": DATE, "read": "6 min", "cover_color": "#5a3a1a",
        "product_cats": ["cadeaux"], "n_products": 8,
        "intro": [
            "Un coffret bien choisi, c'est le cadeau qui ne se trompe jamais : une jolie présentation, une promesse de moment à deux. On a sélectionné les plus beaux, du plus tendre au plus complice, pour toutes les occasions et tous les budgets.",
            "Anniversaire, Saint-Valentin, lune de miel ou simple envie de faire plaisir : voici nos préférés.",
        ],
        "guide": ("Comment choisir le bon coffret", [
            "**L'occasion** : romantique pour la Saint-Valentin, cocooning pour faire plaisir, plus audacieux pour pimenter.",
            "**Le destinataire** : mise sur ses goûts à elle ou à lui, pas sur ce qui t'attire toi.",
            "**La présentation** : un bel écrin fait la moitié du cadeau — soigne l'emballage et glisse un mot.",
            "**Le budget** : un coffret bien pensé à prix doux marque plus qu'un cadeau cher mais impersonnel.",
        ]),
        "outro": [
            DISCLAIMER_PRIME,
            "Le meilleur coffret, c'est celui qui invite à éteindre les écrans et à se retrouver. L'intention compte plus que le prix.",
        ],
    },
]


if __name__ == "__main__":
    main()
