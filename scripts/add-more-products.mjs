// Ajoute N produits Amazon supplémentaires à chaque article du journal,
// en piochant dans la vraie base data.jsx (catégorie détectée via les ASIN déjà présents).
// Usage: node scripts/add-more-products.mjs [--write] [--n=2]
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const WRITE = process.argv.includes("--write");
const N = Number((process.argv.find(a => a.startsWith("--n=")) || "--n=2").split("=")[1]);
const TAG = "lebrunnathali-21";

// --- Charger data.jsx en simulant window ---
const src = readFileSync(join(root, "data.jsx"), "utf8");
const window = {};
new Function("window", src)(window);
const PRODUCTS = window.PRODUCTS;
const byAsin = new Map(PRODUCTS.map(p => [p.asin, p]));
const byCat = {};
for (const p of PRODUCTS) (byCat[p.cat] ||= []).push(p);

// Catégorie de sujet d'après le kicker éditorial (signal le plus fiable).
// Les kickers ambigus (COMPARATIF, TENDANCE, RÉFLEXION...) ne sont pas listés
// -> repli sur la catégorie majoritaire des produits déjà présents.
const KICKER_CAT = {
  "GUIDE LINGERIE": "lingerie",
  "SENSUALITÉ": "sensualite",
  "RITUEL COUPLE": "sensualite",
  "GUIDE NUIT": "nuit",
  "NUIT & LOUNGEWEAR": "nuit",
  "ÉROTISME": "erotisme",
  "JEUX DE COUPLE": "erotisme",
  "SOINS INTIMES": "soins",
  "RITUEL SOINS": "soins",
  "GUIDE BIEN-ÊTRE INTIME": "soins",
  "COFFRETS": "cadeaux",
  "IDÉES CADEAUX": "cadeaux",
  "COFFRETS & CADEAUX": "cadeaux",
};

const cardRe = /<div class="product-card">[\s\S]*?<\/div>\s*<\/div>/g;

function makeCard(p, indent) {
  const url = `https://www.amazon.fr/dp/${p.asin}?tag=${TAG}`;
  const alt = p.name.replace(/"/g, "&quot;");
  return [
    `${indent}<div class="product-card">`,
    `${indent}  <img src="${p.image}" alt="${alt}" loading="lazy"/>`,
    `${indent}  <div class="pc-body">`,
    `${indent}    <div class="pc-name">${p.name}</div>`,
    `${indent}    <div class="pc-sub smallcaps">${p.sub}</div>`,
    `${indent}    <div class="pc-price">${p.price}</div>`,
    `${indent}    <a class="pc-cta" href="${url}" target="_blank" rel="sponsored noopener nofollow">Voir sur Amazon &rarr;</a>`,
    `${indent}  </div>`,
    `${indent}</div>`,
  ].join("\n");
}

const cursor = {}; // rotation par catégorie pour varier les produits
const files = readdirSync(join(root, "journal")).filter(f => f.endsWith(".html") && f !== "index.html");
let report = [];

for (const f of files) {
  const path = join(root, "journal", f);
  let html = readFileSync(path, "utf8");

  const cards = [...html.matchAll(cardRe)];
  if (cards.length === 0) { report.push([f, "—", "aucun bloc produit"]); continue; }

  // ASIN déjà présents
  const presentAsins = new Set([...html.matchAll(/amazon\.fr\/dp\/([A-Z0-9]{10})/g)].map(m => m[1]));

  // Catégorie = kicker éditorial en priorité (signal de sujet fiable),
  // sinon majorité des ASIN présents connus, sinon repli.
  const k = (html.match(/<div class="kicker">([^<]+)<\/div>/) || [])[1]?.trim().toUpperCase();
  let cat = KICKER_CAT[k];
  if (!cat) {
    const cats = {};
    for (const a of presentAsins) { const p = byAsin.get(a); if (p) cats[p.cat] = (cats[p.cat] || 0) + 1; }
    cat = Object.entries(cats).sort((a, b) => b[1] - a[1])[0]?.[0] || "cadeaux";
  }

  // Choisir N produits de la catégorie non déjà présents (rotation)
  const pool = byCat[cat] || [];
  const picks = [];
  let start = cursor[cat] || 0;
  for (let i = 0; i < pool.length && picks.length < N; i++) {
    const p = pool[(start + i) % pool.length];
    if (!presentAsins.has(p.asin) && !picks.some(x => x.asin === p.asin)) picks.push(p);
  }
  cursor[cat] = (start + N) % (pool.length || 1);
  if (picks.length === 0) { report.push([f, cat, "rien à ajouter"]); continue; }

  // Indentation du dernier bloc produit
  const last = cards[cards.length - 1];
  const lineStart = html.lastIndexOf("\n", last.index) + 1;
  const indent = html.slice(lineStart, last.index).match(/^\s*/)[0];

  const insertPos = last.index + last[0].length;
  const block = "\n" + picks.map(p => makeCard(p, indent)).join("\n");
  html = html.slice(0, insertPos) + block + html.slice(insertPos);

  if (WRITE) writeFileSync(path, html);
  report.push([f, cat, `+${picks.length} (${picks.map(p => p.asin).join(", ")})`]);
}

// Résumé
const added = report.filter(r => r[2].startsWith("+")).length;
console.log(`${WRITE ? "ÉCRIT" : "SIMULATION"} — ${added}/${files.length} articles enrichis en produits (n=${N})`);
console.log("Exemples :");
for (const r of report.slice(0, 8)) console.log(`  ${r[0]} [${r[1]}] ${r[2]}`);
const problems = report.filter(r => !r[2].startsWith("+"));
if (problems.length) { console.log(`\n⚠ ${problems.length} sans ajout :`); for (const r of problems) console.log(`  ${r[0]} — ${r[2]}`); }
