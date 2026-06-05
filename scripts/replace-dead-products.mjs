// scripts/replace-dead-products.mjs
// Remplace les produits morts (ASIN délisté / image 404) par de vrais produits
// valides récupérés via PA-API SearchItems, en gardant id/cat/color.

import { createHash, createHmac } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const HOST = "webservices.amazon.fr", REGION = "eu-west-1", SERVICE = "ProductAdvertisingAPI";
const PATH = "/paapi5/searchitems";
const TARGET = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems";

async function loadEnv() {
    const raw = await readFile("/Users/Yann/Documents/oracle/bonsplansmania/.env", "utf-8");
    const env = {};
    for (const line of raw.split("\n")) {
        const m = line.match(/^([A-Z_][A-Z0-9_]*)=(.*)$/);
        if (m) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
    return env;
}
function sign(env, payload) {
    const amzDate = new Date().toISOString().replace(/[:-]|\.\d{3}/g, "");
    const dateStamp = amzDate.slice(0, 8);
    const body = JSON.stringify(payload);
    const payloadHash = createHash("sha256").update(body).digest("hex");
    const headers = { "host": HOST, "x-amz-date": amzDate, "x-amz-target": TARGET,
        "content-encoding": "amz-1.0", "content-type": "application/json; charset=UTF-8" };
    const sk = Object.keys(headers).sort();
    const canonicalHeaders = sk.map(k => `${k}:${headers[k]}\n`).join("");
    const signedHeaders = sk.join(";");
    const cr = ["POST", PATH, "", canonicalHeaders, signedHeaders, payloadHash].join("\n");
    const scope = `${dateStamp}/${REGION}/${SERVICE}/aws4_request`;
    const sts = ["AWS4-HMAC-SHA256", amzDate, scope, createHash("sha256").update(cr).digest("hex")].join("\n");
    const kDate = createHmac("sha256", `AWS4${env.AMAZON_SECRET_KEY}`).update(dateStamp).digest();
    const kRegion = createHmac("sha256", kDate).update(REGION).digest();
    const kService = createHmac("sha256", kRegion).update(SERVICE).digest();
    const kSigning = createHmac("sha256", kService).update("aws4_request").digest();
    const signature = createHmac("sha256", kSigning).update(sts).digest("hex");
    const authorization = `AWS4-HMAC-SHA256 Credential=${env.AMAZON_ACCESS_KEY}/${scope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;
    return { url: `https://${HOST}${PATH}`, headers: { ...headers, Authorization: authorization }, body };
}
async function searchItems(env, keywords, searchIndex) {
    const payload = {
        PartnerTag: env.AMAZON_PARTNER_TAG, PartnerType: "Associates",
        Marketplace: env.AMAZON_MARKETPLACE || "www.amazon.fr",
        Keywords: keywords, SearchIndex: searchIndex, ItemCount: 10,
        Resources: ["Images.Primary.Large", "ItemInfo.Title", "ItemInfo.ByLineInfo",
            "Offers.Listings.Price", "Offers.Listings.SavingBasis",
            "Offers.Listings.DeliveryInfo.IsPrimeEligible"],
    };
    const { url, headers, body } = sign(env, payload);
    const res = await fetch(url, { method: "POST", headers, body });
    const text = await res.text();
    if (!res.ok) throw new Error(`${res.status}: ${text.slice(0, 200)}`);
    return JSON.parse(text);
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Slots morts à remplacer : id existant + mots-clés + index
const SLOTS = [
    { id: 151, cat: "erotisme", color: "#3a1a26", kw: "jeu carte couple coquin", idx: "All" },
    { id: 169, cat: "lingerie", color: "#8b1d2c", kw: "ensemble lingerie dentelle femme", idx: "Apparel" },
    { id: 170, cat: "lingerie", color: "#8b1d2c", kw: "body dentelle femme lingerie", idx: "Apparel" },
    { id: 171, cat: "nuit", color: "#3a2e1f", kw: "pyjama satin femme manches longues", idx: "Apparel" },
    { id: 172, cat: "nuit", color: "#3a2e1f", kw: "robe de chambre femme peignoir polaire", idx: "Apparel" },
    { id: 173, cat: "sensualite", color: "#1a1a1a", kw: "stimulateur clitoridien femme", idx: "HealthPersonalCare" },
    { id: 174, cat: "sensualite", color: "#1a1a1a", kw: "satisfyer stimulateur femme", idx: "HealthPersonalCare" },
    { id: 175, cat: "soins", color: "#c9a961", kw: "soin lavant intime doux femme", idx: "HealthPersonalCare" },
    { id: 176, cat: "soins", color: "#c9a961", kw: "lubrifiant intime chauffant", idx: "HealthPersonalCare" },
    { id: 177, cat: "cadeaux", color: "#b07d2b", kw: "coffret cadeau femme bien-etre bougie", idx: "All" },
    { id: 178, cat: "cadeaux", color: "#b07d2b", kw: "coffret romance couple bougie massage", idx: "All" },
];

function priceStr(listing) {
    const p = listing?.Price?.DisplayAmount;
    return p || "";
}

async function main() {
    const env = await loadEnv();
    const dataPath = join(process.cwd(), "data.jsx");
    let text = await readFile(dataPath, "utf-8");
    const existing = eval(text.match(/const PRODUCTS = (\[[\s\S]*?\n\]);/)[1]);
    const usedAsins = new Set(existing.map(p => p.asin));
    const oldById = Object.fromEntries(existing.map(p => [p.id, p]));

    const onlyIds = process.argv.slice(2).map(Number).filter(Boolean);
    const slots = onlyIds.length ? SLOTS.filter(s => onlyIds.includes(s.id)) : SLOTS;
    const replacements = {};
    for (const slot of slots) {
        let ok = false;
        for (let attempt = 0; attempt < 4 && !ok; attempt++) {
            try {
                const data = await searchItems(env, slot.kw, slot.idx);
                const items = data?.SearchResult?.Items || [];
                for (const it of items) {
                    const img = it?.Images?.Primary?.Large?.URL;
                    const listing = it?.Offers?.Listings?.[0];
                    const price = priceStr(listing);
                    if (!img || usedAsins.has(it.ASIN)) continue;
                    usedAsins.add(it.ASIN);
                    const old = oldById[slot.id];
                    const brand = it?.ItemInfo?.ByLineInfo?.Brand?.DisplayValue || "";
                    replacements[slot.id] = {
                        id: slot.id, cat: slot.cat,
                        name: (it?.ItemInfo?.Title?.DisplayValue || old.name).slice(0, 90),
                        sub: brand ? `Marque · ${brand}` : old.sub,
                        price, was: "", off: "",
                        rating: old.rating, reviews: old.reviews,
                        prime: !!listing?.DeliveryInfo?.IsPrimeEligible,
                        tag: "", color: slot.color, asin: it.ASIN, image: img,
                    };
                    console.log(`✅ ${slot.id} ${slot.cat}: ${it.ASIN} — ${replacements[slot.id].name.slice(0,45)}`);
                    ok = true;
                    break;
                }
                if (!ok) { console.log(`  ⚠️ ${slot.id} ${slot.cat}: aucun résultat valide, retry`); }
            } catch (e) {
                console.log(`  retry ${slot.id} (${e.message.slice(0, 60)})`);
                await sleep(2500 * (attempt + 1));
            }
            await sleep(1800);
        }
        if (!ok) console.log(`❌ ${slot.id} ${slot.cat}: échec`);
    }

    // Splice: remplace chaque objet produit (par id) dans data.jsx
    let updated = 0;
    for (const [id, np] of Object.entries(replacements)) {
        const re = new RegExp(`\\{[^{}]*?"id":\\s*${id}\\b[^{}]*?\\}`);
        if (!re.test(text)) { console.log("  ⚠️ bloc id non trouvé:", id); continue; }
        const json = JSON.stringify(np, null, 2).split("\n").map((l, i) => i === 0 ? l : "  " + l).join("\n");
        text = text.replace(re, json);
        updated++;
    }
    await writeFile(dataPath, text);
    console.log(`\n💾 data.jsx : ${updated} produits remplacés.`);
}
main().catch(e => { console.error(e); process.exit(1); });
