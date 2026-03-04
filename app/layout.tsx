import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GuideSoin — Les Meilleurs Produits Beauté & Soins",
  description: "Guides d'achat et comparatifs beauté : cheveux, visage, corps. Trouvez les meilleurs produits testés et approuvés.",
  keywords: "meilleur shampoing, crème visage, soin cheveux, comparatif beauté, guide achat beauté",
  openGraph: {
    title: "GuideSoin — Les Meilleurs Produits Beauté",
    description: "Comparatifs et guides d'achat beauté pour choisir les meilleurs soins.",
    type: "website",
    locale: "fr_FR",
    url: "https://guide-soin.fr",
  },
};

export const dynamic = "force-dynamic";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>
        {/* HEADER */}
        <header className="sticky top-0 z-50 bg-white border-b border-rose-100 shadow-sm">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <a href="/" className="flex items-center gap-1">
              <span className="text-2xl">🌸</span>
              <span className="text-xl font-bold text-rose-500">Top</span>
              <span className="text-xl font-bold text-gray-800">Soin</span>
            </a>
            <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
              <a href="/categorie/cheveux" className="text-gray-600 hover:text-rose-500 transition">💇 Cheveux</a>
              <a href="/categorie/visage" className="text-gray-600 hover:text-rose-500 transition">✨ Visage</a>
              <a href="/categorie/corps" className="text-gray-600 hover:text-rose-500 transition">🌿 Corps</a>
            </nav>
            <nav className="md:hidden flex items-center gap-4 text-base">
              <a href="/categorie/cheveux" className="hover:text-rose-500">💇</a>
              <a href="/categorie/visage" className="hover:text-rose-500">✨</a>
              <a href="/categorie/corps" className="hover:text-rose-500">🌿</a>
            </nav>
          </div>
        </header>

        <main>{children}</main>

        {/* FOOTER */}
        <footer className="bg-gray-50 border-t border-gray-100 mt-16">
          <div className="max-w-6xl mx-auto px-4 py-12">
            <div className="grid md:grid-cols-3 gap-8">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <span>🌸</span>
                  <span className="font-bold text-rose-500">Guide-Soin.fr</span>
                </div>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Comparatifs et guides d&apos;achat beauté pour trouver les meilleurs produits soins.
                </p>
                <p className="text-xs text-gray-400 mt-3 italic">
                  En tant que partenaire Amazon et Affiliiz, nous percevons une commission sur les achats qualifiés, sans surcoût pour vous.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-gray-700 mb-3">Catégories</h4>
                <ul className="space-y-2 text-sm text-gray-500">
                  <li><a href="/categorie/cheveux" className="hover:text-rose-500 transition">💇 Soins Cheveux</a></li>
                  <li><a href="/categorie/visage" className="hover:text-rose-500 transition">✨ Soins Visage</a></li>
                  <li><a href="/categorie/corps" className="hover:text-rose-500 transition">🌿 Soins Corps</a></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-700 mb-3">Informations</h4>
                <ul className="space-y-2 text-sm text-gray-500">
                  <li><a href="/mentions-legales" className="hover:text-rose-500 transition">Mentions légales</a></li>
                  <li><a href="/confidentialite" className="hover:text-rose-500 transition">Politique de confidentialité</a></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-200 mt-8 pt-6 text-center text-xs text-gray-400">
              © 2026 Guide-Soin.fr — Tous droits réservés
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
