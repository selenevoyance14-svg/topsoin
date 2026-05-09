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

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://guide-soin.fr/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://guide-soin.fr/affiliation.html</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>
  <url><loc>https://guide-soin.fr/mentions-legales.html</loc><changefreq>yearly</changefreq><priority>0.3</priority></url>
  <url><loc>https://guide-soin.fr/confidentialite.html</loc><changefreq>yearly</changefreq><priority>0.3</priority></url>
</urlset>
`;
await writeFile(join(out, "sitemap.xml"), sitemap);

const list = await readdir(out);
console.log("Build OK — files in out/:", list.join(", "));
