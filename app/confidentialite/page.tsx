import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Politique de confidentialité — Guide-Soin.fr",
  description: "Politique de confidentialité et gestion des données personnelles sur Guide-Soin.fr",
};

export default function Confidentialite() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Politique de confidentialité</h1>

      <div className="prose prose-gray max-w-none space-y-8">
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Données collectées</h2>
          <p className="text-gray-600">
            Guide-Soin.fr ne collecte aucune donnée personnelle directement.
            Nous n'avons pas de formulaire d'inscription ni de compte utilisateur.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Cookies et publicités</h2>
          <p className="text-gray-600">
            Ce site utilise Google AdSense pour afficher des publicités personnalisées.
            Google peut utiliser des cookies pour afficher des annonces basées sur vos visites précédentes.
            Vous pouvez désactiver la personnalisation des annonces en visitant les{" "}
            <a href="https://www.google.com/settings/ads" className="text-rose-500 hover:underline" target="_blank" rel="noopener noreferrer">
              paramètres des annonces Google
            </a>.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Liens affiliés</h2>
          <p className="text-gray-600">
            Ce site participe au programme Amazon Partenaires et au programme Affiliiz.
            Ces partenaires peuvent utiliser des cookies pour suivre les achats effectués via nos liens.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Vos droits (RGPD)</h2>
          <p className="text-gray-600">
            Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et de suppression
            de vos données. Pour exercer ces droits, contactez-nous à{" "}
            <a href="mailto:contact@guide-soin.fr" className="text-rose-500 hover:underline">contact@guide-soin.fr</a>.
          </p>
        </section>
      </div>
    </div>
  );
}
