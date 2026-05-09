#!/usr/bin/env python3
"""
Génère les pages du journal Maison Léa à partir des articles définis ci-dessous.

Usage : python3 scripts/build-journal.py
"""

import json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "journal"
JOURNAL.mkdir(exist_ok=True)
DATA_JSX = ROOT / "data.jsx"

PARTNER_TAG = "lebrunnathali-21"


def amazon_url(asin):
    return f"https://www.amazon.fr/dp/{asin}?tag={PARTNER_TAG}"


def load_products():
    """Charge les produits depuis data.jsx pour pouvoir les citer dans les articles."""
    text = DATA_JSX.read_text(encoding="utf-8")
    start = text.find("const PRODUCTS = ")
    if start == -1:
        return []
    json_start = text.find("[", start)
    depth = 0
    for i, c in enumerate(text[json_start:]):
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return json.loads(text[json_start:json_start + i + 1])
    return []


# ────────────────────────────────────────────────────────────────────────────
# Articles — définis ici. Pour en ajouter, copie un bloc et adapte.
ARTICLES = [
    {
        "slug": "comment-choisir-soutien-gorge-sans-armatures",
        "kicker": "GUIDE LINGERIE",
        "title": "Comment choisir un soutien-gorge sans armatures qui tient vraiment",
        "lead": "Le confort sans compromis sur le maintien : c'est possible. Voici comment choisir le bon modèle.",
        "category": "lingerie",
        "date": "9 mai 2026",
        "read": "5 min",
        "cover_color": "#8b1d2c",
        "product_cats": ["lingerie"],
        "max_products": 3,
        "intro": [
            "Pendant longtemps, le soutien-gorge sans armatures était synonyme de \"je laisse tomber\". Aujourd'hui, les marques ont compris que confort ne rime pas forcément avec absence de maintien — et la sélection s'est étoffée.",
            "Si tu cherches à dire adieu aux marques rouges en fin de journée sans pour autant avoir l'impression de flotter, voici ce qu'il faut regarder.",
        ],
        "sections": [
            ("La bonne taille avant tout", [
                "Plus de 70% des femmes portent une mauvaise taille. Pour un sans-armatures, c'est encore plus critique : le maintien repose entièrement sur la coupe, le tissu et la bande de dessous.",
                "Mesure ton tour sous poitrine bien serré (en cm), puis ton tour de poitrine au point le plus large. La différence te donne le bonnet (12 cm = A, 14 = B, 16 = C, 18 = D...).",
            ]),
            ("Les coupes qui tiennent vraiment", [
                "**Bralette croisée dans le dos** : élégante et confortable, parfaite pour bonnets A à C.",
                "**Triangle large à dos nageur** : maintien renforcé sans armatures, idéal pour les activités quotidiennes.",
                "**Soft cup avec bandeau renforcé** : technique éprouvée, fonctionne jusqu'au bonnet E.",
            ]),
            ("Les matières à privilégier", [
                "Le **microfibre stretch** offre le meilleur compromis : il épouse sans serrer. La **dentelle élastique** est élégante mais peut moins maintenir. Le **coton** est doux pour la peau mais s'étire vite.",
                "Évite les modèles 100% polyester rigide : le tissu va vite se déformer après quelques lavages.",
            ]),
            ("Le critère décisif : la bande de dessous", [
                "C'est elle qui fait 80% du maintien sur un sans-armatures. Une bande large (3-4 cm minimum), élastique mais ferme, qui ne remonte pas au cours de la journée.",
                "Mauvais signe : si elle remonte dans le dos quand tu lèves les bras, le modèle ne te conviendra pas.",
            ]),
        ],
        "outro": [
            "Notre conseil : commande **deux tailles différentes** quand tu testes une nouvelle marque (la même \"taille\" ne taille jamais pareil entre deux marques). Renvoie celle qui ne va pas — c'est gratuit avec Amazon Prime.",
        ],
    },
    {
        "slug": "guide-nuisette-satin-tomber-amoureuse-tissu",
        "kicker": "GUIDE NUIT",
        "title": "Nuisette en satin : tomber amoureuse du bon tissu",
        "lead": "Pas tous les satins se valent. On t'explique comment reconnaître la qualité et investir intelligemment.",
        "category": "nuit",
        "date": "9 mai 2026",
        "read": "4 min",
        "cover_color": "#3a2e1f",
        "product_cats": ["nuit"],
        "max_products": 3,
        "intro": [
            "La nuisette en satin a ce pouvoir : elle te fait te sentir belle, même les soirs où tu es seule à la voir. Mais entre une qui te durera dix ans et une qui se déforme au troisième lavage, la différence est ailleurs que dans le prix.",
        ],
        "sections": [
            ("Satin polyester ou satin de soie ?", [
                "Le **satin de polyester** (le plus courant) est lisse, brillant, abordable. Il résiste bien aux lavages mais ne respire pas. À éviter en été ou si tu transpires la nuit.",
                "Le **satin de soie** ou **soie sablée** est plus mat, fluide, respirant et thermorégulateur. Plus cher (souvent 3-5x), mais c'est l'investissement qui se sent immédiatement.",
                "Le **satin de viscose** est un compromis intéressant : douceur proche de la soie, prix proche du polyester.",
            ]),
            ("La coupe qui flatte toutes les morphologies", [
                "**Coupe trapèze à fines bretelles** : l'incontournable. Elle flatte tous les corps en évasant juste au-dessus de la taille.",
                "**Slip dress** (style années 90) : plus moulante, parfaite si tu veux mettre en valeur les courbes.",
                "**Modèle à dentelle sur la poitrine** : ajoute une touche d'élégance sans tomber dans le vulgaire.",
            ]),
            ("L'entretien qui fait la différence", [
                "Toutes les nuisettes en satin **se lavent à 30°C maximum**, sur cycle délicat, idéalement dans un filet. Pas de sèche-linge — étendre à plat.",
                "Pour le repassage : fer tiède côté envers, ou pas du tout (la plupart se défroissent en se portant).",
            ]),
        ],
        "outro": [
            "Astuce de Léa : achète au moins deux nuisettes pour pouvoir les alterner. Le satin de qualité dure dix ans si tu ne le portes pas tous les soirs.",
        ],
    },
    {
        "slug": "bien-choisir-lubrifiant-intime-guide",
        "kicker": "SOINS INTIMES",
        "title": "Bien choisir son lubrifiant intime : guide complet",
        "lead": "Tous les lubrifiants ne se valent pas. Composition, texture, compatibilité — voici tout ce qu'il faut savoir.",
        "category": "soins",
        "date": "9 mai 2026",
        "read": "6 min",
        "cover_color": "#c9a961",
        "product_cats": ["soins"],
        "max_products": 3,
        "intro": [
            "Utiliser un lubrifiant intime, ce n'est ni un signe de problème, ni une solution de dernier recours. C'est juste un produit qui rend tout plus agréable, à tout âge, dans toutes les circonstances.",
            "Mais entre les versions \"chauffant\", \"naturel\", \"silicone\" ou \"goût pomme verte\", on s'y perd. Voici comment choisir le bon, pour la bonne situation.",
        ],
        "sections": [
            ("Base eau, base silicone, base huile : la grande différence", [
                "**Base eau** : naturel, lavable facilement, compatible avec tout (préservatifs, sextoys silicone). Inconvénient : sèche assez vite, à réappliquer.",
                "**Base silicone** : ne sèche pas, glisse plus longtemps, parfait pour la douche. ⚠️ Incompatible avec les sextoys en silicone (les abîme à long terme).",
                "**Base huile** : pour les massages plutôt. ⚠️ À ne pas utiliser avec préservatifs latex (les fait casser).",
            ]),
            ("Les ingrédients à éviter", [
                "**Glycérine** en grande quantité : peut favoriser les mycoses chez certaines femmes.",
                "**Parabens** : perturbateurs endocriniens, à fuir.",
                "**Parfums de synthèse et arômes** : agréables sur le moment mais souvent irritants.",
                "**Propylène glycol** : peut causer des irritations sur peau sensible.",
            ]),
            ("Notre recommandation pour démarrer", [
                "Si tu n'en as jamais utilisé : commence par un **lubrifiant à base d'eau, sans glycérine, certifié bio**. C'est le plus polyvalent et le plus sûr.",
                "Pour la salle de bain ou la piscine, opte pour la **base silicone**. Pour les massages préliminaires, l'**huile chauffante** est idéale.",
            ]),
        ],
        "outro": [
            "Tous les lubrifiants ci-dessous sont disponibles sur Amazon en livraison Prime, et expédiés en colis neutre — discrétion totale, comme tout le reste de notre sélection.",
        ],
    },
    {
        "slug": "vibromasseurs-debutantes-selection",
        "kicker": "SENSUALITÉ",
        "title": "Vibromasseurs pour débutantes : par quoi commencer ?",
        "lead": "Si c'est ton premier achat, voici comment choisir sans te tromper. Discrétion garantie.",
        "category": "sensualite",
        "date": "9 mai 2026",
        "read": "5 min",
        "cover_color": "#1a1a1a",
        "product_cats": ["sensualite"],
        "max_products": 3,
        "intro": [
            "Le premier vibromasseur, c'est souvent un peu intimidant. Trop gros ? Trop bruyant ? Comment ça se nettoie ? Et surtout : par quel modèle commencer ?",
            "Bonne nouvelle : il existe des modèles pensés pour démarrer en douceur, à des prix raisonnables, livrés en colis neutre. Voilà ce qu'il faut regarder.",
        ],
        "sections": [
            ("Les 3 types les plus simples pour commencer", [
                "**Le stimulateur clitoridien (style Womanizer)** : par succion ou ondes, sans contact direct. Très efficace pour les débutantes, courbe d'apprentissage rapide.",
                "**Le mini-vibromasseur \"rouge à lèvres\"** : discret, taille d'un stylo, parfait à glisser dans un sac de voyage.",
                "**L'œuf vibrant à télécommande** : plus ludique, peut s'utiliser seule ou en couple.",
            ]),
            ("Les critères qui changent vraiment l'expérience", [
                "**Silicone médical** : la seule matière acceptable pour le corps. Évite tout ce qui est en plastique dur ou en TPE bas de gamme.",
                "**Rechargeable USB** : plus écologique et économique que les piles. Tous les bons modèles le sont.",
                "**Étanche IPX7** : indispensable pour pouvoir le nettoyer sous l'eau. Vérifie cette mention.",
                "**Niveau sonore** : sous 50 dB = silencieux. Important si tu vis en colocation ou en appartement aux murs fins.",
            ]),
            ("Le bon prix pour démarrer", [
                "Entre **20€ et 50€**, tu trouves d'excellents modèles parfaitement adaptés aux débutantes. Pas besoin d'investir 200€ tout de suite — autant essayer un premier modèle, comprendre ce qui te plaît, puis investir si tu veux.",
                "Méfie-toi des produits sous 15€ : souvent en matière douteuse, peu durables.",
            ]),
            ("L'aspect pratique qu'on oublie", [
                "Tous les modèles Amazon sont livrés en **colis neutre** (carton brun standard sans mention du contenu). Ton facteur ne saura rien. La discrétion va même jusqu'à la facturation : la mention sur ton relevé bancaire est anonyme.",
            ]),
        ],
        "outro": [
            "Si tu hésites encore, regarde les avis. Les modèles ci-dessous ont tous **plusieurs centaines d'avis positifs** sur Amazon, ce qui est rassurant pour un premier achat.",
        ],
    },
    {
        "slug": "idees-cadeaux-couple-romantique",
        "kicker": "COFFRETS",
        "title": "Idées cadeaux couple : 5 coffrets qui font vraiment plaisir",
        "lead": "Saint-Valentin, anniversaire, juste comme ça : des coffrets pour partager un moment à deux.",
        "category": "cadeaux",
        "date": "9 mai 2026",
        "read": "4 min",
        "cover_color": "#5b1a26",
        "product_cats": ["cadeaux"],
        "max_products": 3,
        "intro": [
            "Offrir un cadeau intime à son couple, ce n'est pas forcément hot ou sexy. Ça peut être doux, joueur, sensoriel — l'idée est juste de partager un moment dédié.",
            "Voici nos coups de cœur de la sélection : des coffrets qui tiennent leurs promesses, sans en faire trop.",
        ],
        "sections": [
            ("Pour démarrer en douceur : le coffret massage", [
                "Une huile de massage sensorielle, deux bougies parfumées, parfois un livret avec quelques techniques. Le format parfait pour un dimanche pluvieux.",
                "Le rituel compte autant que le contenu : musique, lumière tamisée, téléphones rangés. Une heure pour vous.",
            ]),
            ("Pour les couples joueurs : les coffrets jeux", [
                "Cartes à gratter, défis hot, jeux de société pour adultes : ces formats brisent la routine sans pression. Tu choisis le niveau (suggestif → osé) selon ton humeur.",
                "Le bonus : ça ouvre des conversations sur ce qui plaît à chacun, sans avoir besoin de \"poser la question\".",
            ]),
            ("Le plus discret : les coffrets bien-être", [
                "Si la personne à qui tu offres est plutôt pudique ou que vous n'êtes pas encore au stade \"tout est ok\", un coffret bien-être (bain, soins, bougies) est une option élégante.",
                "Tu peux le compléter par un mot manuscrit avec ton intention — c'est souvent ce qui touche le plus.",
            ]),
        ],
        "outro": [
            "Pour la livraison : tous nos coffrets arrivent en **colis neutre Amazon**. Si tu offres en main propre, pense à enlever le bordereau. Si tu fais livrer directement chez la personne, c'est encore plus simple.",
        ],
    },
    {
        "slug": "lingerie-et-confiance-soi",
        "kicker": "RÉFLEXION",
        "title": "La lingerie pour soi, pas pour les autres",
        "lead": "Pourquoi le sous-vêtement qu'on choisit chaque matin influence notre humeur — et comment en faire un acte d'amour-propre.",
        "category": "lingerie",
        "date": "9 mai 2026",
        "read": "3 min",
        "cover_color": "#a04848",
        "product_cats": [],
        "max_products": 0,
        "intro": [
            "On parle souvent de lingerie comme d'un cadeau qu'on fait à l'autre. Et si on la voyait comme un cadeau qu'on se fait à soi ?",
        ],
        "sections": [
            ("Le sous-vêtement, c'est la première chose qu'on enfile", [
                "Avant le café, avant la robe, avant le maquillage — ton sous-vêtement est là. Il touche ta peau pendant 16h. Il définit le confort de ta journée. Et secrètement, il définit aussi un peu ton humeur.",
                "Une étude américaine de 2018 (Universities of Houston) a même mesuré l'effet : porter de la \"belle\" lingerie (la définition étant subjective) augmentait la confiance en soi mesurée sur la journée. Pas en cas de date du soir — n'importe quel mardi banal.",
            ]),
            ("Sortir de la logique \"occasion spéciale\"", [
                "On a longtemps gardé la \"belle\" lingerie pour les soirs particuliers. Résultat : elle reste dans le tiroir 360 jours par an.",
                "Et si tu inversais le truc ? Garde le coton blanc pour les jours de gym, et porte la dentelle un mardi pour aller au bureau. Personne ne le saura — sauf toi. Et c'est bien le point.",
            ]),
            ("Investir dans le confort, d'abord", [
                "La plus belle lingerie du monde ne sert à rien si elle gratte ou se voit sous les vêtements. Avant tout, choisis ce qui est **confortable**. La beauté vient ensuite.",
                "Une garde-robe intime fonctionnelle, c'est : 5-6 sous-vêtements de \"tous les jours\" confortables, 2-3 plus jolis pour les jours où tu en as envie, et 1-2 \"spécial occasion\" si ça te plaît.",
            ]),
        ],
        "outro": [
            "La règle d'or de Léa : **achète ce qui te plaît à toi, pas ce qui plairait à un partenaire imaginaire**. C'est toi qui le portes 16h sur 24.",
        ],
    },
]


# ────────────────────────────────────────────────────────────────────────────
def render_section(title, paragraphs):
    body = f'<h2>{title}</h2>\n'
    for p in paragraphs:
        if p.startswith("- ") or p.startswith("**"):
            # Heuristique : liste si plusieurs ** ou tirets
            pass
        body += f'<p>{p.replace("**", "<strong>").replace("</strong>", "**", 0)}</p>\n'
    # Replace ** -> <strong>...</strong>
    body = _bold(body)
    return body


def _bold(s):
    """Convertit **gras** en <strong>gras</strong> (paires)."""
    out = ""
    parts = s.split("**")
    for i, p in enumerate(parts):
        if i % 2 == 0:
            out += p
        else:
            out += f"<strong>{p}</strong>"
    return out


def render_para_block(paragraphs):
    body = ""
    for p in paragraphs:
        body += f'<p>{_bold(p)}</p>\n'
    return body


def render_section_block(title, paragraphs):
    return f'<h2>{title}</h2>\n{render_para_block(paragraphs)}'


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


def render_article(article, products):
    # Sélectionne 0-3 produits dans les bonnes catégories
    selected = []
    if article["product_cats"] and article["max_products"] > 0:
        pool = [p for p in products if p["cat"] in article["product_cats"]]
        # On prend les premiers (déjà ordonnés par pertinence dans le fetch)
        selected = pool[: article["max_products"]]

    sections_html = ""
    for title, paras in article["sections"]:
        sections_html += render_section_block(title, paras)

    products_html = ""
    if selected:
        products_html = '<h2>Notre sélection</h2>\n'
        for p in selected:
            products_html += render_product_card(p)

    intro_html = render_para_block(article["intro"])
    outro_html = render_para_block(article["outro"])

    cover_bg = f"linear-gradient(135deg, {article['cover_color']} 0%, {article['cover_color']}aa 100%)"

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{article['title']} — Maison Léa</title>
<meta name="description" content="{article['lead']}" />
<link rel="canonical" href="https://guide-soin.fr/journal/{article['slug']}.html" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{article['title']}" />
<meta property="og:description" content="{article['lead']}" />
<meta property="og:url" content="https://guide-soin.fr/journal/{article['slug']}.html" />
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
  <div class="kicker">{article['kicker']}</div>
  <h1 class="serif">{article['title']}</h1>
  <p class="lead">{article['lead']}</p>
  <div class="meta">{article['date']} · {article['read']} de lecture</div>

  <div class="cover"><div class="cover-bg" style="background:{cover_bg}"></div></div>

  {intro_html}
  {sections_html}
  {products_html}
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


def render_index(articles):
    cards = ""
    for a in articles:
        cards += f"""<a href="/journal/{a['slug']}.html" class="article-card">
  <div class="ac-cover" style="background:linear-gradient(135deg, {a['cover_color']} 0%, {a['cover_color']}aa 100%)"></div>
  <div class="ac-body">
    <div class="ac-kicker smallcaps">{a['kicker']}</div>
    <div class="ac-title serif">{a['title']}</div>
    <div class="ac-lead">{a['lead']}</div>
    <div class="ac-meta">{a['date']} · {a['read']}</div>
  </div>
</a>
"""

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Le Journal — Maison Léa</title>
<meta name="description" content="Guides, sélections et conseils pour bien choisir sa lingerie, ses soins intimes et ses cadeaux pour couples." />
<link rel="canonical" href="https://guide-soin.fr/journal/" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;1,500&family=Geist:wght@300;400;500;600&family=Geist+Mono:wght@400&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="_style.css" />
<style>
  .articles-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px;margin-top:40px}}
  .article-card{{display:block;text-decoration:none;color:inherit;background:var(--paper);border:1px solid var(--line);border-radius:12px;overflow:hidden;transition:transform .25s ease, box-shadow .25s ease}}
  .article-card:hover{{transform:translateY(-4px);box-shadow:0 12px 32px rgba(0,0,0,.08)}}
  .ac-cover{{aspect-ratio:16/10;width:100%}}
  .ac-body{{padding:18px 22px 24px}}
  .ac-kicker{{color:var(--accent);margin-bottom:10px}}
  .ac-title{{font-size:22px;line-height:1.2;margin-bottom:8px;color:var(--ink)}}
  .ac-lead{{font-size:14px;color:var(--ink-2);line-height:1.5;margin-bottom:14px}}
  .ac-meta{{font-size:11px;color:var(--muted);font-family:"Geist Mono",monospace;letter-spacing:.08em}}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="brand">Maison <em>Léa</em></a>
    <a href="/">← Retour boutique</a>
  </div>
</nav>

<div class="wrap">
  <div class="kicker">LE JOURNAL</div>
  <h1 class="serif">Guides, conseils, sélections.</h1>
  <p class="lead">Tout ce qu'il faut savoir pour choisir avec confiance — de la lingerie aux soins intimes, en passant par les coffrets cadeaux.</p>

  <div class="articles-grid">
    {cards}
  </div>
</div>

<footer class="foot">
  © 2026 Maison Léa · <a href="/">Accueil</a> · <a href="/affiliation.html">Affiliation</a> · <a href="/mentions-legales.html">Mentions légales</a> · <a href="/confidentialite.html">Confidentialité</a>
</footer>
</body>
</html>
"""


def main():
    products = load_products()
    print(f"📚 {len(products)} produits chargés depuis data.jsx")

    # Génère chaque article
    for a in ARTICLES:
        html = render_article(a, products)
        path = JOURNAL / f"{a['slug']}.html"
        path.write_text(html, encoding="utf-8")
        print(f"✓ {path.name}")

    # Génère l'index
    idx = render_index(ARTICLES)
    (JOURNAL / "index.html").write_text(idx, encoding="utf-8")
    print(f"✓ index.html ({len(ARTICLES)} articles listés)")

    print(f"\n✅ Journal généré dans {JOURNAL}")


if __name__ == "__main__":
    main()
