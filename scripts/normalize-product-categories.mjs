import { readFile, writeFile } from "node:fs/promises";

const file = "data.jsx";
let source = await readFile(file, "utf8");
const match = source.match(/const PRODUCTS = (\[[\s\S]*?\n\]);/);
if (!match) throw new Error("Bloc PRODUCTS introuvable");

const products = JSON.parse(match[1]);
const colors = { sensualite: "#1a1a1a", erotisme: "#3a1a26", soins: "#c9a961" };
let changed = 0;

for (const product of products) {
  const title = product.name.toLowerCase();
  let category = product.cat;
  if (/vibromasseur|vibrateur|stimulateur|sex toys?|sextoy|œuf vibrant|oeuf vibrant|gode|boules? geisha|anneau vibrant/.test(title)) {
    category = "sensualite";
  } else if (/roman érotique|roman erotique|récits coquins|recits coquins|livre de jeux|jeu de couple|défis coquins|defis coquins|questions.*couple/.test(title)) {
    category = "erotisme";
  }
  if (category !== product.cat) {
    product.cat = category;
    product.color = colors[category];
    changed++;
  }
}

source = source.replace(match[1], JSON.stringify(products, null, 2));
for (const category of ["lingerie", "nuit", "sensualite", "erotisme", "soins", "cadeaux"]) {
  const count = products.filter((product) => product.cat === category).length;
  source = source.replace(new RegExp(`(id:'${category}'[^\\n]+count:)\\s*\\d+`), `$1 ${count}`);
}
source = source.replace(/(\{ num:')\d+(',\s*label:'produits sélectionnés' \})/, `$1${products.length}$2`);
await writeFile(file, source);
console.log(`${changed} catégories corrigées.`);
