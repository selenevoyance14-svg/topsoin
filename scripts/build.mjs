// Build script — copie les fichiers statiques dans out/ pour Cloudflare Pages
import { mkdir, rm, cp, readdir, writeFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { execFileSync } from "node:child_process";

const root = process.cwd();
const out = join(root, "out");

// Renvoie la date de dernière modif d'un fichier au format YYYY-MM-DD.
// Priorité : dernier commit git (date réelle du contenu) ; repli : mtime fichier.
function lastmodFor(relPath) {
    try {
        const iso = execFileSync("git", ["log", "-1", "--format=%cI", "--", relPath], {
            cwd: root,
            encoding: "utf8",
        }).trim();
        if (iso) return iso.slice(0, 10);
    } catch {
        // git indisponible (ex: build CI shallow) → repli plus bas
    }
    return null;
}
async function lastmodOrMtime(relPath) {
    const gitDate = lastmodFor(relPath);
    if (gitDate) return gitDate;
    const s = await stat(join(root, relPath));
    return s.mtime.toISOString().slice(0, 10);
}

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

// Articles du journal pour le sitemap — lus dynamiquement depuis journal/
// (ainsi le sitemap reste toujours synchronisé avec les articles réels)
const journalEntries = await readdir(join(root, "journal"));
const journalSlugs = journalEntries
    .filter(f => f.endsWith(".html") && f !== "index.html")
    .map(f => f.replace(/\.html$/, ""))
    .sort();
const journalDated = await Promise.all(
    journalSlugs.map(async s => ({
        slug: s,
        lastmod: await lastmodOrMtime(`journal/${s}.html`),
    }))
);
const journalUrls = journalDated
    .map(({ slug, lastmod }) => `  <url><loc>https://guide-soin.fr/journal/${slug}.html</loc><lastmod>${lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>`)
    .join("\n");

// Home + listing journal = fraîcheur du contenu le plus récent (les nouveaux articles y sont mis en avant)
const homeLastmod = journalDated.reduce((max, e) => (e.lastmod > max ? e.lastmod : max), await lastmodOrMtime("index.html"));

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://guide-soin.fr/</loc><lastmod>${homeLastmod}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://guide-soin.fr/journal/</loc><lastmod>${homeLastmod}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>
${journalUrls}
  <url><loc>https://guide-soin.fr/affiliation.html</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>
  <url><loc>https://guide-soin.fr/mentions-legales.html</loc><changefreq>yearly</changefreq><priority>0.3</priority></url>
  <url><loc>https://guide-soin.fr/confidentialite.html</loc><changefreq>yearly</changefreq><priority>0.3</priority></url>
</urlset>
`;
await writeFile(join(out, "sitemap.xml"), sitemap);

const list = await readdir(out);
console.log("Build OK — files in out/:", list.join(", "));
