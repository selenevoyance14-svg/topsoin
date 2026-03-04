import { getArticle, CATEGORIES } from "@/lib/articles";
import { notFound } from "next/navigation";
import { MDXRemote } from "next-mdx-remote/rsc";

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ categorie: string; slug: string }>;
}) {
  const { categorie, slug } = await params;
  const article = getArticle(categorie, slug);
  if (!article) notFound();

  const cat = CATEGORIES[categorie];

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      {/* Breadcrumb */}
      <nav className="text-sm text-gray-400 mb-6 flex items-center gap-2">
        <a href="/" className="hover:text-rose-500">Accueil</a>
        <span>/</span>
        <a href={`/categorie/${categorie}`} className="hover:text-rose-500">{cat?.label}</a>
        <span>/</span>
        <span className="text-gray-600">{article.title}</span>
      </nav>

      {/* Header */}
      <div className="mb-8">
        <span className="badge mb-3 inline-block">{cat?.emoji} {cat?.label}</span>
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 leading-tight">
          {article.title}
        </h1>
        <p className="text-lg text-gray-600">{article.description}</p>
        <p className="text-sm text-gray-400 mt-3">Mis à jour le {new Date(article.date).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })}</p>
      </div>

      {/* Disclaimer affilié */}
      <div className="bg-rose-50 border border-rose-100 rounded-xl p-4 mb-8">
        <p className="affiliate-disclaimer">
          🔗 <strong>Transparence :</strong> Certains liens de cet article sont des liens affiliés.
          Si vous achetez via ces liens, nous percevons une petite commission, sans coût supplémentaire pour vous.
          Cela nous aide à maintenir ce site gratuitement.
        </p>
      </div>

      {/* Contenu MDX */}
      <div className="prose prose-rose prose-lg max-w-none
        prose-headings:font-bold prose-headings:text-gray-900
        prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4
        prose-h3:text-xl prose-h3:mt-6 prose-h3:mb-3
        prose-p:text-gray-600 prose-p:leading-relaxed
        prose-a:text-rose-500 prose-a:no-underline hover:prose-a:underline
        prose-strong:text-gray-900
        prose-li:text-gray-600
        prose-table:text-sm">
        <MDXRemote source={article.content} />
      </div>

      {/* Retour catégorie */}
      <div className="mt-12 pt-8 border-t border-gray-100">
        <a href={`/categorie/${categorie}`} className="text-rose-500 font-semibold hover:underline">
          ← Voir tous les comparatifs {cat?.label}
        </a>
      </div>
    </div>
  );
}
