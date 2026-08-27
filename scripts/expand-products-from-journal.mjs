import { readFile, writeFile, readdir } from "node:fs/promises";
import { join } from "node:path";

const root = process.cwd();
const dataPath = join(root, "data.jsx");
let source = await readFile(dataPath, "utf8");
const productsMatch = source.match(/const PRODUCTS = (\[[\s\S]*?\]);\n\nconst PROMISES/);
if (!productsMatch) throw new Error("Bloc PRODUCTS introuvable dans data.jsx");

const products = JSON.parse(productsMatch[1]);
const existing = new Set(products.map((product) => product.asin));
const colors = { lingerie: "#8b1d2c", nuit: "#3a2e1f", sensualite: "#1a1a1a", erotisme: "#3a1a26", soins: "#c9a961", cadeaux: "#5b1a26" };

function categoryFor(slug, kicker = "") {
  const value = `${slug} ${kicker}`.toLowerCase();
  if (/cadeau|coffret|mariage|saint-valentin|fete-des-meres|evjf|cremaillere|anniversaire/.test(value)) return "cadeaux";
  if (/livre|lecture|roman|kamasutra|carte|jeu|questions|action-ou-verite|fantasme/.test(value)) return "erotisme";
  if (/soin|huile|massage|bougie|bain|gommage|peau|brume|parfum|gel|lubrifiant|secheresse|hygiene|perinee/.test(value)) return "soins";
  if (/vibro|sextoy|jouet|plug|gode|geisha|anneau|bondage|menottes|plaisir|sensualite|preliminaire/.test(value)) return "sensualite";
  if (/pyjama|nuit|peignoir|kimono|chausson|loungewear|cocooning|dormir|sommeil/.test(value)) return "nuit";
  return "lingerie";
}

const candidates = [];
const files = (await readdir(join(root, "journal"))).filter((file) => file.endsWith(".html") && file !== "index.html").sort();
for (const file of files) {
  const html = await readFile(join(root, "journal", file), "utf8");
  const kicker = html.match(/<div class="kicker">([^<]+)<\/div>/)?.[1] || "";
  const cat = categoryFor(file, kicker);
  const cardPattern = /<div class="product-card">\s*<img src="([^"]+)" alt="([^"]+)"[^>]*>\s*<div class="pc-body">\s*<div class="pc-name">([^<]+)<\/div>\s*<div class="pc-sub smallcaps">([^<]+)<\/div>\s*<div class="pc-price">([^<]*)<\/div>\s*<a class="pc-cta" href="([^"]+)"/g;
  for (const match of html.matchAll(cardPattern)) {
    const asin = match[6].match(/\/dp\/([A-Z0-9]+)/i)?.[1];
    if (!asin || existing.has(asin) || candidates.some((item) => item.asin === asin)) continue;
    candidates.push({ cat, image: match[1], name: match[3], sub: match[4], price: match[5], asin, url: match[6] });
  }
}

const targetByCategory = { lingerie: 4, nuit: 4, sensualite: 3, erotisme: 3, soins: 3, cadeaux: 3 };
const selected = [];
for (const [cat, count] of Object.entries(targetByCategory)) selected.push(...candidates.filter((item) => item.cat === cat).slice(0, count));
if (selected.length < 20) selected.push(...candidates.filter((item) => !selected.includes(item)).slice(0, 20 - selected.length));
if (selected.length < 20) throw new Error(`Seulement ${selected.length} produits inédits trouvés dans le journal`);

let nextId = Math.max(...products.map((product) => product.id)) + 1;
for (const item of selected.slice(0, 20)) {
  products.push({ id: nextId++, cat: item.cat, name: item.name, sub: item.sub, price: item.price, was: "", off: "", rating: 0, reviews: 0, prime: false, tag: "Vu dans le Journal", color: colors[item.cat], asin: item.asin, image: item.image, url: item.url });
}

source = source.replace(productsMatch[1], JSON.stringify(products, null, 2));
for (const cat of Object.keys(targetByCategory)) {
  const count = products.filter((product) => product.cat === cat).length;
  source = source.replace(new RegExp(`(id:'${cat}'[^\\n]+count:) \\d+`), `$1 ${count}`);
}
source = source.replace(/\{ num:'48', label:'produits sélectionnés' \}/, `{ num:'${products.length}', label:'produits sélectionnés' }`);
await writeFile(dataPath, source);
console.log(`${selected.slice(0, 20).length} produits du Journal ajoutés — ${products.length} produits au total.`);
