/* ─────────────────────────────────────────────
   charts.js  –  All Chart.js chart factories
   Requires Chart.js loaded via CDN
───────────────────────────────────────────── */

// ── Global Chart defaults ──────────────────────
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = '#334155';
Chart.defaults.font.family = "'Inter', sans-serif";

// ── Color palette helpers ──────────────────────
const C = {
    accent: '#3b82f6',
    success: '#22c55e',
    danger: '#ef4444',
    amber: '#f59e0b',
    purple: '#a855f7',
    teal: '#14b8a6',
    pink: '#ec4899',
    orange: '#f97316',
    accentAlpha: (a) => `rgba(59,130,246,${a})`,
    successAlpha: (a) => `rgba(34,197,94,${a})`,
    dangerAlpha: (a) => `rgba(239,68,68,${a})`,
};

const MULTI_COLORS = [C.accent, C.success, C.orange, C.purple, C.pink, C.teal];

// ── Demo data generators ───────────────────────
function genPriceSeries(n = 504, start = 170, vol = 3) {
    const d = []; let p = start;
    const today = new Date(); today.setHours(0, 0, 0, 0);
    for (let i = n; i >= 0; i--) {
        const dt = new Date(today); dt.setDate(dt.getDate() - i);
        if (dt.getDay() === 0 || dt.getDay() === 6) continue;
        p = Math.max(p + (Math.random() - 0.48) * vol, 10);
        d.push({ x: dt.toISOString().slice(0, 10), y: parseFloat(p.toFixed(2)) });
    }
    return d;
}
function sma(data, n) {
    return data.map((pt, i) => {
        if (i < n - 1) return { x: pt.x, y: null };
        const slice = data.slice(i - n + 1, i + 1).map(d => d.y);
        return { x: pt.x, y: parseFloat((slice.reduce((a, b) => a + b, 0) / n).toFixed(2)) };
    });
}
function genVolume(prices) {
    return prices.map(pt => ({
        x: pt.x,
        y: Math.floor(50e6 + Math.random() * 120e6)
    }));
}
function genSparkline(n = 20, up = true) {
    const d = []; let v = 100;
    for (let i = 0; i < n; i++) {
        v += (Math.random() - (up ? 0.38 : 0.62)) * 5;
        d.push(parseFloat(v.toFixed(2)));
    }
    return d;
}

// ── Destroy + recreate helper ──────────────────
const _instances = {};
function getOrCreate(id, config) {
    if (_instances[id]) { _instances[id].destroy(); }
    const ctx = document.getElementById(id);
    if (!ctx) return null;
    _instances[id] = new Chart(ctx, config);
    return _instances[id];
}

// ─────────────────────────────────────────────
// SPARKLINE (tiny inline chart for KPI cards)
// ─────────────────────────────────────────────
function createSparkline(canvasId, data, color) {
    return getOrCreate(canvasId, {
        type: 'line',
        data: {
            labels: data.map((_, i) => i),
            datasets: [{
                data, borderColor: color, borderWidth: 2,
                fill: true,
                backgroundColor: color.replace('rgb', 'rgba').replace(')', ',0.15)') || color + '25',
                pointRadius: 0, tension: 0.4
            }]
        },
        options: {
            animation: false, responsive: true, maintainAspectRatio: false,
            scales: { x: { display: false }, y: { display: false } },
            plugins: { legend: { display: false }, tooltip: { enabled: false } }
        }
    });
}

// ─────────────────────────────────────────────
// MAIN PRICE CHART  (line + SMA overlays)
// ─────────────────────────────────────────────
const _priceData = genPriceSeries(504, 172, 3.2);
const _sma20 = sma(_priceData, 20);
const _sma50 = sma(_priceData, 50);

function createPriceChart(canvasId, windowDays = 252) {
    const sliced = _priceData.slice(-windowDays);
    const s20 = _sma20.slice(-windowDays);
    const s50 = _sma50.slice(-windowDays);
    const labels = sliced.map(d => d.x);
    const close = sliced.map(d => d.y);
    const sma20v = s20.map(d => d.y);
    const sma50v = s50.map(d => d.y);

    return getOrCreate(canvasId, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Close', data: close, borderColor: C.accent, borderWidth: 2.2,
                    fill: true,
                    backgroundColor: (ctx) => {
                        const c = ctx.chart.ctx, h = ctx.chart.height;
                        const g = c.createLinearGradient(0, 0, 0, h);
                        g.addColorStop(0, C.accentAlpha(0.25));
                        g.addColorStop(1, C.accentAlpha(0.0));
                        return g;
                    },
                    pointRadius: 0, tension: 0.3
                },
                {
                    label: 'SMA 20', data: sma20v, borderColor: C.amber, borderWidth: 1.5,
                    pointRadius: 0, tension: 0.3, fill: false, borderDash: []
                },
                {
                    label: 'SMA 50', data: sma50v, borderColor: C.purple, borderWidth: 1.5,
                    pointRadius: 0, tension: 0.3, fill: false, borderDash: [5, 3]
                }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            animation: { duration: 600, easing: 'easeInOutQuart' },
            scales: {
                x: { grid: { color: '#1e293b' }, ticks: { maxTicksLimit: 8, font: { size: 11 } } },
                y: {
                    grid: { color: '#1e293b' }, ticks: {
                        callback: v => '$' + v.toLocaleString(),
                        font: { size: 11 }
                    }
                }
            },
            plugins: {
                legend: { position: 'top', labels: { usePointStyle: true, pointStyleWidth: 12, padding: 18, font: { size: 12 } } },
                tooltip: {
                    backgroundColor: '#1e293b',
                    borderColor: '#334155', borderWidth: 1,
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: $${ctx.parsed.y?.toFixed(2) ?? '—'}` }
                }
            }
        }
    });
}

// ─────────────────────────────────────────────
// VOLUME CHART
// ─────────────────────────────────────────────
function createVolumeChart(canvasId, windowDays = 60) {
    const sliced = _priceData.slice(-windowDays);
    const vols = genVolume(sliced);
    const colors = sliced.map((d, i) =>
        i === 0 ? C.accentAlpha(0.6) :
            d.y >= sliced[i - 1].y ? C.successAlpha(0.7) : C.dangerAlpha(0.7)
    );

    return getOrCreate(canvasId, {
        type: 'bar',
        data: {
            labels: vols.map(d => d.x),
            datasets: [{
                label: 'Volume', data: vols.map(d => d.y),
                backgroundColor: colors, borderRadius: 3, borderSkipped: false
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => ' Vol: ' + fmtK(ctx.parsed.y) } }
            },
            scales: {
                x: { grid: { display: false }, ticks: { maxTicksLimit: 8, font: { size: 11 } } },
                y: { grid: { color: '#1e293b' }, ticks: { callback: v => fmtK(v), font: { size: 11 } } }
            },
            animation: { duration: 500 }
        }
    });
}

// ─────────────────────────────────────────────
// FEATURE IMPORTANCE CHART  (horizontal bar)
// ─────────────────────────────────────────────
function createFeatureImportanceChart(canvasId) {
    const features = ['SMA 5', 'Return', 'EMA 10', 'SMA 10', 'Vol Change'];
    const values = [0.312, 0.268, 0.198, 0.142, 0.080];

    return getOrCreate(canvasId, {
        type: 'bar',
        data: {
            labels: features,
            datasets: [{
                label: 'Importance', data: values,
                backgroundColor: features.map((_, i) =>
                    `hsl(${220 + i * 18}, 80%, ${65 - i * 8}%)`),
                borderRadius: 6, borderSkipped: false
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => ` ${(ctx.parsed.x * 100).toFixed(1)}%` } }
            },
            scales: {
                x: {
                    grid: { color: '#1e293b' }, max: 0.4,
                    ticks: { callback: v => (v * 100).toFixed(0) + '%', font: { size: 11 } }
                },
                y: { grid: { display: false }, ticks: { font: { size: 12, weight: '600' } } }
            },
            animation: { duration: 800, easing: 'easeOutBounce' }
        }
    });
}

// ─────────────────────────────────────────────
// MULTI-STOCK COMPARISON (normalized, base=100)
// ─────────────────────────────────────────────
const TICKERS = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN'];
const _multiData = {};
TICKERS.forEach((t, ti) => {
    const start = [172, 415, 185, 175, 192][ti];
    const vol = [3, 5.5, 9, 4, 5][ti];
    _multiData[t] = genPriceSeries(252, start, vol);
});

function createCompareChart(canvasId, selected = ['AAPL', 'MSFT', 'TSLA']) {
    const refLen = Math.min(...selected.map(t => _multiData[t].length));
    const labels = _multiData[selected[0]].slice(-refLen).map(d => d.x);
    const datasets = selected.map((t, i) => {
        const prices = _multiData[t].slice(-refLen).map(d => d.y);
        const base = prices[0];
        return {
            label: t,
            data: prices.map(p => parseFloat(((p / base) * 100).toFixed(2))),
            borderColor: MULTI_COLORS[i % MULTI_COLORS.length],
            borderWidth: 2, pointRadius: 0, tension: 0.3, fill: false
        };
    });

    return getOrCreate(canvasId, {
        type: 'line', data: { labels, datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: { position: 'top', labels: { usePointStyle: true, pointStyleWidth: 12, padding: 16, font: { size: 12 } } },
                tooltip: {
                    backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: 1,
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(1)} pts` }
                }
            },
            scales: {
                x: { grid: { color: '#1e293b' }, ticks: { maxTicksLimit: 8 } },
                y: {
                    grid: { color: '#1e293b' },
                    ticks: { callback: v => v.toFixed(0) + ' pts' },
                    title: { display: true, text: 'Normalized (base = 100)', color: '#64748b', font: { size: 11 } }
                }
            },
            animation: { duration: 600 }
        }
    });
}

// ─────────────────────────────────────────────
// CORRELATION HEATMAP  (faked via doughnut + table)
// ─────────────────────────────────────────────
// Correlation matrix data (real-ish values)
const corrMatrix = {
    labels: ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN'],
    values: [
        [1.00, 0.81, 0.53, 0.78, 0.72],
        [0.81, 1.00, 0.48, 0.85, 0.76],
        [0.53, 0.48, 1.00, 0.44, 0.51],
        [0.78, 0.85, 0.44, 1.00, 0.80],
        [0.72, 0.76, 0.51, 0.80, 1.00],
    ]
};

function renderCorrelationTable(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const labs = corrMatrix.labels;
    const vals = corrMatrix.values;
    let html = '<div class="table-wrapper"><table style="font-size:12px"><thead><tr><th></th>';
    labs.forEach(l => { html += `<th style="text-align:center">${l}</th>`; });
    html += '</tr></thead><tbody>';
    vals.forEach((row, ri) => {
        html += `<tr><td style="font-weight:700">${labs[ri]}</td>`;
        row.forEach(v => {
            const pct = ((v + 1) / 2 * 100);
            const h = v >= 0.8 ? 142 : v >= 0.6 ? 220 : v >= 0.3 ? 38 : 0;
            const s = 60, l = 45;
            const bg = `hsla(${h},${s}%,${l}%,0.25)`;
            const col = `hsl(${h},${s}%,${l > 40 ? 70 : 60}%)`;
            html += `<td style="text-align:center;background:${bg};color:${col};font-weight:600">${v.toFixed(2)}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table></div>';
    el.innerHTML = html;
}

// ─────────────────────────────────────────────
// LSTM PREDICTION CHART
// ─────────────────────────────────────────────
function createLSTMChart(canvasId) {
    const n = 80;
    const actual = genPriceSeries(n, 160, 3).map(d => d.y);
    const predicted = actual.map((v, i) => {
        const noise = (Math.random() - 0.5) * 6;
        return parseFloat((v + noise * (i < 20 ? 2 : 1)).toFixed(2));
    });
    // future 10 days
    let last = actual[actual.length - 1];
    const future = [];
    for (let i = 0; i < 10; i++) {
        last += (Math.random() - 0.42) * 3.5;
        future.push(parseFloat(last.toFixed(2)));
    }
    const labels = [...Array(n + 10).keys()].map(i => `Day ${i + 1}`);

    return getOrCreate(canvasId, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Actual', data: [...actual, ...Array(10).fill(null)],
                    borderColor: C.accent, borderWidth: 2, pointRadius: 0, tension: 0.3, fill: false
                },
                {
                    label: 'Predicted', data: [...predicted, ...Array(10).fill(null)],
                    borderColor: C.amber, borderWidth: 1.8, pointRadius: 0, tension: 0.3,
                    fill: false, borderDash: [6, 3]
                },
                {
                    label: 'Future Forecast', data: [...Array(n).fill(null), actual[actual.length - 1], ...future],
                    borderColor: C.success, borderWidth: 2, pointRadius: 3, tension: 0.3,
                    fill: false, borderDash: [4, 4]
                }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: { position: 'top', labels: { usePointStyle: true, pointStyleWidth: 10, padding: 16, font: { size: 12 } } },
                tooltip: {
                    backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: 1,
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: $${ctx.parsed.y?.toFixed(2) ?? '—'}` }
                }
            },
            scales: {
                x: { grid: { color: '#1e293b' }, ticks: { maxTicksLimit: 10, font: { size: 11 } } },
                y: { grid: { color: '#1e293b' }, ticks: { callback: v => '$' + v, font: { size: 11 } } }
            },
            animation: { duration: 900, easing: 'easeInOutQuart' }
        }
    });
}

// ─────────────────────────────────────────────
// ANALYSIS PRICE CHART  (for Stock Analysis page)
// ─────────────────────────────────────────────
function createAnalysisChart(canvasId, ticker = 'AAPL') {
    // Pick realistic base prices per ticker
    const bases = { AAPL: 172, MSFT: 415, TSLA: 185, GOOGL: 175, AMZN: 192, NVDA: 875, META: 505, NFLX: 630 };
    const base = bases[ticker] || 150 + Math.random() * 200;
    const data = genPriceSeries(252, base, base * 0.018);
    const s20 = sma(data, 20);
    const s50 = sma(data, 50);

    return getOrCreate(canvasId, {
        type: 'line',
        data: {
            labels: data.map(d => d.x),
            datasets: [
                {
                    label: 'Close', data: data.map(d => d.y), borderColor: C.accent, borderWidth: 2,
                    fill: true, backgroundColor: (ctx) => {
                        const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height);
                        g.addColorStop(0, C.accentAlpha(0.22)); g.addColorStop(1, C.accentAlpha(0)); return g;
                    }, pointRadius: 0, tension: 0.3
                },
                { label: 'SMA 20', data: s20.map(d => d.y), borderColor: C.amber, borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: false },
                { label: 'SMA 50', data: s50.map(d => d.y), borderColor: C.purple, borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: false, borderDash: [5, 3] }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            animation: { duration: 600 },
            plugins: {
                legend: { position: 'top', labels: { usePointStyle: true, pointStyleWidth: 12, padding: 16, font: { size: 12 } } },
                tooltip: {
                    backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: 1,
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: $${ctx.parsed.y?.toFixed(2) ?? '—'}` }
                }
            },
            scales: {
                x: { grid: { color: '#1e293b' }, ticks: { maxTicksLimit: 8, font: { size: 11 } } },
                y: { grid: { color: '#1e293b' }, ticks: { callback: v => '$' + v.toLocaleString(), font: { size: 11 } } }
            }
        }
    });
}

// ─────────────────────────────────────────────
// COMPARISON METRICS BAR
// ─────────────────────────────────────────────
function createMetricsBar(canvasId, selected) {
    const avgReturns = { AAPL: 14.2, MSFT: 18.7, TSLA: -3.1, GOOGL: 11.4, AMZN: 9.8, NVDA: 62.1, META: 35.4 };
    const vols = { AAPL: 22.1, MSFT: 20.3, TSLA: 58.4, GOOGL: 21.7, AMZN: 26.3, NVDA: 41.2, META: 33.1 };

    return getOrCreate(canvasId, {
        type: 'bar',
        data: {
            labels: selected,
            datasets: [
                { label: 'Avg Return %', data: selected.map(t => avgReturns[t] ?? 10), backgroundColor: C.successAlpha(0.7), borderRadius: 6 },
                { label: 'Volatility %', data: selected.map(t => vols[t] ?? 25), backgroundColor: C.dangerAlpha(0.7), borderRadius: 6 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { usePointStyle: true, padding: 16, font: { size: 12 } } },
                tooltip: { backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: 1 }
            },
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: '#1e293b' }, ticks: { callback: v => v + '%' } }
            },
            animation: { duration: 600 }
        }
    });
}

// ─────────────────────────────────────────────
//  DASHBOARD KPI Sparklines (batch init)
// ─────────────────────────────────────────────
function initDashboardSparklines() {
    createSparkline('spark1', genSparkline(20, true), '#3b82f6');
    createSparkline('spark2', genSparkline(20, true), '#22c55e');
    createSparkline('spark3', genSparkline(20, true), '#f59e0b');
    createSparkline('spark4', genSparkline(20, false), '#a855f7');
}

// ─────────────────────────────────────────────
// GLOBAL:  runAnalysis(ticker)  – used by app.js
// ─────────────────────────────────────────────
function runAnalysis(ticker = 'AAPL') {
    ticker = ticker.toUpperCase();

    // Update stock info card
    const mockPrices = { AAPL: 182.63, MSFT: 420.15, TSLA: 183.42, GOOGL: 176.55, AMZN: 195.78, NVDA: 879.50, META: 509.30, NFLX: 632.15 };
    const mockChg = { AAPL: 1.24, MSFT: 0.87, TSLA: -2.31, GOOGL: 0.54, AMZN: -0.32, NVDA: 3.15, META: 1.78, NFLX: -0.91 };
    const price = mockPrices[ticker] ?? (120 + Math.random() * 300);
    const chg = mockChg[ticker] ?? ((Math.random() - 0.5) * 4);

    const setEl = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
    setEl('info-company', ticker + ' Inc.');
    setEl('info-ticker', ticker);
    setEl('info-price', '$' + price.toFixed(2));
    const chgEl = document.getElementById('info-change');
    if (chgEl) {
        chgEl.textContent = (chg >= 0 ? '+' : '') + chg.toFixed(2) + '%';
        chgEl.className = 'badge ' + (chg >= 0 ? 'badge-success' : 'badge-danger');
    }

    // Indicators
    const vol = (12 + Math.random() * 20).toFixed(2);
    setEl('ind-sma5', '$' + (price * 0.995).toFixed(2));
    setEl('ind-sma20', '$' + (price * 0.97).toFixed(2));
    setEl('ind-ema10', '$' + (price * 0.993).toFixed(2));
    setEl('ind-vol', vol + '%');
    setEl('ind-return', (chg >= 0 ? '+' : '') + chg.toFixed(2) + '%');

    // Draw chart
    createAnalysisChart('analysis-chart', ticker);
    createVolumeChart('analysis-vol-chart', 60);

    // Support / Resistance
    setEl('support-level', '$' + (price * 0.92).toFixed(2));
    setEl('resistance-level', '$' + (price * 1.08).toFixed(2));

    // Show info section
    const infoSec = document.getElementById('analysis-info-section');
    if (infoSec) infoSec.style.display = '';
}
