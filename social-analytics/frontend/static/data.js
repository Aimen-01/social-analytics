// ================================================================
//  SocialMetrics Pro — Shared Dummy Data & Utilities
// ================================================================

const POSTS_DATA = [
  { id:1,  platform:'Instagram', content:'Exploring the mountains at dawn 🏔️ The view from the top was breathtaking — nature at its finest.', type:'Image', date:'2026-05-10', likes:12840, comments:342, shares:218,  reach:84200,  hashtags:['travel','adventure','nature'] },
  { id:2,  platform:'Facebook',  content:'Our new product launch is finally here! Check it out and share your thoughts in the comments below.',   type:'Video', date:'2026-05-09', likes:9420,  comments:634, shares:891,  reach:126000, hashtags:['product','launch','newproduct'] },
  { id:3,  platform:'YouTube',   content:'FULL TUTORIAL: Build a social media dashboard from scratch — 2 hours of hands-on content for beginners!', type:'Video', date:'2026-05-08', likes:18200, comments:1240,shares:2100, reach:312000, hashtags:['tutorial','coding','webdev'] },
  { id:4,  platform:'Twitter',   content:'Hot take: engagement rate matters more than follower count. Here\'s why quality beats quantity every time 👇', type:'Text',  date:'2026-05-08', likes:3210,  comments:580, shares:1420, reach:48000,  hashtags:['marketing','socialmedia','growth'] },
  { id:5,  platform:'Instagram', content:'30-second morning routine that completely changed my productivity. Save this for tomorrow morning! ✨',   type:'Reel',  date:'2026-05-07', likes:15600, comments:890, shares:3200, reach:198000, hashtags:['wellness','morningroutine','health'] },
  { id:6,  platform:'Facebook',  content:'Behind the scenes of our team retreat in Bali 🌴 What an incredible week of creativity and connection!',   type:'Image', date:'2026-05-07', likes:7800,  comments:312, shares:145,  reach:62400,  hashtags:['teamwork','bali','retreat'] },
  { id:7,  platform:'Twitter',   content:'Just crossed 100K followers on Twitter! 🎉 Thank you all so much for the love. Dropping an AMA shortly.',  type:'Image', date:'2026-05-06', likes:4320,  comments:920, shares:540,  reach:58000,  hashtags:['milestone','grateful','AMA'] },
  { id:8,  platform:'YouTube',   content:'The truth about AI replacing jobs — a data-driven analysis of 50 industries in 2026. You need to see this.',  type:'Video', date:'2026-05-06', likes:11500, comments:2840,shares:1680, reach:224000, hashtags:['AI','future','jobs','tech'] },
  { id:9,  platform:'Instagram', content:'New city, new vibes 🌆 Arrived in Tokyo and the energy here is absolutely electric. Day 1 vlog incoming!',   type:'Video', date:'2026-05-05', likes:8900,  comments:278, shares:190,  reach:71200,  hashtags:['tokyo','travel','japan'] },
  { id:10, platform:'Facebook',  content:'We\'re hiring! Looking for a passionate Social Media Manager to join our growing team. DM for details.',     type:'Text',  date:'2026-05-05', likes:2100,  comments:480, shares:720,  reach:42000,  hashtags:['hiring','jobs','remotework'] },
  { id:11, platform:'Instagram', content:'Golden hour magic 🌅 Sometimes all you need is perfect light and a steady hand. No filters, no edits.',        type:'Image', date:'2026-05-04', likes:6700,  comments:198, shares:84,   reach:53600,  hashtags:['photography','sunset','goldenhour'] },
  { id:12, platform:'Twitter',   content:'5 things you\'re doing wrong on social media that are killing your growth in 2026 🧵 (read the thread)',       type:'Text',  date:'2026-05-04', likes:5400,  comments:340, shares:2100, reach:76000,  hashtags:['socialmedia','branding','marketing'] },
  { id:13, platform:'Facebook',  content:'Our CEO sat down for a candid interview about the future of remote work — honest and unfiltered. Full video.',   type:'Video', date:'2026-05-03', likes:8300,  comments:520, shares:340,  reach:89000,  hashtags:['remotework','leadership','future'] },
  { id:14, platform:'Instagram', content:'Reading challenge: 12 books in 12 months. Month 5 update and my top picks so far 📚 Drop yours below!',       type:'Text',  date:'2026-05-03', likes:1200,  comments:340, shares:92,   reach:18400,  hashtags:['books','reading','challenge'] },
  { id:15, platform:'YouTube',   content:'React vs Vue vs Angular in 2026 — which should you learn first? An honest, unbiased comparison with demos.',    type:'Video', date:'2026-05-02', likes:9800,  comments:1820,shares:920,  reach:186000, hashtags:['react','vue','angular','webdev'] },
  { id:16, platform:'Twitter',   content:'Reminder: consistency beats perfection every single time. Post daily for 30 days and watch the magic happen.',   type:'Image', date:'2026-05-02', likes:3900,  comments:210, shares:980,  reach:52000,  hashtags:['consistency','growth','mindset'] },
  { id:17, platform:'Facebook',  content:'Client success story: How we helped BrandX grow from 0 to 50K followers in just 90 days — full case study.',  type:'Image', date:'2026-05-01', likes:5600,  comments:280, shares:430,  reach:68000,  hashtags:['casestudy','success','growth'] },
  { id:18, platform:'Instagram', content:'Our top 5 social media tips condensed into 60 seconds 🚀 Save and share if this was helpful! #tips',           type:'Reel',  date:'2026-05-01', likes:11200, comments:620, shares:2480, reach:142000, hashtags:['tips','growth','instagram'] },
  { id:19, platform:'Twitter',   content:'The algorithm doesn\'t hate you. You\'re just not giving it what it needs. Full breakdown thread 👇',           type:'Text',  date:'2026-04-30', likes:2800,  comments:390, shares:1240, reach:44000,  hashtags:['algorithm','twitter','growthhack'] },
  { id:20, platform:'Facebook',  content:'The best marketing is solving real problems, not just selling products. Share if you agree! 💡',               type:'Text',  date:'2026-04-30', likes:1800,  comments:420, shares:830,  reach:38000,  hashtags:['marketing','philosophy','business'] },
  { id:21, platform:'YouTube',   content:'I tested every major AI writing tool for 30 days — here\'s what actually works for content creators in 2026.',   type:'Video', date:'2026-04-29', likes:14200, comments:2100,shares:1820, reach:264000, hashtags:['AI','content','writing','tools'] },
  { id:22, platform:'Instagram', content:'Coffee + creativity = today\'s content batch ☕ Filming 2 weeks of content in one day! #contentcreator',         type:'Reel',  date:'2026-04-29', likes:7400,  comments:280, shares:420,  reach:59200,  hashtags:['contentcreator','behindthescenes','coffee'] },
  { id:23, platform:'Twitter',   content:'Most analytics dashboards measure the wrong things. Here\'s what actually predicts revenue growth 🧵',          type:'Text',  date:'2026-04-28', likes:4100,  comments:680, shares:1600, reach:62000,  hashtags:['analytics','metrics','revenue','marketing'] },
  { id:24, platform:'Facebook',  content:'Proud to announce our partnership with TechCorp! Together we\'ll reach 10 million people before year end.',    type:'Image', date:'2026-04-28', likes:6200,  comments:340, shares:280,  reach:74000,  hashtags:['partnership','announcement','growth'] },
  { id:25, platform:'Instagram', content:'What\'s your content strategy for Q3? Drop your answer below 👇 Let\'s build something together! #community',  type:'Image', date:'2026-04-27', likes:3800,  comments:560, shares:120,  reach:44800,  hashtags:['community','strategy','Q3'] },
];

// ── Utilities ──────────────────────────────────────────────────────

function getPltClass(p) {
  return { Facebook:'plt-fb', Instagram:'plt-ig', Twitter:'plt-tw', YouTube:'plt-yt' }[p] || 'plt-fb';
}

function getTypClass(t) {
  return { Image:'typ-image', Video:'typ-video', Text:'typ-text', Reel:'typ-reel' }[t] || 'typ-image';
}

function pltBadge(p)  { return `<span class="plt ${getPltClass(p)}">${p}</span>`; }
function typBadge(t)  { return `<span class="typ ${getTypClass(t)}">${t}</span>`; }
function fmtNum(n)    { return n >= 1000 ? (n/1000).toFixed(1).replace(/\.0$/,'') + 'K' : n.toLocaleString(); }
function fmtReach(n)  { return n >= 1000000 ? (n/1000000).toFixed(2) + 'M' : fmtNum(n); }

// Sidebar mobile toggle (shared)
function initSidebar() {
  const btn     = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');
  if (!btn) return;
  const toggle = (state) => {
    sidebar.classList.toggle('open', state);
    overlay.classList.toggle('open', state);
  };
  btn.addEventListener('click', () => toggle(!sidebar.classList.contains('open')));
  overlay.addEventListener('click', () => toggle(false));
}

// Toast notification
function toast(msg, type = 'inf') {
  let box = document.getElementById('toastBox');
  if (!box) {
    box = document.createElement('div');
    box.id = 'toastBox';
    box.className = 'toast-box';
    document.body.appendChild(box);
  }
  const icons = { ok:'✓', err:'✕', inf:'ℹ' };
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span style="font-weight:700;font-size:0.95rem">${icons[type]||'●'}</span><span>${msg}</span>`;
  box.appendChild(el);
  setTimeout(() => {
    el.style.animation = 'toastOut 0.25s ease forwards';
    setTimeout(() => el.remove(), 260);
  }, 3000);
}

// Chart.js shared defaults
function initChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.color          = '#8892a4';
  Chart.defaults.borderColor    = 'rgba(42,45,62,0.6)';
  Chart.defaults.font.family    = "'Inter', -apple-system, sans-serif";
  Chart.defaults.font.size      = 12;
  Chart.defaults.plugins.tooltip.backgroundColor = '#1A1D27';
  Chart.defaults.plugins.tooltip.borderColor      = '#2a2d3e';
  Chart.defaults.plugins.tooltip.borderWidth      = 1;
  Chart.defaults.plugins.tooltip.titleColor       = '#E2E8F0';
  Chart.defaults.plugins.tooltip.bodyColor        = '#8892a4';
  Chart.defaults.plugins.tooltip.padding          = 12;
  Chart.defaults.plugins.tooltip.cornerRadius     = 8;
}
