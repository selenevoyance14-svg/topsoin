import fs from "fs";
import path from "path";
import matter from "gray-matter";

const baseUrl = "https://guide-soin.fr";
const contentDir = path.join(process.cwd(), "content");
const categories = ["cheveux", "visage", "corps", "maquillage", "parfum", "homme"];

const today = new Date().toISOString().split("T")[0];

const urls = [
  `  <url><loc>${baseUrl}</loc><lastmod>${today}</lastmod><priority>1.0</priority></url>`,
];

for (const cat of categories) {
  urls.push(`  <url><loc>${baseUrl}/categorie/${cat}</loc><lastmod>${today}</lastmod><priority>0.9</priority></url>`);
  const catDir = path.join(contentDir, cat);
  if (!fs.existsSync(catDir)) continue;
  const files = fs.readdirSync(catDir).filter((f) => f.endsWith(".mdx"));
  for (const file of files) {
    const slug = file.replace(".mdx", "");
    const raw = fs.readFileSync(path.join(catDir, file), "utf-8");
    const { data } = matter(raw);
    const date = data.date ? new Date(data.date).toISOString().split("T")[0] : today;
    urls.push(`  <url><loc>${baseUrl}/categorie/${cat}/${slug}</loc><lastmod>${date}</lastmod><priority>0.8</priority></url>`);
  }
}

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join("\n")}
</urlset>`;

fs.writeFileSync(path.join(process.cwd(), "public", "sitemap.xml"), sitemap);
console.log(`Sitemap generated with ${urls.length} URLs`);
