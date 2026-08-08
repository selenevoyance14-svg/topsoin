#!/usr/bin/env python3
"""
Ajoute un 3e lot de NOUVEAUX articles au journal Maison Léa SANS toucher aux existants.

Même méthode que add-articles.py / add-articles-batch2.py :
- Génère les fichiers HTML des articles définis dans NEW_ARTICLES.
- Insère leurs cartes en tête de la grille de journal/index.html (non destructif).
- Sélectionne de vrais produits depuis data.jsx, avec rotation par catégorie.

Usage : python3 scripts/add-articles-batch3.py
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
    <strong>Transparence :</strong> En tant que Partenaire Amazon, je réalise un bénéfice sur les achats remplissant les conditions requises. <a href="/affiliation.html">En savoir plus</a>.
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

    for a in to_add:
        (JOURNAL / f"{a['slug']}.html").write_text(render_article(a, products), encoding="utf-8")
        print(f"✓ {a['slug']}.html")

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


DISCLAIMER_PRIME = "Tous les produits ci-dessous sont disponibles sur Amazon, souvent en livraison Prime et expédiés en colis neutre — discrétion totale."


NEW_ARTICLES = [
    # ─────────────────────────────────────── LINGERIE (7) ───────────────────────────────────────
    {
        "slug": "soutien-gorge-triangle-sans-armatures-douceur",
        "kicker": "GUIDE LINGERIE",
        "title": "Soutien-gorge triangle sans armatures : la douceur",
        "lead": "Léger, sans compression, souvent en dentelle : le triangle sans armatures redonne du confort à la poitrine. Pour qui, quand, comment.",
        "category": "lingerie", "date": "26 juillet 2026", "read": "4 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "Il y a des soirs où on décroche l'agrafe avec soulagement, et des jours où l'on préfèrerait ne pas la porter du tout. Le soutien-gorge triangle sans armatures fait le pari du milieu : un léger maintien, aucune baleine, la peau qui respire vraiment.",
        ],
        "sections": [
            ("Le principe : soutien souple, zéro pression", [
                "Pas d'armatures métalliques : c'est la **matière** (souvent une dentelle stretch ou un jersey doublé) qui contient la poitrine, sans la comprimer.",
                "Les bretelles fines répartissent le maintien sur les épaules plutôt que sur la cage thoracique — parfait après une journée assise, en télétravail ou en soirée cocooning.",
            ]),
            ("Pour quelle morphologie", [
                "**Poitrine menue à moyenne (jusqu'au bonnet C)** : c'est sa zone idéale, le triangle donne un joli galbe naturel sans effet gonflé.",
                "**Bonnets D et plus** : préférer les modèles à triangle **doublé + bande de dessous large** pour un vrai maintien. Sinon, réserver aux journées calmes.",
            ]),
            ("Quand le porter", [
                "En **journée douce** : télétravail, week-end, sortie en tissu fluide où l'on cherche la légèreté.",
                "En **lingerie de nuit assumée** : sous une nuisette, il devient une pièce à part entière.",
                "**À éviter** sous un vêtement très ajusté : la coupe ne redessine pas la poitrine comme le ferait un push-up.",
            ]),
            ("Le bon achat", [
                "Repérer l'élasthanne dans la composition (5 à 10 %) : c'est ce qui donne le maintien souple.",
                "Vérifier la **bande de dos** : plus elle est large, mieux elle tient. Un triangle avec une bande fine et lâche tombera en fin de journée.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le triangle sans armatures n'est pas un compromis, c'est un choix : celui du confort assumé. Une fois qu'on y goûte, on ne revient pas facilement en arrière.",
        ],
    },
    {
        "slug": "brassiere-sport-femme-comment-choisir-guide",
        "kicker": "GUIDE LINGERIE",
        "title": "Brassière de sport femme : la choisir vraiment bien",
        "lead": "Yoga, course, HIIT : chaque discipline demande un maintien différent. Notre guide pour trouver la brassière qui suit le mouvement.",
        "category": "lingerie", "date": "26 juillet 2026", "read": "5 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "Une brassière trop souple sur un cours de running, une brassière trop rigide sur un tapis de yoga : mêmes causes, même résultat, on abandonne au bout de deux séances. Le bon modèle se choisit d'abord par le sport pratiqué.",
        ],
        "sections": [
            ("Trois niveaux de maintien", [
                "**Léger** : yoga, pilates, marche. Le buste bouge peu, on privilégie la douceur et une matière respirante.",
                "**Modéré** : vélo, danse, gainage, machines en salle. Une brassière compressive à bretelles moyennes suffit.",
                "**Fort** : course à pied, saut à la corde, sports collectifs. Impératif : encapsulage (chaque sein est logé séparément) et bretelles larges.",
            ]),
            ("Le bon test à faire en magasin (ou à la réception)", [
                "**Sauter à pieds joints** : la poitrine doit rester quasi immobile. Si elle rebondit, le maintien n'est pas assez fort.",
                "**Lever les bras** : la bande de dessous ne doit pas remonter. Si elle bouge, la taille est trop grande.",
                "**Respirer profondément** : on doit pouvoir gonfler la cage thoracique sans gêne. Sinon, la taille est trop petite.",
            ]),
            ("La bonne matière", [
                "**Polyester + élasthanne** : sèche vite, garde sa forme. Le combo standard.",
                "**Nylon** : plus doux, mais retient un peu plus l'humidité. À réserver aux séances courtes.",
                "**Coton** : agréable au repos, mauvais dès qu'on transpire. À éviter pour le sport intensif.",
            ]),
            ("Renouveler quand ?", [
                "Une brassière **perd 20 à 30 % de son maintien après un an** d'utilisation régulière (transpiration + machine à laver).",
                "Le signal : la bande de dessous se détend et le maintien tombe. Il faut la remplacer, même si le tissu paraît intact.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Une bonne brassière, c'est celle qu'on oublie pendant la séance. Si on y pense, c'est qu'elle n'est pas la bonne — un mauvais choix coûte plus cher qu'un modèle bien pensé.",
        ],
    },
    {
        "slug": "soutien-gorge-forte-poitrine-maintien-guide",
        "kicker": "GUIDE MORPHOLOGIE",
        "title": "Forte poitrine : le soutien-gorge qui maintient vraiment",
        "lead": "Bonnets larges, bretelles renforcées, bande de dos structurée : ce qui fait la différence quand on cherche du vrai maintien sans compresser.",
        "category": "lingerie", "date": "26 juillet 2026", "read": "5 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "Trouver un soutien-gorge qui tient une forte poitrine sans faire mal aux épaules, ce n'est pas juste une question de taille. C'est une combinaison d'ingénieries discrètes : la coupe des bonnets, la largeur des bretelles, la solidité de la bande dorsale.",
        ],
        "sections": [
            ("Ce qui compte vraiment", [
                "**La bande de dos** supporte 80 % du poids : elle doit être large (au moins 3 cm), plate contre le corps, et absolument horizontale.",
                "**Les bretelles** doivent être larges et rembourrées, plutôt que fines et décoratives. Elles complètent, mais ne portent pas.",
                "**Les bonnets doivent tout envelopper** : le sein est logé, il ne déborde ni sur le côté ni au-dessus. Si ça déborde, la taille de bonnet est insuffisante.",
            ]),
            ("Le test des cinq points", [
                "1. Passer deux doigts sous la bande de dos : ils passent tout juste.",
                "2. Lever les bras : la bande ne remonte pas dans le dos.",
                "3. Se pencher en avant, ajuster les seins dans les bonnets : ils y restent.",
                "4. Vérifier le pont entre les bonnets : il doit être plat contre le sternum.",
                "5. Bretelles ajustables : le petit doigt passe entre la bretelle et l'épaule, pas plus.",
            ]),
            ("Coupes qui fonctionnent le mieux", [
                "**Balconnet à armatures profondes** : galbe et maintien pour l'habillé.",
                "**Emboîtant plein bonnet** : maintien maximal pour le quotidien.",
                "**Minimiseur** : redistribue le volume vers les côtés, utile sous un chemisier.",
                "**À éviter** : les push-ups classiques (trop peu enveloppants) et les triangles fins sans armatures (aucun maintien).",
            ]),
            ("Où mettre son budget", [
                "Un soutien-gorge de forte poitrine coûte souvent 30-50 €. C'est le prix des armatures larges, des bonnets bien coupés et d'une bande dorsale renforcée.",
                "Mieux vaut **trois modèles bien coupés** que dix soutien-gorges bas de gamme qui se déformeront en trois lavages.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Une forte poitrine bien logée, c'est un dos qui souffre moins et une silhouette qui respire. Prendre le temps de trouver le bon modèle change vraiment la journée.",
        ],
    },
    {
        "slug": "soutien-gorge-petite-poitrine-mettre-en-valeur",
        "kicker": "GUIDE MORPHOLOGIE",
        "title": "Petite poitrine : sublimer son décolleté avec finesse",
        "lead": "Push-up subtil, triangle en dentelle, balconnet léger : les coupes qui mettent en valeur sans tomber dans la surenchère.",
        "category": "lingerie", "date": "26 juillet 2026", "read": "4 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "La petite poitrine n'a rien à cacher — elle a juste besoin d'être bien accompagnée. Contrairement à ce qu'on lit partout, la solution n'est pas de doubler le volume avec de la mousse épaisse, mais de choisir des coupes qui **révèlent la silhouette naturelle**.",
        ],
        "sections": [
            ("Les coupes qui flattent", [
                "**Triangle en dentelle** : suit la ligne naturelle du sein, joli sous un décolleté en V.",
                "**Balconnet léger** : ouvre le buste, souligne la clavicule. Idéal sous un top à encolure large.",
                "**Push-up subtil** : rehausse sans tricher. Attention à choisir une mousse fine et bien coupée, pas une coque rigide qui se voit sous le tissu.",
                "**Bralette** : la version confort du triangle, à porter aussi bien sous un t-shirt qu'en pièce visible.",
            ]),
            ("Ce qui casse tout", [
                "**Le push-up trop épais** : la mousse cassante crée un « effet ballon » qui trahit tout de suite. Le naturel plaît davantage.",
                "**Le bonnet trop grand** : il baille et forme un pli disgracieux. Toujours vérifier que le bonnet est bien comblé.",
                "**Les modèles à armatures rigides** trop larges qui débordent hors du sein.",
            ]),
            ("Bien choisir sa taille", [
                "Beaucoup de femmes à petite poitrine portent **une taille de bonnet trop grande** — reste du souvenir adolescent quand on cherchait à combler.",
                "Vérifier la taille : le bonnet doit être **plein**, plat sur toute sa surface. Si on peut y glisser deux doigts, il est trop grand.",
                "Bonnet A et AA existent chez la plupart des marques : les demander explicitement.",
            ]),
            ("Le petit plus qui change tout", [
                "Une lingerie **assortie** (soutien-gorge + culotte de la même série) donne plus d'impact qu'une taille de bonnet supplémentaire.",
                "Les **détails** — dentelle, ruban satin, nœud — attirent le regard là où on veut. Miser dessus.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La petite poitrine se prête à tous les styles, du minimaliste au très romantique. Le vrai secret : arrêter de vouloir imiter les autres, et choisir ce qui te fait sentir toi.",
        ],
    },
    {
        "slug": "culotte-gainante-shapewear-silhouette-guide",
        "kicker": "GUIDE LINGERIE",
        "title": "Culotte gainante : silhouette impeccable sous la robe",
        "lead": "Ventre plat, hanches redessinées, cuisses fuselées : la gainante bien choisie disparaît sous le vêtement. Notre guide pour bien la choisir.",
        "category": "lingerie", "date": "27 juillet 2026", "read": "4 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "La culotte gainante a mauvaise réputation — souvenirs de gaines qui coupent en deux ou de coutures qui se voient sous la robe. Les modèles modernes n'ont plus rien à voir : ils sculptent en douceur, respirent, et surtout ne se voient pas.",
        ],
        "sections": [
            ("Trois niveaux de gainage", [
                "**Léger** : lisse la peau, atténue les petites irrégularités. À porter au quotidien sous un jean serré ou une robe fluide.",
                "**Moyen** : sculpte la taille et le ventre. C'est le niveau le plus polyvalent pour un événement.",
                "**Fort** : redessine complètement la silhouette. À réserver aux tenues très moulantes, pas au quotidien (compression forte = fatigue en fin de journée).",
            ]),
            ("Longueur : où va-t-elle s'arrêter", [
                "**Taille haute** : couvre le nombril, lisse le ventre. C'est la coupe la plus flatteuse sous une robe cintrée.",
                "**Mi-cuisse** : ajoute un lissage des cuisses. Utile sous une robe fourreau.",
                "**Body gainant** : englobe tout le buste. Choisir sans emplacement pour soutien-gorge intégré (c'est rarement bien coupé) : on porte son propre SG en-dessous.",
            ]),
            ("Ce qui ne se voit pas sous la robe", [
                "**Bord laser** : pas de couture ni d'élastique. C'est la vraie révolution des dernières années.",
                "**Matière fine et lisse** : chercher les composés microfibre + élasthanne. Éviter les nylons épais qui font des plis.",
                "**Couleur nude** : plus proche de ta carnation, mieux c'est. Le blanc et le noir se voient sous les tissus clairs.",
            ]),
            ("Les faux amis", [
                "**La culotte deux tailles trop petite** : ne gaine pas, elle serre. Résultat : bourrelet au-dessus.",
                "**La culotte gainante en dentelle** : jolie sur la photo, quasi zéro effet réel.",
                "**Le body ficelé de partout** : difficile aux toilettes, source de rides sous le vêtement.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Une bonne gainante, c'est un investissement d'occasion — mariage, cérémonie, photo importante. Une seule bien choisie couvre toutes les occasions.",
        ],
    },
    {
        "slug": "body-transparent-audace-elegance-guide",
        "kicker": "GUIDE LINGERIE",
        "title": "Le body transparent : oser l'audace en élégance",
        "lead": "Dentelle, tulle, filet : le body transparent joue sur le voile et le suggéré. Comment le porter avec assurance et raffinement.",
        "category": "lingerie", "date": "27 juillet 2026", "read": "4 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "Le body transparent n'est pas une provocation — c'est une pièce d'élégance qui se joue sur la nuance. Ce qui fait la différence entre vulgaire et magnifique : le choix de la matière, l'assemblage, et la façon dont on le porte.",
        ],
        "sections": [
            ("Trois grands types", [
                "**Le body en dentelle** : le classique intemporel, avec des motifs qui couvrent stratégiquement. C'est le plus « portable ».",
                "**Le body en tulle** : quasi totalement voilé, avec quelques renforts opaques. Réservé à une soirée intime.",
                "**Le body en filet** : maille plus large, effet graphique et moderne. À porter sous une veste ou dans une chambre.",
            ]),
            ("Ce qui fait la qualité", [
                "**Les coutures plates** : elles doivent être quasi invisibles, sinon elles cassent la ligne du corps.",
                "**La bordure des jambes** : élastique très fin, plat contre la peau. Un ourlet grossier gâche tout.",
                "**Le pressionnage à l'entrejambe** : indispensable pour aller aux toilettes sans se déshabiller. Vérifier avant d'acheter.",
            ]),
            ("Comment le porter", [
                "**Sous un blazer** ou une chemise ouverte : les zones opaques restent couvertes, le voile jouté juste à la clavicule et aux avant-bras.",
                "**En pièce intime seule** : sous un peignoir, comme cadeau, comme moment.",
                "**Sous une robe transparente** effet stylistique (tendance mode) : à assumer, très photogénique.",
            ]),
            ("Les erreurs à éviter", [
                "**Choisir la taille en dessous « pour que ça épouse mieux »** : ça marque partout et ça fait mal. Prendre sa taille normale.",
                "**L'associer à des dessous visibles** : la magie du body, c'est qu'il **remplace** la lingerie du dessous.",
                "**Le laver en machine à haute température** : la dentelle et l'élasthanne détestent. Cycle délicat, sac de lavage.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le body transparent, c'est une façon de dire quelque chose sans un mot. À toi de choisir la phrase que tu veux prononcer.",
        ],
    },
    {
        "slug": "corset-serre-taille-cambrer-silhouette-guide",
        "kicker": "GUIDE LINGERIE",
        "title": "Le corset serre-taille : cambrer sa silhouette",
        "lead": "Corset laçage arrière, serre-taille moderne : la pièce qui redessine la taille sans complexer. Comment le choisir et le porter.",
        "category": "lingerie", "date": "27 juillet 2026", "read": "4 min",
        "cover_color": "#8b1d2c", "product_cats": ["lingerie"], "max_products": 3,
        "intro": [
            "Longtemps rangé au rayon costume, le corset revient dans la lingerie contemporaine — mais en beaucoup plus doux. Les nouveaux modèles serre-taille sculptent sans emprisonner, et transforment une simple robe en pièce d'apparat.",
        ],
        "sections": [
            ("Corset vs serre-taille : ce n'est pas pareil", [
                "**Le corset traditionnel** descend sur les hanches et remonte au niveau de la poitrine. Il est baleiné, souvent laçé au dos, et se porte sur un vêtement.",
                "**Le serre-taille** cible uniquement la taille (10-15 cm de large). Il se porte sur ou sous le vêtement, plus discret et plus versatile.",
                "Le premier est spectaculaire, le second se glisse partout.",
            ]),
            ("Bien choisir sa taille", [
                "Mesurer son **tour de taille naturel** (le plus fin, au-dessus du nombril), et retirer 5 à 8 cm pour l'effet cambré. Pas plus au début, sinon on n'y tient pas debout une heure.",
                "Un corset bien porté doit **laisser respirer** : on doit pouvoir manger un dîner sans le desserrer. Sinon on a serré trop.",
            ]),
            ("Comment le porter", [
                "**Sur une chemise en soie** : blanc + serre-taille noir, effet parisien immédiat.",
                "**Sous une veste ouverte** : le corset devient le top principal.",
                "**En lingerie de dessous** : pour une soirée où l'on veut se sentir spectaculaire, même si personne ne le voit.",
            ]),
            ("Les précautions", [
                "**Ne pas dormir avec** : le corps a besoin de bouger la nuit.",
                "**Commencer par 1 h par jour**, augmenter progressivement. La musculature du dos doit s'adapter.",
                "**Éviter juste après un repas copieux** — c'est de bon sens mais on l'oublie.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le corset, ce n'est pas cacher son corps — c'est le mettre en scène. Une pièce qui se choisit sans culpabilité, portée pour soi d'abord.",
        ],
    },

    # ─────────────────────────────────────── NUIT (6) ───────────────────────────────────────
    {
        "slug": "pyjama-court-femme-ete-fraicheur-guide",
        "kicker": "GUIDE NUIT",
        "title": "Pyjama court femme : rester au frais toute la nuit",
        "lead": "Coton respirant, satin léger, viscose : les matières qui font la différence quand la chambre dépasse les 22 degrés.",
        "category": "nuit", "date": "27 juillet 2026", "read": "4 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "Les nuits d'été ne pardonnent pas les mauvais choix de pyjama. Une matière qui étouffe, et on se réveille trois fois pour la retirer. La bonne coupe et le bon tissu changent complètement la qualité du sommeil.",
        ],
        "sections": [
            ("Les matières qui respirent vraiment", [
                "**Coton peigné** : le classique. Absorbe la transpiration, se lave à chaud, dure des années.",
                "**Viscose de bambou** : ultra fluide, plus fraîche que le coton, sèche vite après une nuit chaude.",
                "**Satin de coton** (pas polyester) : le glissé du satin, l'absorption du coton. Le meilleur des deux.",
                "**À éviter** : polyester pur, nylon, tout ce qui « brille sans respirer ».",
            ]),
            ("Coupes qui laissent circuler l'air", [
                "**Débardeur + short** : le duo classique. Chercher un short **taille élastiquée sans cordon** pour la nuit.",
                "**Chemise sans manche + short** : plus habillé, effet loungewear le lendemain matin.",
                "**Nuisette courte** : la version « pas de haut, pas de bas », maximum de respiration.",
            ]),
            ("Les détails qui comptent", [
                "**Coutures plates** : sinon elles s'impriment sur la peau au réveil.",
                "**Bordures fines** aux emmanchures : rien qui coupe la circulation.",
                "**Couleur claire** : renvoie la chaleur. Un pyjama noir se réchauffe plus vite qu'un blanc.",
            ]),
            ("Bien l'entretenir pour l'été", [
                "**Lavage à 30°C** en cycle doux : préserve les fibres et les couleurs claires.",
                "**Séchage à l'air libre** : le sèche-linge cuit le coton et raccourcit sa vie.",
                "**Renouveler après 2-3 ans** : la fibre perd sa capacité d'absorption avec les lavages.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le bon pyjama d'été, c'est celui qu'on oublie pendant qu'on dort. On garde deux ou trois modèles en rotation — un en machine, un sur soi, un dans le placard.",
        ],
    },
    {
        "slug": "debardeur-nuit-femme-confort-choisir-guide",
        "kicker": "GUIDE NUIT",
        "title": "Débardeur de nuit femme : le basique du sommeil",
        "lead": "Léger, sans manche, souvent avec un short : le débardeur de nuit est le meilleur allié des grandes chaleurs et des chambres bien chauffées.",
        "category": "nuit", "date": "27 juillet 2026", "read": "3 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "Simple, ultraléger, souvent négligé : le débardeur de nuit est le sous-vêtement de sommeil le plus efficace pour les chaleurs. On sous-estime la différence qu'il fait avec un t-shirt trop long ou un pyjama trop épais.",
        ],
        "sections": [
            ("Coupe et longueur", [
                "**Coupe droite** : le plus polyvalent, tombe naturellement sans coller à la taille.",
                "**Coupe cintrée** : galbe légèrement la taille, joli si on se lève la nuit.",
                "**Longueur mi-cuisse** : idéale pour dormir sans culotte, tout en restant décent si l'on quitte la chambre.",
            ]),
            ("Bretelles : le détail qui fait tout", [
                "**Bretelles larges** : glissent moins, ne coupent pas les épaules. Meilleures pour dormir.",
                "**Bretelles fines type spaghetti** : joli visuel, mais peuvent tomber pendant le sommeil.",
                "**Bretelles ajustables** : à préférer si l'on a un buste court ou long.",
            ]),
            ("Matières recommandées", [
                "**Coton bio** : pas de résidu chimique, doux dès le premier lavage.",
                "**Modal** : ultra fluide, ne se froisse pas, sèche vite.",
                "**Viscose de bambou** : le plus frais des trois, parfait sous les tropiques.",
            ]),
            ("Bien le porter avec un short", [
                "Assortis coton + coton, satin + satin : ne pas mélanger les matières, sinon les statiques créent de l'inconfort.",
                "Un débardeur suffit-il seul ? Oui l'été, en chambre au-dessus de 24°C.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le débardeur de nuit est le pilier discret des placards bien pensés. Trois modèles en rotation, on n'a plus besoin d'autre chose pour l'été.",
        ],
    },
    {
        "slug": "peignoir-bambou-douceur-alternative-guide",
        "kicker": "GUIDE COCOONING",
        "title": "Peignoir en bambou : l'alternative douce au coton",
        "lead": "Plus doux, plus absorbant, plus léger que le coton : le peignoir en fibre de bambou séduit ceux qui cherchent le vrai confort au réveil.",
        "category": "nuit", "date": "27 juillet 2026", "read": "4 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "Le peignoir en éponge de coton, on connaît. Le peignoir en fibre de bambou, moins — c'est pourtant sur cette matière que la plupart des grands hôtels sont passés ces dernières années. La raison ? Elle absorbe mieux, sèche plus vite, et reste douce lavage après lavage.",
        ],
        "sections": [
            ("Pourquoi le bambou", [
                "**Absorption** : la fibre de bambou capte 30 à 40 % d'eau en plus qu'un coton équivalent. On se sèche vraiment en sortant du bain.",
                "**Douceur naturelle** : la fibre est ronde en microscopie (le coton est irrégulier), donc plus caressante sur la peau.",
                "**Hypoallergénique** : la fibre de bambou est naturellement peu propice aux bactéries et acariens. Utile pour les peaux réactives.",
            ]),
            ("Ce qu'il faut vérifier avant d'acheter", [
                "**Grammage** entre 350 et 500 g/m² : suffisant pour absorber sans être lourd.",
                "**Bambou seul ou mélangé** : un mélange avec 30 % de coton est plus résistant au fil des lavages.",
                "**Poche kangourou et ceinture large** : les détails qui montrent qu'on est sur un modèle bien pensé.",
            ]),
            ("Entretien : simple mais précis", [
                "**Laver à 40°C** en cycle éponge : préserve les fibres.",
                "**Éviter l'adoucissant** : il gomme la capacité d'absorption. Une astuce : vinaigre blanc au rinçage, un demi-verre, une fois sur trois.",
                "**Séchage à l'air ou en sèche-linge doux** : le bambou tolère mieux le sèche-linge que le coton.",
            ]),
            ("À qui l'offrir", [
                "**Cadeau naissance couple** : peignoir bambou + chaussons, un basique qu'on n'oublie pas.",
                "**Emménagement** : plus utile qu'une bougie décorative.",
                "**Retour de vacances** : le contraste avec l'hôtel se sent immédiatement.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un peignoir bien choisi dure 5 à 8 ans. Passer au bambou, c'est un petit surcoût rentabilisé dès la première année, en confort et en durée.",
        ],
    },
    {
        "slug": "pyjama-couple-assorti-cadeau-guide",
        "kicker": "IDÉES CADEAU",
        "title": "Pyjama couple assorti : le cadeau qui touche",
        "lead": "Même matière, mêmes couleurs, coupes adaptées à chacun : le pyjama assorti dit ce qu'on n'ose parfois pas.",
        "category": "nuit", "date": "28 juillet 2026", "read": "4 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "Un pyjama assorti, ça n'a l'air de rien — et c'est pourtant un des cadeaux les plus regardés au moment de l'ouverture. Le message est clair : on prend soin du confort de l'autre, on aime les petits rituels à deux.",
        ],
        "sections": [
            ("Trois grandes familles", [
                "**Satin** : élégant, coquin, se prête aux occasions (Saint-Valentin, anniversaire de rencontre). Effet « photo Instagram ».",
                "**Coton flanelle** : chaud, roots, hivernal. Pour un couple qui aime la vie douce au coin du feu.",
                "**Pilou-pilou** : le côté cocooning assumé, avec motifs. À réserver aux couples qui ont de l'humour.",
            ]),
            ("Ce qui fait un bon pyjama couple", [
                "**Deux coupes** vraiment adaptées, pas un modèle unique décliné en deux tailles.",
                "**Couleurs identiques**, mais pas forcément motif identique — l'assorti fonctionne mieux que le clone.",
                "**Vraie qualité de matière** : c'est un cadeau qui s'utilise 200 nuits par an. Éviter le polyester trop brillant.",
            ]),
            ("Quand l'offrir", [
                "**Premier hiver ensemble** : ancrer le rituel des soirées au chaud.",
                "**Emménagement à deux** : le pyjama assorti fait partie de la première commande commune.",
                "**Anniversaire de mariage** : les 10 ans (noces d'étain) tolèrent très bien le clin d'œil moderne.",
                "**Cadeau de dernière minute** : offrable même la veille, si commandé en Prime.",
            ]),
            ("Ce qu'il ne faut pas faire", [
                "**Choisir sans mesures** : un pyjama qui ne va pas, c'est un cadeau qui reste au fond du placard.",
                "**Prendre trop chaud « au cas où »** : mieux vaut deux modèles saisonniers qu'un pyjama polaire hors-saison.",
                "**Miser sur l'humour douteux** : les pyjamas à messages coquins vieillissent mal.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le pyjama assorti n'est pas un cadeau kitsch — c'est une déclaration silencieuse. Choisi avec goût, il devient un des souvenirs les plus tendres du couple.",
        ],
    },
    {
        "slug": "nuisette-rouge-cadeau-saint-valentin-guide",
        "kicker": "GUIDE LINGERIE",
        "title": "La nuisette rouge : cadeau intense de Saint-Valentin",
        "lead": "Symbole du désir et de la passion, la nuisette rouge se choisit avec soin. Nos conseils pour éviter le kitsch et viser juste.",
        "category": "nuit", "date": "28 juillet 2026", "read": "4 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "Le rouge dit tout ce que la Saint-Valentin veut dire : le désir, la fête, l'amour incarné. Encore faut-il choisir la bonne nuance et la bonne coupe — un rouge trop vif dans une matière bon marché tombe vite dans le déguisement.",
        ],
        "sections": [
            ("Le rouge : plusieurs nuances", [
                "**Rouge bordeaux / grenat** : le plus flatteur sur toutes les carnations. Élégant, presque intemporel.",
                "**Rouge cerise vif** : plus jeune, plus assumé. Superbe sur une peau très claire ou très mate.",
                "**Rouge brique / rouille** : le clin d'œil bohème, moins classique mais très porté.",
                "**À éviter** : le rouge fluo et le rouge orangé, difficiles à assumer sans effet costume.",
            ]),
            ("Matières qui subliment le rouge", [
                "**Satin de soie** : le must. La matière capte la lumière et fait vivre la couleur.",
                "**Dentelle noire sur fond rouge** : effet raffiné, moins « bloc de couleur ».",
                "**Velours** : sensualité tactile, plus habillé — pour une soirée où l'on prend le temps.",
                "**À éviter** : le polyester brillant qui vieillit mal, la dentelle rouge criard.",
            ]),
            ("Bien choisir la coupe", [
                "**Nuisette courte + kimono assorti** : le duo qui laisse le choix (montrer ou couvrir).",
                "**Nuisette mi-longue** : plus flatteuse sur toutes les silhouettes, moins « lingerie de catalogue ».",
                "**Coupe empire** (fronces sous la poitrine) : particulièrement flatteuse en rouge.",
            ]),
            ("Comment l'offrir", [
                "**Dans un joli sac tissu** plutôt qu'une boîte impersonnelle : plus intime.",
                "**Avec un mot manuscrit** : ce que le rouge veut dire, mieux si c'est mis en mots.",
                "**Ni trop tôt, ni trop tard** : le soir de la Saint-Valentin, à la maison, en tête-à-tête. Pas au restaurant.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Une nuisette rouge bien choisie, c'est une seule pièce qui fait toute la soirée. Le budget se joue sur la matière et la coupe, pas sur les détails brillants.",
        ],
    },
    {
        "slug": "pyjama-polaire-femme-hiver-cocooning-guide",
        "kicker": "GUIDE COCOONING",
        "title": "Pyjama polaire femme : dormir au chaud tout l'hiver",
        "lead": "Doudou porté sur soi, chaleur immédiate : la polaire s'impose quand le chauffage baisse la nuit. Notre guide pour bien la choisir.",
        "category": "nuit", "date": "28 juillet 2026", "read": "4 min",
        "cover_color": "#3a2e1f", "product_cats": ["nuit"], "max_products": 3,
        "intro": [
            "Il y a les nuits d'hiver où le chauffage tourne à plein, et celles où on descend le thermostat pour économiser. Dans les deux cas, le pyjama polaire fait la différence entre une nuit paisible et un réveil frigorifié.",
        ],
        "sections": [
            ("Les différentes polaires", [
                "**Polaire microfibre** : la plus courante, légère et douce, sèche vite.",
                "**Polaire coral fleece** : plus longue, plus douce au toucher, effet peluche.",
                "**Polaire sherpa** : imitation mouton, très chaude, plutôt pour les intersaisons froides.",
                "**Coton molleton (jogging)** : plus lourd, plus solide, un peu moins « doudou » mais durable.",
            ]),
            ("Coupes qui gardent la chaleur", [
                "**Combi-pilote (une pièce)** : maximale chaleur, mais pas pratique la nuit pour les toilettes.",
                "**Ensemble haut long + bas long** : le meilleur compromis, la chaleur circule.",
                "**Robe polaire longue** : cocooning sans la ceinture, parfait pour les femmes qui n'aiment pas le pantalon la nuit.",
            ]),
            ("Éviter les mauvaises surprises", [
                "**Peluchage** : les polaires bon marché relâchent des fibres au premier lavage. Investir un peu.",
                "**Statique** : la polaire attire les fibres et fait des étincelles. Utiliser un anti-statique ou vinaigre au rinçage.",
                "**Surchauffe** : au-dessus de 20°C dans la chambre, la polaire fait transpirer. Réservée aux vraies nuits froides.",
            ]),
            ("À qui l'offrir", [
                "**Cadeau Noël femme** : indémodable, tout le monde a besoin d'un bon pyjama chaud.",
                "**Naissance couple** : quand bébé pleure la nuit, se lever sans grelotter aide à ne pas s'énerver.",
                "**Cadeau étudiante** : dans un studio mal chauffé, ça change la vie.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un bon pyjama polaire tient 4-5 hivers si on ne le passe pas au sèche-linge. Un vrai basique, à choisir sans compromis sur la matière.",
        ],
    },

    # ─────────────────────────────────────── SENSUALITÉ (7) ───────────────────────────────────────
    {
        "slug": "vibromasseur-waterproof-bain-douche-guide",
        "kicker": "GUIDE PLAISIR",
        "title": "Vibromasseur waterproof : bain, douche, aucun souci",
        "lead": "Étanchéité complète, silicone premium, entretien facile : le vibromasseur waterproof libère l'usage. Notre guide pour bien choisir.",
        "category": "sensualite", "date": "28 juillet 2026", "read": "4 min",
        "cover_color": "#5b1a26", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "L'étanchéité est probablement le critère le plus sous-estimé quand on achète un premier vibromasseur. Pas parce qu'on veut absolument l'emmener dans le bain — mais parce qu'un jouet **waterproof se nettoie complètement à l'eau savonneuse**, ce qui change tout côté hygiène.",
        ],
        "sections": [
            ("Comprendre les indices d'étanchéité", [
                "**IPX7** : résiste à une immersion jusqu'à 1 m pendant 30 min. Suffisant pour la douche, la baignoire, le nettoyage sous l'eau.",
                "**IPX6** : résiste aux projections mais pas à l'immersion. À laver au chiffon humide uniquement.",
                "**IPX4** : simple résistance aux éclaboussures. À éviter si l'on veut vraiment un « waterproof ».",
            ]),
            ("Pourquoi c'est vraiment utile", [
                "**Nettoyage complet** : eau + savon doux sur toute la surface, y compris le bouton et la charge (à condition d'un port de charge magnétique).",
                "**Utilisation dans le bain** : la chaleur de l'eau détend, les vibrations s'amplifient légèrement. Effet unique.",
                "**Voyage** : moins d'angoisse en cas de contact avec un contenant renversé dans le sac.",
            ]),
            ("Ce à quoi faire attention", [
                "**Port de charge USB classique** : indique souvent que l'étanchéité est bidon. Chercher **la charge magnétique** ou par contact (sans trou dans la coque).",
                "**Silicone médical seul** : pas d'ABS peint qui s'écaille au contact de l'eau.",
                "**Bouton unique bien étanche** : plus il y a de boutons, plus il y a de failles.",
            ]),
            ("Entretien post-usage", [
                "Rincer à l'eau tiède, savonner avec un savon doux (pas de gel douche parfumé qui laisse des résidus).",
                "Sécher soigneusement — surtout autour du bouton — avant de charger.",
                "Ranger dans une pochette tissu (pas de plastique fermé, qui retient l'humidité).",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le waterproof n'est pas un gadget, c'est une norme d'hygiène. Payer 5 à 10 € de plus pour un vrai IPX7 se rentabilise à chaque usage.",
        ],
    },
    {
        "slug": "vibromasseur-telecommande-couple-distance-guide",
        "kicker": "GUIDE PLAISIR",
        "title": "Vibromasseur à télécommande : jouer à distance",
        "lead": "Télécommande physique, app smartphone, connexion Bluetooth : le jouet à contrôle distant réinvente le jeu. Notre guide pour bien choisir.",
        "category": "sensualite", "date": "28 juillet 2026", "read": "5 min",
        "cover_color": "#5b1a26", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "Le vibromasseur à télécommande transforme la logique de l'objet : ce n'est plus soi seul qui décide, c'est un(e) partenaire ou même une routine partagée à distance. Un basculement discret qui ajoute une dimension entière au plaisir.",
        ],
        "sections": [
            ("Télécommande physique vs application", [
                "**Télécommande physique** : simple, fiable, portée courte (5-10 m). Idéale pour un usage à la maison, à deux, dans la même pièce.",
                "**Application smartphone** : portée illimitée (via internet). Idéale pour couples séparés géographiquement.",
                "**Le meilleur des deux** : certains modèles proposent les deux — la télécommande physique pour la chambre, l'application pour l'absence.",
            ]),
            ("Ce qui fait un bon jouet à télécommande", [
                "**Latence faible** : moins d'une seconde entre l'appui et la vibration. Sinon c'est frustrant.",
                "**Autonomie** : au moins 60 min à moyenne intensité. Rien de pire qu'un jouet qui lâche en pleine séance.",
                "**Sécurité de l'app** : chiffrement des commandes envoyées. On ne veut pas que le voisin joue avec.",
                "**Confort porté** : si c'est un jouet à porter en public, il doit tenir sans glisser.",
            ]),
            ("Trois grandes catégories d'usage", [
                "**En solo** : télécommande dans une main, jouet sur soi. Pratique pour explorer sans se contorsionner.",
                "**En couple présent** : l'autre a la télécommande. Ambiance apéro, dîner, cinéma à la maison.",
                "**En couple à distance** : l'application depuis le smartphone du partenaire. Marche même à plusieurs milliers de kilomètres.",
            ]),
            ("Les erreurs classiques", [
                "**Vouloir commencer par la version à distance** sans avoir jamais joué en présence. Trop d'inconnues d'un coup.",
                "**Négliger la première communication** : les intensités, les zones, les mots-code. À caler avant, pas pendant.",
                "**Sous-estimer l'autonomie du téléphone** : contrôler un jouet une heure vide vraiment la batterie.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La télécommande, c'est un jeu de confiance avant d'être un jeu physique. Bien vécu, c'est une des expériences les plus complices du couple moderne.",
        ],
    },
    {
        "slug": "vibromasseur-rechargeable-usb-autonomie-guide",
        "kicker": "GUIDE PLAISIR",
        "title": "Vibromasseur rechargeable USB : liberté et autonomie",
        "lead": "Fini les piles à changer : le rechargeable USB est devenu la norme. Nos critères pour choisir un modèle qui dure vraiment.",
        "category": "sensualite", "date": "28 juillet 2026", "read": "4 min",
        "cover_color": "#5b1a26", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "Le vibromasseur à piles, c'est comme le lecteur MP3 à cassette : ça a existé, ça a fait son temps. La rechargeable USB est la norme depuis 5 ans, et ce n'est pas juste par écologie — c'est aussi par confort d'usage.",
        ],
        "sections": [
            ("Pourquoi c'est mieux que les piles", [
                "**Puissance stable** : les piles perdent en tension au fil de l'usage, la vibration faiblit. Le rechargeable garde son intensité jusqu'au bout.",
                "**Coût réel** : un jouet à piles coûte 30-40 € par an en piles alcalines. Le rechargeable s'amortit en un an.",
                "**Étanchéité** : plus de compartiment à piles = coque hermétique = vraie étanchéité possible.",
                "**Silence** : les moteurs modernes sont beaucoup plus silencieux que les mécaniques à piles.",
            ]),
            ("Ce qui fait la différence entre deux modèles", [
                "**Autonomie annoncée vs réelle** : diviser par 1,5 le chiffre du fabricant pour avoir la réalité à haute intensité.",
                "**Temps de charge** : 90 min à 2 h pour une charge complète est standard. Au-dessus, c'est trop.",
                "**Type de port** : USB-C (moderne), USB-micro (correct), charge magnétique par contact (le must pour l'étanchéité).",
                "**Voyant de charge** : un LED qui indique clairement l'état évite de deviner.",
            ]),
            ("Erreurs à éviter dans l'usage", [
                "**Laisser branché en permanence** : ce n'est pas un téléphone, la batterie n'aime pas la charge continue.",
                "**Charger complètement épuisé** : idéal de recharger vers 20 % restants, pas quand c'est à zéro.",
                "**Utiliser un chargeur non fourni** : les watts trop élevés peuvent abîmer la batterie.",
            ]),
            ("Durée de vie réaliste", [
                "**300 à 500 cycles de charge** : soit 3 à 5 ans d'usage régulier.",
                "**Signal de fin** : quand l'autonomie chute brutalement, c'est que la batterie fatigue. Il est temps de remplacer.",
                "**Recyclage** : ne pas jeter à la poubelle classique. Bacs DEEE en supermarché.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un bon rechargeable USB, c'est 3 à 5 ans de tranquillité et zéro pile à racheter. Le petit surcoût à l'achat se rentabilise très vite.",
        ],
    },
    {
        "slug": "sextoys-premium-luxe-investir-guide",
        "kicker": "GUIDE PLAISIR",
        "title": "Sextoys premium : investir dans la qualité",
        "lead": "Silicone platine, moteurs allemands, design pensé : le sextoy premium n'est pas un caprice. Pourquoi la qualité change tout.",
        "category": "sensualite", "date": "28 juillet 2026", "read": "5 min",
        "cover_color": "#5b1a26", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "On peut acheter un vibromasseur à 15 € en grande surface. On peut aussi en payer 150. La différence n'est pas juste marketing — elle se voit sur le silicone, s'entend sur le moteur, se ressent dès la première utilisation.",
        ],
        "sections": [
            ("Où passe le budget", [
                "**Silicone platine médical** : plus lisse, plus doux, ne retient pas les odeurs. Un ABS peint coûte 10 fois moins mais s'écaille.",
                "**Moteur brushless** : moins bruyant, vibrations plus profondes, longévité 3-4 fois supérieure.",
                "**Batterie longue durée** : cellules de qualité qui gardent leur autonomie 5 ans, contre 18 mois pour du premier prix.",
                "**Étanchéité vraie** : un IPX7 réel demande du design, pas juste un joint autour du bouton.",
            ]),
            ("Ce qui ne se voit pas mais compte", [
                "**Certifications** : REACH, CE, FDA. Les marques premium documentent la composition — les low-cost cachent.",
                "**Garantie** : 2 ans minimum, souvent 5 ans en premium. Rare en low-cost.",
                "**SAV** : joignable, en français, avec renvoi possible. À vérifier avant achat.",
            ]),
            ("Les grandes maisons à connaître", [
                "**Marques scandinaves** (design + silence) : LELO, Fun Factory.",
                "**Marques américaines** (technologie + puissance) : We-Vibe, Womanizer.",
                "**Marques françaises** (finesse + qualité) : Dorcel, Satisfyer (segment premium).",
            ]),
            ("Faut-il vraiment investir 100+ €", [
                "**Non** si c'est un premier essai : commencer avec un modèle à 30-50 € pour tester ses préférences.",
                "**Oui** si l'on utilise régulièrement et qu'on veut monter en gamme : la différence de sensation et de silence est nette.",
                "**Oui** si on cherche un cadeau qui marque : le packaging premium fait partie de la valeur.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le sextoy premium se juge à ce qu'il devient après 6 mois d'usage : silencieux comme au premier jour, silicone impeccable, autonomie stable. Un vrai investissement plaisir.",
        ],
    },
    {
        "slug": "sextoys-budget-qualite-prix-guide",
        "kicker": "GUIDE PLAISIR",
        "title": "Sextoys petit budget : la qualité sans se ruiner",
        "lead": "Sous 30 €, on trouve encore de très bons jouets — à condition de savoir quoi regarder. Nos critères pour éviter les pièges.",
        "category": "sensualite", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#5b1a26", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "Le luxe, c'est bien, mais tout le monde n'a pas 100 € à mettre dans un premier jouet. La bonne nouvelle : le marché du sextoy à moins de 30 € a beaucoup progressé ces dernières années. La moins bonne : il faut savoir trier.",
        ],
        "sections": [
            ("Le minimum absolu à exiger", [
                "**Silicone médical** : c'est aujourd'hui la norme même en entrée de gamme. Refuser tout jouet PVC ou TPE bas prix (poreux, retient les bactéries).",
                "**Rechargeable USB** : les modèles à piles à ce prix-là sont bruyants et vibrent faiblement.",
                "**Vraie étanchéité IPX7** : mentionnée clairement, pas juste « résistant à l'eau ».",
                "**Avis clients français** > 100, note ≥ 4/5 sur Amazon.",
            ]),
            ("Où concéder sans regret", [
                "**Design** : les jouets premium ont un packaging soigné, le budget non. Aucun impact sur l'usage.",
                "**Bruit léger** : un moteur budget fait 45-55 dB, un premium 30-40 dB. La différence se sent, mais reste utilisable.",
                "**Nombre de modes** : 6 modes bien réglés suffisent largement, pas besoin de 20.",
            ]),
            ("Où NE PAS concéder", [
                "**Étanchéité** : sans ça, le nettoyage devient un problème d'hygiène.",
                "**Puissance moteur** : un jouet trop faible ne mène nulle part, autant ne pas acheter.",
                "**Batterie** : les cellules mal fabriquées lâchent en 6 mois. Chercher une marque connue même en budget.",
            ]),
            ("Trois profils, trois choix", [
                "**Curieuse qui essaie** : mini-vibro clitoridien à 20-25 €. Compact, discret, efficace.",
                "**Couple qui explore** : œuf vibrant à télécommande à 25-30 €. Ouvre le jeu à deux.",
                "**Envie d'un rabbit** : les modèles à 30 € marchent honnêtement, mais dureront 12-18 mois. Passer plus cher si l'usage devient régulier.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le sextoy petit budget n'est pas un sous-jouet — c'est un jouet honnête. Bien choisi, il fait le job aussi bien qu'un modèle 3 fois plus cher pour l'usage occasionnel.",
        ],
    },
    {
        "slug": "sextoys-couple-partager-debuter-guide",
        "kicker": "GUIDE COUPLE",
        "title": "Sextoys en couple : partager sans se braquer",
        "lead": "Introduire un jouet à deux demande de la parole avant la pratique. Comment aborder le sujet, choisir, et vivre l'expérience.",
        "category": "sensualite", "date": "29 juillet 2026", "read": "5 min",
        "cover_color": "#5b1a26", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "Introduire un sextoy dans un couple, ce n'est pas déclarer que quelque chose manque — c'est proposer un nouveau chapitre. Encore faut-il en parler comme d'une invitation, pas comme d'une réponse à un problème.",
        ],
        "sections": [
            ("Comment aborder le sujet", [
                "**Choisir le moment** : jamais juste après un moment intime, jamais dans un contexte de tension. En balade, en cuisine, quand l'ambiance est légère.",
                "**Formuler positivement** : « J'aimerais essayer avec toi » et pas « il te manque quelque chose ».",
                "**Écouter la première réaction** sans forcer : un « je sais pas » n'est pas un « non ». Laisser le temps.",
                "**Regarder le catalogue à deux** : dédramatise complètement.",
            ]),
            ("Choisir un premier jouet à deux", [
                "**Œuf vibrant à télécommande** : le partage est immédiat, pas d'intrusion, une main pour chacun.",
                "**Anneau vibrant pour homme** : profite à deux en même temps, souvent bien accueilli.",
                "**Vibro clitoridien externe** : peut se glisser dans les préliminaires sans casser le rythme.",
                "**À éviter au début** : les jouets internes (gode) qui demandent plus de familiarité.",
            ]),
            ("Le premier usage", [
                "**Faire un test seuls avant** : chacun l'essaie, comprend les intensités, sait ce qui lui plaît. On arrive préparé.",
                "**Commencer doux** : première intensité, en dehors du corps, comme un jeu.",
                "**Parler pendant** : « c'est bien là », « moins fort », des mots simples suffisent.",
                "**S'arrêter quand on veut** : le jouet ne dicte rien, c'est un outil pas un objectif.",
            ]),
            ("Après", [
                "**Nettoyer ensemble** : normalise l'objet, comme la brosse à dents.",
                "**Ranger visible** : dans un tiroir accessible, pas caché au fond d'un carton.",
                "**Renouveler la conversation** : ce qui a plu, ce qui a moins plu, ce qu'on veut essayer.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le sextoy en couple, c'est un langage nouveau à apprendre à deux. Pas une performance, une exploration. Et souvent, c'est ce qui rouvre des conversations qu'on n'avait pas depuis longtemps.",
        ],
    },
    {
        "slug": "rangement-discret-sextoys-organisation-guide",
        "kicker": "GUIDE PRATIQUE",
        "title": "Ranger ses sextoys discrètement : nos idées",
        "lead": "Tiroir dédié, pochette tissu, boîte fermée : l'organisation qui préserve l'hygiène et la discrétion. Un guide sans tabou.",
        "category": "sensualite", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#5b1a26", "product_cats": ["sensualite"], "max_products": 3,
        "intro": [
            "On parle beaucoup de choisir un sextoy, très peu de savoir où le mettre après usage. Pourtant c'est là que se joue une grande partie de l'hygiène, de la durée de vie du jouet, et du confort au quotidien.",
        ],
        "sections": [
            ("Les règles d'or de la conservation", [
                "**Chaque jouet dans sa pochette individuelle** : évite le contact silicone-silicone (qui, sur le long terme, dégrade les matières).",
                "**Tissu respirant, pas plastique fermé** : le plastique retient l'humidité résiduelle et favorise les bactéries.",
                "**À l'abri du soleil et de la chaleur** : le silicone déteste les températures > 40°C.",
                "**Batterie chargée à 50-70 %** avant rangement long : plus stable pour la cellule.",
            ]),
            ("Où ranger dans la chambre", [
                "**Tiroir de table de nuit à clé** : classique, sûr, à portée.",
                "**Boîte fermée sur étagère haute** : discret, ventilé, hors des mains d'enfants.",
                "**Sac de rangement dédié** dans le placard : idéal si l'on partage la chambre avec enfants.",
                "**Petit coffre-fort** avec code : la solution pour les foyers avec adolescents curieux.",
            ]),
            ("Ce qui ne doit PAS coexister", [
                "**Silicone et silicone** en contact prolongé : à séparer.",
                "**Jouet et batterie de secours** : source de chaleur possible.",
                "**Objets métalliques pointus** dans la même boîte : rayent les surfaces.",
                "**Lingerie humide** : humidité résiduelle défavorable.",
            ]),
            ("Voyage et déplacement", [
                "**Pochette de voyage rigide** avec compartiments : évite tout contact avec les vêtements.",
                "**Retirer la batterie ou verrouiller** : certains jouets ont un mode voyage qui empêche l'allumage accidentel.",
                "**Bagage cabine** plutôt que soute : moins d'écart de température et de manipulations.",
                "**Aucun souci en douane européenne** : c'est un objet parfaitement légal.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Bien ranger ses jouets, c'est en doubler la durée de vie et supprimer 90 % des soucis d'hygiène. Cinq minutes d'organisation, des années de tranquillité.",
        ],
    },

    # ─────────────────────────────────────── EROTISME (4) ───────────────────────────────────────
    {
        "slug": "roman-erotique-femme-selection-guide",
        "kicker": "GUIDE LECTURE",
        "title": "Romans érotiques pour femmes : notre sélection",
        "lead": "Anaïs Nin, Emma Becker, Louise Chennevière : la littérature érotique féminine a ses grands noms. Notre guide pour commencer.",
        "category": "erotisme", "date": "29 juillet 2026", "read": "5 min",
        "cover_color": "#3a1420", "product_cats": ["erotisme"], "max_products": 3,
        "intro": [
            "Le roman érotique féminin n'a pas attendu Fifty Shades. Depuis Anaïs Nin jusqu'aux voix contemporaines, il existe toute une littérature qui parle vraiment du désir, sans détour et sans cliché. Reste à savoir par où commencer.",
        ],
        "sections": [
            ("Les classiques incontournables", [
                "**Anaïs Nin, *Vénus Erotica*** : le point de départ historique, publié dans les années 40. Écriture sensuelle, personnages complexes.",
                "**Pauline Réage, *Histoire d'O*** : dérangeant, marquant, souvent cité. À lire en connaissance de cause.",
                "**Catherine Millet, *La Vie sexuelle de Catherine M.*** : autobiographique, cru, littérairement solide.",
            ]),
            ("Les voix contemporaines", [
                "**Emma Becker, *La Maison*** : immersion romancée dans une maison close berlinoise. Fort littéraire.",
                "**Louise Chennevière, *Comme la chienne*** : voix percutante, très actuelle sur le corps et le désir.",
                "**Belinda Cannone, *L'Écriture du désir*** : essai + fictions, une réflexion en même temps qu'un plaisir de lecture.",
            ]),
            ("Pour débuter en douceur", [
                "**Anthologies** : un condensé d'auteurs différents pour tester ses goûts. Plusieurs sont disponibles.",
                "**Format nouvelles** : plus court, moins engageant que 400 pages. Idéal en soirée.",
                "**Ebook** : discret, immédiat, pas de dos de livre exposé sur l'étagère.",
            ]),
            ("Ce qu'il faut éviter (au début)", [
                "**Les best-sellers marketing** : Fifty Shades et compagnie sont écrits en pilote automatique. Utiles pour comprendre le phénomène, décevants pour la lecture.",
                "**Les auteurs sans notice biographique** : sur Amazon, beaucoup de pseudonymes derrière du contenu généré. Vérifier qui écrit.",
                "**Le trop violent en premier essai** : commencer par sensuel, on va vers plus dur seulement si l'on veut.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un bon roman érotique, c'est celui qu'on garde sur la table de nuit et qu'on relit. Une bibliothèque de trois ou quatre titres bien choisis vaut mieux que dix best-sellers oubliés.",
        ],
    },
    {
        "slug": "livre-audio-erotique-podcast-decouvrir-guide",
        "kicker": "GUIDE LECTURE",
        "title": "Livre audio érotique : la nouvelle façon de lire chaud",
        "lead": "Voix chuchotées, ambiances sonores, immersion complète : le format audio réinvente la littérature érotique. Notre guide pour se lancer.",
        "category": "erotisme", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#3a1420", "product_cats": ["erotisme"], "max_products": 3,
        "intro": [
            "Le livre érotique a longtemps été un objet à cacher — sous l'oreiller ou entre deux couvertures. Le format audio change complètement la donne : casque sur les oreilles, personne ne sait ce qu'on écoute. Et surtout, une voix bien choisie change tout au ressenti.",
        ],
        "sections": [
            ("Pourquoi ça marche mieux à l'oreille", [
                "**La voix engage l'imagination différemment** : moins de contrôle, plus de projection.",
                "**Le rythme est imposé** : ni trop vite ni trop lent, comme si on écoutait raconter.",
                "**On peut faire autre chose** : dans le bain, en marchant, dans le noir avant de dormir.",
                "**Zéro trace physique** : rien sur l'étagère, rien dans la liste de lecture visible.",
            ]),
            ("Où trouver du contenu de qualité", [
                "**Livres audio Audible** : nombreux romans érotiques classiques (Anaïs Nin, Sade, Bataille) lus par des comédiennes professionnelles.",
                "**Podcasts spécialisés** : plusieurs plateformes proposent des fictions érotiques en épisodes.",
                "**Applications dédiées** : quelques apps comme Dipsea, Quinn, Bloom se spécialisent sur le contenu féminin.",
            ]),
            ("Ce qui distingue une bonne écoute", [
                "**Voix bien choisie** : ni trop jeune, ni caricaturale. La sobriété est plus efficace que le forcing.",
                "**Prise de son propre** : chuchoter demande un micro sérieux, sinon on entend les souffles parasites.",
                "**Ambiance discrète** : quelques sons d'ambiance oui, une bande-son envahissante non.",
                "**Durée gérable** : 20-45 min pour un épisode, pas 3 heures d'une traite.",
            ]),
            ("Pour bien commencer", [
                "**Casque plutôt qu'enceinte** : intimité totale, tu peux écouter dans un train.",
                "**Le soir juste avant le coucher** : moment idéal, transition douce vers le sommeil.",
                "**En couple** : à deux, dans le noir, très proche. Effet inattendu.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "L'audio érotique est un des formats les plus intimes qui existent. Une fois qu'on a trouvé sa voix, on n'y retourne plus par accident : c'est un vrai rendez-vous.",
        ],
    },
    {
        "slug": "kamasutra-livre-debutant-poses-guide",
        "kicker": "GUIDE LECTURE",
        "title": "Kamasutra : le guide pour débuter à deux",
        "lead": "Édition abordable, illustrations claires, sélection des positions vraiment praticables : notre guide pour utiliser le Kamasutra sans se ridiculiser.",
        "category": "erotisme", "date": "29 juillet 2026", "read": "5 min",
        "cover_color": "#3a1420", "product_cats": ["erotisme"], "max_products": 3,
        "intro": [
            "Le Kamasutra est cité partout, ouvert rarement. La plupart des gens en connaissent trois positions et pensent que le reste demande une souplesse de gymnaste. C'est faux — les bonnes éditions montrent surtout que la variété se cache dans les détails.",
        ],
        "sections": [
            ("Choisir une bonne édition", [
                "**Édition illustrée moderne** : les dessins clairs valent mieux que les gravures d'époque quasi illisibles.",
                "**Guide contemporain** : préférer un livre qui contextualise, plutôt qu'une traduction sèche.",
                "**Format cartonné** : ça reste ouvert sur la table de nuit, plus pratique.",
                "**À éviter** : les éditions « best-of 100 positions » qui compilent sans hiérarchie.",
            ]),
            ("Comment l'aborder à deux", [
                "**Feuilleter d'abord tranquillement**, ensemble, pas au moment de passer à l'acte.",
                "**Choisir 2-3 positions qui font envie**, pas 20. Le plaisir n'est pas dans l'inventaire.",
                "**Rire des essais** : si ça marche pas, ça marche pas. C'est justement la beauté de tester.",
                "**Ne pas se mettre la pression** : ce n'est pas un manuel, c'est une source d'idées.",
            ]),
            ("Les positions vraiment praticables au début", [
                "**Cuillères** : la plus intime, tendre, faisable même fatigué.",
                "**Assis face à face** : yeux dans les yeux, contrôle partagé, très connectant.",
                "**Cavalière avancée** : elle contrôle le rythme, très bien pour la lenteur.",
                "**Missionnaire relevé** : version améliorée du classique, plus profond, plus proche.",
            ]),
            ("Ce que le Kamasutra apprend au-delà des poses", [
                "**Les préliminaires** ont une section entière — souvent la plus utile.",
                "**Les mots** : parler pendant l'acte fait partie du texte original. Beaucoup l'ignorent.",
                "**Le lieu et l'ambiance** : parfums, lumière, temps qu'on prend. C'est là que le livre est le plus moderne.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le Kamasutra bien utilisé, ce n'est pas 100 positions à checker — c'est une invitation à la lenteur, à la variation, à la parole. Un vrai cadeau pour un couple qui s'installe dans la durée.",
        ],
    },
    {
        "slug": "jeu-questions-intimes-couple-communiquer-guide",
        "kicker": "GUIDE JEU",
        "title": "Jeu de questions intimes : parler vraiment à deux",
        "lead": "Cartes de questions, décks de conversation, boîtes prompt : les jeux qui font parler du couple, du corps et du désir. Notre sélection.",
        "category": "erotisme", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#3a1420", "product_cats": ["erotisme"], "max_products": 3,
        "intro": [
            "On croit se connaître après cinq, dix, quinze ans. Puis on tire une carte, on lit la question, et l'autre répond quelque chose qu'on n'avait jamais entendu. C'est le pouvoir simple des jeux de questions intimes : ouvrir une porte qu'on ne pousserait pas seuls.",
        ],
        "sections": [
            ("Les trois grands types", [
                "**Cartes de questions ouvertes** : « quel est ton souvenir le plus fort de nous ? », « qu'est-ce qui te manque en ce moment ? ». Format le plus profond.",
                "**Défis coquins** : « raconte un fantasme », « fais-moi rire pendant 1 min ». Format le plus léger.",
                "**Rituels du soir** : une carte par jour ou par semaine, pas de logique de partie. Format le plus régulier.",
            ]),
            ("Quand y jouer", [
                "**Après un dîner à deux** : on est détendu, présent, pas fatigué.",
                "**Sur un week-end en amoureux** : rythme lent, temps devant soi, envie de reconnexion.",
                "**Après une dispute résolue** : reprendre le fil, montrer qu'on est toujours ensemble.",
                "**À éviter** : quand l'un des deux est stressé, énervé, ou distant.",
            ]),
            ("Comment bien jouer", [
                "**Pas d'obligation de répondre** : le droit de passer une carte est essentiel, sinon le jeu devient un interrogatoire.",
                "**Prendre le temps** : ne pas enchaîner. Une bonne carte peut durer 30 min de conversation.",
                "**Ne pas juger la réponse** : ce n'est pas un débat, c'est une écoute.",
                "**Alterner** : celui qui pose ne pose pas la suivante. Symétrie totale.",
            ]),
            ("Ce que ces jeux révèlent", [
                "**Des envies non exprimées** : parfois depuis des années, en attente d'une occasion.",
                "**Des zones d'ombre** : ce qu'on n'ose pas dire, ce qu'on croyait tabou.",
                "**Des souvenirs oubliés** : moments partagés qu'on avait rangés au fond.",
                "**Souvent une envie de se rapprocher** juste après : c'est le but à peine caché.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un bon jeu de questions n'est pas une soirée — c'est un outil du couple. Un jeu de cartes rangé dans un tiroir, à ressortir tous les deux mois, c'est le meilleur investissement de communication qu'on puisse faire à deux.",
        ],
    },

    # ─────────────────────────────────────── SOINS (6) ───────────────────────────────────────
    {
        "slug": "lubrifiant-grossesse-enceinte-securite-guide",
        "kicker": "GUIDE SOIN",
        "title": "Lubrifiant pendant la grossesse : ce qui est sûr",
        "lead": "Base aqueuse, composition claire, pH adapté : le lubrifiant se choisit avec attention pendant la grossesse. Nos repères.",
        "category": "soins", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#2a3a2a", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "La grossesse bouscule le confort intime — plus de sensibilité, plus ou moins d'humidité selon les moments. Le bon lubrifiant est un allié utile, mais tous ne conviennent pas dans cette période particulière.",
        ],
        "sections": [
            ("Ce que le lubrifiant doit être pendant la grossesse", [
                "**Base aqueuse (pas silicone)** : moins de composés à absorber, rinçage plus simple.",
                "**pH proche du pH vaginal (3,8-4,5)** : préserve la flore, particulièrement fragile pendant la grossesse.",
                "**Sans parfum, sans colorant** : moins de risque d'irritation. La peau devient plus réactive.",
                "**Sans glycérine ni glycols** : ces sucres peuvent favoriser des mycoses, plus fréquentes enceinte.",
            ]),
            ("Ce qu'il faut éviter", [
                "**Lubrifiants chauffants ou effet froid** : mentholés et capsaïcines sont trop actifs sur une muqueuse hypersensibilisée.",
                "**Silicone** : globalement sûr en soi, mais plus difficile à rincer, ce qui n'est pas idéal quand la flore change.",
                "**Huiles végétales pures dans le vagin** : elles déséquilibrent la flore et peuvent stagner.",
                "**Produits sans notice française** : origine douteuse, contrôle nul.",
            ]),
            ("À quoi ça sert vraiment", [
                "**Compenser une sécheresse temporaire** : certaines femmes en ont sur des périodes de la grossesse.",
                "**Réduire les frictions** : la peau des muqueuses est plus sensible, une goutte peut tout changer.",
                "**Retrouver du confort après l'accouchement** : dans les mois qui suivent, très utile.",
            ]),
            ("Le point essentiel", [
                "**En cas de doute, demander à sa sage-femme** ou à son médecin. Ils connaissent les marques recommandées.",
                "**Éviter les partages** : ne pas emprunter le lubrifiant du couple d'ami, prendre son propre tube.",
                "**Attention aux dates** : un tube ouvert perd ses garanties après 6 mois.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un bon lubrifiant de grossesse, c'est simple : composition courte, pH physiologique, marque connue. Une petite attention qui change beaucoup pendant les 9 mois et les mois qui suivent.",
        ],
    },
    {
        "slug": "lubrifiant-menopause-secheresse-apaiser-guide",
        "kicker": "GUIDE SOIN",
        "title": "Lubrifiant ménopause : apaiser la sécheresse intime",
        "lead": "Formule enrichie en acide hyaluronique, tolérance parfaite, action longue : les critères qui font vraiment la différence après 50 ans.",
        "category": "soins", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#2a3a2a", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "La ménopause modifie durablement l'hydratation naturelle — baisse d'œstrogènes, muqueuses qui s'amincissent, sécheresse installée. Le lubrifiant devient un compagnon quotidien, plus qu'un accessoire. Encore faut-il choisir un modèle vraiment adapté.",
        ],
        "sections": [
            ("Deux types différents à connaître", [
                "**Lubrifiant classique** : action pendant l'usage. À reprendre à chaque fois.",
                "**Gel hydratant intime** : action prolongée (24 à 72 h). Se met en cure de fond, indépendamment de tout usage.",
                "L'idéal : combiner les deux. Un gel hydratant en fond, un lubrifiant en complément selon les moments.",
            ]),
            ("Les ingrédients qui aident vraiment", [
                "**Acide hyaluronique** : effet réparateur des muqueuses, hydratation en profondeur.",
                "**Aloe vera** : apaisant, tolérance excellente.",
                "**Prébiotiques** : soutiennent la flore, souvent affaiblie à cette période.",
                "**pH bas (3,5-4,5)** : correspond au pH vaginal physiologique.",
            ]),
            ("Ce qu'il faut absolument éviter", [
                "**Parfums synthétiques** : premier facteur d'irritation.",
                "**Glycols et glycérine forte concentration** : sucres qui déséquilibrent la flore.",
                "**Silicone en action réparatrice** : glisse mais ne traite pas.",
                "**Produits « chauffants »** : trop agressifs pour une muqueuse fragilisée.",
            ]),
            ("Faut-il en parler au médecin ?", [
                "Oui, particulièrement au premier signe : la sécheresse s'installe et se traite mieux tôt.",
                "**Certains traitements locaux** (crèmes hormonales, ovules d'acide hyaluronique) complètent le lubrifiant sur prescription.",
                "**Aucun tabou en consultation** : les gynécos entendent ça toutes les semaines. Poser la question ouvertement.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "La ménopause n'est pas la fin de la vie intime — c'est une nouvelle façon d'en prendre soin. Le bon lubrifiant, régulier, transforme complètement le confort quotidien.",
        ],
    },
    {
        "slug": "lubrifiant-preservatif-compatible-choisir-guide",
        "kicker": "GUIDE SOIN",
        "title": "Lubrifiant compatible préservatif : les bons choix",
        "lead": "Base aqueuse ou silicone : tous ne conviennent pas au latex ou au polyisoprène. Notre guide pour choisir sans risque.",
        "category": "soins", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#2a3a2a", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "Le préservatif reste la meilleure protection combinée contre les IST et les grossesses non prévues. Mais un lubrifiant mal choisi peut le fragiliser sans qu'on s'en rende compte — et annuler toute la protection.",
        ],
        "sections": [
            ("Ce qui est compatible", [
                "**Lubrifiant à base d'eau** : compatible avec tous les préservatifs (latex, polyisoprène, polyuréthane). C'est le choix par défaut.",
                "**Lubrifiant à base de silicone** : compatible avec le latex et le polyisoprène. À vérifier pour le polyuréthane (rare, mais possible).",
                "**Lubrifiant hybride (eau + silicone)** : compatible avec le latex et le polyisoprène.",
            ]),
            ("Ce qui est INCOMPATIBLE avec le latex", [
                "**Huile végétale** (coco, olive, amande, jojoba) : fragilise le latex en 60 secondes.",
                "**Vaseline** : idem, dégrade rapidement.",
                "**Crème hydratante corporelle** : contient des huiles, à ne pas utiliser en dépannage.",
                "**Beurre de karité** : même problème.",
                "**Baume à lèvres** : plus fréquent qu'on ne le pense, à éviter aussi.",
            ]),
            ("Pour le sextoy en même temps", [
                "**Silicone sur silicone** : le silicone lubrifiant dégrade le silicone du jouet. Utiliser un lubrifiant aqueux.",
                "**Aqueux universel** : safe partout, avec préservatif comme avec jouet.",
                "**Marquage clair** : les bons fabricants notent explicitement la compatibilité sur l'emballage.",
            ]),
            ("Le bon réflexe au quotidien", [
                "**Vérifier « compatible préservatif » sur l'étiquette** : mention obligatoire si c'est le cas.",
                "**Refuser les produits sans notice française** : origine non contrôlée.",
                "**Un tube d'eau + un tube silicone** : les deux à la maison couvrent 100 % des cas.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le préservatif ne protège que s'il tient. Le bon lubrifiant est autant question de plaisir que de sécurité — et l'eau reste la base la plus sûre en cas de doute.",
        ],
    },
    {
        "slug": "huile-perinee-grossesse-preparer-accouchement",
        "kicker": "GUIDE SOIN",
        "title": "Huile pour le périnée : préparer son accouchement",
        "lead": "Huile d'amande douce, huile de calendula, formules spécifiques : le massage périnéal préparerait le passage de bébé. Notre guide.",
        "category": "soins", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#2a3a2a", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "Le massage du périnée en fin de grossesse est recommandé par de nombreuses sages-femmes pour assouplir les tissus et diminuer le risque de déchirure ou d'épisiotomie. Encore faut-il utiliser la bonne huile et la bonne méthode.",
        ],
        "sections": [
            ("Les huiles recommandées", [
                "**Huile d'amande douce** : la plus classique, bien tolérée, douce.",
                "**Huile de calendula** : apaisante, réparatrice, adaptée aux peaux sensibles.",
                "**Huile de germe de blé** : riche en vitamine E, anti-oxydante.",
                "**Huiles spécifiques « périnée »** : formulées avec calendula, camomille, souvent sans huiles essentielles.",
            ]),
            ("Ce qu'il faut éviter", [
                "**Huiles essentielles** pendant la grossesse : la plupart sont contre-indiquées, y compris en dilution locale.",
                "**Huile minérale (baby oil)** : pas absorbée par la peau, purement filmogène.",
                "**Huiles parfumées** : rique d'irritation d'une zone fragile.",
                "**Composition sans mention « bio »** : les traces de pesticides passent la peau.",
            ]),
            ("Quand commencer", [
                "**À partir de 34-36 semaines** : la période où le massage a le plus d'intérêt, selon la littérature scientifique.",
                "**Deux à trois fois par semaine**, pas plus — inutile de forcer.",
                "**5 à 10 minutes maximum** : c'est suffisant pour le résultat, plus fatigue les tissus.",
                "**Toujours en accord avec la sage-femme** : elle valide la méthode et le timing.",
            ]),
            ("La bonne technique en résumé", [
                "**Position confortable** : semi-assise ou debout jambe surélevée.",
                "**Pouces avec un peu d'huile** : pressions douces vers le bas et les côtés.",
                "**Aucune douleur** : si ça pince, réduire l'intensité.",
                "**Après la douche** : la peau est plus souple, le rituel plus agréable.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le massage du périnée n'est pas une garantie d'accouchement sans déchirure — mais c'est un des rares gestes actifs qu'on peut faire soi-même en fin de grossesse. À valider avec sa sage-femme, à intégrer avec douceur.",
        ],
    },
    {
        "slug": "bougie-parfumee-chambre-ambiance-couple-guide",
        "kicker": "GUIDE AMBIANCE",
        "title": "Bougie parfumée pour la chambre : ambiance couple",
        "lead": "Notes boisées, fleurs blanches, ambrées : la bonne bougie transforme une chambre en refuge. Notre guide des ambiances à deux.",
        "category": "soins", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#2a3a2a", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "La chambre a beaucoup à gagner d'une bougie bien choisie — plus qu'un simple objet déco, elle transforme l'atmosphère en trois minutes. Encore faut-il savoir choisir : toutes les bougies parfumées ne se valent pas, loin s'en faut.",
        ],
        "sections": [
            ("Les grandes familles olfactives", [
                "**Boisées** (cèdre, santal, oud) : ambiance chaude, envelopante, plutôt soir et hiver.",
                "**Fleurs blanches** (jasmin, tubéreuse, ylang-ylang) : sensualité assumée, un peu capiteuse. Idéale en soirée.",
                "**Ambrées** (ambre, vanille, benjoin) : douces et rassurantes, parfaites en cocooning.",
                "**Gourmandes** (chocolat, praliné, café) : ludiques, chaleureuses. À doser sinon écœurant.",
                "**Fraîches** (menthe, eucalyptus, agrumes) : plutôt matin ou pièce de vie, pas idéal en chambre.",
            ]),
            ("Ce qui distingue une bonne bougie", [
                "**Cire végétale** (soja, colza) plutôt que paraffine : combustion plus propre, pas de résidu noir.",
                "**Mèche coton** (pas plomb) : moins de fumée, meilleure diffusion.",
                "**Concentration de parfum ≥ 8 %** : en dessous, on ne sent rien à 3 mètres.",
                "**Durée de combustion 30-50 h** : correspond à un vrai budget, pas un gadget.",
            ]),
            ("Bien la brûler", [
                "**Première fois** : laisser fondre jusqu'aux bords (2-3 h). Sinon, un tunnel de cire se forme et le parfum diminue.",
                "**Ne jamais dépasser 4 h** : la cire chauffe, le parfum s'altère.",
                "**Couper la mèche à 5 mm** avant chaque allumage.",
                "**Éteindre avec un couvercle** ou un souffle sec : moins de fumée.",
            ]),
            ("Pour un moment à deux", [
                "**Allumer 20 min avant** : le parfum a besoin de temps pour se diffuser.",
                "**Une seule bougie** dans la pièce : ça suffit largement à parfumer 15 m².",
                "**Éclairage tamisé** : baisser les lumières, la bougie prend le relais.",
                "**Poser sur une surface stable** : loin des rideaux, jamais sur un livre.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Une bonne bougie de chambre coûte 20-40 €. Elle dure 30 heures. Ramené à l'ambiance qu'elle crée, c'est un des plus petits budgets à haut impact du couple.",
        ],
    },
    {
        "slug": "bain-moussant-couple-rituel-detente-guide",
        "kicker": "GUIDE RITUEL",
        "title": "Bain moussant à deux : le rituel détente du soir",
        "lead": "Mousse abondante, huiles apaisantes, ambiance chaleureuse : le bain à deux se prépare comme un moment. Nos conseils pour le réussir.",
        "category": "soins", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#2a3a2a", "product_cats": ["soins"], "max_products": 3,
        "intro": [
            "Un bain à deux, c'est un moment de mise en pause du monde. Ce n'est pas nécessairement un préliminaire — parfois c'est juste 45 minutes où l'on ne fait rien d'autre qu'être là, ensemble, dans l'eau chaude. Un des rituels les plus simples et les plus sous-utilisés du couple.",
        ],
        "sections": [
            ("Bien préparer le bain", [
                "**Eau à 37-38°C** : ni trop chaud (assèche la peau), ni trop tiède (perd son effet détente).",
                "**Remplir aux 3/4** : quand on est deux dedans, le niveau monte.",
                "**Ajouter le bain moussant** sous le jet, pas dans l'eau immobile : la mousse se forme mieux.",
                "**Prévoir 20 min** de trempage minimum pour que le corps se détende vraiment.",
            ]),
            ("Choisir le bon bain moussant", [
                "**Mousse dense** : la magie du bain à deux, c'est aussi la mousse qui couvre. Chercher les formules « mousse abondante ».",
                "**Sans savon détergent** : le SLS assèche la peau. Préférer les formules « douces » ou « bio ».",
                "**Parfum sobre** : évitez les parfums entêtants, qu'on subit après 30 min dans l'eau chaude.",
                "**Huiles ajoutées** : macadamia, amande douce, karité — la peau ressort nourrie.",
            ]),
            ("Créer l'ambiance", [
                "**Bougie parfumée** à côté du bain (pas dedans, pour la sécurité).",
                "**Éclairage tamisé** : lampe de sel, guirlande, ou juste la bougie.",
                "**Musique douce** : playlist calme depuis une enceinte à distance de l'eau.",
                "**Verres à portée** : eau, tisane ou vin. Pas trop d'alcool avec le chaud.",
            ]),
            ("Après le bain", [
                "**Ne pas se précipiter** : sortir doucement, la circulation a besoin de temps.",
                "**Peignoirs chauds prêts** : effet luxe immédiat.",
                "**Hydratation post-bain** : la peau a été détrempée, une huile ou une crème corps parfait le rituel.",
                "**Rester à deux** : le bain n'est pas un dîner solo, on continue le moment après.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Un bain à deux bien préparé, c'est 45 minutes qui valent une soirée entière ailleurs. Un rituel à réserver un vendredi ou un dimanche soir, et à ne pas expédier — sinon autant se doucher chacun de son côté.",
        ],
    },

    # ─────────────────────────────────────── CADEAUX (5) ───────────────────────────────────────
    {
        "slug": "idee-cadeau-femme-30-ans-elegance-guide",
        "kicker": "IDÉES CADEAU",
        "title": "Idée cadeau femme 30 ans : l'élégance intemporelle",
        "lead": "Lingerie raffinée, coffret cocooning, expérience à vivre : nos idées pour un cadeau qui marque le cap des 30 ans.",
        "category": "cadeaux", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#5a3a1a", "product_cats": ["cadeaux"], "max_products": 3,
        "intro": [
            "À 30 ans, on a compris qu'on préfère peu de belles choses à beaucoup d'objets. Le cadeau qui marque n'est pas nécessairement le plus cher — c'est celui qui montre qu'on a écouté, observé, choisi vraiment.",
        ],
        "sections": [
            ("Trois grandes pistes", [
                "**Cocooning de qualité** : peignoir en bambou, chaussons doux, bougie parfumée haut de gamme. L'univers du chez-soi soigné.",
                "**Lingerie choisie** : ensemble en dentelle ou nuisette satin. Le luxe accessible, à condition de bien connaître la taille.",
                "**Expérience à vivre** : coffret spa duo, week-end, journée en institut. Ne rentre pas dans un placard, marque durablement.",
            ]),
            ("Éviter les fausses bonnes idées", [
                "**Gadget « fun » à 20 €** : à 30 ans, on n'a plus besoin de ça. Investir dans une seule belle pièce vaut mieux.",
                "**Bouquet de fleurs seul** : joli mais ne dure pas et ne dit pas grand-chose de la personne.",
                "**Le fameux chèque cadeau** : dernier recours, jamais premier choix.",
                "**Objet déco « tendance »** : trop personnel, souvent à côté de la plaque.",
            ]),
            ("Ce qui fonctionne toujours", [
                "**Un objet qui devient rituel** : mug préféré, bougie qui s'allume tous les soirs, peignoir qu'on met chaque matin.",
                "**Une pièce d'apparat** : quelque chose qui sort pour les occasions, pas au quotidien. Nuisette satin, robe de chambre en soie, coffret parfum.",
                "**Un mot manuscrit** avec le cadeau, même court. Ça vaut la moitié du cadeau, souvent plus.",
            ]),
            ("Budget conseillé", [
                "**Petit budget (< 30 €)** : bougie premium, livre pertinent, tisane bio.",
                "**Moyen budget (30-80 €)** : peignoir bambou, coffret duo massage, ensemble lingerie basique.",
                "**Grand budget (80-200 €)** : nuisette en soie, coffret spa, coffret cadeau expérience.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le cadeau de 30 ans qui touche, c'est celui qui dit « je te connais ». Prendre 15 minutes pour observer avant d'acheter change tout — plus que d'y mettre 50 € de plus.",
        ],
    },
    {
        "slug": "idee-cadeau-femme-40-ans-raffinement-guide",
        "kicker": "IDÉES CADEAU",
        "title": "Idée cadeau femme 40 ans : raffinement et douceur",
        "lead": "Coffret bien-être haut de gamme, lingerie fine, moment à vivre : nos idées pour marquer le cap des 40 ans avec justesse.",
        "category": "cadeaux", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#5a3a1a", "product_cats": ["cadeaux"], "max_products": 3,
        "intro": [
            "À 40 ans, on sait exactement ce qu'on aime. Le cadeau qui marque n'est plus une surprise gadget — c'est une confirmation, une reconnaissance de ce qu'elle est devenue. Justesse plutôt que spectacle.",
        ],
        "sections": [
            ("Ce qui fonctionne vraiment", [
                "**Coffret cocooning premium** : peignoir en soie, chaussons haut de gamme, bougie de maison. L'univers du refuge chez soi.",
                "**Lingerie de qualité** : pas nécessairement coquine, souvent plus fine et plus élégante que 10 ans plus tôt. Nuisette longue, ensemble en dentelle sobre.",
                "**Expérience haut de gamme** : massage duo, week-end thalasso, dîner étoilé. À vivre ensemble ou seule selon.",
                "**Bijou discret et intemporel** : boucles d'oreilles, bracelet fin. Rien de tape-à-l'œil.",
            ]),
            ("Éviter les faux pas", [
                "**Cadeau « anti-âge »** : crème rides, machine à massage visage, tout ce qui suggère l'usure. Cadeau piège.",
                "**Blague sur l'âge** : mug « 40 ans et alors », etc. À 40 ans, ce type de gag ne fait plus rire.",
                "**Trop dans le fun ado** : la personne a évolué, respecter cette évolution.",
                "**Le cadeau utile** (aspirateur, appareil ménager) : sauf demande explicite, à éviter.",
            ]),
            ("Ce qui touche vraiment", [
                "**Un objet transmissible** : quelque chose qui restera dans 10 ans, pas dans le tiroir.",
                "**Un rituel installé** : l'abonnement box bien choisie, la bougie qu'on rachète chaque année.",
                "**Un moment sans les enfants** (si elle en a) : c'est souvent le luxe ultime à 40 ans.",
            ]),
            ("Budget conseillé", [
                "**Petit budget (< 50 €)** : bougie de grande maison, livre choisi, coffret dégustation.",
                "**Moyen budget (50-150 €)** : peignoir en soie, coffret spa duo, ensemble lingerie fine.",
                "**Grand budget (150 € et +)** : bijou, expérience à vivre, coffret cadeau exceptionnel.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le cadeau des 40 ans se joue sur la justesse : ni gadget, ni cliché, ni utilitaire. Quelque chose qui dit « je vois qui tu es ». Souvent, c'est plus simple qu'on ne le pense.",
        ],
    },
    {
        "slug": "cadeau-mariage-couple-original-idees-guide",
        "kicker": "IDÉES CADEAU",
        "title": "Cadeau mariage couple : nos idées qui touchent",
        "lead": "Peignoirs assortis, coffret nuit de noces, expérience duo : nos idées pour offrir autrement qu'un service en porcelaine.",
        "category": "cadeaux", "date": "29 juillet 2026", "read": "5 min",
        "cover_color": "#5a3a1a", "product_cats": ["cadeaux"], "max_products": 3,
        "intro": [
            "La liste de mariage a ses limites : le grille-pain de la belle-sœur, le vase déjà offert deux fois. À côté, il y a le cadeau qu'on choisit soi, qui sort du lot et qui célèbre le couple, pas juste l'installation.",
        ],
        "sections": [
            ("Trois univers à explorer", [
                "**Cocooning à deux** : peignoirs assortis, plaid en cachemire, service à petit-déjeuner. Le message : prenez soin de vous ensemble.",
                "**Nuit de noces** : coffret lingerie + bougie + huile de massage. À offrir emballé finement, sans blague lourde.",
                "**Expérience à vivre** : week-end, dîner d'exception, séjour spa. Le cadeau qu'ils garderont en mémoire, contrairement au dessous-de-plat.",
            ]),
            ("Ce qui fait la différence", [
                "**Personnalisation légère** : initiales brodées, prénoms, date. À condition que ce soit discret, sinon effet kitsch.",
                "**Emballage soigné** : le mariage est une fête. Un simple sac Amazon décrédibilise le cadeau, même bon.",
                "**Un mot manuscrit** : deux phrases sincères valent mieux qu'un cadeau plus cher.",
                "**Sortir de la liste** : montrer qu'on a réfléchi, pas juste coché.",
            ]),
            ("Les fausses bonnes idées", [
                "**Argent en enveloppe** : accepté mais impersonnel. À réserver aux relations où l'on ne sait vraiment quoi choisir.",
                "**Cadre photo vide** : sans photo, sans intérêt. Attendre après le mariage et offrir avec la photo à l'intérieur.",
                "**Objet décoratif marqué « mariés »** : les couples n'en veulent souvent pas. Cadeau qui finit au fond du placard.",
                "**Cadeau coquin trop appuyé** : sauf si l'on est très proche, ça peut gêner.",
            ]),
            ("Budget conseillé selon la proximité", [
                "**Ami éloigné / collègue (30-60 €)** : coffret cocooning, bougie de maison, livre relié.",
                "**Ami proche (60-150 €)** : peignoirs assortis, coffret spa, expérience à deux.",
                "**Famille proche (150 € et +)** : bijou, week-end, contribution à un projet du couple (voyage, achat).",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le cadeau de mariage qui marque, c'est celui qui parle au couple et pas juste au foyer. Prendre le temps de sortir de la liste, c'est reconnaître que ce jour n'est pas comme les autres — et que les mariés non plus.",
        ],
    },
    {
        "slug": "cadeau-cremaillere-couple-emmenager-idees",
        "kicker": "IDÉES CADEAU",
        "title": "Cadeau crémaillère couple : marquer le nouveau chez-eux",
        "lead": "Bougie signature, plaid douillet, coffret dégustation : nos idées pour dire « bienvenue chez vous » sans tomber dans le cliché.",
        "category": "cadeaux", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#5a3a1a", "product_cats": ["cadeaux"], "max_products": 3,
        "intro": [
            "Un couple qui emménage a besoin de tout — donc l'astuce n'est pas de deviner ce qui manque, mais d'offrir quelque chose qu'on ne mettrait pas soi-même sur une liste. Un cadeau qui devient rituel, pas une case à cocher.",
        ],
        "sections": [
            ("Ce qui fait rituel", [
                "**Bougie parfumée de belle marque** : elle allume à chaque soirée, elle rappelle qui l'a offerte.",
                "**Plaid ou couverture en laine** : investit le canapé, hiver après hiver.",
                "**Service à thé ou à café** : le rituel matin du couple, très porteur.",
                "**Peignoirs assortis** : le luxe du bain à deux dans la nouvelle salle de bain.",
            ]),
            ("Idées originales qu'on n'y pense pas", [
                "**Coffret dégustation huile d'olive** : trois ou quatre huiles de terroir, à utiliser en cuisine.",
                "**Coffret vinaigre balsamique + saveurs** : durable, gourmand.",
                "**Kit à cocktails** : shaker, verres, sirops de qualité. Nouveau chez-soi = nouveaux apéros.",
                "**Coffret plantes vertes** : durables, décoratives, symboliques (le lieu prend vie).",
            ]),
            ("Ce qu'il faut éviter", [
                "**Objet déco très marqué** : goût personnel très risqué. On ne connaît pas encore leur univers dans le nouveau lieu.",
                "**Article encombrant** : sauf demande, ne pas ajouter des choses à ranger.",
                "**Truc utilitaire pur** (aspirateur, machine à café) : sauf s'ils l'ont demandé.",
                "**Le fameux tableau ou poster** : goût très subjectif, à éviter sans consultation.",
            ]),
            ("Le combo qui marche à tous les coups", [
                "**Une bonne bougie + une bouteille de champagne + un mot manuscrit** : ambiance, célébration, personnalisation. Budget maîtrisé, impact fort.",
                "**Peignoirs assortis + coffret cocooning** : ambiance intime, cadeau riche mais pas cher.",
                "**Coffret dîner à la maison** : jolis produits, cadeau qui se consomme le premier soir dans le nouveau chez-soi.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Le cadeau de crémaillère qui plaît, c'est celui qu'ils vont utiliser dans les 15 jours et pas remiser au fond d'un carton. Pense « rituel qui commence », pas « objet à ranger ».",
        ],
    },
    {
        "slug": "cadeau-anniversaire-mariage-10-ans-etain-idees",
        "kicker": "IDÉES CADEAU",
        "title": "Anniversaire de mariage 10 ans : les noces d'étain",
        "lead": "Objet en étain traditionnel ou clin d'œil moderne : nos idées pour marquer la décennie de couple avec goût.",
        "category": "cadeaux", "date": "29 juillet 2026", "read": "4 min",
        "cover_color": "#5a3a1a", "product_cats": ["cadeaux"], "max_products": 3,
        "intro": [
            "Dix ans de mariage, c'est un vrai cap. Assez pour connaître l'autre, assez pour avoir traversé des choses, assez pour se demander ce qu'on célèbre exactement. Les noces d'étain se prêtent à un cadeau qui marque, pas forcément à un objet en étain.",
        ],
        "sections": [
            ("Ce que dit la tradition", [
                "**Noces d'étain** : symbolisent la solidité qui s'installe, la matière qui dure sans devenir précieuse. On construit, on assouplit.",
                "**Objet traditionnel** : chope, cadre, boîte en étain. Beau mais parfois désuet.",
                "**Clin d'œil moderne** : accepté, encouragé. On peut jouer avec la symbolique sans se limiter au métal.",
            ]),
            ("Cadeaux qui célèbrent le couple", [
                "**Peignoirs assortis en belle matière** : le confort à deux qui dure, très dans l'esprit décennie.",
                "**Coffret lingerie / nuisette** : redynamiser le lien intime, avec goût.",
                "**Voyage à deux** : le cadeau qui vaut plus que dix objets. Week-end à l'endroit du voyage de noces si c'est symbolique.",
                "**Coffret spa duo** : moment volé au quotidien, hors du foyer.",
                "**Coffret dégustation** (vins, champagne) : à ouvrir ensemble, souvenir tactile.",
            ]),
            ("Clin d'œil à l'étain qui fonctionne", [
                "**Boîte en étain gravée** avec la date : pour ranger des souvenirs, discret et durable.",
                "**Photophore en étain** pour bougie : rejoint l'univers cocooning.",
                "**Petit objet symbolique** en étain, glissé dans un cadeau principal.",
                "**À éviter** : la chope pour couple qui ne boit pas de bière, l'objet massif « seniors ».",
            ]),
            ("Le geste qui compte plus que l'objet", [
                "**Reproduire un moment fondateur** : dîner au restaurant du premier rendez-vous, à défaut du même style.",
                "**Album souvenir** de la décennie : photos, mots, petits objets. Cadeau qui se prépare des semaines à l'avance.",
                "**Vidéo souvenir** : montage de moments filmés au fil des ans, à visionner ensemble.",
                "**Une lettre écrite** : rare, précieuse, gardée à vie. Sans doute le cadeau le plus fort.",
            ]),
        ],
        "outro": [
            DISCLAIMER_PRIME,
            "Dix ans, ce n'est pas un anniversaire ordinaire — c'est une déclaration silencieuse. Le bon cadeau ne se joue pas sur le budget, il se joue sur l'attention. Un mot vrai vaut plus qu'un objet en étain.",
        ],
    },
]


if __name__ == "__main__":
    main()
