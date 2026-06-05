#!/usr/bin/env python3
"""
Ajoute de NOUVEAUX articles au journal Maison Léa SANS toucher aux existants.

- Génère les fichiers HTML des articles définis dans NEW_ARTICLES.
- Insère leurs cartes en tête de la grille de journal/index.html (non destructif).
- Sélectionne de vrais produits depuis data.jsx, avec rotation par catégorie
  pour éviter que tous les articles d'une catégorie montrent les mêmes produits.

Usage : python3 scripts/add-articles.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "journal"
DATA_JSX = ROOT / "data.jsx"
PARTNER_TAG = "lebrunnathali-21"


def amazon_url(asin):
    return f"https://www.amazon.fr/dp/{asin}?tag={PARTNER_TAG}"


def load_products():
    """Extrait le tableau PRODUCTS de data.jsx en ignorant les crochets
    présents à l'intérieur des chaînes (ex: un nom produit contenant '[6 ...')."""
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


def render_section_block(title, paragraphs):
    return f"<h2>{title}</h2>\n{render_para_block(paragraphs)}"


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


# Curseur de rotation par catégorie : chaque article consomme les produits suivants
_CURSORS = {}


def select_products(products, article):
    cats = article.get("product_cats") or []
    n = article.get("max_products", 0)
    if not cats or n <= 0:
        return []
    cat = cats[0]
    pool = [p for p in products if p["cat"] in cats]
    if not pool:
        return []
    start = _CURSORS.get(cat, 0)
    selected = [pool[(start + i) % len(pool)] for i in range(min(n, len(pool)))]
    _CURSORS[cat] = (start + n) % len(pool)
    return selected


def render_article(article, products):
    selected = select_products(products, article)
    sections_html = "".join(render_section_block(t, ps) for t, ps in article["sections"])
    products_html = ""
    if selected:
        products_html = "<h2>Notre sélection</h2>\n" + "".join(render_product_card(p) for p in selected)
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

    existing = {p.name.replace(".html", "") for p in JOURNAL.glob("*.html")}
    to_add = [a for a in NEW_ARTICLES if a["slug"] not in existing]
    skipped = [a["slug"] for a in NEW_ARTICLES if a["slug"] in existing]
    if skipped:
        print(f"⏭️  Ignorés (déjà présents) : {', '.join(skipped)}")

    # 1) Génère les fichiers HTML
    for a in to_add:
        (JOURNAL / f"{a['slug']}.html").write_text(render_article(a, products), encoding="utf-8")
        print(f"✓ {a['slug']}.html")

    # 2) Insère les cartes en tête de la grille existante (non destructif)
    index_path = JOURNAL / "index.html"
    html = index_path.read_text(encoding="utf-8")
    anchor = '<div class="articles-grid">\n'
    if anchor not in html:
        anchor = '<div class="articles-grid">'
        cards = "\n    " + "\n    ".join(render_card(a).strip() for a in to_add)
        html = html.replace(anchor, anchor + cards, 1)
    else:
        cards = "    " + "    ".join(render_card(a) for a in to_add)
        html = html.replace(anchor, anchor + cards, 1)
    index_path.write_text(html, encoding="utf-8")
    print(f"✓ index.html : +{len(to_add)} cartes insérées")
    print(f"\n✅ {len(to_add)} nouveaux articles ajoutés.")


# ────────────────────────────────────────────────────────────────────────────
# 20 NOUVEAUX articles (slugs vérifiés inédits)
DISCLAIMER_PRIME = "Tous les produits ci-dessous sont disponibles sur Amazon, souvent en livraison Prime et expédiés en colis neutre — discrétion totale."

NEW_ARTICLES = [
    {
        "slug": "soutien-gorge-balconnet-mettre-en-valeur",
        "kicker": "GUIDE LINGERIE",
        "title": "Le soutien-gorge balconnet : sublimer son décolleté",
        "lead": "Coupe basse, bonnets horizontaux : le balconnet redessine la poitrine et s'invite sous les décolletés. Pour qui, comment, avec quoi.",
        "category": "lingerie", "date": "5 juin 2026", "read": "4 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "Le balconnet est ce soutien-gorge qui remonte joliment la poitrine en laissant le haut des seins découvert. C'est l'allié des décolletés carrés et des tenues un peu habillées — mais encore faut-il choisir la bonne coupe pour sa morphologie.",
        ],
        "sections": [
            ("Ce qui distingue le balconnet", [
                "Ses bonnets sont coupés plus horizontalement que ceux d'un soutien-gorge classique : ils soutiennent par le bas et créent un effet **galbe arrondi**.",
                "Les bretelles sont écartées, souvent posées sur l'extérieur de l'épaule : parfait sous un haut à encolure large.",
            ]),
            ("Pour quelle morphologie", [
                "**Poitrine menue à moyenne** : le balconnet apporte du galbe et un joli arrondi, c'est sa zone de confort.",
                "**Forte poitrine** : privilégie un balconnet à armatures larges et bonnets profonds, sinon le maintien manque. Vérifie toujours le tour de dos.",
            ]),
            ("Avec quoi le porter", [
                "Sous un **décolleté carré ou en cœur**, il épouse la ligne du vêtement sans dépasser.",
                "En ensemble coordonné avec une culotte assortie, il devient une pièce de lingerie à part entière, pas seulement un sous-vêtement.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bon réflexe : si tu hésites entre deux tailles de bonnet, prends la plus grande — un balconnet trop juste écrase au lieu de galber. Le retour est gratuit avec Prime.",
        ],
    },
    {
        "slug": "guepiere-bustier-occasion-speciale-choisir",
        "kicker": "GUIDE LINGERIE",
        "title": "Guêpière ou bustier : la pièce des grandes occasions",
        "lead": "Anniversaire, nuit de noces, soir un peu spécial : guêpière et bustier subliment la silhouette. Comment choisir entre les deux.",
        "category": "lingerie", "date": "5 juin 2026", "read": "4 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "La guêpière et le bustier, c'est la lingerie des moments qu'on a envie de marquer. Plus structurées qu'un simple ensemble, elles dessinent la taille et tiennent la silhouette — un vrai effet seconde peau.",
        ],
        "sections": [
            ("Guêpière, bustier : la différence", [
                "Le **bustier** s'arrête à la taille ou aux hanches : il galbe le buste et peut se porter seul ou sous une tenue.",
                "La **guêpière** descend plus bas et intègre souvent des **jarretelles** pour tenir les bas : c'est la pièce la plus habillée, pensée pour les occasions.",
            ]),
            ("Bien la choisir", [
                "Repère un modèle à **baleines souples** et fermeture par agrafes multiples : il s'ajuste précisément et tient sans comprimer.",
                "Pour une première, choisis une matière **dentelle doublée** : élégante et confortable, sans effet rigide.",
            ]),
            ("La porter avec assurance", [
                "Associe-la à des **bas couture** et des talons pour l'effet complet, ou garde-la seule sous un peignoir en satin.",
                "L'important n'est pas la performance, c'est de te sentir bien : choisis la coupe qui te met à l'aise, pas la plus spectaculaire.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Commande quelques jours à l'avance pour avoir le temps d'essayer tranquillement et, au besoin, d'échanger la taille.",
        ],
    },
    {
        "slug": "chemise-de-nuit-coton-ou-satin-choisir",
        "kicker": "GUIDE NUIT",
        "title": "Chemise de nuit : coton ou satin, laquelle pour toi ?",
        "lead": "Douceur du coton ou glissé du satin : deux philosophies du sommeil. On compare confort, saison et entretien pour t'aider à choisir.",
        "category": "nuit", "date": "5 juin 2026", "read": "4 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "La chemise de nuit revient en force, et pour de bonnes raisons : rien n'enserre, l'air circule, on dort vraiment mieux. Reste à choisir la matière — et le match coton contre satin n'a pas de gagnant universel, juste celui qui te convient.",
        ],
        "sections": [
            ("Le coton : douceur et respirabilité", [
                "Le coton **absorbe l'humidité** et laisse la peau respirer : idéal si tu as chaud la nuit ou la peau sensible.",
                "Côté entretien, il passe en machine sans précaution : un vrai basique du quotidien.",
            ]),
            ("Le satin : glissé et élégance", [
                "Le satin offre une sensation **fraîche et fluide** sur la peau, et un tombé flatteur. C'est la matière du plaisir et de l'occasion.",
                "Plus délicat, il se lave en cycle doux : un petit soin en échange d'une vraie sensation de luxe.",
            ]),
            ("Comment trancher", [
                "**Tu transpires la nuit ou tu cherches le confort pur ?** Coton.",
                "**Tu veux te sentir belle et profiter du toucher soyeux ?** Satin.",
                "Beaucoup finissent par avoir les deux : le coton en semaine, le satin pour les soirs qui comptent.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Astuce taille : les chemises de nuit taillent souvent ample. Si tu aimes le près-du-corps, descends d'une taille ; pour le côté flottant, garde ta taille habituelle.",
        ],
    },
    {
        "slug": "chaussons-cocooning-femme-choisir",
        "kicker": "GUIDE NUIT",
        "title": "Chaussons cocooning : le détail qui change tout",
        "lead": "Le rituel cocooning ne s'arrête pas à la robe de chambre. Le bon chausson tient chaud, dure et fait du bien aux pieds. Comment le choisir.",
        "category": "nuit", "date": "5 juin 2026", "read": "3 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "On y pense rarement, et pourtant : une paire de chaussons douillets transforme une soirée d'hiver. C'est le compagnon naturel du peignoir et de la tisane, le petit luxe du quotidien qui ne coûte presque rien.",
        ],
        "sections": [
            ("Ce qui fait un bon chausson", [
                "Une **semelle antidérapante** : indispensable sur du carrelage ou un parquet.",
                "Un **intérieur en fausse fourrure ou polaire** qui garde la chaleur sans faire transpirer.",
                "Un maintien à l'arrière (mule fermée ou bottillon) si tu as les pieds qui glissent facilement.",
            ]),
            ("Mule, bottillon ou charentaise", [
                "**Mule ouverte à l'arrière** : pratique à enfiler, parfaite pour la maison.",
                "**Bottillon montant** : enveloppe la cheville, idéal pour les frileuses.",
                "**Charentaise revisitée** : la semelle fine pour celles qui veulent sentir le sol.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pense à prendre ta pointure habituelle, voire une demi-pointure au-dessus si le modèle est doublé épais : le pied doit rester libre pour avoir bien chaud.",
        ],
    },
    {
        "slug": "plug-debutant-guide-securite-confort",
        "kicker": "GUIDE BIEN-ÊTRE INTIME",
        "title": "Débuter en douceur : bien choisir son premier plug",
        "lead": "Curieuse mais prudente ? On t'explique calmement comment choisir un premier plug en toute sécurité : taille, matière, et le rôle clé du lubrifiant.",
        "category": "sensualite", "date": "5 juin 2026", "read": "5 min",
        "cover_color": "#1a1a1a", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "La curiosité est légitime, et l'aborder avec de bonnes informations change tout. Pour une première fois, deux mots d'ordre : **petit format** et **beaucoup de lubrifiant**. Voici l'essentiel pour démarrer sereinement.",
        ],
        "sections": [
            ("La taille : commencer petit, vraiment", [
                "Pour débuter, choisis le **plus petit diamètre** disponible. On peut toujours évoluer ensuite ; l'inverse est inconfortable.",
                "Repère une **base large évasée** : c'est l'élément de sécurité essentiel pour que l'accessoire reste toujours sous contrôle.",
            ]),
            ("La matière compte", [
                "Privilégie le **silicone médical** ou le **verre/inox** : non poreux, faciles à nettoyer, sans odeur.",
                "Évite les matières poreuses bas de gamme, plus difficiles à désinfecter.",
            ]),
            ("Lubrifiant et hygiène : non négociables", [
                "Un **lubrifiant à base d'eau** généreux est indispensable — la zone ne s'auto-lubrifie pas. Renouvelle l'application sans hésiter.",
                "Nettoie l'accessoire avant et après chaque usage, à l'eau tiède et au savon doux. Prends ton temps, respire, et arrête à la moindre gêne.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le mot d'ordre : aucune précipitation. Le confort et l'écoute de soi priment sur tout le reste.",
        ],
    },
    {
        "slug": "suceur-clitoridien-air-pulse-comprendre",
        "kicker": "GUIDE BIEN-ÊTRE INTIME",
        "title": "Stimulateur à air pulsé : comprendre la sensation",
        "lead": "Ni vibration, ni contact direct : la technologie à air pulsé a changé la donne. On t'explique simplement comment ça marche et comment bien choisir.",
        "category": "sensualite", "date": "5 juin 2026", "read": "4 min",
        "cover_color": "#1a1a1a", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "Les stimulateurs dits « à air pulsé » ou « suceurs » ont une particularité : ils n'appuient pas sur le clitoris, ils créent de petites ondes d'air et de pression. Une sensation différente de la vibration classique, que beaucoup décrivent comme plus douce et plus enveloppante.",
        ],
        "sections": [
            ("Comment ça fonctionne", [
                "Une petite buse posée **autour** (et non sur) la zone émet des variations de pression d'air. Pas de friction directe, donc une sensation moins « mécanique ».",
                "C'est ce qui explique le succès de ces modèles auprès de celles que les vibrations frontales agacent.",
            ]),
            ("Bien le choisir", [
                "Cherche un modèle **étanche** (usage sous la douche et nettoyage facile) et **rechargeable par USB**.",
                "Plusieurs intensités progressives valent mieux qu'une seule trop forte : on monte à son rythme.",
                "Le silicone médical sur la buse est un gage de douceur et d'hygiène.",
            ]),
            ("Avec un peu de lubrifiant", [
                "Une noisette de **lubrifiant à base d'eau** améliore nettement le confort et l'effet de succion. À tester pour trouver sa bonne intensité.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Comme toujours, on commence sur l'intensité la plus basse et on remonte tranquillement.",
        ],
    },
    {
        "slug": "huile-massage-chauffante-sensation-couple",
        "kicker": "RITUEL COUPLE",
        "title": "Huile de massage chauffante : la chaleur qui détend",
        "lead": "Un effet de douce chaleur au contact de la peau : l'huile chauffante transforme un massage en vrai moment sensoriel. Comment la choisir et l'utiliser.",
        "category": "soins", "date": "5 juin 2026", "read": "3 min",
        "cover_color": "#c9a961", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "L'huile de massage chauffante développe une sensation de chaleur agréable dès qu'on la masse ou qu'on souffle dessus. C'est un petit effet de surprise qui rend le moment plus enveloppant — et un excellent prétexte pour ralentir à deux.",
        ],
        "sections": [
            ("L'effet chauffant, comment ça marche", [
                "La chaleur vient d'ingrédients qui réagissent au contact et au souffle. Elle reste **douce et progressive**, jamais brûlante sur un produit de qualité.",
                "Certaines huiles sont aussi **comestibles** : pratique pour un massage qui se prolonge sans contrainte.",
            ]),
            ("Bien la choisir", [
                "Vérifie une **liste d'ingrédients courte** et une mention « testée dermatologiquement » si tu as la peau réactive.",
                "Fais toujours un **test au pli du coude** avant la première utilisation : l'effet chauffant doit être agréable, pas irritant.",
            ]),
            ("Le rituel", [
                "Chauffe quelques gouttes entre les mains, commence par le dos et les épaules, puis souffle doucement pour réveiller la chaleur.",
                "Lumière tamisée, téléphone loin : l'huile fait la moitié du travail, l'attention fait le reste.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Évite le contact avec les yeux et les muqueuses sensibles, et garde un lubrifiant dédié à part : une huile de massage n'est pas un lubrifiant intime.",
        ],
    },
    {
        "slug": "gommage-corps-peau-douce-rituel-maison",
        "kicker": "RITUEL SOINS",
        "title": "Gommage corps : le secret d'une peau douce",
        "lead": "Avant l'hydratation, il y a le gommage. Une étape simple qui rend la peau plus douce, plus lumineuse et prête à recevoir les soins. Mode d'emploi.",
        "category": "soins", "date": "5 juin 2026", "read": "3 min",
        "cover_color": "#c9a961", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "Une peau de pêche, ça commence par le gommage. En éliminant les cellules mortes en surface, on révèle une peau plus douce et on aide les crèmes à mieux pénétrer. C'est l'un des gestes les plus satisfaisants du rituel beauté maison.",
        ],
        "sections": [
            ("Grain fin ou grain épais", [
                "**Grain fin (sucre, jojoba)** : doux, parfait pour le corps entier et les peaux sensibles, une à deux fois par semaine.",
                "**Grain plus épais (sel, noyaux)** : idéal sur les zones rugueuses comme les coudes, les genoux et les talons.",
            ]),
            ("Le bon geste", [
                "Sur peau humide, masse en **mouvements circulaires** des chevilles vers le cœur — ça stimule aussi la circulation.",
                "Rince à l'eau tiède, sèche en tapotant, puis applique tout de suite une **huile ou un lait** : la peau encore tiède absorbe mieux.",
            ]),
            ("À quelle fréquence", [
                "Une à deux fois par semaine suffit largement. Trop fréquent, le gommage fragilise la barrière de la peau.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Évite le gommage juste après l'épilation ou sur une peau irritée : laisse-lui 24 à 48 h pour récupérer.",
        ],
    },
    {
        "slug": "coffret-cadeau-pour-lui-idees-homme",
        "kicker": "IDÉES CADEAUX",
        "title": "Coffret cadeau pour lui : des idées qui font mouche",
        "lead": "Anniversaire, fête, juste pour le plaisir : un coffret bien choisi vaut mille cravates. Nos pistes pour gâter un homme sans se tromper.",
        "category": "cadeaux", "date": "5 juin 2026", "read": "4 min",
        "cover_color": "#b07d2b", "product_cats": ["cadeaux"], "max_products": 3,
        "intro": [
            "Offrir à un homme tourne vite au casse-tête. La bonne nouvelle : un coffret prêt-à-offrir règle tout — c'est joli, complet, et ça montre l'attention sans avoir à tout composer soi-même.",
        ],
        "sections": [
            ("Les valeurs sûres", [
                "**Coffret soin et rasage** : un classique qui plaît, surtout en version naturelle et bien parfumée.",
                "**Coffret bien-être à deux** : bougie de massage, huile, accessoires — l'idée parfaite pour un cadeau qui se partage.",
                "**Coffret expérience** : un moment à vivre plutôt qu'un objet, souvent le souvenir le plus marquant.",
            ]),
            ("Comment ne pas se tromper", [
                "Pars de **ce qu'il aime déjà** : un homme qui soigne sa barbe, un amateur de cocooning, un curieux des sens.",
                "Vérifie la **présentation** : un coffret se juge aussi à son emballage, c'est ce qu'il voit en premier.",
            ]),
            ("Le petit plus", [
                "Glisse un **mot manuscrit** : c'est gratuit et ça transforme n'importe quel coffret en cadeau personnel.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Commande quelques jours avant la date : tu auras le choix des modèles et le temps de soigner l'emballage.",
        ],
    },
    {
        "slug": "jeu-de-des-coquin-pimenter-couple",
        "kicker": "JEUX DE COUPLE",
        "title": "Jeu de dés coquin : pimenter la soirée en riant",
        "lead": "Un accessoire minuscule, zéro pression et beaucoup de complicité : le jeu de dés est la façon la plus légère de réveiller la soirée à deux.",
        "category": "erotisme", "date": "5 juin 2026", "read": "3 min",
        "cover_color": "#3a1a26", "product_cats": ["erotisme"], "max_products": 3,
        "intro": [
            "Pas besoin de grands moyens pour casser la routine : un jeu de dés coquin tient dans une poche et désamorce la gêne par le rire. On lance, on suit la consigne, et la conversation prend un tout autre tour.",
        ],
        "sections": [
            ("Le principe, tout simple", [
                "Chaque dé porte des **actions** (embrasser, caresser, souffler…) et des **zones** (cou, épaule, main…). On lance, on combine, on s'amuse.",
                "Aucune règle compliquée : c'est justement la légèreté qui marche. Le jeu sert de prétexte, le reste vient naturellement.",
            ]),
            ("Bien le choisir", [
                "Les versions **douces** suffisent largement pour débuter : elles instaurent le jeu sans intimider.",
                "Certains coffrets ajoutent des dés **plus audacieux** : à réserver quand la complicité est déjà installée.",
            ]),
            ("Pour que ça marche", [
                "La règle d'or : on peut **toujours repasser son tour**. La complicité grandit dans le respect du rythme de chacun.",
                "Une bougie, un verre, le téléphone en silencieux : le décor compte autant que le jeu.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Idée : glisse-le dans un sac week-end. C'est le genre de petit objet qui transforme un soir d'hôtel en souvenir.",
        ],
    },
    {
        "slug": "ensemble-lingerie-dentelle-assortir-guide",
        "kicker": "GUIDE LINGERIE",
        "title": "Ensemble de lingerie en dentelle : l'art de bien assortir",
        "lead": "Soutien-gorge et culotte coordonnés : pourquoi ça change tout, et comment composer un ensemble qui te ressemble.",
        "category": "lingerie", "date": "31 mai 2026", "read": "4 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "Porter un ensemble assorti, ce n'est pas une question de coquetterie : c'est un petit rituel d'attention à soi. La dentelle, en particulier, a ce pouvoir de transformer une journée ordinaire en quelque chose d'un peu plus précieux.",
        ],
        "sections": [
            ("Pourquoi l'ensemble coordonné fait la différence", [
                "Un soutien-gorge et une culotte de la même collection partagent la coupe, la teinte et le motif de dentelle : visuellement, la silhouette est plus harmonieuse.",
                "Psychologiquement, l'effet est réel : on se sent **posée, soignée, prête**. Et ça se voit dans la posture, même habillée par-dessus.",
            ]),
            ("Les associations qui fonctionnent toujours", [
                "**Dentelle noire** : intemporelle, flatteuse sur toutes les carnations, parfaite pour débuter une collection.",
                "**Tons nude et poudrés** : invisibles sous les vêtements clairs, élégants au quotidien.",
                "**Bordeaux, émeraude, bleu nuit** : les couleurs profondes subliment sans tomber dans le cliché.",
            ]),
            ("Composer sans se ruiner", [
                "Pas besoin d'acheter dix ensembles. **Deux ou trois bien choisis**, dans des coupes que tu sais flatteuses, valent mieux qu'un tiroir plein de pièces jamais portées.",
                "Astuce : un même soutien-gorge en dentelle peut s'associer à plusieurs culottes (string, tanga, shorty) pour multiplier les combinaisons.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bon réflexe : commande ta taille habituelle **et** la taille au-dessus si la marque est nouvelle pour toi. Le retour est gratuit avec Prime, autant essayer tranquillement chez soi.",
        ],
    },
    {
        "slug": "lingerie-grande-taille-sublimer-courbes",
        "kicker": "GUIDE LINGERIE",
        "title": "Lingerie grande taille : sublimer ses courbes avec confort",
        "lead": "Maintien, coupes flatteuses, matières qui ne marquent pas : le guide pour se sentir bien dans sa lingerie, quelle que soit sa taille.",
        "category": "lingerie", "date": "31 mai 2026", "read": "5 min",
        "cover_color": "#5b1a26", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "Trop longtemps, la lingerie grande taille s'est résumée à du fonctionnel beige sans charme. Heureusement, l'offre a explosé : aujourd'hui, on trouve des pièces aussi belles que confortables jusqu'aux grands bonnets et grandes tailles.",
        ],
        "sections": [
            ("Le maintien sans sacrifier l'esthétique", [
                "Pour les poitrines généreuses, cherche des **bonnets entièrement doublés** et des **bretelles larges et réglables** : c'est le secret d'un maintien confortable toute la journée.",
                "La **bande de dessous large** (4 cm et plus) répartit le poids et évite que le soutien-gorge ne remonte dans le dos.",
            ]),
            ("Les coupes qui flattent les courbes", [
                "**Le balconnet** : remonte joliment la poitrine et dessine un beau décolleté.",
                "**La culotte taille haute** : gaine doucement le ventre et allonge la silhouette.",
                "**Le body stretch** : épouse les formes sans comprimer, look élégant sous une robe.",
            ]),
            ("Les matières à privilégier", [
                "Le **microfibre stretch** épouse sans serrer et ne marque pas. La **dentelle élastique** ajoute du charme tout en s'adaptant aux courbes.",
                "Évite les élastiques fins et rigides qui cisaillent : préfère les **bords larges et doux**.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le confort d'abord, toujours. Une belle pièce qu'on n'ose pas garder une journée entière ne sert à rien — choisis ce dans quoi tu te sens libre de bouger.",
        ],
    },
    {
        "slug": "couleur-lingerie-selon-carnation-choisir",
        "kicker": "TENDANCE",
        "title": "Quelle couleur de lingerie selon sa carnation ?",
        "lead": "Le nude n'est pas universel, et le noir ne va pas qu'aux brunes. Petit guide des teintes qui subliment vraiment.",
        "category": "lingerie", "date": "30 mai 2026", "read": "3 min",
        "cover_color": "#a04848", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "On choisit souvent sa lingerie par habitude — noir, blanc, beige. Pourtant, comme pour le maquillage, certaines teintes illuminent la peau quand d'autres l'éteignent. Voici comment viser juste.",
        ],
        "sections": [
            ("Le vrai \"nude\", c'est le tien", [
                "Le nude invisible sous les vêtements n'est pas le beige standard : c'est la teinte **la plus proche de ta propre peau**. Les marques proposent désormais 5 à 8 nuances de nude — choisis la tienne.",
                "Test simple : pose la pièce sur l'intérieur de ton avant-bras. Si elle \"disparaît\", c'est la bonne.",
            ]),
            ("Carnations claires", [
                "Les **pastels** (rose poudré, lavande, bleu ciel) et les **teintes froides** (bordeaux, prune) illuminent les peaux claires.",
                "Le blanc pur peut durcir : préfère l'ivoire ou le crème.",
            ]),
            ("Carnations mates et foncées", [
                "Les **couleurs vives et chaudes** (corail, fuchsia, or, émeraude) éclatent magnifiquement sur les peaux mates et foncées.",
                "Le blanc et les nudes très clairs créent un joli contraste graphique.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La règle au-dessus de toutes les règles : porte ce qui te fait plaisir. Ces repères sont là pour ouvrir le champ, pas pour t'enfermer.",
        ],
    },
    {
        "slug": "string-tanga-shorty-quelle-culotte-choisir",
        "kicker": "GUIDE LINGERIE",
        "title": "String, tanga, shorty : quelle culotte pour quelle occasion ?",
        "lead": "Chaque coupe a son usage. Le guide pour ne plus jamais avoir de marques disgracieuses sous les vêtements.",
        "category": "lingerie", "date": "30 mai 2026", "read": "4 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "La bonne culotte, ce n'est pas une question de mode mais de contexte. Sous un jean, sous une robe moulante, pour le sport ou pour un soir : chaque coupe a sa raison d'être. Petit tour d'horizon.",
        ],
        "sections": [
            ("Le string : l'anti-marques absolu", [
                "Indispensable sous les **vêtements moulants** (robe en maille, pantalon clair) où aucune ligne de culotte ne doit apparaître.",
                "Privilégie une **ceinture fine et plate** et un tissu doux pour le confort prolongé.",
            ]),
            ("Le tanga : le compromis confort/discrétion", [
                "Plus couvrant que le string à l'arrière, plus discret que la culotte classique. **Le meilleur choix au quotidien** pour beaucoup de femmes.",
                "Parfait sous un jean ou un pantalon de tailleur.",
            ]),
            ("Le shorty : confort et style rétro", [
                "Couvrant, doux, idéal pour les **jours \"cocooning\"**, les règles, ou sous une jupe l'hiver.",
                "En dentelle, il devient une pièce glamour à part entière.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "L'idéal : avoir les trois coupes dans son tiroir et piocher selon la tenue du jour. La culotte, c'est la base invisible qui fait que tout le reste tombe bien.",
        ],
    },
    {
        "slug": "nuisette-dentelle-morphologie-choisir",
        "kicker": "GUIDE NUIT",
        "title": "Nuisette en dentelle : la choisir selon sa morphologie",
        "lead": "Toutes les nuisettes ne flattent pas toutes les silhouettes. Voici comment trouver la coupe qui te met en valeur.",
        "category": "nuit", "date": "30 mai 2026", "read": "4 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "La nuisette en dentelle est une des pièces les plus flatteuses du dressing intime — à condition de choisir la coupe adaptée à sa silhouette. La bonne nuisette donne l'impression d'avoir été dessinée pour toi.",
        ],
        "sections": [
            ("Silhouette en A (hanches marquées)", [
                "Préfère une **coupe évasée trapèze** qui s'ouvre sous la poitrine : elle fluidifie la ligne des hanches.",
                "Les détails (dentelle, broderie) en haut attirent le regard vers le visage.",
            ]),
            ("Silhouette en V (épaules larges)", [
                "Un **décolleté plongeant** et des bretelles fines équilibrent le haut du corps.",
                "Évite les empiècements volumineux aux épaules.",
            ]),
            ("Silhouette en sablier ou ronde", [
                "La **slip dress près du corps** sublime les courbes harmonieuses.",
                "Pour les rondeurs, une coupe semi-ajustée avec une **taille légèrement soulignée** flatte sans mouler.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le secret d'une nuisette réussie : elle doit tenir sans que tu aies à la rajuster. Si tu remontes les bretelles toutes les cinq minutes, change de taille.",
        ],
    },
    {
        "slug": "peignoir-satin-elegance-reveil-choisir",
        "kicker": "GUIDE NUIT",
        "title": "Peignoir en satin : l'élégance dès le réveil",
        "lead": "Le geste qui transforme un café du matin en moment d'hôtel de luxe. Comment choisir le bon peignoir satin.",
        "category": "nuit", "date": "29 mai 2026", "read": "3 min",
        "cover_color": "#241c16", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "Enfiler un peignoir en satin le matin, c'est s'offrir trois minutes d'élégance avant que la journée ne commence. Petit objet de plaisir, le bon modèle se choisit sur quelques détails.",
        ],
        "sections": [
            ("Satin de qualité : ce qui change", [
                "Cherche un **satin épais et fluide** (viscose ou polyester haute densité) : il tombe bien et ne devient pas transparent.",
                "Le satin de soie, plus cher, est respirant et thermorégulateur — le summum si tu adoptes vraiment la pièce.",
            ]),
            ("La bonne longueur", [
                "**Court (mi-cuisse)** : léger, parfait pour l'été ou par-dessus une nuisette.",
                "**Long (cheville)** : ambiance robe de chambre de palace, idéal pour les matins d'hiver et les soirées détente.",
            ]),
            ("Les finitions qui font le luxe", [
                "Une **ceinture large nouée**, des **manches kimono** ou des **revers contrastés** élèvent immédiatement l'allure.",
                "Vérifie les coutures : sur le satin, elles doivent être nettes et plates.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un peignoir satin de qualité dure des années si tu le laves à froid sur cycle délicat. C'est aussi une idée cadeau qui ne déçoit jamais.",
        ],
    },
    {
        "slug": "tenue-nuit-ete-respirante-bien-dormir",
        "kicker": "GUIDE NUIT",
        "title": "Bien dormir l'été : la tenue de nuit idéale",
        "lead": "Quand il fait chaud, le choix du tissu fait toute la différence. Nos conseils pour des nuits fraîches et confortables.",
        "category": "nuit", "date": "29 mai 2026", "read": "3 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "Les nuits d'été, on se retourne, on a chaud, on finit par enlever le drap. La tenue de nuit y est pour beaucoup : certaines matières emprisonnent la chaleur, d'autres la laissent filer. Voici comment bien choisir.",
        ],
        "sections": [
            ("Les matières qui respirent", [
                "**Le coton léger** et la **viscose** absorbent l'humidité et laissent circuler l'air.",
                "**La soie et le satin de soie** sont thermorégulateurs : frais en été, doux en hiver.",
                "À éviter en pleine canicule : le polyester épais, qui fait transpirer.",
            ]),
            ("Les coupes à privilégier", [
                "**Nuisette courte et fluide** : un classique de l'été, légère et flatteuse.",
                "**Short + caraco** : liberté de mouvement maximale.",
                "Les coupes amples laissent la peau respirer mieux que les modèles près du corps.",
            ]),
            ("Le petit plus pour les nuits chaudes", [
                "Garde une pièce de rechange à portée de main : changer de tenue au milieu de la nuit aide à se rendormir.",
                "Un tissu clair renvoie mieux la chaleur qu'un tissu foncé.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Mieux dormir l'été tient souvent à des détails : une matière respirante et une coupe ample suffisent à transformer tes nuits.",
        ],
    },
    {
        "slug": "caraco-short-pyjama-duo-confort",
        "kicker": "GUIDE NUIT",
        "title": "Caraco et short : le duo pyjama confort par excellence",
        "lead": "Léger, féminin, polyvalent : pourquoi l'ensemble caraco-short est devenu le pyjama préféré de toutes les saisons.",
        "category": "nuit", "date": "28 mai 2026", "read": "3 min",
        "cover_color": "#241c16", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "Entre le pyjama d'hiver enveloppant et la nuisette glamour, il y a un terrain idéal : l'ensemble caraco + short. Confortable, joli, et assez polyvalent pour traîner un dimanche comme pour dormir.",
        ],
        "sections": [
            ("Pourquoi ça marche si bien", [
                "**Liberté de mouvement** totale : ni manche qui gêne, ni jambe qui entortille.",
                "**Modulable** : on peut dormir avec le caraco seul quand il fait chaud, ajouter le short quand il fait frais.",
                "**Flatteur** : le caraco souligne la taille, le short allonge la jambe.",
            ]),
            ("Les matières selon la saison", [
                "**Satin ou viscose** pour l'effet glamour et la fraîcheur estivale.",
                "**Coton ou modal** pour la douceur et l'absorption au quotidien.",
            ]),
            ("Bien choisir la taille", [
                "Le caraco doit tenir sans bâiller au niveau de la poitrine ; le short doit avoir une **ceinture élastique douce** qui ne marque pas.",
                "En cas de doute entre deux tailles sur du satin glissant, prends la plus grande.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un bon ensemble caraco-short se garde des années et s'assortit facilement à un kimono ou un peignoir pour les matins où on reçoit.",
        ],
    },
    {
        "slug": "vibromasseur-point-g-comprendre-courbe",
        "kicker": "SENSUALITÉ",
        "title": "Vibromasseur point G : comprendre la courbe",
        "lead": "Cette forme incurvée n'est pas un hasard. On t'explique à quoi elle sert et comment bien choisir.",
        "category": "sensualite", "date": "28 mai 2026", "read": "5 min",
        "cover_color": "#1a1a1a", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "Tu as sûrement remarqué que certains vibromasseurs ont une **extrémité incurvée**. Ce n'est pas un détail esthétique : cette courbe est pensée pour atteindre une zone précise. Voici tout ce qu'il faut comprendre avant d'acheter.",
        ],
        "sections": [
            ("À quoi sert la courbe", [
                "La courbe permet d'atteindre le **point G**, situé sur la paroi avant, à quelques centimètres de l'entrée. C'est une zone difficile à stimuler avec un objet droit.",
                "L'extrémité est souvent plus large ou bombée pour appliquer une pression ciblée.",
            ]),
            ("Les critères d'achat", [
                "**Silicone médical** : la seule matière à privilégier pour le corps, douce et facile à nettoyer.",
                "**Rechargeable USB** et **étanche (IPX7)** : pratique et durable.",
                "**Plusieurs intensités et modes** : la découverte de cette zone demande de varier doucement.",
            ]),
            ("Conseils pour bien débuter", [
                "Utilise toujours un **lubrifiant à base d'eau** (compatible silicone) : le confort change tout.",
                "Prends ton temps, sans objectif de performance. La détente est la première condition du plaisir.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Budget conseillé pour un bon premier modèle : 30 à 80 €. Inutile de viser le haut de gamme tout de suite — l'important est de découvrir ce qui te convient.",
        ],
    },
    {
        "slug": "wand-vibromasseur-puissant-mode-emploi",
        "kicker": "SENSUALITÉ",
        "title": "Le wand : le vibromasseur puissant, mode d'emploi",
        "lead": "Grosse tête arrondie, vibrations profondes : le wand est une catégorie à part. À qui s'adresse-t-il ?",
        "category": "sensualite", "date": "27 mai 2026", "read": "5 min",
        "cover_color": "#1a1a1a", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "Reconnaissable à son long manche et sa tête arrondie souple, le **wand** (parfois appelé \"masseur baguette\") est connu pour ses vibrations profondes et enveloppantes. C'est l'un des accessoires les plus appréciés — mais il ne convient pas à tout le monde de la même manière.",
        ],
        "sections": [
            ("Une stimulation large et profonde", [
                "Contrairement aux modèles ciblés, le wand diffuse des **vibrations amples sur une grande surface**. Idéal pour qui aime une stimulation enveloppante plutôt que pointue.",
                "Il sert aussi de vrai **masseur musculaire** (nuque, dos) — un double usage que beaucoup apprécient.",
            ]),
            ("Bien doser la puissance", [
                "Les wands sont souvent puissants : commence par le **mode le plus doux**, éventuellement à travers un vêtement, puis augmente progressivement.",
                "Cherche un modèle avec **plusieurs niveaux** plutôt qu'un seul réglage trop intense.",
            ]),
            ("Filaire ou rechargeable ?", [
                "Les **modèles rechargeables** offrent la liberté de mouvement et sont silencieux ; les modèles secteur délivrent une puissance constante.",
                "Vérifie que la tête est en **silicone** et, idéalement, **détachable** pour le nettoyage.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le wand est un excellent investissement polyvalent : plaisir et détente musculaire dans le même objet. Choisis un modèle reconnu plutôt qu'une copie bas de gamme.",
        ],
    },
    {
        "slug": "anneau-vibrant-couple-plaisir-partage",
        "kicker": "SENSUALITÉ",
        "title": "Anneau vibrant : le plaisir partagé, simplement",
        "lead": "Petit accessoire, grand effet à deux. Comment ça marche et comment bien le choisir pour le couple.",
        "category": "sensualite", "date": "27 mai 2026", "read": "4 min",
        "cover_color": "#1a1a1a", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "L'anneau vibrant est l'un des rares accessoires pensés d'emblée pour le couple. Discret, simple d'utilisation et abordable, c'est souvent une excellente première expérience d'achat à deux.",
        ],
        "sections": [
            ("Le principe", [
                "C'est un **anneau souple en silicone** muni d'un petit moteur vibrant. Porté par l'homme, il procure des sensations aux deux partenaires pendant le rapport.",
                "Certains modèles sont **rechargeables**, d'autres jetables avec une pile intégrée — préfère les rechargeables, plus durables.",
            ]),
            ("Bien le choisir", [
                "**Silicone extensible** : confortable et adaptable à toutes les morphologies.",
                "**Moteur silencieux et plusieurs intensités** pour varier les sensations.",
                "Vérifie qu'il est **lavable et étanche** pour un nettoyage facile.",
            ]),
            ("Conseils d'usage", [
                "Associez-le à un **lubrifiant à base d'eau** pour le confort.",
                "Communiquez : l'intérêt de l'accessoire de couple, c'est d'ajuster ensemble ce qui plaît à chacun.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pour un premier achat à deux, l'anneau vibrant est idéal : peu intimidant, peu coûteux, et un vrai support de complicité.",
        ],
    },
    {
        "slug": "boules-geisha-perinee-plaisir-guide",
        "kicker": "SENSUALITÉ",
        "title": "Boules de geisha : plaisir et tonus du périnée",
        "lead": "Entre bien-être, rééducation et sensualité : tout comprendre sur les boules de geisha et comment débuter.",
        "category": "sensualite", "date": "26 mai 2026", "read": "5 min",
        "cover_color": "#1a1a1a", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "Les boules de geisha (ou \"boules de Kegel\") ont une double réputation : accessoire de bien-être pour **tonifier le périnée**, et objet de sensualité. Les deux sont vrais — voici comment les aborder sereinement.",
        ],
        "sections": [
            ("À quoi elles servent", [
                "En se contractant pour les maintenir, on **muscle naturellement le plancher pelvien** — utile après une grossesse ou simplement pour l'entretien.",
                "Le mouvement interne des billes procure aussi des **sensations subtiles** appréciées au quotidien.",
            ]),
            ("Bien débuter", [
                "Commence par un modèle **unique et plutôt léger**, en silicone médical, avec un **cordon de retrait**.",
                "Porte-les quelques minutes par jour au début, puis augmente progressivement.",
                "Un **lubrifiant à base d'eau** facilite la mise en place.",
            ]),
            ("Hygiène et sécurité", [
                "Lave-les avant et après chaque usage à l'eau tiède et au savon doux.",
                "Choisis impérativement du **silicone médical sans phtalates** : on évite les matières poreuses bas de gamme.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "En cas de doute après une grossesse ou un souci de santé, un avis de sage-femme ou de kiné spécialisé reste la meilleure boussole avant de commencer.",
        ],
    },
    {
        "slug": "bondage-leger-debuter-menottes-foulards",
        "kicker": "ÉROTISME",
        "title": "Bondage léger : débuter en douceur (menottes, foulards)",
        "lead": "Jeux de pouvoir et lâcher-prise, version accessible. Comment explorer en confiance et en sécurité.",
        "category": "erotisme", "date": "26 mai 2026", "read": "5 min",
        "cover_color": "#3a1a26", "product_cats": ["erotisme", "sensualite"], "max_products": 3,
        "intro": [
            "Le \"bondage léger\" — bandeau sur les yeux, menottes douces, foulards — est une porte d'entrée accessible vers le jeu de rôle et le lâcher-prise à deux. Pas besoin de mise en scène compliquée : juste un peu de complicité et quelques règles simples.",
        ],
        "sections": [
            ("Commencer par le plus simple", [
                "**Le bandeau sur les yeux** est l'accessoire le plus doux : il décuple les autres sens sans aucune contrainte physique.",
                "**Les menottes en velours ou les liens en tissu** viennent ensuite : confortables et faciles à retirer.",
            ]),
            ("La règle d'or : le consentement et le mot d'arrêt", [
                "Avant de jouer, décidez ensemble d'un **mot d'arrêt** clair qui stoppe tout immédiatement.",
                "Le jeu repose sur la **confiance** : on avance par petits pas, en vérifiant que chacun est à l'aise.",
            ]),
            ("La sécurité, toujours", [
                "Ne serrez jamais un lien au point de couper la circulation : on doit pouvoir glisser un doigt.",
                "Préférez des **attaches à ouverture rapide** et gardez de quoi libérer facilement à portée de main.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bondage léger n'est pas une affaire de matériel mais de confiance et de communication. Le bon accessoire est simplement celui qui vous met tous les deux en confiance.",
        ],
    },
    {
        "slug": "des-jeux-coquins-soiree-couple",
        "kicker": "ÉROTISME",
        "title": "Dés et jeux coquins : pimenter une soirée à deux",
        "lead": "Sans pression et avec le sourire : les jeux qui relancent la complicité et ouvrent la conversation.",
        "category": "erotisme", "date": "25 mai 2026", "read": "4 min",
        "cover_color": "#3a1a26", "product_cats": ["erotisme"], "max_products": 3,
        "intro": [
            "Les jeux coquins ont un mérite que peu d'accessoires ont : ils **brisent la routine en douceur**, par le jeu et le rire, sans aucune pression de performance. Dés, cartes, défis — il y en a pour toutes les humeurs.",
        ],
        "sections": [
            ("Les dés coquins : le format express", [
                "Un dé \"action\" + un dé \"zone\" : on lance, on suit. Simple, ludique, parfait pour une fin de soirée détendue.",
                "Idéal pour les couples qui veulent tester sans s'engager dans une longue partie.",
            ]),
            ("Les jeux de cartes : la montée en complicité", [
                "Les éditions modernes (cartes à défis, questions, niveaux ajustables) sont **bien écrites et esthétiques**, loin des clichés des années 90.",
                "Le vrai bonus : elles ouvrent des **conversations** sur ce qui plaît à chacun, sans avoir à \"poser la question\".",
            ]),
            ("Choisir le bon niveau", [
                "La plupart des jeux proposent une **progression** (suggestif → osé). Commencez doux, vous monterez si l'envie est là.",
                "Discrétion garantie : livraison en colis neutre.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le meilleur jeu est celui qui vous fait rire ensemble. La complicité d'abord, le reste suit naturellement.",
        ],
    },
    {
        "slug": "lecture-erotique-par-quel-livre-commencer",
        "kicker": "ÉROTISME",
        "title": "Lecture érotique : par quel livre commencer ?",
        "lead": "Pour soi ou à deux, la littérature sensuelle a ce pouvoir d'éveiller l'imaginaire. Nos repères pour bien démarrer.",
        "category": "erotisme", "date": "25 mai 2026", "read": "4 min",
        "cover_color": "#3a1a26", "product_cats": ["erotisme"], "max_products": 3,
        "intro": [
            "Avant tout accessoire, il y a l'imaginaire. La lecture érotique réveille le désir en douceur, stimule la curiosité et peut même devenir un jeu à deux (se lire un passage à voix haute, par exemple). Encore faut-il savoir par où commencer.",
        ],
        "sections": [
            ("Les genres pour débuter", [
                "**La romance sensuelle** : l'histoire prime, les scènes sont suggérées plus que crues. Parfait pour s'initier en douceur.",
                "**Les recueils de nouvelles** : courts, variés, on picore selon l'humeur.",
                "**Les guides illustrés** : pour qui préfère apprendre et explorer avec des repères concrets.",
            ]),
            ("Lire à deux", [
                "Choisissez un passage et lisez-le à voix haute l'un pour l'autre : c'est un excellent **brise-glace** et un jeu de complicité.",
                "Ça ouvre la porte à parler de ses envies sans avoir à les formuler frontalement.",
            ]),
            ("Le format qui vous convient", [
                "**Livre papier** pour le plaisir de l'objet, **liseuse** pour la discrétion absolue dans les transports.",
                "Beaucoup de titres existent en édition poche à petit prix pour tester sans se ruiner.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pas de \"bon\" ou \"mauvais\" goût en la matière : suis ta curiosité. Le bon livre est celui qui te donne envie de tourner la page.",
        ],
    },
    {
        "slug": "gel-retardant-comprendre-utiliser",
        "kicker": "SOINS INTIMES",
        "title": "Gel retardant : comprendre et bien l'utiliser",
        "lead": "Un produit utile et décomplexé pour profiter plus longtemps à deux. Mode d'emploi et précautions.",
        "category": "soins", "date": "24 mai 2026", "read": "4 min",
        "cover_color": "#c9a961", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "Parler de gel retardant n'a rien de tabou : c'est un produit simple, qui aide à prolonger les moments à deux. Comme tout soin intime, il s'utilise correctement et avec quelques précautions. Voici l'essentiel.",
        ],
        "sections": [
            ("Comment ça fonctionne", [
                "Le gel contient un **agent légèrement désensibilisant** qui réduit la sensibilité de manière temporaire et localisée.",
                "L'effet dure le temps d'un rapport et disparaît ensuite.",
            ]),
            ("Le bon usage", [
                "Applique une **petite quantité** quelques minutes avant, puis essuie l'excédent pour ne pas transférer le produit au partenaire.",
                "Commence toujours par une **dose minimale** : on peut en remettre, on ne peut pas en enlever.",
            ]),
            ("Précautions", [
                "Vérifie la **compatibilité avec les préservatifs** (la plupart des gels à base d'eau le sont).",
                "Fais un **test sur une petite zone** la première fois pour écarter toute réaction.",
                "En cas d'irritation ou de doute, demande conseil à un pharmacien.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Utilisé avec modération et bon sens, c'est un petit coup de pouce sans complexe. La communication dans le couple reste, comme toujours, le meilleur des \"produits\".",
        ],
    },
    {
        "slug": "soin-intime-ph-equilibre-routine",
        "kicker": "SOINS INTIMES",
        "title": "Soin intime : respecter son pH au quotidien",
        "lead": "La zone intime a un équilibre fragile. Quels produits choisir, lesquels éviter, et la routine qui respecte tout ça.",
        "category": "soins", "date": "24 mai 2026", "read": "5 min",
        "cover_color": "#c9a961", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "La zone intime se nettoie et s'entretient avec douceur : son équilibre (le fameux pH) est fragile, et les produits trop agressifs font souvent plus de mal que de bien. Voici une routine simple et respectueuse.",
        ],
        "sections": [
            ("Comprendre le pH intime", [
                "La flore intime est naturellement **légèrement acide** (pH autour de 4 à 5), ce qui la protège des déséquilibres.",
                "Un savon classique (pH 9-10) casse cet équilibre : d'où l'intérêt d'un **soin spécifique au pH adapté**.",
            ]),
            ("Ce qu'il faut éviter", [
                "**Les douches internes** : inutiles et souvent contre-productives, la zone se nettoie d'elle-même.",
                "**Les parfums et savons agressifs** : irritants, ils favorisent les déséquilibres.",
                "Le \"trop\" est l'ennemi : un nettoyage doux **une fois par jour** suffit.",
            ]),
            ("La routine douce", [
                "Un **gel intime au pH physiologique**, sans savon ni parfum agressif, appliqué à l'extérieur uniquement.",
                "Des sous-vêtements en **coton respirant** complètent l'hygiène au quotidien.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "En cas d'inconfort persistant (démangeaisons, odeur inhabituelle), aucun produit ne remplace l'avis d'un professionnel de santé : consulte sans hésiter.",
        ],
    },
    {
        "slug": "huile-massage-parfumee-ou-neutre-choisir",
        "kicker": "SOINS INTIMES",
        "title": "Huile de massage : parfumée ou neutre, laquelle choisir ?",
        "lead": "Le bon support transforme un massage. On t'aide à choisir entre les textures, les parfums et les formules.",
        "category": "soins", "date": "23 mai 2026", "read": "4 min",
        "cover_color": "#c9a961", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "Une huile de massage, ça paraît simple, et pourtant le choix change tout : trop grasse, elle colle ; trop parfumée, elle entête ; mal formulée, elle irrite. Voici comment trouver celle qui rendra vos massages parfaits.",
        ],
        "sections": [
            ("Neutre ou parfumée ?", [
                "**Neutre** : idéale si l'un de vous est sensible aux odeurs, ou pour un usage fréquent. Polyvalente et sûre.",
                "**Parfumée** : crée une ambiance et prolonge la détente, à condition de choisir des **parfums naturels** (lavande, ylang-ylang) plutôt que synthétiques.",
            ]),
            ("La bonne texture", [
                "Cherche une huile qui **glisse longtemps sans coller** et **pénètre sans laisser de film gras**.",
                "Les huiles végétales (amande douce, jojoba, coco) sont douces pour la peau.",
            ]),
            ("Les précautions", [
                "⚠️ Les huiles **ne sont pas compatibles avec les préservatifs en latex** (elles les fragilisent).",
                "Fais un test sur une petite zone si tu as la peau réactive, et range l'huile à l'abri de la chaleur.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pour aller plus loin, découvre aussi les **bougies de massage** qui fondent en huile tiède : un rituel sensoriel à part entière.",
        ],
    },
    {
        "slug": "coffret-decouverte-sensualite-debuter-couple",
        "kicker": "COFFRETS",
        "title": "Coffret découverte sensualité : par où commencer à deux",
        "lead": "L'idée cadeau parfaite pour s'initier sans pression : un coffret bien pensé qui ouvre la porte en douceur.",
        "category": "cadeaux", "date": "23 mai 2026", "read": "4 min",
        "cover_color": "#5b1a26", "product_cats": ["cadeaux", "soins"], "max_products": 3,
        "intro": [
            "Quand on veut explorer la sensualité à deux mais qu'on ne sait pas par où commencer, le coffret découverte est la réponse idéale : plusieurs petits plaisirs réunis, choisis pour aller ensemble, dans un format rassurant.",
        ],
        "sections": [
            ("Pourquoi un coffret plutôt qu'un achat isolé", [
                "Tout est **pensé pour fonctionner ensemble** : on évite les erreurs de débutant et on a tout sous la main.",
                "Le format \"cadeau\" dédramatise : c'est une **invitation au jeu**, pas un achat intimidant.",
            ]),
            ("Ce qu'on trouve dans un bon coffret", [
                "Souvent : une **huile ou bougie de massage**, un **accessoire doux**, parfois un **jeu de cartes** ou un bandeau.",
                "Le meilleur coffret est **progressif** : il y a de quoi commencer en douceur et de quoi explorer ensuite.",
            ]),
            ("Bien le choisir", [
                "Privilégie les coffrets aux **matières de qualité** (silicone médical, cosmétiques sans parfums agressifs).",
                "Regarde les avis : un coffret bien noté sur plusieurs centaines d'avis est un bon repère.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "À offrir ou à s'offrir : le coffret découverte est le cadeau qui dit \"prenons du temps pour nous\" — et c'est souvent ça, le vrai luxe.",
        ],
    },
    {
        "slug": "coffret-lune-de-miel-jeunes-maries-idees",
        "kicker": "COFFRETS",
        "title": "Coffret lune de miel : nos idées pour jeunes mariés",
        "lead": "Pour célébrer le début d'une histoire : des idées tendres, romantiques et un brin sensuelles à offrir aux amoureux.",
        "category": "cadeaux", "date": "22 mai 2026", "read": "4 min",
        "cover_color": "#5b1a26", "product_cats": ["cadeaux", "nuit"], "max_products": 3,
        "intro": [
            "Offrir un cadeau pour une lune de miel, c'est célébrer l'intimité naissante d'un couple. L'idée n'est pas d'en faire trop, mais de toucher juste : romantique, raffiné, et un soupçon de sensualité.",
        ],
        "sections": [
            ("Le combo gagnant : élégance + tendresse", [
                "Une **belle nuisette ou un ensemble en satin** pour la mariée, à associer à un coffret bien-être à partager.",
                "Le mot manuscrit qui accompagne fait toute la différence : il transforme l'objet en souvenir.",
            ]),
            ("Pour un voyage", [
                "Pensez **pratique et léger** : une nuisette en satin se glisse partout, une trousse de soins de voyage est toujours utile.",
                "Les formats compacts et discrets sont parfaits pour la valise.",
            ]),
            ("Le geste qui marque", [
                "Un coffret \"première nuit\" personnalisé (bougie, huile de massage, petit accessoire doux) crée un **rituel à deux** dès le début.",
                "Misez sur la qualité plutôt que la quantité : un seul beau cadeau vaut mieux que dix gadgets.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le plus beau cadeau de lune de miel reste celui qui invite le couple à **prendre du temps pour lui**. Le reste n'est qu'un joli prétexte.",
        ],
    },
]


if __name__ == "__main__":
    main()
