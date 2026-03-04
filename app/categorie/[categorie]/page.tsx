import { getArticlesByCategorie, CATEGORIES } from "@/lib/articles";
import { notFound } from "next/navigation";

export default async function CategoriePage({ params }: { params: Promise<{ categorie: string }> }) {
  const { categorie } = await params;
  const cat = CATEGORIES[categorie];
  if (!cat) notFound();

  const articles = getArticlesByCategorie(categorie);

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      {/* Header catégorie */}
      <div className="text-center mb-12">
        <span className="text-5xl block mb-3">{cat.emoji}</span>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Les Meilleurs Soins <span className="text-rose-500">{cat.label}</span>
        </h1>
        <p className="text-gray-500 max-w-xl mx-auto">{cat.description}</p>
      </div>

      {articles.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-4xl mb-4">🌸</p>
          <p>Guides en cours de rédaction — revenez bientôt !</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article) => (
            <a key={article.slug} href={`/categorie/${categorie}/${article.slug}`}
              className="card-article group">
              <div className="bg-rose-50 h-40 flex items-center justify-center text-4xl">
                {cat.emoji}
              </div>
              <div className="p-5">
                <h2 className="font-bold text-gray-900 mb-2 group-hover:text-rose-500 transition leading-snug">
                  {article.title}
                </h2>
                <p className="text-sm text-gray-500 line-clamp-3 mb-4">{article.description}</p>
                <span className="text-rose-500 text-sm font-semibold">Voir le comparatif →</span>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
