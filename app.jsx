// app.jsx — Maison Léa: Amazon affiliate edition
const { useState: useStateApp, useEffect: useEffectApp } = React;

const PALETTE = {
  accent: '#5b1a26', accent2: '#8b2d3f',
  bg: '#f5efe6', bg2: '#ede4d3',
  paper: '#fbf6ed', ink: '#1a1410'
};

function applyPalette() {
  const r = document.documentElement.style;
  r.setProperty('--accent', PALETTE.accent);
  r.setProperty('--accent-2', PALETTE.accent2);
  r.setProperty('--bg', PALETTE.bg);
  r.setProperty('--bg-2', PALETTE.bg2);
  r.setProperty('--paper', PALETTE.paper);
  r.setProperty('--ink', PALETTE.ink);
  r.setProperty('--ink-2', '#3a2e26');
  r.setProperty('--muted', '#8a7866');
  r.setProperty('--line', 'rgba(26,20,16,.14)');
  r.setProperty('--line-2', 'rgba(26,20,16,.07)');
  document.body.style.background = PALETTE.bg;
  document.body.style.color = PALETTE.ink;
}

function App() {
  const [gateOpen, setGateOpen] = useStateApp(() => {
    if (typeof window === 'undefined') return true;
    return window.localStorage.getItem('ml_age_ok') !== '1';
  });
  const [favs, setFavs] = useStateApp(new Set());

  useEffectApp(() => { applyPalette(); }, []);

  const onFav = (id) => setFavs(s => {
    const n = new Set(s); if (n.has(id)) n.delete(id); else n.add(id); return n;
  });

  const onPassGate = () => {
    try { window.localStorage.setItem('ml_age_ok', '1'); } catch (e) {}
    setGateOpen(false);
  };

  return (
    <div>
      {gateOpen && <window.AgeGate onPass={onPassGate}/>}
      <window.TopBar/>
      <window.Header favCount={favs.size}/>
      <window.DisclosureBar/>
      <window.Hero/>
      <window.Promises/>
      <window.StatsStrip/>
      <window.Collections/>
      <window.ProductGrid favs={favs} onFav={onFav}/>
      <window.Editorial/>
      <window.Newsletter/>
      <window.Footer/>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('app')).render(<App/>);
