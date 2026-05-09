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
// Collections
function Collections() {
  return (
    <section style={{maxWidth:1360, margin:'0 auto', padding:'80px 32px 24px'}}>
      <div style={{display:'flex', alignItems:'flex-end', justifyContent:'space-between', marginBottom:36, flexWrap:'wrap', gap:16}}>
        <div>
          <div className="smallcaps" style={{color:'var(--accent)', marginBottom:10}}>● Nos univers</div>
          <h2 className="serif" style={{fontSize:'clamp(40px,5vw,72px)', margin:0, color:'var(--ink)'}}>
            Six territoires <em style={{fontStyle:'italic'}}>intimes.</em>
          </h2>
        </div>
        <a href="#" style={{fontSize:14, color:'var(--ink)', borderBottom:'1px solid var(--ink)', paddingBottom:2}}>Tout parcourir →</a>
      </div>
      <div style={{display:'grid', gridTemplateColumns:'repeat(6,1fr)', gap:14}}>
        {window.COLLECTIONS.map((c, i) => (
          <a key={c.id} href="#" style={{display:'block'}}>
            <div style={{
              position:'relative', aspectRatio:'3/4', borderRadius:8, overflow:'hidden',
              background:`linear-gradient(180deg,
                hsl(${[15,28,350,340,40,355][i]}, ${[35,40,30,38,28,45][i]}%, ${[35,28,18,22,55,22][i]}%) 0%,
                hsl(${[10,25,355,335,38,350][i]}, ${[40,45,35,42,30,50][i]}%, ${[20,18,12,14,40,14][i]}%) 100%)`,
              transition:'transform .4s ease', cursor:'pointer'
            }}
              onMouseEnter={e => e.currentTarget.style.transform='translateY(-4px)'}
              onMouseLeave={e => e.currentTarget.style.transform='translateY(0)'}>
              <div style={{
                position:'absolute', inset:0, opacity:.16,
                backgroundImage:'repeating-linear-gradient(45deg, transparent 0 12px, rgba(255,255,255,.7) 12px 13px)'
              }}/>
              <div style={{
                position:'absolute', top:14, left:14,
                fontSize:10, fontFamily:'Geist Mono', color:'rgba(255,255,255,.7)', letterSpacing:'.12em'
              }}>0{i+1}{c.adult ? ' · 18+' : ''}</div>
              <div style={{position:'absolute', bottom:0, left:0, right:0, padding:18, color:'#fff'}}>
                <div className="serif" style={{fontSize:30, lineHeight:1, marginBottom:6}}>{c.label}</div>
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
  const filtered = active === 'all' ? window.PRODUCTS : window.PRODUCTS.filter(p => p.cat === active);
  return (
    <section style={{maxWidth:1360, margin:'0 auto', padding:'80px 32px 24px'}}>
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
