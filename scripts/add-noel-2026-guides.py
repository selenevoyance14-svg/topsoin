"""Ajoute trois guides pratiques de Noël ; conserve les autres articles du journal."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = [
    {
        "slug": "cadeau-couple-noel-sans-taille-ni-parfum",
        "title": "Cadeau de Noël pour un couple : choisir sans connaître les tailles ni les parfums",
        "description": "Trois pistes pour offrir une attention à deux sans deviner une taille de lingerie ou un parfum : activité, textile de maison et coffret à composer.",
        "image": "cadeau-couple",
        "sections": [
            ("Partir d’un moment que les deux personnes apprécient", "Demandez-vous ce que le couple fait volontiers ensemble : préparer un repas, recevoir des amis, lire au calme ou découvrir une activité. Cette information est plus utile qu’un cadeau uniquement choisi pour son emballage. Si vous connaissez surtout l’un des deux, cherchez une idée qui laisse une place à l’autre plutôt que de supposer des goûts identiques."),
            ("Choisir une attention qui ne demande pas de taille", "Un carnet à remplir à deux, un jeu de conversation ou un accessoire pour une soirée à la maison évitent de choisir une taille de vêtement. Pour un textile de maison, vérifiez tout de même les dimensions et l’entretien. Un plaid pour une personne et un grand modèle à partager n’ont pas le même usage. Regardez aussi la place disponible et les couleurs déjà présentes chez eux."),
            ("Préférer une composition simple à un parfum choisi au hasard", "Si vous ne connaissez pas leurs préférences, vous pouvez composer un petit ensemble autour d’un moment : une carte personnelle, un accessoire utile et une activité proposée. Les bougies parfumées et les soins demandent davantage d’informations sur leurs goûts. Il est possible de laisser ce choix aux destinataires avec une carte cadeau d’une enseigne qu’ils fréquentent, après vérification de ses conditions."),
            ("Préparer un cadeau qui peut vraiment être utilisé", "Pour une expérience, consultez les lieux proposés, les créneaux et les modalités de réservation avant d’acheter. Pour un objet, vérifiez le vendeur, la variante et les frais au moment de la commande. Ajoutez un mot qui explique votre choix. Un cadeau commun n’a pas besoin d’être coûteux pour montrer que vous avez pensé aux deux personnes."),
        ],
        "related": ["coffret-spa-duo-verifier-prestation-reservation", "coffret-soins-ou-selection-personnalisee"],
    },
    {
        "slug": "coffret-noel-comparer-contenances-budget",
        "title": "Coffret de Noël : comparer le contenu réel et le budget",
        "description": "Miniatures, accessoires, volumes et frais : une méthode concrète pour comparer un coffret de Noël avec une sélection de produits séparés.",
        "image": "soins-massage",
        "sections": [
            ("Lister ce que la personne utilisera vraiment", "Recopiez le contenu du coffret en distinguant les produits, leurs formats et les accessoires. Un grand nombre d’éléments ne veut pas dire que tout sera utilisé. Si seuls deux produits correspondent aux habitudes de la personne, comparez aussi leur achat séparé. Un petit coffret cohérent peut avoir plus de sens qu’une grande boîte remplie de formats qui resteront au placard."),
            ("Distinguer miniature, format habituel et accessoire", "Le visuel du coffret ne permet pas toujours de juger la taille des flacons. Relevez les contenances indiquées sur la fiche et regardez si les produits sont vendus dans les mêmes versions à l’unité. Une miniature sert à découvrir ou à emporter ; un format plus grand peut convenir à un produit déjà apprécié. Évitez de comparer uniquement le nombre de pièces."),
            ("Faire une comparaison chiffrée qui a du sens", "Pour un même produit, divisez son prix par sa contenance, puis multipliez par 100 pour obtenir un repère au 100 ml. Exemple fictif : un tube de 30 ml à 6 € revient à 20 € au 100 ml ; un tube de 75 ml à 12 € revient à 16 € au 100 ml. Cela ne suffit pas à choisir : le grand tube n’est intéressant que si son usage convient. N’additionnez pas comme équivalents les volumes de produits différents."),
            ("Compter aussi la présentation et les frais", "Comparez le coût final du coffret avec celui des produits séparés, des frais éventuels et d’un emballage simple. Un prix barré n’explique pas à lui seul la valeur du contenu. Au moment de commander, vérifiez la variante, le vendeur et les conditions proposées. Gardez la référence exacte pour que le destinataire puisse retrouver un produit apprécié."),
        ],
        "related": ["coffret-bien-etre-femme-comment-comparer", "creme-mains-sac-ou-grand-format"],
    },
    {
        "slug": "pyjama-cadeau-noel-verifications-avant-achat",
        "title": "Offrir un pyjama à Noël : cinq vérifications avant de choisir",
        "description": "Coupe, guide des tailles, composition, entretien et présentation : préparez un cadeau de nuit adapté aux habitudes de la personne.",
        "image": "nuit-cocooning",
        "sections": [
            ("Observer le vêtement qu’elle aime déjà porter", "Chemise de nuit, ensemble long ou caraco avec short : partez d’une coupe déjà appréciée. Pensez à la température de son logement et à la façon dont elle utilise ses vêtements de nuit. Un modèle très habillé peut plaire pour son style sans être celui qu’elle portera chaque soir. L’idée est de lui offrir un usage qui lui ressemble."),
            ("Utiliser le guide de tailles de la référence", "Une lettre S, M ou L ne suffit pas à comparer deux marques. Consultez le tableau de la référence et, si possible, les mesures d’un vêtement similaire apprécié. Regardez la longueur du pantalon, les manches et l’aisance annoncée. Si vous ne pouvez pas vérifier ces points discrètement, demandez une préférence ou choisissez une autre catégorie de cadeau."),
            ("Lire la composition et l’entretien ensemble", "La description du toucher ne remplace pas l’étiquette de composition. Notez les fibres annoncées et vérifiez les consignes d’entretien : lavage, séchage et éventuel repassage. Un vêtement délicat ne correspond pas forcément à une personne qui préfère tout laver ensemble. Le satin décrit un type de tissage et ne suffit pas à identifier la fibre ; notre guide satin ou soie développe cette distinction."),
            ("Vérifier la variante et préparer une présentation simple", "Avant de commander, contrôlez la taille, la couleur et ce que contient réellement l’ensemble photographié. Consultez les conditions d’échange de l’article choisi, sans supposer qu’elles seront identiques chez tous les vendeurs. Gardez l’étiquette et un justificatif adapté au cadeau. Une carte expliquant pourquoi vous avez pensé à ce modèle suffit à personnaliser l’attention."),
        ],
        "related": ["pyjama-satin-soie-difference-entretien", "matiere-pyjama-modal-bambou-coton-comparatif"],
    },
]

cards = []
for guide in GUIDES:
    esc = html.escape
    slug, title, description = guide["slug"], guide["title"], guide["description"]
    url = f"https://guide-soin.fr/journal/{slug}.html"
    image = f'/assets/journal/{guide["image"]}.webp'
    schema = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": title, "description": description, "datePublished": "2026-11-20", "dateModified": "2026-11-20", "mainEntityOfPage": url, "image": "https://guide-soin.fr"+image, "author": {"@type": "Organization", "name": "Maison Léa", "url": "https://guide-soin.fr/"}}, ensure_ascii=False)
    toc = ''.join(f'<li><a href="#conseil-{i}">{esc(heading)}</a></li>' for i, (heading, _) in enumerate(guide["sections"]))
    sections = ''.join(f'<section id="conseil-{i}"><h2>{esc(heading)}</h2><p>{esc(body)}</p></section>' for i, (heading, body) in enumerate(guide["sections"]))
    related = ''.join(f'<li><a href="/journal/{other}.html">{esc(other.replace("-", " ").capitalize())}</a></li>' for other in guide["related"])
    page = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — Maison Léa</title><meta name="description" content="{esc(description, quote=True)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{esc(title, quote=True)}"><meta property="og:description" content="{esc(description, quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="https://guide-soin.fr{image}"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="_style.css"><script type="application/ld+json">{schema}</script></head>
<body><nav class="nav"><div class="nav-inner"><a href="/" class="brand">Maison <em>Léa</em></a><a href="/journal/">Le Journal</a></div></nav>
<article class="wrap"><p class="kicker">PRÉPARER NOËL</p><h1>{esc(title)}</h1><p class="lead">{esc(description)}</p><p class="meta">20 novembre 2026 · 3 min de lecture · Rédaction Maison Léa</p>
<img src="{image}" alt="Illustration de l’univers cadeau Maison Léa" width="1200" height="800"><nav aria-label="Sommaire"><h2>Dans ce guide</h2><ul>{toc}</ul></nav>{sections}
<h2>Notre méthode</h2><p>Conseils éditoriaux pour préparer un achat. Aucun produit de ce guide n’a fait l’objet d’un test par notre rédaction. Les prix, les variantes et les conditions restent à vérifier sur la fiche du marchand au moment de l’achat.</p>
<p><a href="/#produits">Explorer la sélection Maison Léa</a> · <a href="/affiliation.html">Comprendre nos liens affiliés</a></p><h2>À lire aussi</h2><ul>{related}</ul><a class="cta-back" href="/journal/">Tous les guides</a></article>
<footer class="foot">© 2026 Maison Léa · <a href="/">Accueil</a> · <a href="/mentions-legales.html">Mentions légales</a> · <a href="/confidentialite.html">Confidentialité</a></footer></body></html>'''
    (ROOT / "journal" / f"{slug}.html").write_text(page)
    cards.append(f'<a class="article-card" href="/journal/{slug}.html"><img class="ac-cover" src="{image}" alt="" loading="lazy" width="1200" height="800"><div class="ac-body"><p class="ac-kicker smallcaps">PRÉPARER NOËL</p><h2 class="ac-title serif">{esc(title)}</h2><p class="ac-lead">{esc(description)}</p><p class="ac-meta">20 NOVEMBRE 2026 · 3 MIN</p></div></a>')

index = ROOT / "journal" / "index.html"
source = index.read_text()
if GUIDES[0]["slug"] not in source:
    source = source.replace('<div class="articles-grid">', '<div class="articles-grid">\n'+ '\n'.join(cards), 1)
    index.write_text(source)
print("Trois guides de Noël ajoutés et reliés au journal.")
