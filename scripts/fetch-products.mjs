// scripts/fetch-products.mjs
// Récupère les produits Amazon via Creators API et génère data.jsx.
//
// Usage:
//   node scripts/fetch-products.mjs            → fait toutes les catégories
//   node scripts/fetch-products.mjs --test     → test rapide avec une seule recherche
//
// Variables d'env requises :
//   AMAZON_CREATORS_CREDENTIAL_ID
//   AMAZON_CREATORS_CREDENTIAL_SECRET
//   AMAZON_CREATORS_CREDENTIAL_VERSION (3.2 pour l'Europe)
//   AMAZON_PARTNER_TAG

import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

// ────────────────────────────────────────────────────────────────────────────
// Charge d'abord l'environnement du processus, puis les .env locaux disponibles.
async function loadEnv() {
    const env = { ...process.env };
    for (const envPath of [join(process.cwd(), ".env"), "/Users/Yann/Documents/oracle/bonsplansmania/.env"]) {
        try {
            const raw = await readFile(envPath, "utf-8");
            for (const line of raw.split("\n")) {
                const m = line.match(/^([A-Z_][A-Z0-9_]*)=(.*)$/);
                if (m && !env[m[1]]) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
            }
        } catch {
            // Fichier facultatif : les secrets CI viennent de l'environnement.
        }
    }
    return env;
}

function creatorsConfig(env) {
    const version = env.AMAZON_CREATORS_CREDENTIAL_VERSION || "3.2";
    const tokenUrl = version.startsWith("3.")
        ? "https://api.amazon.co.uk/auth/o2/token"
        : "https://creatorsapi.auth.eu-south-2.amazoncognito.com/oauth2/token";
    return { version, tokenUrl };
}

async function getAccessToken(env) {
    const id = env.AMAZON_CREATORS_CREDENTIAL_ID;
    const secret = env.AMAZON_CREATORS_CREDENTIAL_SECRET;
    const { version, tokenUrl } = creatorsConfig(env);
    const isV3 = version.startsWith("3.");
    const headers = { "content-type": isV3 ? "application/json" : "application/x-www-form-urlencoded" };
    const body = isV3
        ? JSON.stringify({ grant_type: "client_credentials", client_id: id, client_secret: secret, scope: "creatorsapi::default" })
        : new URLSearchParams({ grant_type: "client_credentials", client_id: id, client_secret: secret, scope: "creatorsapi/default" });
    const res = await fetch(tokenUrl, { method: "POST", headers, body });
    const data = await res.json();
    if (!res.ok || !data.access_token) throw new Error(`Creators API auth ${res.status}: ${JSON.stringify(data).slice(0, 300)}`);
    return { token: data.access_token, version };
}

async function searchItems(env, auth, { keywords, searchIndex = "All", itemCount = 10 }) {
    const payload = {
        partnerTag: env.AMAZON_PARTNER_TAG,
        marketplace: env.AMAZON_MARKETPLACE || "www.amazon.fr",
        keywords,
        searchIndex,
        itemCount,
        resources: [
            "images.primary.large",
            "itemInfo.title",
            "itemInfo.byLineInfo",
            "offersV2.listings.price",
            "offersV2.listings.availability",
        ],
    };
    const authorization = auth.version.startsWith("2.")
        ? `Bearer ${auth.token}, Version ${auth.version}`
        : `Bearer ${auth.token}`;
    const res = await fetch("https://creatorsapi.amazon/catalog/v1/searchItems", {
        method: "POST",
        headers: { authorization, "content-type": "application/json", "x-marketplace": payload.marketplace },
        body: JSON.stringify(payload),
    });
    const text = await res.text();
    if (!res.ok) {
        throw new Error(`Creators API ${res.status}: ${text.slice(0, 500)}`);
    }
    return JSON.parse(text);
}

// ────────────────────────────────────────────────────────────────────────────
async function main() {
    const env = await loadEnv();
    if (!env.AMAZON_CREATORS_CREDENTIAL_ID || !env.AMAZON_CREATORS_CREDENTIAL_SECRET) {
        console.error("❌ Identifiants Creators API manquants. Créez-les dans Associates Central > Outils > Creators API.");
        process.exit(1);
    }
    if (!env.AMAZON_PARTNER_TAG) throw new Error("AMAZON_PARTNER_TAG manquant");
    const auth = await getAccessToken(env);
    console.log("🔑 Creators API connectée · Tag:", env.AMAZON_PARTNER_TAG, "· Version:", auth.version);

    if (process.argv.includes("--test")) {
        console.log("\n🧪 Test : recherche 'soutien-gorge dentelle'");
        const data = await searchItems(env, auth, { keywords: "soutien-gorge dentelle", searchIndex: "Apparel", itemCount: 3 });
        const items = data?.searchResult?.items || [];
        console.log(`✅ API OK — ${items.length} produits reçus`);
        for (const it of items.slice(0, 3)) {
            console.log(`  · ${it.asin} — ${(it.itemInfo?.title?.displayValue || "").slice(0, 70)} — ${it.offersV2?.listings?.[0]?.price?.money?.displayAmount || "—"}`);
        }
        return;
    }

    // Catégories Maison Léa
    const CATEGORIES = [
        { id: "lingerie", keywords: ["ensemble dentelle femme", "soutien-gorge balconnet", "body dentelle", "bralette sans armature", "culotte taille haute femme"], searchIndex: "Apparel", color: "#8b1d2c", count: 13 },
        { id: "nuit", keywords: ["nuisette satin", "kimono satin femme", "peignoir femme", "pyjama femme élégant"], searchIndex: "Apparel", color: "#3a2e1f", count: 12 },
        { id: "sensualite", keywords: ["vibromasseur silicone", "stimulateur intime", "anneau vibrant couple"], searchIndex: "HealthPersonalCare", color: "#1a1a1a", count: 11 },
        { id: "erotisme", keywords: ["jeu couple coquin", "carte couple sexy", "livre couple intimité"], searchIndex: "All", color: "#3a1a26", count: 11 },
        { id: "soins", keywords: ["lubrifiant intime naturel", "huile massage sensorielle", "bougie massage", "soin corps femme"], searchIndex: "HealthPersonalCare", color: "#c9a961", count: 11 },
        { id: "cadeaux", keywords: ["coffret lingerie cadeau", "coffret massage couple", "coffret bien être femme", "cadeau couple"], searchIndex: "All", color: "#5b1a26", count: 10 },
    ];

    const allProducts = [];
    let id = 1;

    for (const cat of CATEGORIES) {
        console.log(`\n📦 ${cat.id} — recherches : ${cat.keywords.join(" / ")}`);
        const seen = new Set();
        for (const kw of cat.keywords) {
            if (allProducts.filter(p => p.cat === cat.id).length >= cat.count) break;
            try {
                const data = await searchItems(env, auth, { keywords: kw, searchIndex: cat.searchIndex, itemCount: 8 });
                const items = data?.searchResult?.items || [];
                for (const it of items) {
                    if (allProducts.filter(p => p.cat === cat.id).length >= cat.count) break;
                    if (seen.has(it.asin)) continue;
                    seen.add(it.asin);
                    const title = it.itemInfo?.title?.displayValue;
                    const image = it.images?.primary?.large?.url;
                    const offer = it.offersV2?.listings?.[0];
                    const priceDisplay = offer?.price?.money?.displayAmount || "";
                    const priceAmount = offer?.price?.money?.amount;
                    const wasDisplay = offer?.price?.savingBasis?.money?.displayAmount || "";
                    const wasAmount = offer?.price?.savingBasis?.money?.amount;
                    // OffersV2 ne fournit plus l'éligibilité Prime. Ne jamais l'inventer.
                    const prime = false;
                    if (!title || !image) continue;
                    const brand = it.itemInfo?.byLineInfo?.brand?.displayValue || it.itemInfo?.byLineInfo?.manufacturer?.displayValue || "";

                    let off = "";
                    if (priceDisplay && wasDisplay && priceAmount && wasAmount && wasAmount > priceAmount) {
                        const pct = Math.round((1 - priceAmount / wasAmount) * 100);
                        if (pct >= 5) off = `-${pct}%`;
                    }

                    allProducts.push({
                        id: id++,
                        cat: cat.id,
                        name: title.length > 60 ? title.slice(0, 57) + "..." : title,
                        sub: brand ? `Marque · ${brand}` : "Sélection Léa",
                        price: priceDisplay || "",
                        was: wasDisplay || "",
                        off,
                        rating: 0,
                        reviews: 0,
                        prime,
                        tag: "",
                        color: cat.color,
                        asin: it.asin,
                        image,
                        url: it.detailPageURL || `https://www.amazon.fr/dp/${it.asin}?tag=${env.AMAZON_PARTNER_TAG}`,
                    });
                    console.log(`  ✓ ${it.asin} — ${title.slice(0, 55)} — ${priceDisplay || "no price"}`);
                }
            } catch (e) {
                console.error(`  ⚠ ${kw}: ${e.message.slice(0, 100)}`);
            }
        }
    }

    if (allProducts.length === 0) {
        throw new Error("Aucun produit Amazon reçu : data.jsx est conservé et la publication est annulée.");
    }

    console.log(`\n📝 ${allProducts.length} produits collectés. Génération de data.jsx...`);

    const generatedAt = new Date().toISOString();
    const dataJsx = `// data.jsx — Maison Léa: Amazon affiliate edition (généré automatiquement)
const AMAZON_DATA_UPDATED_AT = ${JSON.stringify(generatedAt)};
const COLLECTIONS = [
  { id:'lingerie',   label:'Lingerie',          fr:'Soutiens-gorge, culottes, bodies', count: ${allProducts.filter(p => p.cat === "lingerie").length} },
  { id:'nuit',       label:'Nuit & loungewear', fr:'Nuisettes, peignoirs, kimonos',     count: ${allProducts.filter(p => p.cat === "nuit").length} },
  { id:'sensualite', label:'Sensualité',        fr:'Accessoires intimes & jeux',         count: ${allProducts.filter(p => p.cat === "sensualite").length}, adult:true },
  { id:'erotisme',   label:'Érotisme',          fr:'Lecture, jeux coquins, fantaisies',  count: ${allProducts.filter(p => p.cat === "erotisme").length}, adult:true },
  { id:'soins',      label:'Soins intimes',     fr:'Lubrifiants, huiles, bougies',       count: ${allProducts.filter(p => p.cat === "soins").length} },
  { id:'cadeaux',    label:'Coffrets',          fr:'Édition limitée, idées cadeaux',    count: ${allProducts.filter(p => p.cat === "cadeaux").length} },
];

const PRODUCTS = ${JSON.stringify(allProducts, null, 2)};

const PROMISES = [
  { kicker:'01', title:'Sélection éditoriale', body:'Maison Léa compare et organise des produits disponibles sur Amazon selon des critères utiles.' },
  { kicker:'02', title:'Prix vérifiés automatiquement', body:'Les prix sont affichés uniquement lorsqu\\u2019ils ont été actualisés récemment via l\\u2019API Amazon.' },
  { kicker:'03', title:'Transparence totale',          body:'Liens affiliés signalés clairement. Une commission Amazon nous rémunère, jamais vous.' },
  { kicker:'04', title:'Achat chez le vendeur',         body:'Vérifiez le vendeur, la livraison, les retours et la disponibilité directement sur Amazon.' },
];

const EDITORIAL = {
  kicker:'LE GUIDE · ÉDITION N°1',
  title:'Mes indispensables intimes.',
  excerpt:'Maison Léa partage une sélection éditoriale du moment, du soutien-gorge sans armatures au massage sensoriel. Prix et disponibilité sont confirmés sur Amazon.',
  read:'8 min'
};

const STATS = [
  { num:'${allProducts.length}', label:'produits sélectionnés' },
  { num:'6', label:'territoires' },
  { num:'24h', label:'fraîcheur maximale des prix' },
  { num:'100%', label:'liens affiliés signalés' },
];

Object.assign(window, { AMAZON_DATA_UPDATED_AT, COLLECTIONS, PRODUCTS, PROMISES, EDITORIAL, STATS });
`;

    await writeFile(join(process.cwd(), "data.jsx"), dataJsx);
    console.log(`✅ data.jsx régénéré (${allProducts.length} produits réels Amazon)`);
}

main().catch(e => {
    console.error("❌", e);
    process.exit(1);
});
