{% verbatim %}
// ══════════════════════════════════════════════════════════════════
//  MAKTABA YA SECTIONS ZA JAMIITEK (editor.html)
//
//  Kila block ni section kamili ya kitaalamu: inatumia rangi ya brand
//  (var(--accent)), font za site (var(--font-head)) na CSS yenye media
//  queries — kwa hiyo inakaa vizuri kwenye simu bila kuguswa.
//  CSS inaingia kwenye CssComposer ya GrapesJS (class .jb-*), kwa hiyo
//  mteja anaweza kuibadilisha kwenye Style Manager kama kawaida.
// ══════════════════════════════════════════════════════════════════
(function(){
const bm = editor.BlockManager;

// Picha ya kishika-nafasi (SVG) — mteja anabofya mara mbili kuweka yake
const PH = (w, h, t) => 'data:image/svg+xml;utf8,' + encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">` +
  `<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e2e8f0"/>` +
  `<stop offset="1" stop-color="#cbd5e1"/></linearGradient></defs><rect width="100%" height="100%" fill="url(#g)"/>` +
  `<text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" font-family="Arial,sans-serif" ` +
  `font-size="${Math.round(w / 24)}" fill="#64748b">${t || 'Double-click to add your image'}</text></svg>`);

// Mchoro mdogo wa block: [x, y, w, h, rangi, radius]
const C = {a: '#22d3ee', v: '#8b5cf6', d: '#1e293b', l: '#94a3b8', m: '#475569', w: '#e2e8f0', g: '#25d366', k: '#0b0f19'};
const TH = rects => `<svg viewBox="0 0 72 48" width="72" height="48" xmlns="http://www.w3.org/2000/svg">` +
  `<rect width="72" height="48" rx="6" fill="#0f1a2e"/>` +
  rects.map(([x, y, w, h, c, r]) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r || 1.5}" fill="${C[c] || c}"/>`).join('') + '</svg>';

const BASE = `
.jb-sec{padding:clamp(64px,9vw,120px) 20px}
.jb-wrap{max-width:1160px;margin:0 auto}
.jb-kicker{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--accent,#2563eb);margin-bottom:14px}
.jb-h1{font-family:var(--font-head,inherit);font-size:clamp(38px,6.4vw,76px);line-height:1.04;letter-spacing:-.04em;font-weight:800;margin:0 0 20px}
.jb-h2{font-family:var(--font-head,inherit);font-size:clamp(30px,4.2vw,48px);line-height:1.1;letter-spacing:-.03em;font-weight:800;color:#0f172a;margin:0 0 16px}
.jb-lead{font-size:clamp(16px,1.6vw,19px);line-height:1.7;color:#475569;max-width:620px;margin:0}
.jb-center{text-align:center}.jb-center .jb-lead{margin-left:auto;margin-right:auto}
.jb-btns{display:flex;flex-wrap:wrap;gap:12px;margin-top:32px}
.jb-center .jb-btns{justify-content:center}
.jb-btn{display:inline-block;padding:15px 28px;border-radius:12px;background:var(--accent,#2563eb);color:#fff;font-weight:700;text-decoration:none;
  box-shadow:0 12px 30px color-mix(in srgb,var(--accent,#2563eb) 30%,transparent);transition:transform .2s}
.jb-btn:hover{transform:translateY(-2px)}
.jb-btn2{display:inline-block;padding:14px 26px;border-radius:12px;border:1.5px solid currentColor;color:inherit;font-weight:700;text-decoration:none}
.jb-dark{background:#0b0f19;color:#cbd5e1}.jb-dark .jb-h2,.jb-dark .jb-h1{color:#fff}.jb-dark .jb-lead{color:#94a3b8}
.jb-soft{background:#f8fafc}
.jb-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:22px;margin-top:52px}
.jb-card{background:#fff;border:1px solid #e2e8f0;border-radius:20px;padding:30px;box-shadow:0 20px 50px rgba(15,23,42,.06)}
.jb-card h3{font-size:19px;color:#0f172a;margin:0 0 8px;letter-spacing:-.01em}
.jb-card p{margin:0;color:#475569;line-height:1.65;font-size:15px}
.jb-ic{width:52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;
  background:color-mix(in srgb,var(--accent,#2563eb) 12%,#fff);margin-bottom:18px}
.jb-img{display:block;width:100%;height:auto;border-radius:22px;object-fit:cover}
@media(max-width:600px){.jb-btns a{flex:1 1 100%;text-align:center}}
`;
const add = (id, label, cat, media, html, css) =>
  bm.add('jb-' + id, {label, category: cat, media: TH(media), content: `${html}<style>${BASE}${css || ''}</style>`});

const HERO = '🚀 Hero', FEAT = '✨ Features & Services', PROOF = '⭐ Social proof', PRICE = '💰 Pricing',
      CONT = '📖 Content', CTA = '📣 Contact & Call to action', LAY = '📐 Layout';

// ───────────── HERO ─────────────
add('hero-center', 'Hero — Centered', HERO,
  [[0,0,72,48,'k',6],[20,10,32,3,'a'],[12,16,48,6,'#fff'],[16,25,40,3,'l'],[22,33,13,6,'a',3],[37,33,13,6,'m',3]],
  `<section class="jb-sec jb-dark jb-center jb-hero1"><div class="jb-wrap">
  <span class="jb-kicker">Welcome to [[site:name]]</span>
  <h1 class="jb-h1">A headline that makes your customers say “yes”</h1>
  <p class="jb-lead">One or two sentences about what you do, who you do it for, and why you are the best choice in town.</p>
  <div class="jb-btns"><a class="jb-btn" href="[[site:whatsapp]]">Chat on WhatsApp</a><a class="jb-btn2" href="#services">See what we offer</a></div>
</div></section>`,
  `.jb-hero1{background:radial-gradient(900px 500px at 50% -10%,color-mix(in srgb,var(--accent,#2563eb) 35%,transparent),transparent 70%),#0b0f19;padding-top:clamp(90px,13vw,170px);padding-bottom:clamp(90px,13vw,170px)}`);

add('hero-split', 'Hero — Text + image', HERO,
  [[6,12,28,5,'d'],[6,20,24,3,'l'],[6,26,20,3,'l'],[6,34,12,6,'a',3],[40,8,26,32,'w',4]],
  `<section class="jb-sec jb-hero2"><div class="jb-wrap jb-hero2-in">
  <div><span class="jb-kicker">[[site:tagline]]</span>
    <h1 class="jb-h1">Quality you can see, service you can trust</h1>
    <p class="jb-lead">Tell visitors in plain words what makes you different. Keep it short, warm and confident.</p>
    <div class="jb-btns"><a class="jb-btn" href="[[site:whatsapp]]">Get started</a><a class="jb-btn2" href="/p/contact/">Contact us</a></div>
    <div class="jb-hero2-proof"><b>500+</b> happy customers · <b>4.9★</b> rating</div></div>
  <img class="jb-img jb-hero2-img" src="${PH(900, 1000)}" alt="">
</div></section>`,
  `.jb-hero2{background:linear-gradient(180deg,#fff,#f8fafc)}
.jb-hero2-in{display:grid;grid-template-columns:1.05fr .95fr;gap:clamp(30px,6vw,80px);align-items:center}
.jb-hero2 .jb-h1{color:#0f172a}
.jb-hero2-img{aspect-ratio:9/10;box-shadow:0 40px 90px rgba(15,23,42,.18)}
.jb-hero2-proof{margin-top:26px;font-size:14px;color:#64748b}.jb-hero2-proof b{color:#0f172a}
@media(max-width:860px){.jb-hero2-in{grid-template-columns:1fr}}`);

add('hero-image', 'Hero — Full image', HERO,
  [[0,0,72,48,'#334155',6],[0,0,72,48,'rgba(0,0,0,.35)',6],[10,16,40,6,'#fff'],[10,25,30,3,'w'],[10,32,14,6,'a',3]],
  `<section class="jb-sec jb-hero3"><div class="jb-wrap">
  <h1 class="jb-h1">Your story, told with one beautiful picture</h1>
  <p class="jb-lead">Select this section and change the background image in the Style panel → Background.</p>
  <div class="jb-btns"><a class="jb-btn" href="[[site:whatsapp]]">Book now</a></div>
</div></section>`,
  `.jb-hero3{min-height:78vh;display:flex;align-items:center;color:#fff;
  background:linear-gradient(90deg,rgba(2,6,23,.82),rgba(2,6,23,.25)),url("${PH(1600, 900, ' ')}") center/cover no-repeat}
.jb-hero3 .jb-wrap{width:100%}.jb-hero3 .jb-h1{color:#fff;max-width:760px}.jb-hero3 .jb-lead{color:rgba(255,255,255,.85)}`);

// ───────────── FEATURES ─────────────
add('features-3', 'Features — 3 cards', FEAT,
  [[22,6,28,4,'d'],[5,16,19,26,'w',3],[27,16,19,26,'w',3],[49,16,19,26,'w',3],[8,19,6,6,'a',2],[30,19,6,6,'a',2],[52,19,6,6,'a',2]],
  `<section class="jb-sec jb-soft" id="services"><div class="jb-wrap">
  <div class="jb-center"><span class="jb-kicker">Why choose us</span><h2 class="jb-h2">Everything you need, done right</h2>
    <p class="jb-lead">Three reasons customers keep coming back.</p></div>
  <div class="jb-grid">
    <div class="jb-card"><div class="jb-ic">⚡</div><h3>Fast service</h3><p>Explain the benefit in one or two short sentences your customer cares about.</p></div>
    <div class="jb-card"><div class="jb-ic">🛡️</div><h3>Trusted quality</h3><p>Mention guarantees, certificates or years of experience that build trust.</p></div>
    <div class="jb-card"><div class="jb-ic">💬</div><h3>Always reachable</h3><p>Tell them how quickly you reply on WhatsApp, phone or email.</p></div>
  </div>
</div></section>`);

add('features-split', 'Features — Image + checklist', FEAT,
  [[5,8,28,32,'w',4],[40,10,26,4,'d'],[40,19,4,4,'a',2],[46,20,18,2,'l'],[40,26,4,4,'a',2],[46,27,18,2,'l'],[40,33,4,4,'a',2],[46,34,18,2,'l']],
  `<section class="jb-sec"><div class="jb-wrap jb-fs">
  <img class="jb-img" src="${PH(900, 800)}" alt="">
  <div><span class="jb-kicker">What you get</span><h2 class="jb-h2">Built around what matters to you</h2>
    <p class="jb-lead">A short paragraph that sets up the list below.</p>
    <ul class="jb-check"><li>Clear, honest prices with no surprises</li><li>Friendly team that speaks Swahili and English</li>
      <li>Delivery or service anywhere in town</li><li>Easy payment — M-Pesa, Tigo Pesa, Airtel Money or card</li></ul>
    <div class="jb-btns"><a class="jb-btn" href="[[site:whatsapp]]">Ask a question</a></div></div>
</div></section>`,
  `.jb-fs{display:grid;grid-template-columns:1fr 1fr;gap:clamp(30px,6vw,80px);align-items:center}
.jb-fs .jb-img{aspect-ratio:9/8}
.jb-check{list-style:none;padding:0;margin:26px 0 0;display:flex;flex-direction:column;gap:14px}
.jb-check li{position:relative;padding-left:36px;font-size:16px;color:#1e293b;line-height:1.5}
.jb-check li::before{content:"✓";position:absolute;left:0;top:-1px;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:800;color:#fff;background:var(--accent,#2563eb)}
@media(max-width:860px){.jb-fs{grid-template-columns:1fr}}`);

add('services-6', 'Services — 6 tiles', FEAT,
  [[22,5,28,4,'d'],[5,14,19,13,'w',3],[27,14,19,13,'w',3],[49,14,19,13,'w',3],[5,30,19,13,'w',3],[27,30,19,13,'w',3],[49,30,19,13,'w',3]],
  `<section class="jb-sec"><div class="jb-wrap">
  <div class="jb-center"><span class="jb-kicker">Our services</span><h2 class="jb-h2">What we can do for you</h2></div>
  <div class="jb-grid jb-svc">
    <div class="jb-card"><div class="jb-ic">🎯</div><h3>Service one</h3><p>Short description and a starting price, e.g. from TZS 50,000.</p></div>
    <div class="jb-card"><div class="jb-ic">🧰</div><h3>Service two</h3><p>Short description and a starting price.</p></div>
    <div class="jb-card"><div class="jb-ic">🚚</div><h3>Service three</h3><p>Short description and a starting price.</p></div>
    <div class="jb-card"><div class="jb-ic">📦</div><h3>Service four</h3><p>Short description and a starting price.</p></div>
    <div class="jb-card"><div class="jb-ic">🤝</div><h3>Service five</h3><p>Short description and a starting price.</p></div>
    <div class="jb-card"><div class="jb-ic">🏆</div><h3>Service six</h3><p>Short description and a starting price.</p></div>
  </div>
</div></section>`,
  `.jb-svc .jb-card{transition:transform .2s,border-color .2s}.jb-svc .jb-card:hover{transform:translateY(-4px);border-color:var(--accent,#2563eb)}`);

add('steps', 'How it works — 3 steps', FEAT,
  [[22,6,28,4,'d'],[8,20,10,10,'a',5],[31,20,10,10,'a',5],[54,20,10,10,'a',5],[18,24,13,2,'l'],[41,24,13,2,'l'],[4,34,18,2,'l'],[27,34,18,2,'l'],[50,34,18,2,'l']],
  `<section class="jb-sec jb-soft"><div class="jb-wrap">
  <div class="jb-center"><span class="jb-kicker">How it works</span><h2 class="jb-h2">Three simple steps</h2></div>
  <div class="jb-steps">
    <div><b>1</b><h3>Tell us what you need</h3><p>Send a message on WhatsApp or fill in the form.</p></div>
    <div><b>2</b><h3>Get a clear quote</h3><p>We reply quickly with the price and timing.</p></div>
    <div><b>3</b><h3>Relax, it’s done</h3><p>We deliver on time and follow up to make sure you are happy.</p></div>
  </div>
</div></section>`,
  `.jb-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:52px;counter-reset:s}
.jb-steps>div{text-align:center;padding:10px}
.jb-steps b{display:inline-flex;width:58px;height:58px;border-radius:50%;align-items:center;justify-content:center;font-size:22px;
  color:#fff;background:var(--accent,#2563eb);box-shadow:0 0 0 8px color-mix(in srgb,var(--accent,#2563eb) 15%,transparent);margin-bottom:22px}
.jb-steps h3{font-size:19px;color:#0f172a;margin:0 0 8px}.jb-steps p{color:#475569;margin:0;line-height:1.6}
@media(max-width:760px){.jb-steps{grid-template-columns:1fr}}`);

// ───────────── SOCIAL PROOF ─────────────
add('stats', 'Numbers / stats', PROOF,
  [[0,12,72,24,'k',0],[6,18,12,6,'a'],[22,18,12,6,'a'],[38,18,12,6,'a'],[54,18,12,6,'a'],[6,27,12,2,'l'],[22,27,12,2,'l'],[38,27,12,2,'l'],[54,27,12,2,'l']],
  `<section class="jb-sec jb-dark jb-stats"><div class="jb-wrap jb-stats-in">
  <div><b>10+</b><span>Years of experience</span></div><div><b>2,500</b><span>Happy customers</span></div>
  <div><b>98%</b><span>Would recommend us</span></div><div><b>24/7</b><span>WhatsApp support</span></div>
</div></section>`,
  `.jb-stats{padding-top:clamp(50px,7vw,80px);padding-bottom:clamp(50px,7vw,80px)}
.jb-stats-in{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;text-align:center}
.jb-stats b{display:block;font-family:var(--font-head,inherit);font-size:clamp(36px,5vw,56px);font-weight:800;letter-spacing:-.03em;color:#fff}
.jb-stats b::first-letter{color:var(--accent,#2563eb)}
.jb-stats span{font-size:14px;color:#94a3b8}
@media(max-width:760px){.jb-stats-in{grid-template-columns:1fr 1fr;row-gap:34px}}`);

add('testimonials', 'Testimonials — 3 quotes', PROOF,
  [[22,5,28,4,'d'],[5,14,19,28,'w',3],[27,14,19,28,'w',3],[49,14,19,28,'w',3],[8,17,10,2,'a'],[30,17,10,2,'a'],[52,17,10,2,'a']],
  `<section class="jb-sec jb-soft"><div class="jb-wrap">
  <div class="jb-center"><span class="jb-kicker">Testimonials</span><h2 class="jb-h2">Loved by our customers</h2></div>
  <div class="jb-grid jb-quotes">
    <figure class="jb-card"><div class="jb-stars">★★★★★</div><blockquote>“Fast, friendly and exactly what I asked for. I recommend them to everyone.”</blockquote>
      <figcaption><span>AM</span><b>Asha M.</b><small>Dar es Salaam</small></figcaption></figure>
    <figure class="jb-card"><div class="jb-stars">★★★★★</div><blockquote>“They replied on WhatsApp within minutes and delivered the same day.”</blockquote>
      <figcaption><span>JK</span><b>John K.</b><small>Arusha</small></figcaption></figure>
    <figure class="jb-card"><div class="jb-stars">★★★★★</div><blockquote>“Great quality at a fair price. We will definitely come back.”</blockquote>
      <figcaption><span>NR</span><b>Neema R.</b><small>Mwanza</small></figcaption></figure>
  </div>
</div></section>`,
  `.jb-quotes figure{margin:0;display:flex;flex-direction:column;gap:18px}
.jb-stars{color:#f59e0b;letter-spacing:3px;font-size:16px}
.jb-quotes blockquote{margin:0;font-size:17px;line-height:1.65;color:#1e293b;flex:1}
.jb-quotes figcaption{display:grid;grid-template-columns:auto 1fr;column-gap:12px;align-items:center}
.jb-quotes figcaption span{grid-row:span 2;width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:14px;color:#fff;background:var(--accent,#2563eb)}
.jb-quotes figcaption b{color:#0f172a;font-size:15px}.jb-quotes figcaption small{color:#64748b}`);

add('logos', 'Logos / partners strip', PROOF,
  [[24,14,24,3,'l'],[4,26,12,6,'m',2],[18,26,12,6,'m',2],[32,26,12,6,'m',2],[46,26,12,6,'m',2],[60,26,8,6,'m',2]],
  `<section class="jb-sec jb-logos"><div class="jb-wrap jb-center">
  <p class="jb-logos-t">Trusted by teams and families across Tanzania</p>
  <div class="jb-logos-row"><span>Partner One</span><span>Company Two</span><span>Brand Three</span><span>Group Four</span><span>Studio Five</span></div>
</div></section>`,
  `.jb-logos{padding-top:48px;padding-bottom:48px;border-top:1px solid #eef1f5;border-bottom:1px solid #eef1f5}
.jb-logos-t{margin:0 0 22px;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:#94a3b8;font-weight:700}
.jb-logos-row{display:flex;flex-wrap:wrap;justify-content:center;gap:14px 44px}
.jb-logos-row span{font-family:var(--font-head,inherit);font-size:22px;font-weight:800;letter-spacing:-.02em;color:#94a3b8}`);

// ───────────── PRICING ─────────────
add('pricing', 'Pricing — 3 plans', PRICE,
  [[22,4,28,4,'d'],[5,13,19,31,'w',3],[27,11,19,35,'a',3],[49,13,19,31,'w',3],[9,18,10,4,'d'],[31,17,10,4,'#fff'],[53,18,10,4,'d']],
  `<section class="jb-sec jb-soft"><div class="jb-wrap">
  <div class="jb-center"><span class="jb-kicker">Pricing</span><h2 class="jb-h2">Simple, honest prices</h2><p class="jb-lead">Pick the package that fits you. No hidden costs.</p></div>
  <div class="jb-plans">
    <div class="jb-plan"><h3>Basic</h3><div class="jb-price">TZS 50,000<small>/month</small></div>
      <ul><li>First benefit</li><li>Second benefit</li><li>Third benefit</li></ul><a class="jb-btn2" href="[[site:whatsapp]]">Choose Basic</a></div>
    <div class="jb-plan jb-plan-hot"><span class="jb-badge">Most popular</span><h3>Standard</h3><div class="jb-price">TZS 120,000<small>/month</small></div>
      <ul><li>Everything in Basic</li><li>Extra benefit</li><li>Priority support</li><li>Another great benefit</li></ul><a class="jb-btn" href="[[site:whatsapp]]">Choose Standard</a></div>
    <div class="jb-plan"><h3>Premium</h3><div class="jb-price">TZS 250,000<small>/month</small></div>
      <ul><li>Everything in Standard</li><li>Dedicated manager</li><li>Custom work</li></ul><a class="jb-btn2" href="[[site:whatsapp]]">Choose Premium</a></div>
  </div>
</div></section>`,
  `.jb-plans{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:52px;align-items:stretch}
.jb-plan{position:relative;display:flex;flex-direction:column;background:#fff;border:1px solid #e2e8f0;border-radius:24px;padding:34px 30px;color:#0f172a}
.jb-plan h3{margin:0 0 10px;font-size:18px}
.jb-price{font-family:var(--font-head,inherit);font-size:34px;font-weight:800;letter-spacing:-.03em;margin-bottom:22px}
.jb-price small{font-size:14px;font-weight:600;color:#64748b;margin-left:4px}
.jb-plan ul{list-style:none;padding:0;margin:0 0 30px;display:flex;flex-direction:column;gap:12px;flex:1;color:#475569}
.jb-plan li::before{content:"✓";color:var(--accent,#2563eb);font-weight:800;margin-right:10px}
.jb-plan a{text-align:center}
.jb-plan-hot{background:#0b0f19;color:#fff;border-color:transparent;transform:scale(1.03);box-shadow:0 40px 80px rgba(15,23,42,.25)}
.jb-plan-hot ul{color:#cbd5e1}.jb-plan-hot .jb-price small{color:#94a3b8}
.jb-badge{position:absolute;top:-13px;left:50%;transform:translateX(-50%);background:var(--accent,#2563eb);color:#fff;font-size:12px;font-weight:700;
  padding:6px 14px;border-radius:999px;white-space:nowrap}
@media(max-width:900px){.jb-plans{grid-template-columns:1fr}.jb-plan-hot{transform:none}}`);

// ───────────── CONTENT ─────────────
add('about', 'About — story', CONT,
  [[5,10,28,6,'d'],[5,20,22,3,'a'],[40,10,26,2,'l'],[40,15,26,2,'l'],[40,20,26,2,'l'],[40,25,20,2,'l'],[40,32,26,2,'l'],[40,37,18,2,'l']],
  `<section class="jb-sec"><div class="jb-wrap jb-about">
  <div><span class="jb-kicker">Our story</span><h2 class="jb-h2">Started with one idea: do it properly</h2></div>
  <div><p class="jb-lead">Tell visitors how your business started, what you believe in, and the people behind it. Real stories build trust faster than anything else.</p>
    <p class="jb-lead" style="margin-top:18px">Add a second paragraph about your promise to customers and where you are going next.</p></div>
</div></section>`,
  `.jb-about{display:grid;grid-template-columns:1fr 1.2fr;gap:clamp(24px,6vw,80px);align-items:start}
@media(max-width:820px){.jb-about{grid-template-columns:1fr}}`);

add('team', 'Team — 4 people', CONT,
  [[22,4,28,4,'d'],[6,14,13,13,'w',7],[23,14,13,13,'w',7],[40,14,13,13,'w',7],[57,14,13,13,'w',7],[6,31,13,2,'d'],[23,31,13,2,'d'],[40,31,13,2,'d'],[57,31,13,2,'d']],
  `<section class="jb-sec"><div class="jb-wrap">
  <div class="jb-center"><span class="jb-kicker">Our team</span><h2 class="jb-h2">The people behind [[site:name]]</h2></div>
  <div class="jb-team">
    <div><img src="${PH(400, 400, 'Photo')}" alt=""><h3>Full Name</h3><p>Founder & CEO</p></div>
    <div><img src="${PH(400, 400, 'Photo')}" alt=""><h3>Full Name</h3><p>Operations</p></div>
    <div><img src="${PH(400, 400, 'Photo')}" alt=""><h3>Full Name</h3><p>Customer care</p></div>
    <div><img src="${PH(400, 400, 'Photo')}" alt=""><h3>Full Name</h3><p>Sales</p></div>
  </div>
</div></section>`,
  `.jb-team{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-top:52px;text-align:center}
.jb-team img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:24px;margin-bottom:16px}
.jb-team h3{margin:0;font-size:17px;color:#0f172a}.jb-team p{margin:4px 0 0;color:#64748b;font-size:14px}
@media(max-width:860px){.jb-team{grid-template-columns:1fr 1fr}}`);

add('faq', 'FAQ — questions', CONT,
  [[22,4,28,4,'d'],[8,14,56,6,'w',2],[8,22,56,6,'w',2],[8,30,56,6,'w',2],[8,38,56,6,'w',2],[58,16,3,2,'a'],[58,24,3,2,'a']],
  `<section class="jb-sec jb-soft"><div class="jb-wrap jb-faq">
  <div class="jb-center"><span class="jb-kicker">FAQ</span><h2 class="jb-h2">Questions customers ask</h2></div>
  <details open><summary>How do I order or book?</summary><p>Tap the WhatsApp button or fill in the contact form — we reply fast.</p></details>
  <details><summary>How much does it cost?</summary><p>Explain your prices or give a starting price, and say what affects it.</p></details>
  <details><summary>Which payment methods do you accept?</summary><p>M-Pesa, Tigo Pesa, Airtel Money, bank transfer or cash.</p></details>
  <details><summary>Where are you located?</summary><p>[[site:address]] — we also serve customers outside town.</p></details>
</div></section>`,
  `.jb-faq{max-width:820px}
.jb-faq .jb-center{margin-bottom:40px}
.jb-faq details{background:#fff;border:1px solid #e2e8f0;border-radius:16px;margin-bottom:12px;padding:0 24px;transition:box-shadow .2s}
.jb-faq details[open]{box-shadow:0 14px 34px rgba(15,23,42,.07)}
.jb-faq summary{cursor:pointer;list-style:none;padding:20px 0;font-weight:700;font-size:17px;color:#0f172a;display:flex;justify-content:space-between;gap:16px}
.jb-faq summary::-webkit-details-marker{display:none}
.jb-faq summary::after{content:"+";font-size:24px;line-height:1;color:var(--accent,#2563eb);transition:transform .2s}
.jb-faq details[open] summary::after{transform:rotate(45deg)}
.jb-faq details p{margin:0;padding:0 0 20px;color:#475569;line-height:1.65}`);

add('gallery', 'Gallery — 6 photos', CONT,
  [[22,4,28,4,'d'],[5,13,20,15,'w',2],[27,13,20,15,'w',2],[49,13,18,15,'w',2],[5,30,20,14,'w',2],[27,30,20,14,'w',2],[49,30,18,14,'w',2]],
  `<section class="jb-sec"><div class="jb-wrap">
  <div class="jb-center"><span class="jb-kicker">Gallery</span><h2 class="jb-h2">A look at our work</h2></div>
  <div class="jb-gal">
    <img src="${PH(800, 600, 'Photo 1')}" alt=""><img src="${PH(800, 600, 'Photo 2')}" alt=""><img src="${PH(800, 600, 'Photo 3')}" alt="">
    <img src="${PH(800, 600, 'Photo 4')}" alt=""><img src="${PH(800, 600, 'Photo 5')}" alt=""><img src="${PH(800, 600, 'Photo 6')}" alt="">
  </div>
</div></section>`,
  `.jb-gal{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:48px}
.jb-gal img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:18px;transition:transform .3s}
.jb-gal img:hover{transform:scale(1.02)}
@media(max-width:760px){.jb-gal{grid-template-columns:1fr 1fr;gap:10px}}`);

add('video', 'Video (YouTube)', CONT,
  [[22,4,28,4,'d'],[10,12,52,30,'k',3],[31,22,10,10,'a',5]],
  `<section class="jb-sec"><div class="jb-wrap jb-center">
  <span class="jb-kicker">Watch</span><h2 class="jb-h2">See us in action</h2>
  <div class="jb-video"><iframe src="https://www.youtube.com/embed/ScMzIvxBSi4" title="Video" loading="lazy" allowfullscreen
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe></div>
  <p class="jb-lead" style="margin-top:18px">To use your own video: select the video and change its link in Settings (⚙).</p>
</div></section>`,
  `.jb-video{position:relative;aspect-ratio:16/9;border-radius:22px;overflow:hidden;margin-top:36px;box-shadow:0 40px 90px rgba(15,23,42,.2);background:#0b0f19}
.jb-video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}`);

// ───────────── CONTACT & CTA ─────────────
add('cta-band', 'Call to action band', CTA,
  [[0,10,72,28,'a',0],[8,17,34,5,'#fff'],[8,25,26,2,'#fff'],[50,19,16,8,'#fff',4]],
  `<section class="jb-sec jb-cta"><div class="jb-wrap jb-cta-in">
  <div><h2 class="jb-h2">Ready to get started?</h2><p class="jb-lead">Message us now and get an answer in minutes.</p></div>
  <div class="jb-btns"><a class="jb-btn" href="[[site:whatsapp]]">Chat on WhatsApp</a><a class="jb-btn2" href="/p/contact/">Contact us</a></div>
</div></section>`,
  `.jb-cta{background:radial-gradient(700px 300px at 90% 0%,rgba(255,255,255,.2),transparent 70%),var(--accent,#2563eb);color:#fff}
.jb-cta-in{display:flex;align-items:center;justify-content:space-between;gap:28px;flex-wrap:wrap}
.jb-cta .jb-h2{color:#fff;margin-bottom:8px}.jb-cta .jb-lead{color:rgba(255,255,255,.9)}
.jb-cta .jb-btns{margin-top:0}
.jb-cta .jb-btn{background:#fff;color:var(--accent,#2563eb);box-shadow:0 14px 34px rgba(0,0,0,.18)}`);

add('whatsapp', 'WhatsApp card', CTA,
  [[10,10,52,28,'g',6],[16,16,8,8,'#fff',4],[28,17,26,3,'#fff'],[28,23,18,2,'#fff'],[16,29,20,5,'#075e54',2]],
  `<section class="jb-sec"><div class="jb-wrap"><div class="jb-wa">
  <div class="jb-wa-ic">💬</div>
  <div class="jb-wa-tx"><h2>Questions? Chat with us on WhatsApp</h2><p>We usually reply within minutes — in Swahili or English.</p></div>
  <a class="jb-wa-btn" href="[[site:whatsapp]]">Start chat →</a>
</div></div></section>`,
  `.jb-wa{display:flex;align-items:center;gap:24px;flex-wrap:wrap;padding:clamp(26px,4vw,44px);border-radius:28px;color:#fff;
  background:linear-gradient(135deg,#25d366,#128c7e);box-shadow:0 30px 70px rgba(18,140,126,.3)}
.jb-wa-ic{width:72px;height:72px;border-radius:22px;background:rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center;font-size:36px}
.jb-wa-tx{flex:1;min-width:220px}.jb-wa-tx h2{margin:0 0 6px;font-size:clamp(22px,3vw,30px);letter-spacing:-.02em;color:#fff}
.jb-wa-tx p{margin:0;opacity:.9}
.jb-wa-btn{background:#fff;color:#075e54;font-weight:800;padding:15px 28px;border-radius:14px;text-decoration:none}`);

add('contact', 'Contact — details + map', CTA,
  [[5,8,28,4,'d'],[5,17,4,4,'a',2],[11,18,18,2,'l'],[5,24,4,4,'a',2],[11,25,18,2,'l'],[5,31,4,4,'a',2],[11,32,18,2,'l'],[38,8,29,32,'#cbd5e1',4]],
  `<section class="jb-sec jb-soft"><div class="jb-wrap jb-contact">
  <div><span class="jb-kicker">Contact</span><h2 class="jb-h2">Come visit or say hello</h2>
    <ul class="jb-cl"><li><span>📞</span><div><b>Phone</b>[[site:phone]]</div></li><li><span>✉️</span><div><b>Email</b>[[site:email]]</div></li>
      <li><span>📍</span><div><b>Address</b>[[site:address]]</div></li><li><span>🕘</span><div><b>Hours</b>Mon – Sat, 8:00 – 18:00</div></li></ul>
    <div class="jb-btns"><a class="jb-btn" href="[[site:whatsapp]]">WhatsApp us</a></div></div>
  <div class="jb-map"><iframe src="https://www.google.com/maps?q=Dar%20es%20Salaam&output=embed" title="Map" loading="lazy"></iframe></div>
</div></section>`,
  `.jb-contact{display:grid;grid-template-columns:1fr 1.1fr;gap:clamp(28px,5vw,64px);align-items:stretch}
.jb-cl{list-style:none;padding:0;margin:28px 0 0;display:flex;flex-direction:column;gap:18px}
.jb-cl li{display:flex;gap:14px;align-items:flex-start;color:#0f172a;font-weight:600}
.jb-cl span{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:19px;flex-shrink:0;
  background:color-mix(in srgb,var(--accent,#2563eb) 12%,#fff)}
.jb-cl b{display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#64748b;font-weight:700;margin-bottom:2px}
.jb-map{min-height:360px;border-radius:24px;overflow:hidden;box-shadow:0 30px 70px rgba(15,23,42,.12)}
.jb-map iframe{width:100%;height:100%;min-height:360px;border:0;display:block}
@media(max-width:860px){.jb-contact{grid-template-columns:1fr}}`);

// ───────────── LAYOUT ─────────────
add('section', 'Empty section', LAY, [[4,8,64,32,'w',3],[26,21,20,6,'l',2]],
  `<section class="jb-sec"><div class="jb-wrap"><h2 class="jb-h2">New section</h2><p class="jb-lead">Drag blocks in here or type your text.</p></div></section>`);
add('cols-2', '2 columns', LAY, [[4,8,31,32,'w',3],[37,8,31,32,'w',3]],
  `<section class="jb-sec"><div class="jb-wrap jb-cols jb-c2"><div><h3>Column one</h3><p>Text for the first column.</p></div><div><h3>Column two</h3><p>Text for the second column.</p></div></div></section>`,
  `.jb-cols{display:grid;gap:clamp(20px,4vw,48px)}.jb-c2{grid-template-columns:1fr 1fr}.jb-c3{grid-template-columns:repeat(3,1fr)}
.jb-cols h3{margin:0 0 8px;font-size:20px;color:#0f172a}.jb-cols p{margin:0;color:#475569;line-height:1.65}
@media(max-width:760px){.jb-c2,.jb-c3{grid-template-columns:1fr}}`);
add('cols-3', '3 columns', LAY, [[4,8,20,32,'w',3],[26,8,20,32,'w',3],[48,8,20,32,'w',3]],
  `<section class="jb-sec"><div class="jb-wrap jb-cols jb-c3"><div><h3>Column one</h3><p>Text here.</p></div><div><h3>Column two</h3><p>Text here.</p></div><div><h3>Column three</h3><p>Text here.</p></div></div></section>`,
  `.jb-cols{display:grid;gap:clamp(20px,4vw,48px)}.jb-c2{grid-template-columns:1fr 1fr}.jb-c3{grid-template-columns:repeat(3,1fr)}
.jb-cols h3{margin:0 0 8px;font-size:20px;color:#0f172a}.jb-cols p{margin:0;color:#475569;line-height:1.65}
@media(max-width:760px){.jb-c2,.jb-c3{grid-template-columns:1fr}}`);
add('spacer', 'Spacer', LAY, [[4,22,64,4,'m',2]], `<div class="jb-spacer"></div>`, `.jb-spacer{height:64px}`);
add('divider', 'Divider line', LAY, [[8,23,56,2,'l']], `<div class="jb-wrap"><hr class="jb-hr"></div>`,
  `.jb-hr{border:0;height:1px;background:#e2e8f0;margin:24px 0}`);
add('button', 'Button', LAY, [[22,18,28,12,'a',6]], `<div class="jb-btns jb-center" style="margin:20px 0"><a class="jb-btn" href="[[site:whatsapp]]">Click me</a></div>`);
add('embed', 'Custom HTML / embed', LAY, [[8,10,56,28,'k',3],[14,16,12,2,'a'],[14,21,30,2,'l'],[14,26,24,2,'l'],[14,31,14,2,'v']],
  `<div class="jb-embed" data-gjs-type="default"><p style="margin:0;padding:24px;border:2px dashed #94a3b8;border-radius:14px;text-align:center;color:#64748b">
  Select this box and open <b>&lt;/&gt; Code</b> to paste any HTML — a form, a booking widget or a map.</p></div>`);
})();
{% endverbatim %}
