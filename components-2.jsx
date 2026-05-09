// components-2.jsx — Maison Léa: Amazon affiliate edition
const { useState: useState2 } = React;

// ─────────────────────────────────────────────────────────────────────────────
// Stars renderer
function Stars({ rating, size=12 }) {
  const full = Math.round(rating);
  return (
    <span style={{display:'inline-flex', alignItems:'center', gap:1, color:'#f5b800', fontSize:size}}>
      {[1,2,3,4,5].map(i => <span key={i} style={{opacity: i<=full?1:.25}}>★</span>)}
    </span>
  );
}

// Product visual placeholder
function ProductVisual({ color, label, tag, image, alt }) {
  return (
    <div style={{
      position:'relative', aspectRatio:'1/1', overflow:'hidden',
      background: image ? '#fff' : `linear-gradient(160deg, ${color} 0%, ${color}cc 100%)`,
      borderRadius:6
    }}>
      {image ? (
        <img src={image} alt={alt || label}
          style={{width:'100%', height:'100%', objectFit:'contain', padding:'8%'}}
          loading="lazy" />
      ) : (
        <div style={{
          position:'absolute', inset:0, opacity:.18,
          backgroundImage:'repeating-linear-gradient(135deg, transparent 0 14px, rgba(255,255,255,.5) 14px 15px)'
        }}/>
      )}
      {!image && (
        <div style={{
          position:'absolute', left:0, right:0, bottom:0, padding:'10px 12px',
          display:'flex', justifyContent:'space-between', alignItems:'flex-end',
          color:'rgba(255,255,255,.78)', fontSize:9, letterSpacing:'.12em',
          fontFamily:'Geist Mono, monospace'
        }}>
          <span>{label}</span>
          <span>◇</span>
        </div>
      )}
      {tag && (
        <div className="smallcaps" style={{
          position:'absolute', top:10, left:10, padding:'4px 8px',
          background:'var(--paper)', color:'var(--accent)',
          borderRadius:3, fontSize:9, fontWeight:600
        }}>{tag}</div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Illustrations line-art par catégorie (SVG cream sur fond tonal)
const ILLUS = {
  lingerie: (
    <g stroke="rgba(251,246,237,.85)" strokeWidth="1" fill="none" strokeLinecap="round" strokeLinejoin="round">
      <path d="M30 60 q20 -8 40 -8 q20 0 40 8" />
      <path d="M30 60 q-2 18 18 24 q12 4 22 -4" />
      <path d="M110 60 q2 18 -18 24 q-12 4 -22 -4" />
      <circle cx="50" cy="74" r="2" />
      <circle cx="90" cy="74" r="2" />
      <path d="M55 110 q15 6 30 0 q4 18 -2 30 q-13 6 -26 0 q-6 -12 -2 -30 z" />
      <path d="M70 116 v18" />
    </g>
  ),
  nuit: (
    <g stroke="rgba(251,246,237,.85)" strokeWidth="1" fill="none" strokeLinecap="round" strokeLinejoin="round">
      <path d="M40 35 v100 q0 8 6 10 l24 0" />
      <path d="M100 35 v100 q0 8 -6 10 l-24 0" />
      <path d="M40 35 q30 -8 60 0" />
      <path d="M70 45 v100" />
      <path d="M55 60 q15 4 30 0" />
      <path d="M50 90 q20 6 40 0" />
      <path d="M115 30 a14 14 0 1 0 4 22 a11 11 0 1 1 -4 -22 z" />
    </g>
  ),
  sensualite: (
    <g stroke="rgba(251,246,237,.85)" strokeWidth="1" fill="none" strokeLinecap="round" strokeLinejoin="round">
      <path d="M70 28 q-3 6 0 12 q3 -6 0 -12 z" fill="rgba(251,246,237,.4)" />
      <line x1="70" y1="40" x2="70" y2="58" />
      <rect x="58" y="58" width="24" height="58" rx="2" />
      <line x1="58" y1="70" x2="82" y2="70" />
      <path d="M30 80 q10 6 0 14 q-8 -6 0 -14 z" />
      <path d="M30 94 q-2 18 0 36" />
      <path d="M100 100 q12 12 24 6 q12 -8 6 14 q-12 6 -24 -6 q-12 -12 -6 -14 z" />
    </g>
  ),
  erotisme: (
    <g stroke="rgba(251,246,237,.85)" strokeWidth="1" fill="none" strokeLinecap="round" strokeLinejoin="round">
      <path d="M30 60 q40 -10 80 0 v60 q-40 -8 -80 0 z" />
      <line x1="70" y1="60" x2="70" y2="120" />
      <line x1="40" y1="74" x2="62" y2="72" />
      <line x1="40" y1="84" x2="62" y2="82" />
      <line x1="40" y1="94" x2="62" y2="92" />
      <line x1="78" y1="72" x2="100" y2="74" />
      <line x1="78" y1="82" x2="100" y2="84" />
      <line x1="78" y1="92" x2="100" y2="94" />
      <path d="M70 70 v40 l8 8 l-8 -4 l-8 4 l8 -8 z" stroke="#c66" />
      <path d="M115 30 q-4 14 -10 18 q-3 2 -5 5 l8 4 q3 -3 5 -5 q14 -6 18 -10" />
    </g>
  ),
  soins: (
    <g stroke="rgba(20,16,10,.78)" strokeWidth="1" fill="none" strokeLinecap="round" strokeLinejoin="round">
      <rect x="34" y="56" width="22" height="64" rx="2" />
      <path d="M40 56 v-8 q0 -4 4 -4 h6 q4 0 4 4 v8" />
      <path d="M38 76 h14" />
      <rect x="62" y="42" width="20" height="78" rx="2" />
      <path d="M67 42 v-6 q0 -3 3 -3 h4 q3 0 3 3 v6" />
      <path d="M65 64 h12" />
      <rect x="88" y="64" width="22" height="56" rx="2" />
      <path d="M94 64 v-7 q0 -3 3 -3 h6 q3 0 3 3 v7" />
      <path d="M125 50 q-4 8 0 18 q4 -8 0 -18 z" fill="rgba(20,16,10,.4)" />
      <path d="M28 30 q4 6 12 4 q-2 8 -10 8" />
      <path d="M22 38 q4 4 10 4" />
    </g>
  ),
  cadeaux: (
    <g stroke="rgba(251,246,237,.85)" strokeWidth="1" fill="none" strokeLinecap="round" strokeLinejoin="round">
      <rect x="30" y="60" width="80" height="60" />
      <line x1="70" y1="60" x2="70" y2="120" />
      <line x1="30" y1="80" x2="110" y2="80" />
      <path d="M70 60 q-20 -16 -10 -24 q10 -6 10 24 q0 -30 10 -24 q10 8 -10 24" />
      <rect x="86" y="34" width="34" height="22" />
      <path d="M86 34 l17 14 l17 -14" />
      <circle cx="103" cy="56" r="3" fill="rgba(255,80,80,.7)" />
    </g>
  ),
};

function Collections() {
  return (
    <section id="collections" style={{maxWidth:1360, margin:'0 auto', padding:'80px 32px 24px'}}>
      <div style={{display:'flex', alignItems:'flex-end', justifyContent:'space-between', marginBottom:36, flexWrap:'wrap', gap:16}}>
        <div>
          <div className="smallcaps" style={{color:'var(--accent)', marginBottom:10}}>● Nos univers</div>
          <h2 className="serif" style={{fontSize:'clamp(40px,5vw,72px)', margin:0, color:'var(--ink)'}}>
            Six territoires <em style={{fontStyle:'italic'}}>intimes.</em>
          </h2>
        </div>
        <a href="#produits" style={{fontSize:14, color:'var(--ink)', borderBottom:'1px solid var(--ink)', paddingBottom:2}}>Tout parcourir →</a>
      </div>
      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(180px, 1fr))', gap:14}}>
        {window.COLLECTIONS.map((c, i) => (
          <a key={c.id} href={`#cat=${c.id}`} style={{display:'block'}}>
            <div style={{
              position:'relative', aspectRatio:'3/4', borderRadius:8, overflow:'hidden',
              background:`linear-gradient(180deg,
                hsl(${[15,28,350,340,40,355][i]}, ${[35,40,30,38,28,45][i]}%, ${[35,28,18,22,55,22][i]}%) 0%,
                hsl(${[10,25,355,335,38,350][i]}, ${[40,45,35,42,30,50][i]}%, ${[20,18,12,14,40,14][i]}%) 100%)`,
              transition:'transform .4s ease', cursor:'pointer'
            }}
              onMouseEnter={e => e.currentTarget.style.transform='translateY(-4px)'}
              onMouseLeave={e => e.currentTarget.style.transform='translateY(0)'}>

              {/* Illustration line-art */}
              <svg viewBox="0 0 140 160" style={{position:'absolute', top:'8%', left:'50%', transform:'translateX(-50%)', width:'70%', height:'auto', opacity:.95}}>
                {ILLUS[c.id]}
              </svg>

              <div style={{
                position:'absolute', inset:0, opacity:.06,
                backgroundImage:'repeating-linear-gradient(45deg, transparent 0 12px, rgba(255,255,255,.7) 12px 13px)'
              }}/>
              <div style={{
                position:'absolute', top:14, left:14,
                fontSize:10, fontFamily:'Geist Mono', color: c.id==='soins' ? 'rgba(20,16,10,.55)' : 'rgba(255,255,255,.7)', letterSpacing:'.12em'
              }}>0{i+1}{c.adult ? ' · 18+' : ''}</div>
              <div style={{position:'absolute', bottom:0, left:0, right:0, padding:18, color: c.id==='soins' ? '#1a1410' : '#fff'}}>
                <div className="serif" style={{fontSize:28, lineHeight:1, marginBottom:6}}>{c.label}</div>
                <div style={{fontSize:12, opacity:.78, marginBottom:10}}>{c.fr}</div>
                <div className="mono" style={{fontSize:10, letterSpacing:'.12em', opacity:.6}}>{c.count} produits →</div>
              </div>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Amazon-style product card
function AffiliateCard({ p, onFav, faved }) {
  return (
    <article style={{
      background:'var(--paper)', borderRadius:12, overflow:'hidden',
      border:'1px solid var(--line-2)', display:'flex', flexDirection:'column',
      transition:'transform .25s ease, box-shadow .25s ease'
    }}
    onMouseEnter={e => { e.currentTarget.style.transform='translateY(-3px)'; e.currentTarget.style.boxShadow='0 16px 40px rgba(0,0,0,.08)'; }}
    onMouseLeave={e => { e.currentTarget.style.transform='translateY(0)'; e.currentTarget.style.boxShadow='none'; }}>
      <div style={{position:'relative'}}>
        <ProductVisual color={p.color} label={`${p.sub.toUpperCase()}`} tag={p.tag} image={p.image} alt={p.name}/>
        <button onClick={() => onFav(p.id)} style={{
          position:'absolute', top:10, right:10, width:32, height:32, borderRadius:'50%',
          background:'var(--paper)', border:0, cursor:'pointer', fontSize:14,
          color: faved ? 'var(--accent)' : 'var(--muted)',
          boxShadow:'0 2px 8px rgba(0,0,0,.1)'
        }}>{faved ? '♥' : '♡'}</button>
      </div>

      <div style={{padding:16, display:'flex', flexDirection:'column', gap:8, flex:1}}>
        <div className="serif" style={{fontSize:20, color:'var(--ink)', lineHeight:1.15}}>{p.name}</div>
        <div style={{fontSize:12, color:'var(--muted)'}}>{p.sub}</div>

        <div style={{display:'flex', alignItems:'center', gap:8, marginTop:2}}>
          <Stars rating={p.rating} size={13}/>
          <span style={{fontSize:12, color:'var(--ink-2)', fontWeight:600}}>{p.rating}</span>
          <span style={{fontSize:12, color:'var(--muted)'}}>({p.reviews.toLocaleString('fr-FR')})</span>
        </div>

        <div style={{display:'flex', alignItems:'baseline', gap:8, marginTop:6}}>
          <span className="serif" style={{fontSize:26, color:'var(--ink)', fontWeight:600}}>{p.price}</span>
          {p.was && <span style={{fontSize:13, color:'var(--muted)', textDecoration:'line-through'}}>{p.was}</span>}
          {p.off && <span className="mono" style={{
            fontSize:11, fontWeight:700, color:'var(--accent)',
            background:'rgba(91,26,38,.08)', padding:'2px 7px', borderRadius:4
          }}>{p.off}</span>}
        </div>

        {p.prime && (
          <div style={{display:'flex', alignItems:'center', gap:6, fontSize:11, color:'var(--ink-2)'}}>
            <span style={{
              fontSize:10, fontWeight:700, color:'#fff', background:'#00a8e1',
              padding:'2px 6px', borderRadius:3, letterSpacing:'.04em'
            }}>prime</span>
            <span>Livraison gratuite en 24h</span>
          </div>
        )}

        <a href={`https://www.amazon.fr/dp/${p.asin}?tag=lebrunnathali-21`} target="_blank" rel="sponsored noopener nofollow" style={{
          marginTop:'auto', padding:'12px 14px', background:'#febd69',
          color:'#0f1111', textAlign:'center', borderRadius:999,
          fontSize:13, fontWeight:600, fontFamily:'inherit',
          display:'flex', alignItems:'center', justifyContent:'center', gap:8
        }}>
          Voir sur Amazon
          <span style={{fontSize:14}}>→</span>
        </a>
        <div className="mono" style={{fontSize:10, color:'var(--muted)', textAlign:'center', letterSpacing:'.06em'}}>
          Lien sponsorisé Amazon
        </div>
      </div>
    </article>
  );
}

// Product grid
function ProductGrid({ favs, onFav }) {
  const [active, setActive] = useState2('all');

  // Synchronise avec l'URL : #cat=lingerie filtre + scroll vers la grille
  React.useEffect(() => {
    const apply = () => {
      const m = window.location.hash.match(/cat=([a-z]+)/);
      if (m && window.COLLECTIONS.some(c => c.id === m[1])) {
        setActive(m[1]);
        const el = document.getElementById('produits');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      } else if (window.location.hash === '#produits') {
        setActive('all');
      }
    };
    apply();
    window.addEventListener('hashchange', apply);
    return () => window.removeEventListener('hashchange', apply);
  }, []);

  const filtered = active === 'all' ? window.PRODUCTS : window.PRODUCTS.filter(p => p.cat === active);
  return (
    <section id="produits" style={{maxWidth:1360, margin:'0 auto', padding:'80px 32px 24px', scrollMarginTop:'80px'}}>
      <div style={{display:'flex', alignItems:'flex-end', justifyContent:'space-between', marginBottom:32, flexWrap:'wrap', gap:24}}>
        <div>
          <div className="smallcaps" style={{color:'var(--accent)', marginBottom:10}}>● Sélection Léa · sur Amazon</div>
          <h2 className="serif" style={{fontSize:'clamp(40px,5vw,72px)', margin:0, color:'var(--ink)'}}>
            Choisies <em style={{fontStyle:'italic'}}>une à une.</em>
          </h2>
          <p style={{fontSize:14, color:'var(--muted)', marginTop:10, maxWidth:480}}>
            Léa teste, classe et sélectionne. Vous achetez en sécurité chez Amazon — mêmes prix, livraison Prime.
          </p>
        </div>

        <div style={{display:'flex', gap:6, flexWrap:'wrap'}}>
          {[{id:'all',label:'Tout'}, ...window.COLLECTIONS].map(c => {
            const on = c.id === active;
            return (
              <button key={c.id} onClick={() => setActive(c.id)} style={{
                padding:'8px 14px', borderRadius:999,
                border: on ? '1px solid var(--ink)' : '1px solid var(--line)',
                background: on ? 'var(--ink)' : 'transparent',
                color: on ? 'var(--paper)' : 'var(--ink-2)',
                fontWeight:500, fontSize:12, cursor:'pointer', fontFamily:'inherit'
              }}>{c.label}</button>
            );
          })}
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:24}}>
        {filtered.map(p => (
          <AffiliateCard key={p.id} p={p} onFav={onFav} faved={favs.has(p.id)}/>
        ))}
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Stats strip
function StatsStrip() {
  return (
    <section style={{borderTop:'1px solid var(--line-2)', borderBottom:'1px solid var(--line-2)', background:'var(--paper)'}}>
      <div style={{maxWidth:1360, margin:'0 auto', padding:'32px 32px',
        display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:24}}>
        {window.STATS.map((s,i) => (
          <div key={i} style={{display:'flex', flexDirection:'column', gap:4}}>
            <div className="serif" style={{fontSize:38, color:'var(--accent)', fontStyle:'italic'}}>{s.k}</div>
            <div style={{fontSize:13, color:'var(--muted)'}}>{s.v}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Editorial
function Editorial() {
  const e = window.EDITORIAL;
  return (
    <section style={{marginTop:80, padding:'96px 0', background:'var(--accent)', color:'var(--paper)', position:'relative', overflow:'hidden'}}>
      <div style={{position:'absolute', inset:0, opacity:.06,
        backgroundImage:'repeating-linear-gradient(135deg, transparent 0 18px, #fff 18px 19px)'}}/>
      <div style={{maxWidth:1100, margin:'0 auto', padding:'0 32px', position:'relative',
        display:'grid', gridTemplateColumns:'1fr 1fr', gap:64, alignItems:'center'}}>
        <div>
          <div className="smallcaps" style={{color:'rgba(251,246,237,.6)', marginBottom:18}}>
            ● {e.kicker} · {e.read} de lecture
          </div>
          <h2 className="serif" style={{fontSize:'clamp(48px,5.5vw,84px)', margin:'0 0 24px', color:'var(--paper)'}}>
            Mes 7 <em style={{fontStyle:'italic'}}>indispensables</em> intimes.
          </h2>
          <p style={{fontSize:17, lineHeight:1.55, opacity:.85, margin:'0 0 28px', maxWidth:480}}>{e.excerpt}</p>
          <a href="/journal/" style={{display:'inline-block', padding:'13px 22px', background:'var(--paper)',
            color:'var(--accent)', borderRadius:10, fontWeight:600, fontSize:14}}>Lire le journal →</a>
        </div>
        <blockquote style={{margin:0, padding:'24px 0 24px 32px', borderLeft:'2px solid rgba(251,246,237,.4)'}}>
          <div className="serif" style={{fontSize:'clamp(28px,3vw,42px)', fontStyle:'italic', lineHeight:1.25, color:'var(--paper)'}}>
            "Je ne recommande que ce que j'utilise vraiment. Si c'est dans la sélection,
            c'est que ça a passé six mois sur ma table de chevet."
          </div>
          <div className="smallcaps" style={{marginTop:24, color:'rgba(251,246,237,.7)'}}>
            — Léa, fondatrice & curatrice
          </div>
        </blockquote>
      </div>
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Avis clientes & clients
const REVIEWS = [
  { name:'Camille L.', age:34, city:'Lyon', rating:5, text:'Je cherchais un soutien-gorge sans armatures qui tienne vraiment, je l’ai trouvé grâce à la sélection. Le guide m’a aidée à choisir la bonne taille du premier coup.', cat:'Lingerie' },
  { name:'Mehdi & Sarah',  age:null, city:'Bordeaux', rating:5, text:'On a offert un coffret massage à notre couple — colis neutre, livraison rapide, contenu conforme à la description. Belle découverte pour nous.', cat:'Coffrets' },
  { name:'Élise R.',  age:42, city:'Nantes', rating:5, text:'C’est ma première commande de ce type. La discrétion et les conseils m’ont mise en confiance. Je reviendrai.', cat:'Sensualité' },
  { name:'Julie M.',   age:29, city:'Paris', rating:4, text:'Belle nuisette en satin, exactement comme sur la photo. Petit bémol sur le délai mais Amazon a bien suivi.', cat:'Nuit' },
  { name:'Anonyme',    age:null, city:'Toulouse', rating:5, text:'Article du journal sur le lubrifiant intime très clair. J’ai compris ce qu’il fallait éviter et fait le bon choix. Merci Léa.', cat:'Soins' },
  { name:'Léa & Tom',  age:null, city:'Marseille', rating:5, text:'On a démarré en couple grâce à la sélection débutant. Le ton bienveillant change tout, on s’est sentis accompagnés sans être jugés.', cat:'Sensualité' },
];

function Reviews() {
  return (
    <section style={{maxWidth:1360, margin:'0 auto', padding:'80px 32px 24px'}}>
      <div style={{display:'flex', alignItems:'flex-end', justifyContent:'space-between', marginBottom:32, flexWrap:'wrap', gap:24}}>
        <div>
          <div className="smallcaps" style={{color:'var(--accent)', marginBottom:10}}>● Elles & ils en parlent</div>
          <h2 className="serif" style={{fontSize:'clamp(40px,5vw,72px)', margin:0, color:'var(--ink)', lineHeight:1.05}}>
            La parole <em style={{fontStyle:'italic'}}>aux client·e·s.</em>
          </h2>
          <p style={{fontSize:14, color:'var(--muted)', marginTop:10, maxWidth:480}}>
            Avis vérifiés sur les achats Amazon réalisés via la sélection Maison Léa.
          </p>
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(300px, 1fr))', gap:18}}>
        {REVIEWS.map((r, i) => (
          <div key={i} style={{
            background:'var(--paper)', border:'1px solid var(--line-2)', borderRadius:12,
            padding:'24px 26px', display:'flex', flexDirection:'column', gap:14
          }}>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
              <Stars rating={r.rating} size={14}/>
              <div className="smallcaps" style={{fontSize:9, color:'var(--accent)'}}>{r.cat}</div>
            </div>
            <p className="serif" style={{fontSize:18, lineHeight:1.4, fontStyle:'italic', color:'var(--ink)', margin:0}}>
              &ldquo;{r.text}&rdquo;
            </p>
            <div style={{borderTop:'1px solid var(--line-2)', paddingTop:12, fontSize:13, color:'var(--ink-2)'}}>
              <strong style={{fontWeight:600}}>{r.name}</strong>
              {r.age ? `, ${r.age} ans` : ""}
              <span style={{color:'var(--muted)'}}> · {r.city}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

// Alias pour conserver le nom Newsletter référencé dans app.jsx
const Newsletter = Reviews;

// ─────────────────────────────────────────────────────────────────────────────
// Affiliate disclosure banner (sticky bottom-style sidebar info)
function DisclosureBar() {
  return (
    <div style={{
      background:'var(--bg-2)', borderTop:'1px solid var(--line-2)', borderBottom:'1px solid var(--line-2)',
      padding:'14px 24px', textAlign:'center'
    }}>
      <div style={{maxWidth:900, margin:'0 auto', fontSize:12, color:'var(--ink-2)', lineHeight:1.5}}>
        <b style={{color:'var(--accent)'}}>Transparence :</b> Maison Léa est un site de curation indépendant.
        En tant que <i>Partenaire Amazon</i>, nous percevons une commission sur les achats éligibles —
        sans surcoût pour vous. Nous ne recommandons que des produits testés.
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Footer
function Footer() {
  return (
    <footer style={{marginTop:80, paddingTop:56, borderTop:'1px solid var(--line-2)', background:'var(--bg-2)'}}>
      <div style={{maxWidth:1360, margin:'0 auto', padding:'24px 32px 24px'}}>
        <div className="serif" style={{fontSize:'clamp(56px, 9vw, 144px)', color:'var(--ink)', lineHeight:.9, marginBottom:48}}>
          Maison <em style={{fontStyle:'italic', color:'var(--accent)'}}>Léa.</em>
        </div>
        <div style={{display:'grid', gridTemplateColumns:'2fr repeat(3,1fr)', gap:32, paddingBottom:32}}>
          <p style={{fontSize:13, color:'var(--muted)', lineHeight:1.6, margin:0, maxWidth:360}}>
            Site indépendant de curation, partenaire Amazon. Léa sélectionne le meilleur de la
            lingerie et de l'intimité disponible sur Amazon.fr — vous achetez chez Amazon, en confiance.
          </p>
          {[
            ['Univers', [['Lingerie','#collections'],['Nuit','#collections'],['Sensualité','#collections'],['Érotisme','#collections'],['Soins','#collections'],['Coffrets','#collections']]],
            ['Le site', [['Notre méthode','#promesses'],['Le journal','/journal/'],['Guides','/journal/'],['Top des ventes','#produits']]],
            ['Légal', [['Mentions légales','/mentions-legales.html'],['Affiliation Amazon','/affiliation.html'],['Confidentialité','/confidentialite.html'],['Cookies','/confidentialite.html#cookies']]],
          ].map(([h, items]) => (
            <div key={h}>
              <div className="smallcaps" style={{marginBottom:14, color:'var(--ink)'}}>{h}</div>
              <ul style={{listStyle:'none', padding:0, margin:0, display:'flex', flexDirection:'column', gap:8}}>
                {items.map(([label, href]) => (<li key={label}><a href={href} style={{fontSize:13, color:'var(--ink-2)'}}>{label}</a></li>))}
              </ul>
            </div>
          ))}
        </div>
        <div style={{paddingTop:20, paddingBottom:24, borderTop:'1px solid var(--line)',
          display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:12,
          fontSize:12, color:'var(--muted)'}}>
          <div>© 2026 Maison Léa · Site réservé aux personnes majeures · <i>Partenaire Amazon</i></div>
          <div className="mono" style={{letterSpacing:'.08em'}}>guide-soin.fr</div>
        </div>
      </div>
    </footer>
  );
}

Object.assign(window, { Stars, AffiliateCard, Collections, ProductGrid, StatsStrip, Editorial, Newsletter, DisclosureBar, Footer });
