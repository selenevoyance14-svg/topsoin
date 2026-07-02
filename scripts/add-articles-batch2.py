#!/usr/bin/env python3
"""
Ajoute un 2e lot de NOUVEAUX articles au journal Maison Léa SANS toucher aux existants.

Même méthode éprouvée que add-articles.py :
- Génère les fichiers HTML des articles définis dans NEW_ARTICLES.
- Insère leurs cartes en tête de la grille de journal/index.html (non destructif).
- Sélectionne de vrais produits depuis data.jsx, avec rotation par catégorie.

Usage : python3 scripts/add-articles-batch2.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "journal"
DATA_JSX = ROOT / "data.jsx"
PARTNER_TAG = "lebrunnathali-21"


def amazon_url(asin):
    return f"https://www.amazon.fr/dp/{asin}?tag={PARTNER_TAG}"


def load_products():
    """Extrait le tableau PRODUCTS de data.jsx (string-aware)."""
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

    # Réécrit TOUJOURS le HTML des articles du lot (idempotent : permet de
    # régénérer avec un nombre de produits différent sans casser l'index).
    for a in NEW_ARTICLES:
        (JOURNAL / f"{a['slug']}.html").write_text(render_article(a, products), encoding="utf-8")
        print(f"✓ {a['slug']}.html")

    # N'insère que les cartes dont le slug n'est pas déjà dans l'index (pas de doublon).
    index_path = JOURNAL / "index.html"
    html = index_path.read_text(encoding="utf-8")
    to_card = [a for a in NEW_ARTICLES if f"/journal/{a['slug']}.html" not in html]
    if to_card:
        anchor = '<div class="articles-grid">\n'
        if anchor not in html:
            anchor = '<div class="articles-grid">'
            cards = "\n    " + "\n    ".join(render_card(a).strip() for a in to_card)
        else:
            cards = "    " + "    ".join(render_card(a) for a in to_card)
        html = html.replace(anchor, anchor + cards, 1)
        index_path.write_text(html, encoding="utf-8")
    print(f"✓ index.html : +{len(to_card)} cartes insérées (déjà présentes : {len(NEW_ARTICLES) - len(to_card)})")
    print(f"\n✅ {len(NEW_ARTICLES)} articles régénérés.")


# ────────────────────────────────────────────────────────────────────────────
DATE = "2 juillet 2026"
DISCLAIMER_PRIME = "Tous les produits ci-dessous sont disponibles sur Amazon, souvent en livraison Prime et expédiés en colis neutre — discrétion totale."

NEW_ARTICLES = [
    # ─────────────── LINGERIE (7) ───────────────
    {
        "slug": "culotte-invisible-fini-marques-sous-vetement",
        "kicker": "GUIDE LINGERIE", "category": "lingerie",
        "title": "Culotte invisible : dire adieu aux marques",
        "lead": "Sous une robe moulante ou un pantalon clair, la culotte invisible se fait oublier. Coupes, matières, astuces : le guide pour un rendu lisse.",
        "date": DATE, "read": "4 min", "cover_color": "#8b1d2c",
        "product_cats": ["lingerie"], "max_products": 6,
        "intro": [
            "Rien ne gâche une belle tenue comme la ligne d'une culotte qui se dessine sous le tissu. La culotte invisible règle le problème sans sacrifier le confort — encore faut-il choisir la bonne coupe et la bonne matière.",
        ],
        "sections": [
            ("Ce qui rend une culotte vraiment invisible", [
                "Des **bords laser** (découpés à chaud, sans ourlet) : c'est le vrai secret d'un rendu plat sous le vêtement.",
                "Une matière **microfibre extensible** qui épouse la peau sans marquer, plutôt qu'un coton à élastique épais.",
            ]),
            ("Quelle coupe sous quelle tenue", [
                "**Robe moulante ou jersey fin** : le tanga sans couture reste le plus discret.",
                "**Pantalon clair ou blanc** : préfère une culotte nude proche de ta carnation, plus efficace que le blanc qui ressort.",
                "**Recherche de gainage léger** : un shorty taille haute sans couture lisse aussi le ventre.",
            ]),
            ("Les erreurs à éviter", [
                "Une taille trop juste crée une marque là où on voulait justement l'effacer : prends ta taille habituelle, pas en dessous.",
                "Le lavage en machine à haute température ramollit l'élasthanne : cycle doux et pas de sèche-linge pour garder le maintien.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bon réflexe : garde deux ou trois modèles nude en rotation, ce sont ceux que tu porteras le plus souvent sous tes tenues du quotidien.",
        ],
    },
    {
        "slug": "soutien-gorge-allaitement-confort-style",
        "kicker": "GUIDE LINGERIE", "category": "lingerie",
        "title": "Soutien-gorge d'allaitement : confort et style",
        "lead": "Allaiter ne veut pas dire renoncer à se sentir belle. Comment choisir un soutien-gorge pratique, doux et flatteur pour cette période.",
        "date": DATE, "read": "4 min", "cover_color": "#8b1d2c",
        "product_cats": ["lingerie"], "max_products": 6,
        "intro": [
            "Le soutien-gorge d'allaitement, on l'imagine souvent utilitaire et sans charme. C'est un cliché : les modèles actuels combinent ouverture pratique, vrai maintien et jolie coupe. Voici comment bien le choisir.",
        ],
        "sections": [
            ("Les critères vraiment importants", [
                "Une **ouverture d'une seule main** (clip sur la bretelle) : indispensable quand on a bébé dans l'autre bras.",
                "Une matière **douce et respirante**, sans armature rigide les premières semaines pour ne pas gêner la montée de lait.",
            ]),
            ("Trouver sa taille qui bouge", [
                "La poitrine varie beaucoup pendant l'allaitement : privilégie un **dos extensible** et plusieurs rangs d'agrafes.",
                "Mieux vaut un modèle un peu souple qu'un bonnet fixe : le confort prime sur l'ajustement parfait à cette période.",
            ]),
            ("Se sentir belle malgré tout", [
                "Certains modèles en **dentelle douce** existent en version allaitement : rien n'oblige à choisir le tout-fonctionnel.",
                "Une couleur qui te plaît change tout le moral : offre-toi deux modèles, un pratique de jour et un plus joli.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Astuce : prévois-en au moins trois pour tourner facilement au lavage. Le confort d'une matière douce, on le mesure surtout la nuit.",
        ],
    },
    {
        "slug": "entretien-lingerie-delicate-laver-guide",
        "kicker": "GUIDE LINGERIE", "category": "lingerie",
        "title": "Laver sa lingerie délicate sans l'abîmer",
        "lead": "Dentelle, satin, armatures : la belle lingerie mérite mieux que la machine à 40°. Le guide pour la faire durer des années.",
        "date": DATE, "read": "4 min", "cover_color": "#8b1d2c",
        "product_cats": ["lingerie"], "max_products": 6,
        "intro": [
            "Une belle pièce de lingerie représente un petit investissement — autant qu'elle dure. La plupart des dégâts (dentelle qui file, armatures qui percent, bonnets déformés) viennent d'un lavage inadapté. Bonne nouvelle : bien l'entretenir prend deux minutes.",
        ],
        "sections": [
            ("Le lavage à la main, le plus sûr", [
                "Eau tiède, une noisette de lessive douce, on laisse tremper dix minutes puis on presse sans tordre : la dentelle et le satin adorent.",
                "On rince à l'eau claire et on **presse dans une serviette** pour absorber l'eau, jamais d'essorage brutal.",
            ]),
            ("La machine, si vraiment nécessaire", [
                "Toujours dans un **filet de lavage**, agrafes fermées, sur cycle délicat à 30° maximum.",
                "On évite l'adoucissant qui encrasse les fibres élastiques : c'est lui qui fait perdre le maintien avec le temps.",
            ]),
            ("Le séchage et le rangement", [
                "Jamais de sèche-linge : la chaleur tue l'élasthanne. On sèche **à plat, à l'ombre**.",
                "On range les soutiens-gorge à plat, bonnet dans bonnet, sans les retourner : ça préserve la forme des armatures.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un filet de lavage et un flacon de lessive douce, c'est tout ce qu'il faut pour doubler la durée de vie de tes plus belles pièces.",
        ],
    },
    {
        "slug": "culotte-menstruelle-confort-regles-guide",
        "kicker": "GUIDE LINGERIE", "category": "lingerie",
        "title": "La culotte menstruelle : confort et sérénité",
        "lead": "Fini les protections jetables : la culotte de règles absorbe, respire et se lave. Comment la choisir et l'adopter au quotidien.",
        "date": DATE, "read": "5 min", "cover_color": "#8b1d2c",
        "product_cats": ["lingerie"], "max_products": 6,
        "intro": [
            "La culotte menstruelle a conquis beaucoup de femmes en quelques années, et pour de bonnes raisons : elle est confortable, économique sur la durée et bien plus respirante que les protections classiques. Reste à choisir le bon modèle et à bien l'utiliser.",
        ],
        "sections": [
            ("Comment ça marche", [
                "Plusieurs couches invisibles : une qui **absorbe**, une qui **retient**, une qui garde la peau au sec. On ne sent rien, ça reste fin.",
                "Selon le flux, on choisit une capacité **léger, moyen ou abondant** — l'équivalent de plusieurs tampons pour les modèles les plus absorbants.",
            ]),
            ("Bien la choisir", [
                "Regarde la **coupe** (taille haute pour la nuit, classique pour le jour) et la matière du contact peau, idéalement coton.",
                "Prévois-en assez pour tenir un cycle sans lessive quotidienne : trois à cinq pièces selon la durée de tes règles.",
            ]),
            ("L'entretien, tout simple", [
                "On rince à l'eau froide après usage jusqu'à ce que l'eau soit claire, puis lavage machine à 30° sans adoucissant.",
                "Séchage à l'air libre, jamais au sèche-linge : bien entretenue, une culotte tient plusieurs années.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pour débuter, commence par deux modèles de capacités différentes : tu verras vite lesquels correspondent à tes journées.",
        ],
    },
    {
        "slug": "body-gainant-silhouette-elegance",
        "kicker": "GUIDE LINGERIE", "category": "lingerie",
        "title": "Le body gainant : lisser sa silhouette",
        "lead": "Sous une robe ajustée, le body gainant affine la taille et efface les démarcations. Comment le choisir pour qu'il reste invisible et confortable.",
        "date": DATE, "read": "4 min", "cover_color": "#8b1d2c",
        "product_cats": ["lingerie"], "max_products": 6,
        "intro": [
            "Le body gainant n'a rien de contraignant quand il est bien choisi : il lisse la silhouette, tient le ventre et disparaît sous la tenue. L'objectif n'est pas de se serrer, mais de se sentir bien dans une robe qui compte.",
        ],
        "sections": [
            ("Choisir le bon niveau de gainage", [
                "**Gainage léger** : effet seconde peau, pour un rendu lisse sans compression — le plus confortable au quotidien.",
                "**Gainage fort** : réserve-le aux occasions ponctuelles, il structure davantage mais se porte moins longtemps sans gêne.",
            ]),
            ("Le confort avant tout", [
                "Vérifie l'**entrejambe à pressions** : indispensable pour aller aux toilettes sans tout retirer.",
                "Des bretelles réglables et un dos qui ne roule pas : ce sont les détails qui font la différence sur une journée entière.",
            ]),
            ("Le rendre invisible", [
                "Choisis une teinte proche de ta peau plutôt que le noir sous une tenue claire.",
                "Un modèle sans couture aux cuisses évite la démarcation qui trahirait le gainage sous une robe fluide.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La règle d'or : un body qui te coupe le souffle est trop petit. Bien ajusté, il doit se faire oublier au bout de cinq minutes.",
        ],
    },
    {
        "slug": "lingerie-rouge-oser-couleur-seduction",
        "kicker": "GUIDE LINGERIE", "category": "lingerie",
        "title": "La lingerie rouge : oser la couleur",
        "lead": "Audacieuse et intemporelle, la lingerie rouge assume la séduction. Quelle nuance, quelle pièce, pour qui : le guide pour l'apprivoiser.",
        "date": DATE, "read": "4 min", "cover_color": "#8b1d2c",
        "product_cats": ["lingerie"], "max_products": 6,
        "intro": [
            "Le rouge, c'est la couleur qui ne se cache pas. En lingerie, il évoque la confiance et le désir — et contrairement aux idées reçues, il va à toutes les femmes. Tout est question de nuance et de pièce.",
        ],
        "sections": [
            ("Trouver sa bonne nuance de rouge", [
                "**Rouge profond ou bordeaux** : chaleureux et facile à porter, il flatte les carnations claires comme mates.",
                "**Rouge vif** : le plus audacieux, parfait pour une occasion où l'on veut se sentir spectaculaire.",
            ]),
            ("Par quelle pièce commencer", [
                "Pour un premier pas, une **culotte en dentelle rouge** sous une tenue neutre : l'audace reste ton secret.",
                "Pour l'occasion, un **ensemble complet** ou un body : le rouge se suffit à lui-même, inutile d'en rajouter.",
            ]),
            ("L'associer avec goût", [
                "Le rouge se marie très bien avec le **noir** (dentelle, bas) et l'or des bijoux : une combinaison classique et sûre.",
                "Évite d'accumuler les couleurs fortes : le rouge est déjà la star, laisse-le occuper le devant de la scène.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La lingerie rouge se porte d'abord pour soi : le jour où on la choisit, c'est souvent qu'on a envie de se sentir puissante. Et ça, ça se voit.",
        ],
    },
    {
        "slug": "lingerie-noire-indemodable-guide",
        "kicker": "GUIDE LINGERIE", "category": "lingerie",
        "title": "La lingerie noire : l'indémodable absolu",
        "lead": "Élégante, flatteuse, valeur sûre : la lingerie noire va à tout le monde. Comment bâtir sa base et éviter l'effet trop sage.",
        "date": DATE, "read": "4 min", "cover_color": "#8b1d2c",
        "product_cats": ["lingerie"], "max_products": 6,
        "intro": [
            "S'il ne fallait garder qu'une couleur en lingerie, ce serait le noir. Il affine, se marie avec tout et traverse les modes sans prendre une ride. Encore faut-il savoir le choisir pour qu'il reste chic et jamais banal.",
        ],
        "sections": [
            ("Pourquoi ça marche à tous les coups", [
                "Le noir **structure la silhouette** et donne un effet plus net que les teintes claires : c'est la valeur sûre.",
                "Il s'accorde avec toutes les carnations et toutes les tenues : c'est la base qu'on ne regrette jamais d'acheter.",
            ]),
            ("Construire sa base essentielle", [
                "Un **ensemble uni** pour le quotidien, un modèle en **dentelle** pour les jours qui comptent : deux pièces suffisent pour commencer.",
                "Ajoute un body ou une nuisette noire : la même couleur, mais une intention totalement différente.",
            ]),
            ("Éviter l'effet trop sage", [
                "Joue sur les **matières** (dentelle, transparence, satin) plutôt que sur la couleur pour apporter du relief.",
                "Un détail — un ruban, une bordure, une découpe — transforme un noir basique en pièce désirable.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le noir, c'est l'assurance de ne jamais se tromper. Construis ta base autour de lui, tu piocheras les couleurs ensuite selon l'envie.",
        ],
    },

    # ─────────────── NUIT (7) ───────────────
    {
        "slug": "nuisette-grande-taille-sublimer-nuit",
        "kicker": "GUIDE NUIT", "category": "nuit",
        "title": "Nuisette grande taille : élégance la nuit",
        "lead": "Fluidité, matières nobles, coupes flatteuses : la nuisette sublime toutes les silhouettes. Comment choisir la sienne en grande taille.",
        "date": DATE, "read": "4 min", "cover_color": "#3a2e1f",
        "product_cats": ["nuit"], "max_products": 6,
        "intro": [
            "La nuisette n'appartient à aucune taille : elle sublime les courbes autant qu'elle habille les silhouettes fines. En grande taille, l'enjeu est de choisir une coupe qui accompagne le corps au lieu de le contraindre.",
        ],
        "sections": [
            ("Les coupes les plus flatteuses", [
                "La coupe **empire** (resserrée sous la poitrine puis fluide) allonge et met la taille en valeur : une valeur sûre.",
                "Évite les modèles trop droits : c'est le tombé fluide qui flatte, pas la matière qui plaque.",
            ]),
            ("Les bonnes matières", [
                "Le **satin** glisse et flatte les courbes, le **modal** offre une douceur mate plus discrète : deux belles options.",
                "Cherche un modèle avec un vrai soutien de poitrine (bonnets ou bandeau intégré) pour le confort et le maintien.",
            ]),
            ("Se sentir belle, vraiment", [
                "Une **encolure plongeante** et des bretelles fines allègent visuellement le haut du corps.",
                "Choisis d'abord ce qui te plaît à toi : la nuisette est une pièce qu'on porte pour son propre plaisir avant tout.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Astuce taille : les nuisettes en satin taillent parfois juste. Si tu hésites, la taille au-dessus garantit le tombé fluide recherché.",
        ],
    },
    {
        "slug": "combinaison-pyjama-cocooning-hiver",
        "kicker": "GUIDE NUIT", "category": "nuit",
        "title": "La combinaison pyjama : le cocon de l'hiver",
        "lead": "Douce, chaude, ultra confortable : la combinaison pyjama est le refuge des soirées froides. Comment choisir la vôtre sans faux pas.",
        "date": DATE, "read": "3 min", "cover_color": "#3a2e1f",
        "product_cats": ["nuit"], "max_products": 6,
        "intro": [
            "Quand l'hiver s'installe, rien ne remplace la combinaison pyjama : on s'y glisse, on est enveloppée de la tête aux pieds, et la soirée cocooning peut commencer. Encore faut-il choisir la bonne matière et la bonne coupe.",
        ],
        "sections": [
            ("La matière fait tout", [
                "La **polaire** tient très chaud pour les soirées canapé, le **coton molletonné** respire mieux pour dormir dedans.",
                "Vérifie que l'intérieur reste doux : c'est le contact direct sur la peau qui rend la combinaison agréable ou non.",
            ]),
            ("Les détails pratiques", [
                "Une **fermeture zippée** facilite l'enfilage et les passages aux toilettes, plus qu'une combinaison fermée intégralement.",
                "Des poignets et chevilles resserrés gardent la chaleur ; une capuche, c'est le petit plus cocon.",
            ]),
            ("Bien choisir sa taille", [
                "Les combinaisons taillent souvent ample, c'est voulu : le confort vient de l'aisance, pas du près-du-corps.",
                "Trop grande, elle gêne pour marcher ; trop juste, elle serre à l'entrejambe. Ta taille habituelle est le bon repère.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "C'est le vêtement doudou par excellence : à offrir ou à s'offrir dès les premiers froids, on ne le regrette jamais.",
        ],
    },
    {
        "slug": "short-de-nuit-ete-leger-fraicheur",
        "kicker": "GUIDE NUIT", "category": "nuit",
        "title": "Le short de nuit : fraîcheur des nuits d'été",
        "lead": "Quand il fait chaud, le short de nuit devient l'allié du bon sommeil. Matières, coupes, associations : comment bien dormir en été.",
        "date": DATE, "read": "3 min", "cover_color": "#3a2e1f",
        "product_cats": ["nuit"], "max_products": 6,
        "intro": [
            "Dormir quand il fait 28° la nuit, c'est tout un art. Le short de nuit, léger et libre aux jambes, fait souvent la différence entre une nuit moite et un vrai repos. Voici comment bien le choisir.",
        ],
        "sections": [
            ("Les matières qui laissent respirer", [
                "Le **coton** et le **modal** absorbent la transpiration et gardent la peau au sec : les meilleurs alliés de l'été.",
                "Évite le polyester pur qui colle à la peau dès qu'il fait chaud : la respirabilité prime sur tout.",
            ]),
            ("La bonne coupe pour la nuit", [
                "Une **taille élastiquée souple** et une jambe ample : rien ne doit serrer pour ne pas gêner le sommeil.",
                "En duo caraco + short, on module facilement selon la température de la chambre.",
            ]),
            ("Le petit plus confort", [
                "Un ensemble assorti fait aussi tenue d'intérieur : pratique pour le petit-déjeuner sur le balcon.",
                "Prévois deux jeux pour tourner : par forte chaleur, on apprécie de changer chaque soir.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bon réflexe d'été : privilégie les fibres naturelles et les coupes amples. Ton sommeil t'en remerciera dès la première canicule.",
        ],
    },
    {
        "slug": "matiere-pyjama-modal-bambou-coton-comparatif",
        "kicker": "GUIDE NUIT", "category": "nuit",
        "title": "Modal, bambou ou coton : quel pyjama ?",
        "lead": "Trois matières douces, trois sensations différentes. On compare toucher, respirabilité et entretien pour choisir son pyjama idéal.",
        "date": DATE, "read": "4 min", "cover_color": "#3a2e1f",
        "product_cats": ["nuit"], "max_products": 6,
        "intro": [
            "Coton, modal, bambou : sur l'étiquette, on ne sait pas toujours ce qui se cache derrière ces mots. Pourtant, la matière change tout dans un pyjama — sensation, chaleur, longévité. Petit comparatif pour choisir en connaissance de cause.",
        ],
        "sections": [
            ("Le coton, le classique fiable", [
                "**Respirant, résistant, facile à laver** : le coton est la valeur sûre, idéale toute l'année.",
                "Son seul défaut : il peut sembler un peu moins doux que le modal ou le bambou au premier contact.",
            ]),
            ("Le modal, la douceur soyeuse", [
                "Issu du hêtre, le modal offre un **toucher fluide et frais**, plus soyeux que le coton, avec un beau tombé.",
                "Il garde sa douceur lavage après lavage : un vrai confort de peau pour dormir.",
            ]),
            ("Le bambou, doux et thermorégulant", [
                "La viscose de bambou est **très douce et respirante**, appréciée par les peaux sensibles.",
                "Elle régule bien la température : agréable pour celles qui ont chaud puis froid dans la nuit.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "En résumé : coton pour la robustesse, modal pour la douceur soyeuse, bambou pour les peaux sensibles. Aucune mauvaise réponse, juste la tienne.",
        ],
    },
    {
        "slug": "pyjama-grossesse-bien-dormir-enceinte",
        "kicker": "GUIDE NUIT", "category": "nuit",
        "title": "Bien dormir enceinte : le pyjama de grossesse",
        "lead": "Ventre qui s'arrondit, chaleur, sommeil léger : la grossesse chamboule les nuits. Comment choisir un pyjama qui accompagne ces mois.",
        "date": DATE, "read": "4 min", "cover_color": "#3a2e1f",
        "product_cats": ["nuit"], "max_products": 6,
        "intro": [
            "Pendant la grossesse, le corps change vite et le sommeil devient précieux. Un bon pyjama de grossesse — doux, évolutif, respirant — aide à passer de meilleures nuits, et servira souvent aussi pour l'allaitement.",
        ],
        "sections": [
            ("Une coupe qui suit le ventre", [
                "Cherche une **matière extensible** et une taille qui s'adapte au ventre qui pousse : inutile de racheter chaque mois.",
                "Les modèles amples ou empire accompagnent l'arrondi sans jamais serrer.",
            ]),
            ("La respirabilité, essentielle", [
                "On a souvent plus chaud enceinte : le **coton et le modal** évacuent la transpiration et évitent les réveils moites.",
                "Un ensemble caraco + short permet d'ajuster facilement selon les nuits.",
            ]),
            ("Penser à l'après", [
                "Un modèle à **ouverture facilitée** servira aussi pour l'allaitement : deux usages pour un seul achat.",
                "La douceur compte double après l'accouchement : privilégie les matières les plus tendres.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bon plan : choisis dès le 2e trimestre un pyjama évolutif qui te suivra jusqu'à l'allaitement. Confortable et malin.",
        ],
    },
    {
        "slug": "peignoir-eponge-apres-bain-choisir",
        "kicker": "GUIDE NUIT", "category": "nuit",
        "title": "Le peignoir éponge : le confort d'après-bain",
        "lead": "Sortie de douche, matin tranquille : le peignoir éponge enveloppe et sèche. Grammage, matière, coupe : comment choisir le bon.",
        "date": DATE, "read": "3 min", "cover_color": "#3a2e1f",
        "product_cats": ["nuit"], "max_products": 6,
        "intro": [
            "Le peignoir en éponge, c'est le petit luxe simple du matin et de l'après-bain : on s'enveloppe, on sèche sans effort, on prolonge la douceur de la douche. Tous ne se valent pas, et le détail qui compte s'appelle le grammage.",
        ],
        "sections": [
            ("Le grammage, critère numéro un", [
                "Un **grammage élevé** (400 g/m² et plus) donne un peignoir épais, moelleux et très absorbant : la sensation d'hôtel.",
                "Un grammage plus léger sèche plus vite et pèse moins : pratique pour l'été ou les voyages.",
            ]),
            ("Coton, bambou ou microfibre", [
                "Le **coton bouclette** reste la référence pour l'absorption et la douceur durable.",
                "Le bambou apporte une douceur soyeuse, la microfibre sèche très vite mais absorbe un peu moins.",
            ]),
            ("La coupe et les détails", [
                "Une **ceinture bien placée** et des poches, c'est le confort au quotidien.",
                "Col châle pour le cocon enveloppant, col kimono pour un rendu plus léger : à choisir selon l'usage.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pour un cadeau qui plaît toujours : un peignoir épais en coton, dans une couleur neutre. C'est le confort qu'on n'achète jamais pour soi mais qu'on adore recevoir.",
        ],
    },
    {
        "slug": "loungewear-tenue-detente-maison-style",
        "kicker": "GUIDE NUIT", "category": "nuit",
        "title": "Le loungewear : stylée même à la maison",
        "lead": "Entre le pyjama et la vraie tenue, le loungewear habille les journées maison avec allure. Comment composer une tenue détente chic.",
        "date": DATE, "read": "4 min", "cover_color": "#3a2e1f",
        "product_cats": ["nuit"], "max_products": 6,
        "intro": [
            "Le loungewear, c'est l'art de rester confortable sans se laisser aller : des matières douces, des coupes soignées, et l'assurance d'être présentable si on ouvre la porte. Devenu incontournable, il mérite qu'on le choisisse bien.",
        ],
        "sections": [
            ("La différence avec le pyjama", [
                "Le loungewear se veut **présentable** : on peut recevoir, télétravailler ou sortir chercher le pain sans se changer.",
                "Les matières restent douces mais les coupes sont plus structurées qu'un simple pyjama.",
            ]),
            ("Composer sa tenue détente", [
                "Un **ensemble maille ou molleton** coordonné donne tout de suite une allure soignée, même très confortable.",
                "Joue les superpositions : caraco + gilet long, ou tee-shirt + pantalon fluide, pour un rendu pensé.",
            ]),
            ("Les couleurs qui font chic", [
                "Les **tons neutres** (beige, gris, écru, noir) donnent instantanément un effet élégant et facile à assortir.",
                "Une matière côtelée ou un joli tombé suffisent à faire la différence avec un jogging basique.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "L'idée du loungewear : se sentir aussi bien qu'en pyjama, tout en ayant l'air d'avoir fait un effort. Le confort n'exclut jamais l'allure.",
        ],
    },

    # ─────────────── SOINS (7) ───────────────
    {
        "slug": "peau-seche-routine-hydratation-corps",
        "kicker": "RITUEL SOINS", "category": "soins",
        "title": "Peau sèche : la routine hydratation",
        "lead": "Tiraillements, rugosité, inconfort : la peau sèche demande une routine simple mais régulière. Les gestes et produits qui changent tout.",
        "date": DATE, "read": "4 min", "cover_color": "#2a3a2a",
        "product_cats": ["soins"], "max_products": 6,
        "intro": [
            "La peau sèche, ce n'est pas une fatalité : elle manque surtout d'eau et de lipides pour retenir cette eau. Avec une routine simple et régulière, on retrouve confort et douceur en quelques jours.",
        ],
        "sections": [
            ("Nettoyer sans agresser", [
                "Bannis les gels douche décapants : préfère une **huile lavante ou un gel surgras** qui n'assèche pas davantage.",
                "L'eau trop chaude aggrave la sécheresse : douche tiède et rapide, c'est déjà un grand pas.",
            ]),
            ("Hydrater au bon moment", [
                "Applique ta crème ou ton lait **sur peau encore humide**, juste après la douche : l'hydratation est bien mieux retenue.",
                "Pour les zones très sèches (coudes, genoux, tibias), un **beurre corporel** plus riche fait des merveilles le soir.",
            ]),
            ("Les bons gestes en plus", [
                "Un **gommage doux** une fois par semaine aide la crème à mieux pénétrer, sans frotter fort.",
                "Bois suffisamment et, en hiver, un humidificateur limite l'air sec qui déshydrate la peau.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La clé n'est pas le produit miracle mais la régularité : deux minutes chaque soir valent mieux qu'un soin intense une fois par mois.",
        ],
    },
    {
        "slug": "creme-ou-huile-corps-choisir",
        "kicker": "RITUEL SOINS", "category": "soins",
        "title": "Crème ou huile pour le corps : que choisir ?",
        "lead": "Deux textures, deux usages. On compare crème et huile corporelle pour savoir laquelle convient à ta peau et à tes envies.",
        "date": DATE, "read": "4 min", "cover_color": "#2a3a2a",
        "product_cats": ["soins"], "max_products": 6,
        "intro": [
            "Crème, lait, huile, beurre : le rayon soin du corps peut donner le vertige. En réalité, tout se joue entre deux grandes familles — les crèmes à base d'eau et les huiles à base de corps gras. Chacune a sa force.",
        ],
        "sections": [
            ("La crème : hydratation confort", [
                "Riche en eau, la crème **hydrate en profondeur** et pénètre vite : parfaite pour le matin avant de s'habiller.",
                "Idéale pour les peaux normales à sèches qui cherchent du confort sans effet gras.",
            ]),
            ("L'huile : nutrition et éclat", [
                "L'huile **nourrit et gaine la peau**, lui donne un fini satiné et un joli parfum : sensuelle et réconfortante.",
                "Une **huile sèche** pénètre sans laisser de film gras : le compromis idéal pour celles qui n'aiment pas la sensation d'huile.",
            ]),
            ("Comment choisir", [
                "**Peau qui tiraille, sensation d'inconfort ?** La crème apaise vite.",
                "**Peau qui manque d'éclat, envie de rituel cocooning ?** L'huile, en massage, transforme le soin en moment de plaisir.",
                "Beaucoup combinent : crème le matin, huile le soir en massage.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le vrai secret, c'est le geste : appliquer en massant quelques minutes vaut plus que la richesse du produit lui-même.",
        ],
    },
    {
        "slug": "gommage-corps-avant-epilation-peau-douce",
        "kicker": "RITUEL SOINS", "category": "soins",
        "title": "Le gommage : préparer sa peau en douceur",
        "lead": "Avant l'épilation ou le bronzage, un bon gommage change tout. Comment l'utiliser sans irriter, pour une peau lisse et nette.",
        "date": DATE, "read": "3 min", "cover_color": "#2a3a2a",
        "product_cats": ["soins"], "max_products": 6,
        "intro": [
            "Le gommage, c'est le geste qu'on saute trop souvent alors qu'il fait toute la différence : peau plus lisse, épilation plus nette, bronzage plus uniforme et crèmes qui pénètrent mieux. À condition de bien le faire.",
        ],
        "sections": [
            ("Pourquoi gommer régulièrement", [
                "Le gommage **élimine les cellules mortes** qui ternissent la peau et bouchent les pores.",
                "Il limite les **poils incarnés** en dégageant la surface : un vrai allié avant et entre les épilations.",
            ]),
            ("Le bon geste, sans agresser", [
                "Sur peau humide, masse en **mouvements circulaires doux**, sans appuyer : la peau doit être exfoliée, pas frottée à vif.",
                "Une à deux fois par semaine suffit : trop souvent, on fragilise la barrière cutanée.",
            ]),
            ("Quand et avec quoi", [
                "Gomme **la veille** d'une épilation ou d'une exposition au soleil, pas juste avant, pour laisser la peau se calmer.",
                "Termine toujours par une hydratation : la peau fraîchement gommée boit littéralement la crème ou l'huile.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un gommage doux, une fois ou deux par semaine, et ta peau reste nette toute l'année. C'est le geste le plus rentable de la routine corps.",
        ],
    },
    {
        "slug": "soin-mains-douces-hiver-guide",
        "kicker": "RITUEL SOINS", "category": "soins",
        "title": "Mains douces en hiver : le soin oublié",
        "lead": "Froid, lavages répétés : les mains trinquent en hiver. Les gestes simples et les soins pour retrouver une peau souple et nette.",
        "date": DATE, "read": "3 min", "cover_color": "#2a3a2a",
        "product_cats": ["soins"], "max_products": 6,
        "intro": [
            "Les mains sont la partie du corps la plus exposée et la plus oubliée. En hiver, entre le froid et les lavages fréquents, elles tiraillent et se dessèchent vite. Quelques gestes simples suffisent à les garder douces.",
        ],
        "sections": [
            ("Pourquoi les mains souffrent l'hiver", [
                "Le froid et le vent **assèchent la peau fine** du dessus des mains, pauvre en glandes sébacées.",
                "Les lavages répétés à l'eau chaude éliminent le film protecteur naturel : d'où les tiraillements.",
            ]),
            ("La routine express", [
                "Une **crème mains après chaque lavage** : c'est le geste le plus efficace, à condition de le répéter.",
                "Le soir, une couche généreuse et, en cas de peau très abîmée, des gants de coton la nuit pour un effet soin intensif.",
            ]),
            ("Les bons réflexes", [
                "Porte des **gants dehors** dès qu'il fait froid : la meilleure protection reste d'éviter l'exposition.",
                "Choisis une crème riche en agents nourrissants (beurre de karité, glycérine) plutôt qu'une simple crème parfumée.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Garde un petit tube dans le sac et un plus riche sur la table de nuit : des mains douces, c'est surtout une question de constance.",
        ],
    },
    {
        "slug": "lubrifiant-hybride-eau-silicone-comprendre",
        "kicker": "SOINS INTIMES", "category": "soins",
        "title": "Le lubrifiant hybride : le duo gagnant",
        "lead": "Entre le confort de l'eau et la longévité du silicone, le lubrifiant hybride combine les deux. Pour qui, quand, comment le choisir.",
        "date": DATE, "read": "4 min", "cover_color": "#2a3a2a",
        "product_cats": ["soins"], "max_products": 6,
        "intro": [
            "On oppose souvent lubrifiant à base d'eau et à base de silicone. Le lubrifiant hybride réconcilie les deux : la douceur naturelle de l'eau, plus la tenue et le glissé du silicone. Un bon compromis quand on hésite.",
        ],
        "sections": [
            ("Ce qu'apporte l'hybride", [
                "Il **glisse plus longtemps** qu'un lubrifiant à l'eau, sans devenir collant, grâce à une petite part de silicone.",
                "Il reste **plus léger et facile à rincer** qu'un silicone pur : le meilleur des deux mondes pour beaucoup.",
            ]),
            ("Les précautions à connaître", [
                "Comme tout produit contenant du silicone, il peut **abîmer les jouets en silicone** : vérifie la compatibilité ou choisis un modèle marqué compatible.",
                "Regarde la **composition** : privilégie une liste courte, sans parfum ni glycérine agressive pour les zones sensibles.",
            ]),
            ("Pour qui c'est idéal", [
                "Pour celles qui trouvent l'eau trop vite absorbée mais le silicone trop gras : l'hybride tombe juste au milieu.",
                "Aussi pratique dans l'eau (douche, bain) où un lubrifiant à l'eau se dissout trop vite.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "En cas de doute, garde un petit format à l'eau pour les jouets et un hybride pour le reste : tu couvres toutes les situations.",
        ],
    },
    {
        "slug": "secheresse-intime-comprendre-apaiser",
        "kicker": "SOINS INTIMES", "category": "soins",
        "title": "Sécheresse intime : comprendre et apaiser",
        "lead": "Fréquente et rarement évoquée, la sécheresse intime a des solutions simples et douces. Causes, gestes et produits pour retrouver le confort.",
        "date": DATE, "read": "4 min", "cover_color": "#2a3a2a",
        "product_cats": ["soins"], "max_products": 6,
        "intro": [
            "La sécheresse intime touche beaucoup de femmes, à tout âge, et pourtant on en parle peu. C'est un inconfort banal, souvent passager, qui se soulage bien avec les bons gestes. Faisons le point sans tabou.",
        ],
        "sections": [
            ("D'où ça vient", [
                "Les variations hormonales (cycle, grossesse, ménopause), le stress ou certains produits trop décapants **perturbent l'hydratation naturelle**.",
                "Une toilette trop fréquente ou trop agressive fait souvent plus de mal que de bien.",
            ]),
            ("Les bons gestes au quotidien", [
                "Utilise un **soin lavant doux au pH adapté**, une fois par jour maximum, sans savon parfumé.",
                "Un **gel hydratant intime** (différent du lubrifiant) répare et apaise sur la durée, en cure de quelques jours.",
            ]),
            ("Pour le confort ponctuel", [
                "Un **lubrifiant doux à base d'eau** soulage immédiatement l'inconfort lors des rapports.",
                "Si la gêne persiste ou s'accompagne de démangeaisons, un avis médical s'impose : mieux vaut vérifier.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Rien de honteux là-dedans : la sécheresse intime est courante et bien prise en charge. Les bons produits doux font souvent toute la différence.",
        ],
    },
    {
        "slug": "brume-parfumee-corps-touche-finale",
        "kicker": "RITUEL SOINS", "category": "soins",
        "title": "Brume parfumée : la touche finale sensuelle",
        "lead": "Plus légère qu'un parfum, la brume corporelle enveloppe la peau d'un sillage subtil. Comment la choisir et l'utiliser avec justesse.",
        "date": DATE, "read": "3 min", "cover_color": "#2a3a2a",
        "product_cats": ["soins"], "max_products": 6,
        "intro": [
            "La brume parfumée pour le corps, c'est la touche finale qu'on s'offre après la douche : un nuage léger, un parfum discret, une peau qui sent bon toute la journée sans l'intensité d'un parfum classique.",
        ],
        "sections": [
            ("Brume ou parfum : la différence", [
                "La brume est **moins concentrée** : son sillage est plus doux, plus proche de la peau, idéal pour le jour.",
                "On peut la vaporiser généreusement, sur tout le corps, sans crainte de l'effet trop fort d'un parfum.",
            ]),
            ("Bien l'appliquer", [
                "Vaporise **sur peau propre et hydratée** : la brume tient mieux sur une peau nourrie que sur une peau sèche.",
                "Un nuage à 20 cm, dans lequel on marche, répartit le parfum plus joliment qu'une application ciblée.",
            ]),
            ("Créer un sillage cohérent", [
                "Superpose la brume avec un lait corps de la **même famille de senteur** pour un parfum qui tient plus longtemps.",
                "Choisis une senteur qui te correspond : florale légère, gourmande, fraîche… la brume se veut avant tout un plaisir.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La brume, c'est le petit geste bonheur du matin : léger, sensuel, jamais envahissant. Parfait pour celles qui trouvent le parfum trop marqué.",
        ],
    },

    # ─────────────── SENSUALITÉ (7) ───────────────
    {
        "slug": "massage-dos-couple-detente-rapprochement",
        "kicker": "SENSUALITÉ", "category": "sensualite",
        "title": "Le massage du dos à deux : la détente",
        "lead": "Simple, accessible, profondément apaisant : le massage du dos rapproche sans mode d'emploi compliqué. Les gestes pour bien débuter.",
        "date": DATE, "read": "4 min", "cover_color": "#5b1a26",
        "product_cats": ["sensualite"], "max_products": 6,
        "intro": [
            "Pas besoin d'être masseur professionnel pour offrir un vrai moment de détente. Le massage du dos est le plus simple à réussir, et l'un des plus efficaces pour dénouer les tensions et se reconnecter à deux.",
        ],
        "sections": [
            ("Créer le bon cadre", [
                "Une pièce **chaude**, une lumière douce, une serviette sur le lit ou au sol : le confort compte autant que les gestes.",
                "Une **huile de massage** tiédie entre les mains facilite le glissé et rend le contact plus agréable.",
            ]),
            ("Les gestes qui marchent", [
                "Commence par de **grands mouvements lents** le long de la colonne, sans jamais appuyer sur les vertèbres.",
                "Travaille les épaules et le bas du dos, zones de tension, avec les pouces en petits cercles.",
            ]),
            ("Le secret : la lenteur", [
                "La régularité et la lenteur comptent plus que la technique : un rythme posé installe la détente.",
                "Reste à l'écoute : un mot, un soupir suffisent à savoir où insister ou alléger.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Dix minutes suffisent à transformer une soirée. Le massage du dos, c'est le rituel le plus simple pour prendre soin l'un de l'autre.",
        ],
    },
    {
        "slug": "rituel-massage-sensuel-debuter-couple",
        "kicker": "SENSUALITÉ", "category": "sensualite",
        "title": "Le massage sensuel : créer un rituel à deux",
        "lead": "Au-delà de la détente, le massage sensuel installe une complicité rare. Comment en faire un vrai rituel, sans pression ni attentes.",
        "date": DATE, "read": "5 min", "cover_color": "#5b1a26",
        "product_cats": ["sensualite"], "max_products": 6,
        "intro": [
            "Le massage sensuel n'a pas de but à atteindre : c'est un temps pour ralentir, se toucher autrement, redécouvrir l'autre sans agenda. En faire un rituel régulier, c'est offrir au couple une bulle rien qu'à lui.",
        ],
        "sections": [
            ("Poser une intention, pas un objectif", [
                "L'idée n'est pas la performance mais la **présence** : on masse pour offrir du plaisir, sans attendre de retour immédiat.",
                "Se mettre d'accord à l'avance sur ce moment enlève toute pression et rend le lâcher-prise possible.",
            ]),
            ("L'ambiance qui fait tout", [
                "Une **bougie de massage**, une musique douce, un téléphone en silence : le décor met en condition.",
                "La chaleur de la pièce est essentielle : on ne se détend pas quand on a froid.",
            ]),
            ("Le toucher qui reconnecte", [
                "Alterne les **rythmes et les zones**, du dos aux bras, de la nuque aux jambes, sans se précipiter.",
                "Le silence ou quelques mots suffisent : c'est le corps qui dialogue, laisse-le mener.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Instauré une fois par semaine, ce rituel devient un rendez-vous attendu. La régularité crée l'intimité bien plus que l'intensité.",
        ],
    },
    {
        "slug": "ambiance-sensuelle-chambre-lumiere-parfum",
        "kicker": "SENSUALITÉ", "category": "sensualite",
        "title": "Créer une ambiance sensuelle : les clés",
        "lead": "Lumière, parfum, musique, textures : l'ambiance prépare le terrain de l'intimité. Les ingrédients simples d'une atmosphère réussie.",
        "date": DATE, "read": "4 min", "cover_color": "#5b1a26",
        "product_cats": ["sensualite"], "max_products": 6,
        "intro": [
            "L'intimité se prépare autant qu'elle s'improvise. Une chambre pensée pour la détente — lumière tamisée, parfum discret, textures douces — met naturellement en condition et invite au lâcher-prise. Voici les ingrédients simples.",
        ],
        "sections": [
            ("La lumière, d'abord", [
                "Bannis le plafonnier : une **lumière basse et chaude** (bougies, lampe d'appoint) flatte la peau et apaise.",
                "La bougie ajoute la lueur mouvante qui rend chaque instant plus doux.",
            ]),
            ("Le parfum et l'odeur", [
                "Une **senteur légère** (bougie parfumée, brume d'oreiller) crée un souvenir olfactif associé au moment.",
                "Reste subtil : un parfum trop présent lasse vite, l'idée est d'envelopper, pas de saturer.",
            ]),
            ("Le son et les textures", [
                "Une **playlist douce** couvre les bruits extérieurs et installe un rythme.",
                "Un beau linge, une matière soyeuse sous la main : le toucher participe autant que le reste à l'atmosphère.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pas besoin de tout réunir : une lumière douce et un parfum suffisent souvent à transformer une chambre ordinaire en cocon.",
        ],
    },
    {
        "slug": "bain-a-deux-rituel-detente-couple",
        "kicker": "SENSUALITÉ", "category": "sensualite",
        "title": "Le bain à deux : le rituel détente",
        "lead": "Chaleur, mousse, lumière douce : le bain partagé est un moment de complicité simple. Comment le réussir pour en faire un vrai rendez-vous.",
        "date": DATE, "read": "4 min", "cover_color": "#5b1a26",
        "product_cats": ["sensualite"], "max_products": 6,
        "intro": [
            "Le bain à deux, c'est un rituel désuet qu'on redécouvre avec plaisir : on ralentit, on se pose, on se parle sans écran. Un moment de complicité tout simple qui ne demande qu'un peu de mise en scène.",
        ],
        "sections": [
            ("Préparer le décor", [
                "**Bougies, lumière éteinte, serviettes chaudes à portée** : le confort commence avant même d'entrer dans l'eau.",
                "Une eau à bonne température et un produit moussant doux transforment la baignoire en cocon.",
            ]),
            ("Les petits plus", [
                "Une **huile de bain** parfumée, deux verres, une playlist tranquille : les détails font le moment.",
                "Un massage des épaules dans l'eau chaude prolonge naturellement la détente.",
            ]),
            ("Prolonger après le bain", [
                "Enveloppez-vous dans des peignoirs moelleux : la douceur ne s'arrête pas à la baignoire.",
                "Un lait ou une huile appliqués mutuellement prolongent le rituel une fois séchés.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bain à deux ne coûte presque rien et vaut toutes les sorties : c'est le rendez-vous qu'on s'offre quand on a envie de se retrouver au calme.",
        ],
    },
    {
        "slug": "parfum-seduction-pouvoir-des-senteurs",
        "kicker": "SENSUALITÉ", "category": "sensualite",
        "title": "Parfum et séduction : le pouvoir des senteurs",
        "lead": "L'odeur est le sens le plus lié à l'émotion et au désir. Comment jouer des senteurs, sur soi et dans l'espace, pour séduire.",
        "date": DATE, "read": "4 min", "cover_color": "#5b1a26",
        "product_cats": ["sensualite"], "max_products": 6,
        "intro": [
            "L'odorat est notre sens le plus émotionnel : une senteur peut réveiller un souvenir, une envie, un frisson. En matière de séduction, le parfum joue un rôle qu'on sous-estime souvent. Voici comment en faire un allié.",
        ],
        "sections": [
            ("Pourquoi l'odeur séduit", [
                "L'odorat est directement relié aux zones du cerveau liées à l'**émotion et à la mémoire** : une senteur marque durablement.",
                "Une odeur agréable crée une association positive inconsciente : on se souvient d'une personne à son parfum.",
            ]),
            ("Le parfum sur soi", [
                "Applique le parfum sur les **points de pulsation** (cou, poignets, creux des coudes) où la chaleur le diffuse.",
                "Moins, c'est mieux : un sillage qu'on découvre en s'approchant est plus séduisant qu'un nuage qui précède.",
            ]),
            ("Parfumer l'espace", [
                "Une **bougie ou un diffuseur** discret dans la chambre crée une atmosphère cohérente avec ton parfum.",
                "Le linge parfumé (brume d'oreiller) prolonge la sensation jusque dans les draps.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le parfum est une signature invisible : bien choisi, il en dit autant qu'un regard. Joue-le avec subtilité, c'est là qu'il opère.",
        ],
    },
    {
        "slug": "lenteur-jeu-seduction-couple",
        "kicker": "SENSUALITÉ", "category": "sensualite",
        "title": "La lenteur : un jeu de séduction",
        "lead": "Ralentir, faire durer, différer : la lenteur est une arme de séduction sous-estimée. Comment cultiver l'attente et l'intensité à deux.",
        "date": DATE, "read": "4 min", "cover_color": "#5b1a26",
        "product_cats": ["sensualite"], "max_products": 6,
        "intro": [
            "Dans un monde pressé, la lenteur devient un luxe — et un formidable jeu de séduction. Faire durer, différer, savourer chaque étape : l'attente décuple le désir bien plus que la précipitation.",
        ],
        "sections": [
            ("Pourquoi la lenteur intensifie", [
                "L'attente **aiguise le désir** : ce qu'on fait durer prend de la valeur, l'anticipation fait partie du plaisir.",
                "Ralentir laisse la place aux sensations : on remarque ce que la précipitation fait manquer.",
            ]),
            ("Cultiver l'attente", [
                "Un message dans la journée, une promesse pour le soir : la séduction commence bien avant le moment lui-même.",
                "Différer, taquiner, faire monter doucement : le jeu de la lenteur se savoure à deux, sans se presser.",
            ]),
            ("Dans l'instant", [
                "Privilégie les **caresses lentes**, les regards, les pauses : chaque geste retardé gagne en intensité.",
                "Respirez ensemble, ralentissez le rythme : la lenteur partagée crée une connexion rare.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La prochaine fois, essayez de tout ralentir de moitié. Vous découvrirez que le désir aime prendre son temps.",
        ],
    },
    {
        "slug": "sensualite-solo-prendre-soin-de-soi",
        "kicker": "SENSUALITÉ", "category": "sensualite",
        "title": "Sensualité en solo : (re)découvrir son corps",
        "lead": "Prendre soin de soi, connaître son corps, s'accorder du plaisir : la sensualité commence par soi. Un guide bienveillant et sans tabou.",
        "date": DATE, "read": "4 min", "cover_color": "#5b1a26",
        "product_cats": ["sensualite"], "max_products": 6,
        "intro": [
            "La sensualité ne se vit pas qu'à deux : elle commence par la relation qu'on entretient avec son propre corps. Prendre du temps pour soi, apprendre à se connaître, s'accorder du plaisir — c'est une forme d'estime de soi.",
        ],
        "sections": [
            ("Se réapproprier son corps", [
                "Un **rituel de soin** (bain, huile, massage) sans autre but que le plaisir reconnecte au corps en douceur.",
                "Se regarder avec bienveillance, sans jugement, est déjà un pas vers plus de confiance.",
            ]),
            ("Le plaisir sans culpabilité", [
                "Le plaisir en solo est **naturel et sain** : il aide à mieux se connaître et à mieux communiquer ses envies ensuite.",
                "Il n'y a ni norme ni performance : chacune son rythme, ses envies, son intimité.",
            ]),
            ("Créer son moment", [
                "Comme pour un rendez-vous, soigne le **cadre** : lumière douce, temps devant soi, téléphone loin.",
                "Le lâcher-prise vient avec l'habitude de s'accorder ces moments sans se presser ni se juger.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Prendre soin de sa sensualité, seule, n'a rien d'égoïste : c'est la base d'un rapport apaisé à son corps et, souvent, d'une intimité plus épanouie à deux.",
        ],
    },

    # ─────────────── ÉROTISME (6) ───────────────
    {
        "slug": "vibromasseur-double-stimulation-comprendre",
        "kicker": "ÉROTISME", "category": "erotisme",
        "title": "Le vibromasseur double stimulation expliqué",
        "lead": "Deux zones stimulées en même temps : le principe qui séduit tant. Comment fonctionne un double stimulateur et comment bien le choisir.",
        "date": DATE, "read": "4 min", "cover_color": "#3a1420",
        "product_cats": ["erotisme"], "max_products": 6,
        "intro": [
            "Le vibromasseur double stimulation stimule deux zones à la fois : l'un des designs les plus appréciés, parce qu'il combine des sensations complémentaires. Encore faut-il comprendre son principe pour bien le choisir.",
        ],
        "sections": [
            ("Le principe de la double stimulation", [
                "Un bras interne et une extension externe agissent **simultanément** : c'est la combinaison qui fait son succès.",
                "Beaucoup de modèles permettent de **régler les deux moteurs séparément** pour doser chaque sensation.",
            ]),
            ("Bien le choisir", [
                "Vérifie l'**écartement** entre les deux parties : toutes les morphologies sont différentes, un modèle ajustable est plus polyvalent.",
                "Privilégie un **silicone médical**, un moteur silencieux et une charge USB : les repères d'un produit de qualité.",
            ]),
            ("Débuter en douceur", [
                "Commence sur les **vitesses basses** pour apprivoiser la double sensation, souvent plus intense qu'attendu.",
                "Un lubrifiant à base d'eau améliore le confort et se rince facilement.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bon réflexe : un modèle rechargeable, étanche et en silicone doux. Ce sont les critères qui font durer le plaisir dans le temps.",
        ],
    },
    {
        "slug": "jouets-connectes-distance-couple",
        "kicker": "ÉROTISME", "category": "erotisme",
        "title": "Jouets connectés : pimenter même à distance",
        "lead": "Pilotés par appli, les jouets connectés rapprochent les couples éloignés. Comment ça marche, ce qu'il faut vérifier avant d'acheter.",
        "date": DATE, "read": "4 min", "cover_color": "#3a1420",
        "product_cats": ["erotisme"], "max_products": 6,
        "intro": [
            "Les jouets connectés se pilotent depuis une application, parfois à l'autre bout du monde. Pour les couples à distance — ou simplement joueurs — ils ouvrent un nouveau terrain de complicité. Voici l'essentiel pour bien débuter.",
        ],
        "sections": [
            ("Comment ça fonctionne", [
                "Le jouet se connecte en **Bluetooth** à une appli : à courte portée pour un usage à deux dans la pièce.",
                "Pour la distance, l'appli passe par **internet** : l'un pilote, l'autre reçoit, où qu'ils soient.",
            ]),
            ("Ce qu'il faut vérifier", [
                "La **confidentialité de l'appli** : préfère les marques sérieuses, regarde ce qui est collecté et évite de partager des données sensibles.",
                "La compatibilité avec ton téléphone et l'autonomie : un jouet qui se décharge en pleine soirée gâche le moment.",
            ]),
            ("Bien l'utiliser à deux", [
                "Établissez ensemble les **règles du jeu** : c'est le consentement et la complicité qui font le plaisir.",
                "Testez d'abord dans la même pièce avant de tenter à distance : ça évite les mauvaises surprises techniques.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pour les couples séparés par la distance, c'est un vrai fil complice. Choisis une marque fiable : la discrétion des données compte autant que le plaisir.",
        ],
    },
    {
        "slug": "premier-jouet-couple-par-ou-commencer",
        "kicker": "ÉROTISME", "category": "erotisme",
        "title": "Premier jouet à deux : par où commencer",
        "lead": "Franchir le pas sans se tromper ni se mettre la pression. Nos conseils pour choisir un premier accessoire simple, doux et rassurant.",
        "date": DATE, "read": "4 min", "cover_color": "#3a1420",
        "product_cats": ["erotisme"], "max_products": 6,
        "intro": [
            "Introduire un premier jouet dans le couple, ça peut intimider. Pourtant, bien abordé, c'est surtout un jeu de plus à partager. La clé : en parler d'abord, et choisir simple pour une première fois réussie.",
        ],
        "sections": [
            ("En parler avant d'acheter", [
                "Choisir **ensemble** enlève toute gêne et transforme l'achat en jeu complice, pas en test.",
                "L'idée n'est pas de combler un manque mais d'**ajouter du plaisir** : le dire clairement rassure.",
            ]),
            ("Quel type pour débuter", [
                "Un **petit stimulateur externe** ou un modèle à utiliser à deux est plus rassurant qu'un objet intimidant pour une première.",
                "Discret, silencieux, facile à prendre en main : mieux vaut simple et bien conçu que complexe.",
            ]),
            ("Les critères de qualité", [
                "**Silicone médical**, rechargeable, étanche : les repères d'un produit sûr et durable.",
                "Prévois un **lubrifiant à base d'eau**, compatible avec tout et parfait pour débuter en douceur.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pas de pression : un premier jouet, c'est juste une nouvelle façon de jouer. Commencez simple, vous affinerez vos envies ensuite.",
        ],
    },
    {
        "slug": "entretien-hygiene-jouets-intimes-guide",
        "kicker": "ÉROTISME", "category": "erotisme",
        "title": "Nettoyer et ranger ses jouets intimes",
        "lead": "L'hygiène des accessoires intimes est essentielle et souvent négligée. Comment les nettoyer, les sécher et les ranger pour qu'ils durent.",
        "date": DATE, "read": "3 min", "cover_color": "#3a1420",
        "product_cats": ["erotisme"], "max_products": 6,
        "intro": [
            "On parle peu d'entretien, et pourtant c'est ce qui garantit à la fois la sécurité et la longévité de ses accessoires. Bonne nouvelle : bien nettoyer un jouet prend une minute et évite bien des désagréments.",
        ],
        "sections": [
            ("Nettoyer après chaque usage", [
                "Eau tiède et **savon doux** ou nettoyant dédié suffisent pour la plupart des jouets en silicone.",
                "Attention aux **modèles électroniques** : ne pas immerger si le produit n'est pas marqué étanche, on nettoie la surface seulement.",
            ]),
            ("Bien sécher", [
                "Sèche complètement à l'air libre sur un linge propre **avant de ranger** : l'humidité favorise les bactéries.",
                "Évite les serviettes qui peluchent sur les matières poreuses.",
            ]),
            ("Ranger correctement", [
                "Un **étui en tissu** ou une pochette dédiée évite que les matières se touchent (certains silicones réagissent entre eux).",
                "À l'abri de la poussière, de la chaleur et de la lumière directe : le tiroir fermé reste l'idéal.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un nettoyant adapté et une pochette de rangement, c'est le petit kit qui prolonge la vie de tes accessoires et te garantit une hygiène irréprochable.",
        ],
    },
    {
        "slug": "parler-de-ses-envies-couple-intimite",
        "kicker": "ÉROTISME", "category": "erotisme",
        "title": "Parler de ses envies : la clé de l'intimité",
        "lead": "Oser dire ce qui plaît, écouter l'autre : la communication est le vrai moteur du désir. Comment en parler sans gêne ni jugement.",
        "date": DATE, "read": "4 min", "cover_color": "#3a1420",
        "product_cats": ["erotisme"], "max_products": 6,
        "intro": [
            "Le plus grand accélérateur de plaisir dans un couple n'est pas un objet : c'est la parole. Savoir dire ses envies et écouter celles de l'autre change tout. Pourtant, c'est souvent ce qu'on ose le moins. Quelques pistes pour se lancer.",
        ],
        "sections": [
            ("Pourquoi c'est si difficile", [
                "La peur du jugement ou de vexer freine : on préfère parfois se taire plutôt que risquer un malaise.",
                "Or l'autre n'est pas devin : ce qui n'est pas dit reste souvent une occasion manquée de plaisir partagé.",
            ]),
            ("Créer le bon moment", [
                "Aborder le sujet **en dehors du lit**, dans un moment détendu, enlève la pression de l'instant.",
                "Parler de ce qu'on **aime** (plutôt que de ce qui manque) rend l'échange positif et ouvert.",
            ]),
            ("Des outils pour se lancer", [
                "Un **jeu de cartes** ou un carnet à deux peut servir de prétexte pour aborder les envies sans se sentir exposé.",
                "Poser des questions ouvertes et écouter sans juger : la confiance se construit échange après échange.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La communication est le préliminaire le plus sous-estimé. Un couple qui se parle de ses envies est un couple qui se découvre sans fin.",
        ],
    },
    {
        "slug": "varier-preliminaires-raviver-desir-couple",
        "kicker": "ÉROTISME", "category": "erotisme",
        "title": "Varier les préliminaires pour raviver le désir",
        "lead": "La routine émousse le désir ; la nouveauté le réveille. Des idées simples pour renouveler les préliminaires et prolonger le plaisir.",
        "date": DATE, "read": "4 min", "cover_color": "#3a1420",
        "product_cats": ["erotisme"], "max_products": 6,
        "intro": [
            "Avec le temps, les habitudes s'installent et le désir peut s'endormir — non par lassitude de l'autre, mais par routine. Varier les préliminaires, prendre son temps autrement, suffit souvent à raviver l'étincelle.",
        ],
        "sections": [
            ("Sortir du pilote automatique", [
                "La routine n'est pas un problème d'amour mais d'**habitude** : changer un détail relance l'attention.",
                "Inverser l'ordre, changer de lieu, de moment de la journée : la nouveauté réveille le désir.",
            ]),
            ("Jouer sur les sens", [
                "Un **massage**, une huile chauffante, un bandeau sur les yeux : réveiller le toucher change toute la perception.",
                "La lenteur et l'anticipation valent mille techniques : faire durer, c'est déjà renouveler.",
            ]),
            ("S'aider d'un accessoire", [
                "Un **jeu coquin** ou un petit accessoire sert de prétexte joyeux pour sortir des sentiers battus.",
                "L'important reste la complicité : on essaie, on rit, on ajuste — la légèreté est le meilleur aphrodisiaque.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Pas besoin de tout révolutionner : un seul changement, une seule nouveauté par-ci par-là, suffit à entretenir la flamme sur la durée.",
        ],
    },

    # ─────────────── CADEAUX (6) ───────────────
    {
        "slug": "cadeau-saint-valentin-homme-idees",
        "kicker": "IDÉES CADEAUX", "category": "cadeaux",
        "title": "Cadeaux Saint-Valentin pour lui : nos idées",
        "lead": "Trouver le bon cadeau pour un homme sans tomber dans le cliché. Nos idées, du confort au coquin, pour une Saint-Valentin réussie.",
        "date": DATE, "read": "4 min", "cover_color": "#5a3a1a",
        "product_cats": ["cadeaux"], "max_products": 6,
        "intro": [
            "Offrir un cadeau à un homme pour la Saint-Valentin tourne vite au casse-tête : ni trop cliché, ni trop tiède. La bonne piste ? Un cadeau qui parle de vous deux, entre confort, plaisir et petite touche complice.",
        ],
        "sections": [
            ("Le confort qui fait toujours plaisir", [
                "Un **peignoir moelleux**, un ensemble d'intérieur douillet : le confort qu'un homme n'achète jamais pour lui-même.",
                "Un cadeau qu'il utilisera au quotidien reste toujours plus apprécié qu'un objet décoratif.",
            ]),
            ("La touche coquine", [
                "Un **coffret couple** ou un jeu à deux transforme le cadeau en promesse de moment partagé.",
                "L'idée n'est pas de gêner mais de proposer un jeu complice : à doser selon votre complicité.",
            ]),
            ("Le cadeau qui se vit à deux", [
                "Le meilleur cadeau reste souvent une **expérience partagée** : un dîner, une soirée pensée, un moment rien qu'à vous.",
                "Accompagne l'objet d'un mot : c'est l'intention qui transforme un présent en souvenir.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bon cadeau pour lui, c'est celui qui raconte votre histoire à deux — pas le plus cher, mais le plus juste.",
        ],
    },
    {
        "slug": "fete-des-meres-cadeau-bien-etre",
        "kicker": "IDÉES CADEAUX", "category": "cadeaux",
        "title": "Fête des Mères : offrir du bien-être",
        "lead": "Pour la fête des Mères, rien ne vaut un cadeau qui invite à souffler. Nos idées douceur et cocooning pour lui faire vraiment plaisir.",
        "date": DATE, "read": "4 min", "cover_color": "#5a3a1a",
        "product_cats": ["cadeaux"], "max_products": 6,
        "intro": [
            "Pour la fête des Mères, le cadeau le plus juste est souvent le plus simple : un moment de répit, une invitation à prendre soin d'elle. Le bien-être et le cocooning font mouche à tous les coups.",
        ],
        "sections": [
            ("Le cocooning qui fait du bien", [
                "Un **peignoir douillet**, une paire de chaussons moelleux : le cadeau qui dit « pose-toi, tu le mérites ».",
                "Ces objets du quotidien qu'on n'achète jamais pour soi sont ceux qui touchent le plus.",
            ]),
            ("Le rituel soin", [
                "Un **coffret de soins** (huile, gommage, bougie) transforme un simple bain en parenthèse rien qu'à elle.",
                "L'idée : offrir un moment, pas seulement un objet.",
            ]),
            ("Le petit plus qui touche", [
                "Un **coffret bien-être** joliment présenté, accompagné d'un mot, vaut mieux qu'un cadeau plus cher mais impersonnel.",
                "Et si le cadeau, c'était aussi du temps ? Un moment offert compte souvent plus que l'objet.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le meilleur cadeau de fête des Mères, c'est celui qui l'invite à ralentir. Un peu de douceur, un peu d'attention, et le tour est joué.",
        ],
    },
    {
        "slug": "evjf-idees-cadeaux-qui-font-mouche",
        "kicker": "IDÉES CADEAUX", "category": "cadeaux",
        "title": "EVJF : des cadeaux qui font mouche",
        "lead": "Pour l'enterrement de vie de jeune fille, on veut un cadeau drôle, tendre ou coquin — mais jamais gênant. Nos idées bien dosées.",
        "date": DATE, "read": "4 min", "cover_color": "#5a3a1a",
        "product_cats": ["cadeaux"], "max_products": 6,
        "intro": [
            "L'enterrement de vie de jeune fille, c'est l'occasion d'un cadeau à part : assez complice pour faire rire, assez délicat pour toucher. Tout est question de dosage — voici comment viser juste selon la future mariée.",
        ],
        "sections": [
            ("Le cadeau tendre", [
                "Une belle pièce de **lingerie** ou un coffret cocooning : élégant, personnel, apprécié bien après la fête.",
                "Parfait si la future mariée est plutôt réservée : on reste dans l'attention plutôt que la blague.",
            ]),
            ("Le cadeau qui fait rire", [
                "Un **jeu coquin** ou un accessoire complice détend l'ambiance et lance les fous rires du groupe.",
                "À adapter à sa personnalité : ce qui amuse l'une peut gêner l'autre, on connaît la mariée.",
            ]),
            ("Le cadeau collectif", [
                "Un **coffret commun** entre copines, plus généreux, marque le coup mieux que dix petits cadeaux dispersés.",
                "On glisse un mot signé de toutes : le souvenir compte autant que le contenu.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La règle d'or de l'EVJF : le cadeau doit faire plaisir à la mariée, pas amuser la galerie à ses dépens. Ajuste toujours à sa personnalité.",
        ],
    },
    {
        "slug": "couple-distance-cadeaux-qui-rapprochent",
        "kicker": "IDÉES CADEAUX", "category": "cadeaux",
        "title": "Couple à distance : des cadeaux qui rapprochent",
        "lead": "Quand les kilomètres séparent, le bon cadeau maintient le lien. Nos idées pour se sentir proche malgré la distance.",
        "date": DATE, "read": "4 min", "cover_color": "#5a3a1a",
        "product_cats": ["cadeaux"], "max_products": 6,
        "intro": [
            "Aimer à distance, c'est apprendre à entretenir le lien autrement. Le bon cadeau devient alors un fil qui relie : un objet qui rappelle l'autre, une attention qui traverse les kilomètres. Voici des idées qui rapprochent vraiment.",
        ],
        "sections": [
            ("Les objets qui rappellent l'autre", [
                "Un **parfum, un vêtement doux** qui porte l'odeur ou la présence de l'autre : le sensoriel comble un peu l'absence.",
                "Un peignoir ou un pull partagé devient un objet chargé de sens quand on est loin.",
            ]),
            ("Les cadeaux qui se vivent ensemble", [
                "Un **jouet connecté** pilotable à distance, un jeu à faire en visio : la technologie recrée de la complicité.",
                "L'idée : partager une expérience en même temps, malgré les kilomètres.",
            ]),
            ("Les attentions qui comptent", [
                "Un **coffret surprise** envoyé sans raison marque plus qu'un cadeau d'anniversaire attendu.",
                "Le petit mot manuscrit glissé dans le colis vaut souvent plus que l'objet lui-même.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "À distance, ce n'est pas la valeur du cadeau qui compte, mais le lien qu'il entretient. Un objet qui dit « je pense à toi » vaut tous les grands gestes.",
        ],
    },
    {
        "slug": "cadeau-couple-petit-budget-moins-30-euros",
        "kicker": "IDÉES CADEAUX", "category": "cadeaux",
        "title": "Faire plaisir à deux pour moins de 30 €",
        "lead": "Petit budget ne veut pas dire petit effet. Nos idées de cadeaux couple malins, tendres ou coquins, sans se ruiner.",
        "date": DATE, "read": "4 min", "cover_color": "#5a3a1a",
        "product_cats": ["cadeaux"], "max_products": 6,
        "intro": [
            "On peut faire très plaisir sans exploser son budget : le secret, c'est de miser sur l'intention et l'usage plutôt que sur le prix. Voici des idées de cadeaux couple à moins de 30 € qui ont vraiment de l'effet.",
        ],
        "sections": [
            ("Le petit luxe accessible", [
                "Une **bougie de massage**, une huile parfumée : peu coûteux, mais l'effet cocooning est immédiat.",
                "Ces petits plaisirs sensoriels donnent beaucoup pour leur prix.",
            ]),
            ("Le cadeau ludique", [
                "Un **jeu de cartes ou de dés coquin** coûte peu et offre des soirées entières de complicité.",
                "Idéal pour surprendre sans se ruiner, et souvent plus mémorable qu'un objet cher.",
            ]),
            ("L'attention qui compte double", [
                "Associe un **petit objet à un moment offert** (un massage, une soirée préparée) : l'intention démultiplie la valeur.",
                "Un joli emballage et un mot transforment un cadeau modeste en attention précieuse.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La preuve qu'un beau geste ne se mesure pas en euros : bien choisi, un cadeau à 20 € marque plus qu'un présent impersonnel bien plus cher.",
        ],
    },
    {
        "slug": "offrir-cadeau-intime-avec-tact-elegance",
        "kicker": "IDÉES CADEAUX", "category": "cadeaux",
        "title": "Offrir un cadeau intime avec tact",
        "lead": "Lingerie, accessoire, coffret coquin : le cadeau intime demande de la délicatesse. Comment l'offrir avec justesse, sans gêne.",
        "date": DATE, "read": "4 min", "cover_color": "#5a3a1a",
        "product_cats": ["cadeaux"], "max_products": 6,
        "intro": [
            "Offrir un cadeau intime, c'est délicat : mal amené, il peut gêner ; bien pensé, il touche et fait sourire. Tout est dans l'intention, le moment et la présentation. Voici comment le faire avec élégance.",
        ],
        "sections": [
            ("Choisir en pensant à l'autre", [
                "Le cadeau intime doit faire plaisir à **celui ou celle qui le reçoit**, pas seulement à celui qui l'offre.",
                "Pour de la lingerie, connais ses goûts et sa taille : un cadeau mal ajusté rate sa cible.",
            ]),
            ("Le bon moment", [
                "Réserve-le à un moment **complice et intime**, pas au milieu d'un repas de famille : le contexte fait tout.",
                "En cas de doute sur la réception, commence par une attention plus douce (coffret bien-être) qu'un accessoire osé.",
            ]),
            ("La présentation qui change tout", [
                "Un **bel emballage discret** et un mot tendre transforment le cadeau en attention élégante.",
                "La livraison en **colis neutre** garantit la discrétion jusqu'au moment où tu choisis de l'offrir.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le cadeau intime réussi, c'est une question de tact : offert avec délicatesse et au bon moment, il devient un souvenir complice plutôt qu'un malaise.",
        ],
    },
]


if __name__ == "__main__":
    main()
