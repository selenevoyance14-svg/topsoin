import { getAllArticles, CATEGORIES } from "@/lib/articles";
import { Flower2, Search, MessageSquare, RefreshCw } from "lucide-react";

export default function HomePage() {
  const articles = getAllArticles();
  const recent = articles.slice(0, 6);

  return (
    <div>
      {/* HERO */}
      <section className="bg-gradient-to-br from-rose-50 to-pink-50 py-16 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <Flower2 size={48} className="text-rose-400 mx-auto mb-4" />
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Les <span className="text-rose-500">Meilleurs</span> Soins Beauté
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
            Comparatifs honnêtes et guides d&apos;achat pour choisir les meilleurs produits beauté.
            Cheveux, visage, corps — on a tout testé pour vous.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            {Object.entries(CATEGORIES).map(([slug, cat]) => (
              <a key={slug} href={`/categorie/${slug}`} className="btn-rose flex items-center gap-2">
                <cat.Icon size={16} /> {cat.label}
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* CATÉGORIES */}
      <section className="max-w-6xl mx-auto px-4 py-14">
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Nos catégories</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {Object.entries(CATEGORIES).map(([slug, cat]) => {
            const count = articles.filter((a) => a.categorie === slug).length;
            return (
              <a key={slug} href={`/categorie/${slug}`}
                className="card-article p-8 text-center group">
                <div className="flex justify-center mb-3 text-rose-400">
                  <cat.Icon size={40} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-rose-500 transition">
                  {cat.label}
                </h3>
                <p className="text-sm text-gray-500 mb-4">{cat.description}</p>
                <span className="badge">{count} guide{count > 1 ? "s" : ""}</span>
              </a>
            );
          })}
        </div>
      </section>

      {/* DERNIERS ARTICLES */}
      {recent.length > 0 && (
        <section className="max-w-6xl mx-auto px-4 pb-14">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">Derniers comparatifs</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recent.map((article) => {
              const cat = CATEGORIES[article.categorie];
              return (
                <a key={article.slug} href={`/categorie/${article.categorie}/${article.slug}`}
                  className="card-article group">
                  <div className="bg-rose-50 h-40 flex items-center justify-center text-rose-300">
                    {cat ? <cat.Icon size={48} /> : <Flower2 size={48} />}
                  </div>
                  <div className="p-5">
                    <span className="badge mb-2 inline-flex items-center gap-1">
                      {cat && <cat.Icon size={11} />} {cat?.label}
                    </span>
                    <h3 className="font-bold text-gray-900 mb-2 group-hover:text-rose-500 transition leading-snug">
                      {article.title}
                    </h3>
                    <p className="text-sm text-gray-500 line-clamp-2">{article.description}</p>
                  </div>
                </a>
              );
            })}
          </div>
        </section>
      )}

      {/* POURQUOI NOUS FAIRE CONFIANCE */}
      <section className="bg-rose-50 py-14 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Pourquoi nous faire confiance ?</h2>
          <div className="grid md:grid-cols-3 gap-6 text-center">
            {[
              { Icon: Search,        title: "Sélection rigoureuse",    desc: "Chaque produit est analysé en détail : composition, avis clients, rapport qualité/prix." },
              { Icon: MessageSquare, title: "Avis authentiques",        desc: "Nous agrégeons des milliers d'avis réels pour vous donner une vue objective." },
              { Icon: RefreshCw,     title: "Mis à jour régulièrement", desc: "Nos comparatifs sont mis à jour chaque mois pour refléter les dernières sorties." },
            ].map((item) => (
              <div key={item.title} className="bg-white rounded-2xl p-6 shadow-sm">
                <div className="flex justify-center mb-3 text-rose-400">
                  <item.Icon size={32} />
                </div>
                <h3 className="font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-sm text-gray-500">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
