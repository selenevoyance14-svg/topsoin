// Ajoute 30 produits déjà vérifiés dans les comparatifs du journal au catalogue principal.

import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const SOURCES = [
  { cat: "lingerie", color: "#8b1d2c", files: ["meilleure-lingerie-selection-comparatif.html"] },
  { cat: "nuit", color: "#3a2e1f", files: ["meilleur-pyjama-nuisette-comparatif.html"] },
  { cat: "sensualite", color: "#1a1a1a", files: ["meilleurs-vibromasseurs-comparatif-guide.html"] },
  { cat: "erotisme", color: "#3a1a26", files: ["jeux-cartes-coquins-couple-selection.html", "kamasutra-livre-debutant-poses-guide.html", "des-jeux-coquins-soiree-couple.html", "roman-erotique-femme-selection-guide.html", "lecture-erotique-par-quel-livre-commencer.html"] },
  { cat: "soins", color: "#c9a961", files: ["meilleurs-soins-corps-selection.html"] },
  { cat: "cadeaux", color: "#5b1a26", files: ["meilleurs-coffrets-cadeaux-couple-comparatif.html", "coffret-cadeau-couple-anniversaire-idees.html"] },
];

const decodeHtml = (value) => value
  .replace(/&amp;/g, "&")
  .replace(/&#39;|&apos;/g, "'")
  .replace(/&quot;/g, '"')
  .replace(/&nbsp;| /g, " ")
  .replace(/&euro;/g, "€")
  .trim();

function parseCards(html) {
  const cards = [];
  const cardPattern = /<div class="product-card">([\s\S]*?)<\/div>\s*<\/div>/g;
  for (const match of html.matchAll(cardPattern)) {
    const block = match[1];
    const image = block.match(/<img src="([^"]+)"/)?.[1];
    const name = block.match(/<div class="pc-name">([\s\S]*?)<\/div>/)?.[1];
    const sub = block.match(/<div class="pc-sub smallcaps">([\s\S]*?)<\/div>/)?.[1];
    const price = block.match(/<div class="pc-price">([\s\S]*?)<\/div>/)?.[1];
    const link = block.match(/href="https:\/\/www\.amazon\.fr\/dp\/([A-Z0-9]{10})[^\"]*"/)?.[1];
    if (image && name && sub && price && link) {
      cards.push({ image, name: decodeHtml(name), sub: decodeHtml(sub), price: decodeHtml(price), asin: link });
    }
  }
  return cards;
}

async function main() {
  const dataPath = join(process.cwd(), "data.jsx");
  const content = await readFile(dataPath, "utf8");
  const existingMatch = content.match(/const PRODUCTS = (\[[\s\S]*?\n\]);/);
  if (!existingMatch) throw new Error("PRODUCTS introuvable dans data.jsx");

  const existing = eval(existingMatch[1]);
  const usedAsins = new Set(existing.map((product) => product.asin));
  const additions = [];
  let nextId = Math.max(...existing.map((product) => product.id)) + 1;

  for (const source of SOURCES) {
    const cards = [];
    for (const file of source.files) {
      const html = await readFile(join(process.cwd(), "journal", file), "utf8");
      cards.push(...parseCards(html));
    }
    const seenCandidates = new Set();
    const picks = cards.filter((product) => {
      if (usedAsins.has(product.asin) || seenCandidates.has(product.asin)) return false;
      seenCandidates.add(product.asin);
      return true;
    }).slice(0, 5);
    if (picks.length !== 5) throw new Error(`${source.cat}: seulement ${picks.length} nouveaux produits disponibles`);

    for (const product of picks) {
      usedAsins.add(product.asin);
      additions.push({
        id: nextId++,
        cat: source.cat,
        name: product.name,
        sub: product.sub,
        price: product.price,
        was: "",
        off: "",
        rating: 0,
        reviews: 0,
        prime: false,
        tag: "",
        color: source.color,
        asin: product.asin,
        image: product.image,
        url: `https://www.amazon.fr/dp/${product.asin}?tag=lebrunnathali-21`,
      });
    }
  }

  const products = [...existing, ...additions];
  const counts = Object.fromEntries(SOURCES.map(({ cat }) => [cat, products.filter((product) => product.cat === cat).length]));
  const updated = content
    .replace(/const AMAZON_DATA_UPDATED_AT = "[^"]+";/, `const AMAZON_DATA_UPDATED_AT = "${new Date().toISOString()}";`)
    .replace(/(const PRODUCTS = )\[[\s\S]*?\n\];/, `$1${JSON.stringify(products, null, 2)};`)
    .replace(/(\{ id:'lingerie',[^\n]*count:)\s*\d+/, `$1 ${counts.lingerie}`)
    .replace(/(\{ id:'nuit',[^\n]*count:)\s*\d+/, `$1 ${counts.nuit}`)
    .replace(/(\{ id:'sensualite',[^\n]*count:)\s*\d+/, `$1 ${counts.sensualite}`)
    .replace(/(\{ id:'erotisme',[^\n]*count:)\s*\d+/, `$1 ${counts.erotisme}`)
    .replace(/(\{ id:'soins',[^\n]*count:)\s*\d+/, `$1 ${counts.soins}`)
    .replace(/(\{ id:'cadeaux',[^\n]*count:)\s*\d+/, `$1 ${counts.cadeaux}`)
    .replace(/(\{ num:')\d+(',\s*label:'produits sélectionnés' \})/, `$1${products.length}$2`);

  await writeFile(dataPath, updated, "utf8");
  console.log(`Ajoutés : ${additions.length}; catalogue : ${existing.length} → ${products.length}.`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
