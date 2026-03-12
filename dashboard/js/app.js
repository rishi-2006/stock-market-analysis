/* ─────────────────────────────────────────────
   app.js  –  SPA Router, Sidebar, Theme toggle
───────────────────────────────────────────── */

// ── Page definitions ──────────────────────────
const pages = [
    { id: 'dashboard', label: 'Dashboard', icon: 'layout-dashboard' },
    { id: 'analysis', label: 'Stock Analysis', icon: 'bar-chart-2' },
    { id: 'predictions', label: 'AI Predictions', icon: 'brain' },
    { id: 'compare', label: 'Compare Companies', icon: 'git-compare' },
    { id: 'lstm', label: 'LSTM Model', icon: 'activity' },
    { id: 'reports', label: 'Reports', icon: 'file-text' },
    { id: 'settings', label: 'Settings', icon: 'settings' },
];

let currentPage = 'dashboard';

// ── Navigate ───────────────────────────────────
function navigate(pageId) {
    currentPage = pageId;

    // Toggle active section
    document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(`page-${pageId}`);
    if (target) target.classList.add('active');

    // Highlight nav item
    document.querySelectorAll('.nav-item').forEach(n => {
        n.classList.toggle('active', n.dataset.page === pageId);
    });

    // Update page header breadcrumb
    const h = pages.find(p => p.id === pageId);
    const el = document.getElementById('page-title-text');
    if (el && h) el.textContent = h.label;

    // Close mobile sidebar
    closeMobileSidebar();

    // Scroll to top
    document.querySelector('.main-content').scrollTo(0, 0);

    // Fire page-specific init
    if (window[`init_${pageId}`]) window[`init_${pageId}`]();
}

// ── Sidebar mobile ──────────────────────────────
function openMobileSidebar() {
    document.querySelector('.sidebar').classList.add('open');
    document.querySelector('.sidebar-overlay').classList.add('show');
}
function closeMobileSidebar() {
    document.querySelector('.sidebar').classList.remove('open');
    document.querySelector('.sidebar-overlay').classList.remove('show');
}

// ── Theme toggle ────────────────────────────────
let darkMode = true;
function toggleTheme() {
    darkMode = !darkMode;
    document.body.classList.toggle('light-theme', !darkMode);
    const btn = document.getElementById('theme-btn');
    if (btn) {
        btn.innerHTML = darkMode
            ? '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>'
            : '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>';
    }
    // sync settings toggle
    const settingsToggle = document.getElementById('theme-toggle-settings');
    if (settingsToggle) settingsToggle.checked = darkMode;
}

// ── Ticker search ───────────────────────────────
function handleSearch(e) {
    if (e.key === 'Enter') {
        const val = e.target.value.trim().toUpperCase();
        if (val) {
            navigate('analysis');
            const tickerInput = document.getElementById('analysis-ticker-input');
            if (tickerInput) {
                tickerInput.value = val;
                runAnalysis(val);
            }
        }
    }
}

// ── Format numbers ──────────────────────────────
function fmt(n, decimals = 2) {
    if (n === null || n === undefined) return '—';
    return Number(n).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}
function fmtPct(n) { return (n >= 0 ? '+' : '') + fmt(n) + '%'; }
function fmtK(n) {
    if (Math.abs(n) >= 1e9) return (n / 1e9).toFixed(1) + 'B';
    if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(1) + 'M';
    if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(1) + 'K';
    return n;
}

// ── Animate counter ─────────────────────────────
function animateCounter(el, end, duration = 900, prefix = '', suffix = '') {
    const start = 0;
    const range = end - start;
    const step = 16;
    const steps = Math.ceil(duration / step);
    let cur = 0;
    const timer = setInterval(() => {
        cur++;
        const val = Math.round(easeOut(cur / steps) * range + start);
        el.textContent = prefix + val.toLocaleString() + suffix;
        if (cur >= steps) { clearInterval(timer); el.textContent = prefix + end.toLocaleString() + suffix; }
    }, step);
}
function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

// ── Boot ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Wire nav items
    document.querySelectorAll('.nav-item[data-page]').forEach(item => {
        item.addEventListener('click', () => navigate(item.dataset.page));
    });

    // Hamburger
    const hbg = document.querySelector('.hamburger');
    if (hbg) hbg.addEventListener('click', openMobileSidebar);

    // Overlay
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) overlay.addEventListener('click', closeMobileSidebar);

    // Theme btn
    const themeBtnEl = document.getElementById('theme-btn');
    if (themeBtnEl) themeBtnEl.addEventListener('click', toggleTheme);

    // Search
    const searchEl = document.getElementById('main-search');
    if (searchEl) searchEl.addEventListener('keydown', handleSearch);

    // Analyse button in topnav
    const analyseBtn = document.getElementById('analyse-btn');
    if (analyseBtn) analyseBtn.addEventListener('click', () => {
        const val = document.getElementById('main-search')?.value.trim().toUpperCase() || 'AAPL';
        navigate('analysis');
        const tickerInput = document.getElementById('analysis-ticker-input');
        if (tickerInput) { tickerInput.value = val; runAnalysis(val); }
    });

    // Compare btn
    const compareBtn = document.getElementById('compare-btn');
    if (compareBtn) compareBtn.addEventListener('click', () => navigate('compare'));

    // Settings theme toggle sync
    const st = document.getElementById('theme-toggle-settings');
    if (st) {
        st.checked = true; // dark = default
        st.addEventListener('change', toggleTheme);
    }

    // Start on dashboard
    navigate('dashboard');
});
