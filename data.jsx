// data.jsx — Maison Léa: Amazon affiliate edition (généré automatiquement)
const AMAZON_DATA_UPDATED_AT = "2026-08-08T14:55:18.490Z";
const COLLECTIONS = [
  { id:'lingerie',   label:'Lingerie',          fr:'Soutiens-gorge, culottes, bodies', count: 0 },
  { id:'nuit',       label:'Nuit & loungewear', fr:'Nuisettes, peignoirs, kimonos',     count: 0 },
  { id:'sensualite', label:'Sensualité',        fr:'Accessoires intimes & jeux',         count: 0, adult:true },
  { id:'erotisme',   label:'Érotisme',          fr:'Lecture, jeux coquins, fantaisies',  count: 0, adult:true },
  { id:'soins',      label:'Soins intimes',     fr:'Lubrifiants, huiles, bougies',       count: 0 },
  { id:'cadeaux',    label:'Coffrets',          fr:'Édition limitée, idées cadeaux',    count: 0 },
];

const PRODUCTS = [];

const PROMISES = [
  { kicker:'01', title:'Sélection éditoriale', body:'Maison Léa compare et organise des produits disponibles sur Amazon selon des critères utiles.' },
  { kicker:'02', title:'Prix vérifiés automatiquement', body:'Les prix sont affichés uniquement lorsqu\u2019ils ont été actualisés récemment via l\u2019API Amazon.' },
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
  { num:'0', label:'produits sélectionnés' },
  { num:'6', label:'territoires' },
  { num:'24h', label:'fraîcheur maximale des prix' },
  { num:'100%', label:'liens affiliés signalés' },
];

Object.assign(window, { AMAZON_DATA_UPDATED_AT, COLLECTIONS, PRODUCTS, PROMISES, EDITORIAL, STATS });
