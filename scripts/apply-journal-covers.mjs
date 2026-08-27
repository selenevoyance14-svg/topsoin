import { readFile, writeFile, readdir } from "node:fs/promises";
import { join } from "node:path";

const root = process.cwd();
const journalDir = join(root, "journal");

const covers = {
  lingerie: "/assets/journal/lingerie-editorial.webp",
  nuit: "/assets/journal/nuit-cocooning.webp",
  plaisir: "/assets/journal/plaisir-bien-etre.webp",
  cadeaux: "/assets/journal/cadeau-couple.webp",
  soins: "/assets/journal/soins-massage.webp",
  lecture: "/assets/journal/lecture-jeux.webp",
};

function themeFor(slug, kicker = "") {
  const value = `${slug} ${kicker}`.toLowerCase();
  if (/livre|lecture|roman|kamasutra|carte|jeu|questions|action-ou-verite|fantasme/.test(value)) return "lecture";
  if (/cadeau|coffret|mariage|saint-valentin|fete-des-meres|evjf|cremaillere|anniversaire/.test(value)) return "cadeaux";
  if (/soin|huile|massage|bougie|bain|gommage|peau|brume|parfum|gel|lubrifiant|secheresse|hygiene|perinee/.test(value)) return "soins";
  if (/vibro|sextoy|jouet|plug|gode|geisha|anneau|bondage|menottes|plaisir|sensualite|preliminaire/.test(value)) return "plaisir";
  if (/pyjama|nuit|peignoir|kimono|chausson|loungewear|cocooning|dormir|sommeil/.test(value)) return "nuit";
  return "lingerie";
}

const files = (await readdir(journalDir)).filter((file) => file.endsWith(".html") && file !== "index.html");
for (const file of files) {
  const path = join(journalDir, file);
  let html = await readFile(path, "utf8");
  const slug = file.replace(/\.html$/, "");
  const kicker = html.match(/<div class="kicker">([^<]+)<\/div>/)?.[1] || "";
  const title = html.match(/<h1[^>]*>([^<]+)<\/h1>/)?.[1] || "Guide Maison Léa";
  const cover = covers[themeFor(slug, kicker)];
  html = html.replace(/<div class="cover-bg" style="[^"]*"><\/div>/, `<div class="cover-bg" role="img" aria-label="${title.replaceAll('"', '&quot;')}" style="background-image:url('${cover}')"></div>`);
  if (!html.includes('property="og:image"')) {
    html = html.replace(/(<meta property="og:url"[^>]+>)/, `$1\n<meta property="og:image" content="https://guide-soin.fr${cover}" />`);
  }
  html = html.replace(/Tous les produits ci-dessous sont disponibles sur Amazon, souvent en livraison Prime et expédiés en colis neutre — discrétion totale\./g, "Les produits présentés sont proposés sur Amazon. Vérifiez le vendeur, les conditions de livraison, les retours et la disponibilité directement sur la fiche produit.");
  await writeFile(path, html);
}

const indexPath = join(journalDir, "index.html");
let index = await readFile(indexPath, "utf8");
index = index.replace(/<a href="\/journal\/([^\"]+)\.html" class="article-card">\s*<(?:div|img) class="ac-cover"[^>]*(?:><\/div>)?/g, (match, slug) => {
  const card = index.slice(index.indexOf(match), index.indexOf(match) + 900);
  const kicker = card.match(/class="ac-kicker smallcaps">([^<]+)/)?.[1] || "";
  const title = card.match(/class="ac-title serif">([^<]+)/)?.[1] || "Guide Maison Léa";
  const cover = covers[themeFor(slug, kicker)];
  return `<a href="/journal/${slug}.html" class="article-card">\n  <img class="ac-cover" src="${cover}" alt="${title.replaceAll('"', '&quot;')}" loading="lazy" decoding="async">`;
});
await writeFile(indexPath, index);

console.log(`Couvertures éditoriales appliquées à ${files.length} articles et à l'index.`);
