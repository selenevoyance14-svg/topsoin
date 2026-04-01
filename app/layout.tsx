import type { Metadata } from "next";
import "./globals.css";
import { Flower2, Scissors, Sparkles, Leaf } from "lucide-react";

export const metadata: Metadata = {
  title: "GuideSoin — Les Meilleurs Produits Beauté & Soins",
  description: "Guides d'achat et comparatifs beauté : cheveux, visage, corps. Trouvez les meilleurs produits testés et approuvés.",
  keywords: "meilleur shampoing, crème visage, soin cheveux, comparatif beauté, guide achat beauté",
  icons: {
    icon: "/favicon.svg",
  },
  openGraph: {
    title: "GuideSoin — Les Meilleurs Produits Beauté",
    description: "Comparatifs et guides d'achat beauté pour choisir les meilleurs soins.",
    type: "website",
    locale: "fr_FR",
    url: "https://guide-soin.fr",
  },
};


export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5064203547863113"
          crossOrigin="anonymous"
        />
      </head>
      <body>
        {/* HEADER */}
        <header className="sticky top-0 z-50 bg-white border-b border-rose-100 shadow-sm">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2">
              <Flower2 size={22} className="text-rose-400" />
              <span className="text-xl font-bold text-rose-500">Top</span>
              <span className="text-xl font-bold text-gray-800">Soin</span>
            </a>
            <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
              <a href="/categorie/cheveux" className="flex items-center gap-1.5 text-gray-600 hover:text-rose-500 transition">
                <Scissors size={15} /> Cheveux
              </a>
              <a href="/categorie/visage" className="flex items-center gap-1.5 text-gray-600 hover:text-rose-500 transition">
                <Sparkles size={15} /> Visage
              </a>
              <a href="/categorie/corps" className="flex items-center gap-1.5 text-gray-600 hover:text-rose-500 transition">
                <Leaf size={15} /> Corps
              </a>
            </nav>
            <nav className="md:hidden flex items-center gap-4">
              <a href="/categorie/cheveux" className="text-gray-600 hover:text-rose-500"><Scissors size={20} /></a>
              <a href="/categorie/visage" className="text-gray-600 hover:text-rose-500"><Sparkles size={20} /></a>
              <a href="/categorie/corps" className="text-gray-600 hover:text-rose-500"><Leaf size={20} /></a>
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
                  <Flower2 size={18} className="text-rose-400" />
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
                  <li><a href="/categorie/cheveux" className="flex items-center gap-1.5 hover:text-rose-500 transition"><Scissors size={13} /> Soins Cheveux</a></li>
                  <li><a href="/categorie/visage" className="flex items-center gap-1.5 hover:text-rose-500 transition"><Sparkles size={13} /> Soins Visage</a></li>
                  <li><a href="/categorie/corps" className="flex items-center gap-1.5 hover:text-rose-500 transition"><Leaf size={13} /> Soins Corps</a></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-700 mb-3">Informations</h4>
                <ul className="space-y-2 text-sm text-gray-500">
                  <li><a href="/mentions-legales" className="hover:text-rose-500 transition">Mentions légales</a></li>
                  <li><a href="/confidentialite" className="hover:text-rose-500 transition">Politique de confidentialité</a></li>
                  <li className="pt-1">
                    <a href="mailto:bonsplansmania@gmail.com" className="hover:text-rose-500 transition">contact@guide-soin.fr</a>
                    <span className="block text-xs text-gray-400 mt-0.5">Partenariats &amp; collaborations</span>
                  </li>
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
