// Build script — copie les fichiers statiques dans out/ pour Cloudflare Pages
import { mkdir, rm, cp, readdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

const root = process.cwd();
const out = join(root, "out");

const filesToCopy = [
    "index.html",
    "mentions-legales.html",
    "confidentialite.html",
    "affiliation.html",
    "app.jsx",
    "components.jsx",
    "components-2.jsx",
    "data.jsx",
    "assets",
    "ads.txt",
    "google90481d72c7059505.html",
    "journal",
    "favicon.svg",
];

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });

for (const f of filesToCopy) {
    await cp(join(root, f), join(out, f), { recursive: true });
}

const robots = `User-agent: *
Allow: /
Disallow: /assets/
Sitemap: https://guide-soin.fr/sitemap.xml
`;
await writeFile(join(out, "robots.txt"), robots);

// Articles du journal pour le sitemap
const journalSlugs = [
    "comment-choisir-soutien-gorge-sans-armatures",
    "guide-nuisette-satin-tomber-amoureuse-tissu",
    "bien-choisir-lubrifiant-intime-guide",
    "vibromasseurs-debutantes-selection",
    "idees-cadeaux-couple-romantique",
    "lingerie-et-confiance-soi",
    "comment-trouver-sa-taille-soutien-gorge",
    "bralette-confort-elegance",
    "body-dentelle-guide-bien-choisir",
    "culotte-taille-haute-confort-style",
    "kimono-peignoir-robe-chambre-difference",
    "pyjama-satin-luxe-quotidien",
    "stimulateur-clitoridien-tout-comprendre",
    "bougie-massage-rituel-sensoriel",
    "pimenter-couple-7-idees-simples",
    "saint-valentin-7-idees-cadeaux",
];
const journalUrls = journalSlugs
    .map(s => `  <url><loc>https://guide-soin.fr/journal/${s}.html</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>`)
    .join("\n");

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://guide-soin.fr/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://guide-soin.fr/journal/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>
${journalUrls}
  <url><loc>https://guide-soin.fr/affiliation.html</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>
  <url><loc>https://guide-soin.fr/mentions-legales.html</loc><changefreq>yearly</changefreq><priority>0.3</priority></url>
  <url><loc>https://guide-soin.fr/confidentialite.html</loc><changefreq>yearly</changefreq><priority>0.3</priority></url>
</urlset>
`;
await writeFile(join(out, "sitemap.xml"), sitemap);

const list = await readdir(out);
console.log("Build OK — files in out/:", list.join(", "));
