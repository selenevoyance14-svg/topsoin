// components.jsx — Maison Léa: AgeGate, Header, Hero, Promises
const { useState, useEffect, useRef, useMemo } = React;

// ─────────────────────────────────────────────────────────────────────────────
// Age Gate (18+)
function AgeGate({ onPass }) {
  const [closing, setClosing] = useState(false);
  const accept = () => { setClosing(true); setTimeout(onPass, 350); };
  return (
    <div style={{
      position:'fixed', inset:0, zIndex:200,
      background:'rgba(26,20,16,.84)', backdropFilter:'blur(14px)',
      display:'flex', alignItems:'center', justifyContent:'center', padding:24,
      animation: closing ? 'fade-in .35s reverse' : 'fade-in .35s'
    }}>
      <div style={{
        background:'var(--paper)', borderRadius:16, maxWidth:480, width:'100%',
        padding:'40px 36px', textAlign:'center',
        boxShadow:'0 30px 90px rgba(0,0,0,.4)'
      }}>
        <div className="serif" style={{fontSize:44, color:'var(--ink)', marginBottom:6}}>
          Maison <em style={{fontStyle:'italic', color:'var(--accent)'}}>Léa</em>
        </div>
        <div className="smallcaps" style={{color:'var(--muted)', marginBottom:24}}>
          Lingerie & intimité · Paris
        </div>
        <p style={{fontSize:15, color:'var(--ink-2)', lineHeight:1.6, marginBottom:28}}>
          Ce site est destiné à un public majeur. En entrant, vous confirmez avoir
          <b> 18&nbsp;ans ou plus</b> et accepter notre politique de confidentialité.
        </p>
        <div style={{display:'flex', flexDirection:'column', gap:10}}>
          <button onClick={accept} style={{
            padding:'15px 22px', background:'var(--ink)', color:'var(--paper)',
            border:0, borderRadius:10, fontSize:14, fontWeight:600,
            cursor:'pointer', letterSpacing:'.02em'
          }}>J'ai 18 ans ou plus — Entrer</button>
          <a href="https://www.google.com" style={{
            fontSize:13, color:'var(--muted)', padding:'10px',
            textDecoration:'underline', textUnderlineOffset:3
          }}>Je n'ai pas l'âge requis — Quitter</a>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Top whisper bar
function TopBar() {
  return (
    <div style={{
      background:'var(--ink)', color:'var(--paper)', fontSize:12,
      padding:'10px 24px', textAlign:'center', letterSpacing:'.04em'
    }}>
      <span style={{opacity:.6}}>●</span> &nbsp;Sélection 100% disponible sur Amazon ·
      Livraison Prime en 24h · Colis neutre Amazon · &nbsp;
      <a href="#" style={{textDecoration:'underline', textUnderlineOffset:3}}>En savoir plus</a>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Header / Nav
function Header({ favCount = 0 }) {
  return (
    <header style={{
      borderBottom:'1px solid var(--line-2)', background:'var(--bg)',
      position:'sticky', top:0, zIndex:50,
      backgroundColor:'rgba(245,239,230,.94)', backdropFilter:'blur(12px)'
    }}>
      <div style={{
        maxWidth:1360, margin:'0 auto', padding:'18px 32px',
        display:'grid', gridTemplateColumns:'1fr auto 1fr', alignItems:'center', gap:24
      }}>
        <nav style={{display:'flex', gap:24, fontSize:13}}>
          {['Lingerie','Nuit','Sensualité','Érotisme','Soins','Coffrets'].map(n => (
            <a key={n} href="#" style={{color:'var(--ink-2)', fontWeight:500}}
               onMouseEnter={e=>e.currentTarget.style.color='var(--accent)'}
               onMouseLeave={e=>e.currentTarget.style.color='var(--ink-2)'}>
              {n}
            </a>
          ))}
        </nav>

        <a href="#" className="serif" style={{
          fontSize:30, color:'var(--ink)', lineHeight:.9, textAlign:'center',
          display:'flex', flexDirection:'column', alignItems:'center'
        }}>
          <span>Maison <em style={{fontStyle:'italic', color:'var(--accent)'}}>Léa</em></span>
          <span className="smallcaps" style={{fontSize:9, color:'var(--muted)', marginTop:4}}>
            PARIS · EST. 2024
          </span>
        </a>

        <div style={{display:'flex', justifyContent:'flex-end', gap:18, alignItems:'center'}}>
          <a href="#" style={{fontSize:13, color:'var(--ink-2)'}}>Le Journal</a>
          <a href="#" style={{fontSize:13, color:'var(--ink-2)'}}>Conseils</a>
          <button style={iconBtn}>⌕</button>
          <button style={{...iconBtn, position:'relative'}}>
            ♡
            {favCount > 0 && (
              <span style={{
                position:'absolute', top:-2, right:-4, minWidth:16, height:16, borderRadius:8,
                background:'var(--accent)', color:'#fff', fontSize:10, fontWeight:700,
                display:'flex', alignItems:'center', justifyContent:'center', padding:'0 4px'
              }}>{favCount}</span>
            )}
          </button>
          <a href="#" style={{
            padding:'8px 14px', background:'#febd69', color:'#0f1111',
            borderRadius:999, fontSize:12, fontWeight:600
          }}>Voir sur Amazon →</a>
        </div>
      </div>
    </header>
  );
}
const iconBtn = {
  width:32, height:32, borderRadius:'50%', border:'1px solid var(--line)',
  background:'transparent', color:'var(--ink)', cursor:'pointer', fontSize:14,
  display:'inline-flex', alignItems:'center', justifyContent:'center'
};

// ─────────────────────────────────────────────────────────────────────────────
// Hero — editorial, Léa portrait + serif headline + collection card
function Hero() {
  return (
    <section style={{
      maxWidth:1360, margin:'0 auto', padding:'40px 32px 24px',
      display:'grid', gridTemplateColumns:'1fr 1fr', gap:32, alignItems:'stretch'
    }}>
      {/* Left: editorial copy */}
      <div style={{
        display:'flex', flexDirection:'column', justifyContent:'space-between',
        padding:'48px 8px 24px'
      }}>
        <div>
          <div className="smallcaps" style={{color:'var(--muted)', marginBottom:24}}>
            ● Collection Printemps · n°04
          </div>
          <h1 className="serif" style={{
            fontSize:'clamp(64px, 8vw, 128px)', margin:'0 0 24px', color:'var(--ink)'
          }}>
            L'art<br/>de se<br/><em style={{fontStyle:'italic', color:'var(--accent)'}}>désirer.</em>
          </h1>
          <p style={{
            fontSize:17, lineHeight:1.55, color:'var(--ink-2)', maxWidth:440,
            margin:'0 0 32px'
          }}>
            Une maison française de lingerie et d'intimité.
            Pièces choisies, conçues pour soi d'abord —
            de la dentelle aux objets du plaisir.
          </p>
          <div style={{display:'flex', gap:12, flexWrap:'wrap'}}>
            <button style={btnPrimary}>Découvrir la collection</button>
            <button style={btnGhost}>Le mot de Léa →</button>
          </div>
        </div>

        <div style={{
          marginTop:48, paddingTop:24, borderTop:'1px solid var(--line-2)',
          display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:16, fontSize:12
        }}>
          {[
            ['◇', 'Dentelle de Calais','Made in France'],
            ['◐', 'Emballage discret','100% neutre'],
            ['☉', '+38 000 femmes','nous font confiance'],
          ].map(([i,a,b],idx) => (
            <div key={idx}>
              <div style={{fontSize:18, color:'var(--accent)', marginBottom:6}}>{i}</div>
              <div style={{color:'var(--ink)', fontWeight:600, marginBottom:2}}>{a}</div>
              <div style={{color:'var(--muted)'}}>{b}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Right: Léa portrait */}
      <div style={{position:'relative', minHeight:680}}>
        <div style={{
          position:'absolute', inset:0, borderRadius:8, overflow:'hidden',
          background:'#3a2e26'
        }}>
          <img src="assets/lea-persona.png" alt="Léa, fondatrice"
               style={{width:'100%', height:'100%', objectFit:'cover',
                       animation:'kenburns 18s ease-in-out infinite alternate',
                       transformOrigin:'50% 35%'}}/>
        </div>

        {/* Caption card bottom-left */}
        <div style={{
          position:'absolute', left:24, bottom:24,
          padding:'18px 22px', background:'rgba(251,246,237,.92)',
          backdropFilter:'blur(10px)', borderRadius:8, maxWidth:300
        }}>
          <div className="smallcaps" style={{fontSize:10, color:'var(--accent)', marginBottom:8}}>
            ● Léa · Fondatrice
          </div>
          <p className="serif" style={{
            fontSize:20, fontStyle:'italic', margin:0, color:'var(--ink)', lineHeight:1.3
          }}>
            "Une maison où l'on parle d'intimité comme on parle de mode :
            avec exigence et sans détour."
          </p>
        </div>

        {/* Stamp top-right */}
        <div style={{
          position:'absolute', top:24, right:24,
          width:96, height:96, borderRadius:'50%',
          border:'1px solid rgba(251,246,237,.6)',
          color:'#fff', display:'flex', alignItems:'center', justifyContent:'center',
          fontSize:10, letterSpacing:'.18em', textAlign:'center', lineHeight:1.4,
          background:'rgba(0,0,0,.18)', backdropFilter:'blur(4px)',
          padding:8, fontWeight:500
        }}>
          MADE IN<br/>FRANCE<br/>—<br/>2024
        </div>
      </div>
    </section>
  );
}

const btnPrimary = {
  background:'var(--ink)', color:'var(--paper)', border:0,
  padding:'15px 24px', borderRadius:10, fontWeight:600, fontSize:14,
  cursor:'pointer', letterSpacing:'.01em', fontFamily:'inherit'
};
const btnGhost = {
  background:'transparent', color:'var(--ink)', border:'1.5px solid var(--ink)',
  padding:'13px 22px', borderRadius:10, fontWeight:500, fontSize:14,
  cursor:'pointer', fontFamily:'inherit'
};

// ─────────────────────────────────────────────────────────────────────────────
// Promises strip
function Promises() {
  return (
    <section style={{
      borderTop:'1px solid var(--line-2)', borderBottom:'1px solid var(--line-2)',
      background:'var(--paper)'
    }}>
      <div style={{
        maxWidth:1360, margin:'0 auto', padding:'40px 32px',
        display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:32
      }}>
        {window.PROMISES.map(p => (
          <div key={p.kicker} style={{borderLeft:'1px solid var(--line)', paddingLeft:18}}>
            <div className="serif" style={{fontSize:32, fontStyle:'italic', color:'var(--accent)', marginBottom:8}}>
              {p.kicker}
            </div>
            <div style={{fontSize:15, fontWeight:600, color:'var(--ink)', marginBottom:6}}>
              {p.title}
            </div>
            <p style={{fontSize:13, color:'var(--muted)', lineHeight:1.5, margin:0}}>
              {p.body}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

Object.assign(window, { AgeGate, TopBar, Header, Hero, Promises, btnPrimary, btnGhost });
