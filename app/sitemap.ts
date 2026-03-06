import { MetadataRoute } from "next";
import { getAllArticles, CATEGORIES } from "@/lib/articles";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = "https://guide-soin.fr";
  const articles = getAllArticles();

  const articleUrls = articles.map((article) => ({
    url: `${baseUrl}/categorie/${article.categorie}/${article.slug}`,
    lastModified: new Date(article.date),
    changeFrequency: "monthly" as const,
    priority: 0.8,
  }));

  const categoryUrls = Object.keys(CATEGORIES).map((slug) => ({
    url: `${baseUrl}/categorie/${slug}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.9,
  }));

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    ...categoryUrls,
    ...articleUrls,
  ];
}