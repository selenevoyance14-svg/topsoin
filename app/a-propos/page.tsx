import type { Metadata } from "next";
import { Flower2, Search, MessageSquare, RefreshCw, ShieldCheck } from "lucide-react";

export const metadata: Metadata = {
  title: "À propos — Guide-Soin.fr",
  description: "Découvrez l'équipe et la méthode derrière Guide-Soin.fr : comment nous testons et comparons les produits beauté et soins.",
};

export default function APropos() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">À propos de Guide-Soin.fr</h1>

      <div className="prose prose-gray max-w-none space-y-8">
        <section>
          <div className="flex items-center gap-2 mb-3">
            <Flower2 size={20} className="text-rose-400" />
            <h2 className="text-xl font-semibold text-gray-800 m-0">Notre mission</h2>
          </div>
          <p className="text-gray-600">
            Guide-Soin.fr est né d'un constat simple : face aux centaines de produits beauté disponibles en pharmacie, en supermarché ou en ligne, il est difficile de savoir lequel choisir. Notre mission est de vous aider à trouver les meilleurs soins pour vos cheveux, votre visage et votre corps, grâce à des comparatifs honnêtes et détaillés.
          </p>
          <p className="text-gray-600">
            Nous sommes une équipe de passionnées de beauté et de soins, basée en France. Nous testons, analysons et comparons les produits du quotidien pour vous faire gagner du temps et de l'argent. Pas de publicité déguisée, pas de classements payants — juste des recommandations sincères.
          </p>
        </section>

        <section>
          <div className="flex items-center gap-2 mb-3">
            <Search size={20} className="text-rose-400" />
            <h2 className="text-xl font-semibold text-gray-800 m-0">Notre méthode de sélection</h2>
          </div>
          <p className="text-gray-600">
            Chaque comparatif publié sur Guide-Soin.fr suit une méthodologie rigoureuse en plusieurs étapes :
          </p>
          <ul className="text-gray-600 space-y-2">
            <li><strong>Recherche approfondie</strong> — Nous étudions les compositions (INCI), les certifications (bio, cruelty-free, dermatologiquement testé) et les avis consommateurs sur plusieurs plateformes.</li>
            <li><strong>Analyse des ingrédients</strong> — Nous vérifions la présence d'actifs reconnus par la communauté dermatologique (acide hyaluronique, niacinamide, rétinol, céramides, etc.) et l'absence d'ingrédients controversés.</li>
            <li><strong>Rapport qualité-prix</strong> — Un bon produit n'est pas forcément le plus cher. Nous intégrons systématiquement des alternatives accessibles dans nos sélections.</li>
            <li><strong>Retours utilisateurs</strong> — Nous croisons les avis de milliers d'utilisatrices et utilisateurs pour confirmer l'efficacité réelle des produits recommandés.</li>
            <li><strong>Mise à jour régulière</strong> — Les formulations changent, les prix évoluent, de nouveaux produits arrivent. Nos comparatifs sont mis à jour pour rester pertinents.</li>
          </ul>
        </section>

        <section>
          <div className="flex items-center gap-2 mb-3">
            <MessageSquare size={20} className="text-rose-400" />
            <h2 className="text-xl font-semibold text-gray-800 m-0">Ce que vous trouverez sur notre site</h2>
          </div>
          <p className="text-gray-600">
            Guide-Soin.fr couvre six univers beauté :
          </p>
          <ul className="text-gray-600 space-y-1">
            <li><strong>Cheveux</strong> — Shampoings, après-shampoings, masques, huiles capillaires, outils de coiffure</li>
            <li><strong>Visage</strong> — Crèmes hydratantes, sérums, nettoyants, exfoliants, soins coréens (K-Beauty)</li>
            <li><strong>Corps</strong> — Huiles, gommages, crèmes, soins solaires, anti-vergetures</li>
            <li><strong>Maquillage</strong> — Fonds de teint, mascaras, rouges à lèvres, palettes, primers</li>
            <li><strong>Parfum</strong> — Parfums femme et homme, eaux de toilette, coffrets, fragrances de niche</li>
            <li><strong>Homme</strong> — Rasage, barbe, soins visage homme, anti-âge, déodorants</li>
          </ul>
          <p className="text-gray-600">
            Pour chaque catégorie, nous publions des guides d'achat complets avec tableau comparatif, avis détaillé de notre top choix, alternatives par budget, et conseils d'utilisation.
          </p>
        </section>

        <section>
          <div className="flex items-center gap-2 mb-3">
            <ShieldCheck size={20} className="text-rose-400" />
            <h2 className="text-xl font-semibold text-gray-800 m-0">Indépendance et transparence</h2>
          </div>
          <p className="text-gray-600">
            Guide-Soin.fr est un site indépendant. Aucune marque ne paie pour apparaître dans nos comparatifs ou pour obtenir une meilleure note. Nos revenus proviennent de liens affiliés (Amazon Partenaires et Affiliiz) : si vous achetez un produit via l'un de nos liens, nous percevons une petite commission, sans aucun surcoût pour vous. C'est ce qui nous permet de maintenir le site gratuitement et de continuer à publier des guides de qualité.
          </p>
          <p className="text-gray-600">
            Cette affiliation n'influence jamais nos choix éditoriaux. Un produit mal noté reste mal noté, qu'il soit affilié ou non.
          </p>
        </section>

        <section>
          <div className="flex items-center gap-2 mb-3">
            <RefreshCw size={20} className="text-rose-400" />
            <h2 className="text-xl font-semibold text-gray-800 m-0">Nous contacter</h2>
          </div>
          <p className="text-gray-600">
            Une question, une suggestion, une demande de partenariat ? Écrivez-nous à{" "}
            <a href="mailto:bonsplansmania@gmail.com" className="text-rose-500 hover:underline">contact@guide-soin.fr</a>.
            Nous répondons à tous les messages.
          </p>
        </section>
      </div>
    </div>
  );
}
