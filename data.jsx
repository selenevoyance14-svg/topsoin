// data.jsx — Maison Léa: Amazon affiliate edition
const COLLECTIONS = [
  { id:'lingerie',   label:'Lingerie',          fr:'Soutiens-gorge, culottes, bodies', count:148 },
  { id:'nuit',       label:'Nuit & loungewear', fr:'Nuisettes, peignoirs, kimonos',     count:62  },
  { id:'sensualite', label:'Sensualité',        fr:'Accessoires intimes & jeux',         count:94, adult:true },
  { id:'erotisme',   label:'Érotisme',          fr:'Lecture, jeux coquins, fantaisies',  count:46, adult:true },
  { id:'soins',      label:'Soins intimes',     fr:'Lubrifiants, huiles, bougies',       count:38  },
  { id:'cadeaux',    label:'Coffrets',          fr:'Édition limitée, idées cadeaux',    count:24  },
];

// Amazon-style products with rating, prime, deal info
const PRODUCTS = [
  { id:1, cat:'lingerie',   name:'Ensemble dentelle Calais',        sub:'Marque · Maison Lejaby',        price:'128€', was:'159€', off:'-19%', rating:4.6, reviews:1284, prime:true,  tag:'COUP DE ♥', color:'#8b1d2c', asin:'B0CG7XYZ12' },
  { id:2, cat:'nuit',       name:'Kimono soie lavée',               sub:'Marque · Aubade',                price:'195€', was:'249€', off:'-22%', rating:4.8, reviews:412,  prime:true,  tag:'AMAZON\u2019S CHOICE', color:'#3a2e1f', asin:'B0BX9KL45' },
  { id:3, cat:'sensualite', name:'Vibromasseur silicone USB',       sub:'Marque · Womanizer Premium 2',   price:'89€',  was:'149€', off:'-40%', rating:4.7, reviews:8924, prime:true,  tag:'BEST-SELLER', color:'#1a1a1a', asin:'B09QW1234' },
  { id:4, cat:'lingerie',   name:'Body tulle plumetis dos nu',      sub:'Marque · Etam Sélection',        price:'82€',  was:'',     off:'',     rating:4.4, reviews:340,  prime:true,  tag:'',           color:'#d4a16a', asin:'B0DKZL567' },
  { id:5, cat:'soins',      name:'Huile de massage sensorielle',    sub:'Marque · Bijoux Indiscrets',     price:'34€',  was:'42€',  off:'-19%', rating:4.5, reviews:687,  prime:true,  tag:'',           color:'#c9a961', asin:'B07FP9876' },
  { id:6, cat:'cadeaux',    name:'Coffret découverte trio',         sub:'Marque · Smile Makers',          price:'149€', was:'179€', off:'-17%', rating:4.9, reviews:215,  prime:true,  tag:'IDÉE CADEAU',color:'#5b1a26', asin:'B0CXYZ333' },
  { id:7, cat:'lingerie',   name:'Triangle balconnet ivoire',       sub:'Marque · Simone Pérèle',         price:'69€',  was:'',     off:'',     rating:4.3, reviews:528,  prime:false, tag:'',           color:'#efe6d6', asin:'B0BDR4422' },
  { id:8, cat:'sensualite', name:'Foulard satin & plumeau set',     sub:'Marque · Liebe Seele',           price:'58€',  was:'72€',  off:'-19%', rating:4.6, reviews:1130, prime:true,  tag:'NOUVEAU',    color:'#2a1a1f', asin:'B0DAA9911' },
  { id:9, cat:'erotisme',   name:'Cartes de jeu pour couple',       sub:'Marque · Tease & Please',        price:'19€',  was:'24€',  off:'-21%', rating:4.5, reviews:2340, prime:true,  tag:'BEST-SELLER', color:'#6a1a2e', asin:'B0FUNCARDS' },
  { id:10,cat:'erotisme',   name:'Anthologie érotique illustrée',   sub:'Éditions La Musardine',          price:'29€',  was:'',     off:'',     rating:4.7, reviews:412,  prime:true,  tag:'COUP DE ♥',   color:'#3a1a26', asin:'B0FBOOK009' },
  { id:11,cat:'erotisme',   name:'Bandeau soie & menottes velours', sub:'Marque · Bijoux Indiscrets',     price:'42€',  was:'55€',  off:'-24%', rating:4.6, reviews:890,  prime:true,  tag:'',            color:'#1f1015', asin:'B0FCUFF456' },
];

// Why this site exists
const PROMISES = [
  { kicker:'01', title:'Sélection Léa, achat Amazon', body:'Léa teste, sélectionne et classe. Vous achetez directement chez Amazon, en toute sécurité.' },
  { kicker:'02', title:'Livraison Prime, prix Amazon', body:'Mêmes prix qu\u2019Amazon, livraison Prime, retours simples. Aucun surcoût pour vous.' },
  { kicker:'03', title:'Transparence totale',          body:'Liens affiliés signalés clairement. Une commission Amazon nous rémunère, jamais vous.' },
  { kicker:'04', title:'Discrétion garantie',          body:'Amazon expédie en colis neutre. Vous restez en maison de confiance.' },
];

const EDITORIAL = {
  kicker:'LE GUIDE · ÉDITION N°12',
  title:'Mes 7 indispensables intimes.',
  excerpt:'Léa partage sa sélection du moment : 7 pièces testées et approuvées, du soutien-gorge sans armatures au vibromasseur silencieux. Tous disponibles sur Amazon, livrés en 24h.',
  read:'8 min'
};

const STATS = [
  { k:'420+', v:'produits sélectionnés' },
  { k:'4,6★', v:'note moyenne des picks' },
  { k:'24h',  v:'livraison Prime' },
  { k:'100%', v:'liens affiliés signalés' },
];

Object.assign(window, { COLLECTIONS, PRODUCTS, PROMISES, EDITORIAL, STATS });
