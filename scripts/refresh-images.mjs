// scripts/refresh-images.mjs
// Récupère via PA-API GetItems les images valides pour une liste d'ASIN cassés,
// puis met à jour le champ image dans data.jsx (sans rien casser d'autre).
//
// Usage: node scripts/refresh-images.mjs B07R5VVGDF B0BVNBR7Y2 ...

import { createHash, createHmac } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const HOST = "webservices.amazon.fr";
const REGION = "eu-west-1";
const SERVICE = "ProductAdvertisingAPI";
const PATH = "/paapi5/getitems";
const TARGET = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems";

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
    const headers = {
        "host": HOST, "x-amz-date": amzDate, "x-amz-target": TARGET,
        "content-encoding": "amz-1.0", "content-type": "application/json; charset=UTF-8",
    };
    const sortedHeaders = Object.keys(headers).sort();
    const canonicalHeaders = sortedHeaders.map(k => `${k}:${headers[k]}\n`).join("");
    const signedHeaders = sortedHeaders.join(";");
    const canonicalRequest = ["POST", PATH, "", canonicalHeaders, signedHeaders, payloadHash].join("\n");
    const credentialScope = `${dateStamp}/${REGION}/${SERVICE}/aws4_request`;
    const stringToSign = ["AWS4-HMAC-SHA256", amzDate, credentialScope,
        createHash("sha256").update(canonicalRequest).digest("hex")].join("\n");
    const kDate = createHmac("sha256", `AWS4${env.AMAZON_SECRET_KEY}`).update(dateStamp).digest();
    const kRegion = createHmac("sha256", kDate).update(REGION).digest();
    const kService = createHmac("sha256", kRegion).update(SERVICE).digest();
    const kSigning = createHmac("sha256", kService).update("aws4_request").digest();
    const signature = createHmac("sha256", kSigning).update(stringToSign).digest("hex");
    const authorization = `AWS4-HMAC-SHA256 Credential=${env.AMAZON_ACCESS_KEY}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;
    return { url: `https://${HOST}${PATH}`, headers: { ...headers, Authorization: authorization }, body };
}

async function getItems(env, asins) {
    const payload = {
        PartnerTag: env.AMAZON_PARTNER_TAG,
        PartnerType: "Associates",
        Marketplace: env.AMAZON_MARKETPLACE || "www.amazon.fr",
        ItemIds: asins,
        Resources: ["Images.Primary.Large", "ItemInfo.Title", "Offers.Listings.Price"],
    };
    const { url, headers, body } = sign(env, payload);
    const res = await fetch(url, { method: "POST", headers, body });
    const text = await res.text();
    if (!res.ok) throw new Error(`PA-API ${res.status}: ${text.slice(0, 400)}`);
    return JSON.parse(text);
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function main() {
    const asins = process.argv.slice(2);
    if (!asins.length) { console.error("Donne des ASIN en argument"); process.exit(1); }
    const env = await loadEnv();
    const imageByAsin = {};
    for (let i = 0; i < asins.length; i += 10) {
        const batch = asins.slice(i, i + 10);
        let attempt = 0;
        while (attempt < 5) {
            try {
                const data = await getItems(env, batch);
                for (const it of data?.ItemsResult?.Items || []) {
                    const img = it?.Images?.Primary?.Large?.URL;
                    if (img) imageByAsin[it.ASIN] = img;
                }
                const errs = data?.Errors || [];
                for (const e of errs) console.log("  ⚠️", e.Code, e.Message);
                break;
            } catch (e) {
                attempt++;
                const wait = 2000 * attempt;
                console.log(`  retry ${attempt} (${e.message.slice(0, 80)}) — attente ${wait}ms`);
                await sleep(wait);
            }
        }
        await sleep(1500);
    }
    console.log(`\n✅ Images récupérées : ${Object.keys(imageByAsin).length}/${asins.length}`);

    // Met à jour data.jsx par remplacement ciblé image pour chaque ASIN
    const dataPath = join(process.cwd(), "data.jsx");
    let text = await readFile(dataPath, "utf-8");
    let updated = 0;
    for (const [asin, img] of Object.entries(imageByAsin)) {
        // bloc d'objet contenant cet ASIN
        const re = new RegExp(`(\\{[^{}]*?"asin":\\s*"${asin}"[^{}]*?"image":\\s*")[^"]*(")`);
        const re2 = new RegExp(`(\\{[^{}]*?"image":\\s*")[^"]*("[^{}]*?"asin":\\s*"${asin}")`);
        if (re.test(text)) { text = text.replace(re, `$1${img}$2`); updated++; }
        else if (re2.test(text)) { text = text.replace(re2, `$1${img}$2`); updated++; }
        else console.log("  ⚠️ ASIN non trouvé dans data.jsx pour maj:", asin);
    }
    await writeFile(dataPath, text);
    console.log(`💾 data.jsx mis à jour : ${updated} images remplacées`);
    // Affiche les ASIN sans image (à remplacer manuellement)
    const missing = asins.filter(a => !imageByAsin[a]);
    if (missing.length) console.log("❌ Toujours sans image (produit probablement retiré):", missing.join(", "));
}

main().catch(e => { console.error(e); process.exit(1); });
