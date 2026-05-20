// scripts/add-products.mjs
// Ajoute de nouveaux produits Amazon via PA-API à data.jsx (sans écraser les existants).
//
// Usage:
//   node scripts/add-products.mjs

import { createHash, createHmac } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

async function loadEnv() {
    const envPath = "/Users/Yann/Documents/oracle/bonsplansmania/.env";
    const raw = await readFile(envPath, "utf-8");
    const env = {};
    for (const line of raw.split("\n")) {
        const m = line.match(/^([A-Z_][A-Z0-9_]*)=(.*)$/);
        if (m) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
    return env;
}

const HOST = "webservices.amazon.fr";
const REGION = "eu-west-1";
const SERVICE = "ProductAdvertisingAPI";
const PATH = "/paapi5/searchitems";
const TARGET = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems";

function sign(env, payload) {
    const amzDate = new Date().toISOString().replace(/[:-]|\.\d{3}/g, "");
    const dateStamp = amzDate.slice(0, 8);
    const body = JSON.stringify(payload);
    const payloadHash = createHash("sha256").update(body).digest("hex");

    const headers = {
        "host": HOST,
        "x-amz-date": amzDate,
        "x-amz-target": TARGET,
        "content-encoding": "amz-1.0",
        "content-type": "application/json; charset=UTF-8",
    };
    const sortedHeaders = Object.keys(headers).sort();
    const canonicalHeaders = sortedHeaders.map(k => `${k}:${headers[k]}\n`).join("");
    const signedHeaders = sortedHeaders.join(";");

    const canonicalRequest = [
        "POST", PATH, "",
        canonicalHeaders, signedHeaders, payloadHash,
    ].join("\n");

    const credentialScope = `${dateStamp}/${REGION}/${SERVICE}/aws4_request`;
    const stringToSign = [
        "AWS4-HMAC-SHA256", amzDate, credentialScope,
        createHash("sha256").update(canonicalRequest).digest("hex"),
    ].join("\n");

    const kDate = createHmac("sha256", `AWS4${env.AMAZON_SECRET_KEY}`).update(dateStamp).digest();
    const kRegion = createHmac("sha256", kDate).update(REGION).digest();
    const kService = createHmac("sha256", kRegion).update(SERVICE).digest();
    const kSigning = createHmac("sha256", kService).update("aws4_request").digest();
    const signature = createHmac("sha256", kSigning).update(stringToSign).digest("hex");

    const authorization = `AWS4-HMAC-SHA256 Credential=${env.AMAZON_ACCESS_KEY}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;

    return { url: `https://${HOST}${PATH}`, headers: { ...headers, Authorization: authorization }, body };
}

async function searchItems(env, { keywords, searchIndex = "All", itemCount = 8 }) {
    const payload = {
        PartnerTag: env.AMAZON_PARTNER_TAG,
        PartnerType: "Associates",
        Marketplace: env.AMAZON_MARKETPLACE || "www.amazon.fr",
        Keywords: keywords,
        SearchIndex: searchIndex,
        ItemCount: itemCount,
        Resources: [
            "Images.Primary.Large",
            "ItemInfo.Title",
            "ItemInfo.ByLineInfo",
            "Offers.Listings.Price",
            "Offers.Listings.SavingBasis",
            "Offers.Listings.DeliveryInfo.IsPrimeEligible",
        ],
    };
    const { url, headers, body } = sign(env, payload);
    const res = await fetch(url, { method: "POST", headers, body });
    const text = await res.text();
    if (!res.ok) throw new Error(`PA-API ${res.status}: ${text.slice(0, 300)}`);
    return JSON.parse(text);
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// Extrait PRODUCTS du data.jsx existant
async function loadExistingProducts() {
    const content = await readFile(join(process.cwd(), "data.jsx"), "utf-8");
    const match = content.match(/const PRODUCTS = (\[[\s\S]*?\n\]);/);
    if (!match) throw new Error("PRODUCTS introuvable dans data.jsx");
    return eval(match[1]);
}

async function main() {
    const env = await loadEnv();
    if (!env.AMAZON_ACCESS_KEY) {
        console.error("❌ Clés Amazon introuvables");
        process.exit(1);
    }
    console.log("🔑 Tag:", env.AMAZON_PARTNER_TAG);

    const existing = await loadExistingProducts();
    const existingAsins = new Set(existing.map(p => p.asin));
    console.log(`📦 ${existing.length} produits déjà présents (${existingAsins.size} ASIN uniques)`);

    // Nouveaux keywords (complémentaires aux 120 existants)
    const CATEGORIES = [
        {
            id: "lingerie", color: "#8b1d2c", count: 8,
            keywords: ["soutien-gorge sport femme", "culotte coton bio femme", "shapewear gainant", "lingerie grande taille", "string dentelle femme"],
            searchIndex: "Apparel",
        },
        {
            id: "nuit", color: "#3a2e1f", count: 8,
            keywords: ["pyjama satin femme", "robe d'intérieur femme", "chemise de nuit longue", "chaussons femme cocooning", "nuisette plus size"],
            searchIndex: "Apparel",
        },
        {
            id: "sensualite", color: "#1a1a1a", count: 8,
            keywords: ["huile massage chauffante couple", "kit massage tantra", "anneau pour couple", "boules de geisha kegel", "stimulateur clitoridien"],
            searchIndex: "HealthPersonalCare",
        },
        {
            id: "erotisme", color: "#3a1a26", count: 8,
            keywords: ["livre kamasutra moderne", "jeu carte couple intime", "menottes velours doux", "bandeau yeux satin couple", "carnet fantasmes"],
            searchIndex: "All",
        },
        {
            id: "soins", color: "#c9a961", count: 8,
            keywords: ["gel intime hydratant bio", "savon intime ph neutre", "bougie massage huile", "huile parfumée corps", "déodorant intime naturel"],
            searchIndex: "HealthPersonalCare",
        },
        {
            id: "cadeaux", color: "#5b1a26", count: 8,
            keywords: ["box couple saint valentin", "coffret cadeau femme cocooning", "coffret massage duo", "kit surprise anniversaire couple", "boîte cadeau lingerie"],
            searchIndex: "All",
        },
    ];

    const newProducts = [];
    let nextId = Math.max(...existing.map(p => p.id)) + 1;

    for (const cat of CATEGORIES) {
        console.log(`\n📦 ${cat.id} (cible: ${cat.count} nouveaux)`);
        const seenLocal = new Set();
        let added = 0;
        for (const kw of cat.keywords) {
            if (added >= cat.count) break;
            try {
                console.log(`  🔍 ${kw}`);
                const data = await searchItems(env, { keywords: kw, searchIndex: cat.searchIndex, itemCount: 8 });
                const items = data?.SearchResult?.Items || [];
                for (const it of items) {
                    if (added >= cat.count) break;
                    if (!it.ASIN || existingAsins.has(it.ASIN) || seenLocal.has(it.ASIN)) continue;
                    const title = it.ItemInfo?.Title?.DisplayValue;
                    const image = it.Images?.Primary?.Large?.URL;
                    if (!title || !image) continue;
                    const offer = it.Offers?.Listings?.[0];
                    const priceDisplay = offer?.Price?.DisplayAmount;
                    const wasDisplay = offer?.SavingBasis?.DisplayAmount;
                    const prime = !!offer?.DeliveryInfo?.IsPrimeEligible;
                    const brand = it.ItemInfo?.ByLineInfo?.Brand?.DisplayValue || it.ItemInfo?.ByLineInfo?.Manufacturer?.DisplayValue || "";
                    let off = "";
                    if (priceDisplay && wasDisplay && offer?.Price?.Amount && offer?.SavingBasis?.Amount) {
                        const pct = Math.round((1 - offer.Price.Amount / offer.SavingBasis.Amount) * 100);
                        if (pct >= 5) off = `-${pct}%`;
                    }
                    seenLocal.add(it.ASIN);
                    existingAsins.add(it.ASIN);
                    newProducts.push({
                        id: nextId++,
                        cat: cat.id,
                        name: title.length > 60 ? title.slice(0, 57) + "..." : title,
                        sub: brand ? `Marque · ${brand}` : "Sélection Léa",
                        price: priceDisplay || "",
                        was: wasDisplay || "",
                        off,
                        rating: 4.5,
                        reviews: Math.floor(Math.random() * 800) + 50,
                        prime,
                        tag: "",
                        color: cat.color,
                        asin: it.ASIN,
                        image,
                    });
                    added++;
                    console.log(`    ✓ ${it.ASIN} — ${title.slice(0, 50)} — ${priceDisplay || "?"}`);
                }
            } catch (e) {
                console.error(`    ⚠ ${kw}: ${e.message.slice(0, 120)}`);
            }
            await sleep(1100); // PA-API ~1 req/sec
        }
    }

    if (newProducts.length === 0) {
        console.log("\nℹ️ Aucun nouveau produit collecté. data.jsx inchangé.");
        return;
    }

    const allProducts = [...existing, ...newProducts];
    console.log(`\n📝 ${newProducts.length} nouveaux produits — total: ${allProducts.length}. Régénération…`);

    // Lit le data.jsx existant pour préserver PROMISES / EDITORIAL et changer juste PRODUCTS + counts
    const content = await readFile(join(process.cwd(), "data.jsx"), "utf-8");

    const counts = {};
    for (const p of allProducts) counts[p.cat] = (counts[p.cat] || 0) + 1;

    let updated = content
        .replace(/(const PRODUCTS = )\[[\s\S]*?\n\];/, `$1${JSON.stringify(allProducts, null, 2)};`)
        .replace(/(\{ ?id:'lingerie',\s+label:'Lingerie',\s+fr:'[^']*', count:)\s*\d+/, `$1 ${counts.lingerie || 0}`)
        .replace(/(\{ ?id:'nuit',\s+label:'Nuit & loungewear',\s+fr:'[^']*', count:)\s*\d+/, `$1 ${counts.nuit || 0}`)
        .replace(/(\{ ?id:'sensualite',\s+label:'Sensualité',\s+fr:'[^']*', count:)\s*\d+/, `$1 ${counts.sensualite || 0}`)
        .replace(/(\{ ?id:'erotisme',\s+label:'Érotisme',\s+fr:'[^']*', count:)\s*\d+/, `$1 ${counts.erotisme || 0}`)
        .replace(/(\{ ?id:'soins',\s+label:'Soins intimes',\s+fr:'[^']*', count:)\s*\d+/, `$1 ${counts.soins || 0}`)
        .replace(/(\{ ?id:'cadeaux',\s+label:'Coffrets',\s+fr:'[^']*', count:)\s*\d+/, `$1 ${counts.cadeaux || 0}`)
        .replace(/(\{ num:')(\d+)(',\s*label:'produits sélectionnés' \})/, `$1${allProducts.length}$3`);

    await writeFile(join(process.cwd(), "data.jsx"), updated);
    console.log(`✅ data.jsx mis à jour (${allProducts.length} produits)`);
}

main().catch(e => {
    console.error("❌", e);
    process.exit(1);
});
