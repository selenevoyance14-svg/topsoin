# Prix Amazon automatiques

Le site utilise désormais **Amazon Creators API**, qui remplace PA-API 5.0.

## Configuration requise

Dans Amazon Partenaires : **Outils > Creators API > Create Application > Create Credential**.

Conserver les trois valeurs affichées :

- Credential ID
- Credential Secret
- Credential Version (`3.2` en Europe)

Dans les secrets GitHub du dépôt `topsoin`, créer :

- `AMAZON_CREATORS_CREDENTIAL_ID`
- `AMAZON_CREATORS_CREDENTIAL_SECRET`

Dans les variables GitHub, créer si nécessaire :

- `AMAZON_CREATORS_CREDENTIAL_VERSION` (valeur fournie par Amazon)
- `AMAZON_PARTNER_TAG` (`lebrunnathali-21`)

Le workflow `.github/workflows/amazon-prices.yml` s'exécute chaque matin. Il récupère les produits, prix et images, reconstruit le site puis publie `data.jsx` si les données ont changé.

Les prix ne sont affichés sur le site que si leur mise à jour date de moins de 24 heures. Sinon, le site affiche « Voir le prix sur Amazon ».

Les secrets ne doivent jamais être ajoutés au dépôt ou dans du JavaScript envoyé au navigateur.
