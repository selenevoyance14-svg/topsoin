import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mentions légales — Guide-Soin.fr",
  description: "Mentions légales du site Guide-Soin.fr",
};

export default function MentionsLegales() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Mentions légales</h1>

      <div className="prose prose-gray max-w-none space-y-8">
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Éditeur du site</h2>
          <p className="text-gray-600">
            Le site Guide-Soin.fr est un site personnel édité à titre non professionnel.<br />
            Contact : <a href="mailto:contact@guide-soin.fr" className="text-rose-500 hover:underline">contact@guide-soin.fr</a>
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Hébergement</h2>
          <p className="text-gray-600">
            Ce site est hébergé par Vercel Inc., 340 Pine Street, Suite 701, San Francisco, CA 94104, États-Unis.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Propriété intellectuelle</h2>
          <p className="text-gray-600">
            L'ensemble des contenus présents sur ce site (textes, images, comparatifs) est protégé par le droit d'auteur.
            Toute reproduction sans autorisation est interdite.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Liens affiliés</h2>
          <p className="text-gray-600">
            Certains liens présents sur ce site sont des liens affiliés (programme Amazon Partenaires et Affiliiz).
            Si vous effectuez un achat via ces liens, nous percevons une commission sans coût supplémentaire pour vous.
            Cela nous permet de maintenir ce site gratuitement.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Responsabilité</h2>
          <p className="text-gray-600">
            Les informations présentes sur ce site sont fournies à titre indicatif.
            Nous nous efforçons de les maintenir à jour mais ne pouvons garantir leur exactitude à tout moment.
          </p>
        </section>
      </div>
    </div>
  );
}
