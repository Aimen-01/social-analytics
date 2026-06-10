/* ================================================================
   SocialMetrics Pro — API Layer
   Coordinates frontend fetch requests to the Flask backend (Port 5000)
   ================================================================ */

const API_BASE = 'http://127.0.0.1:5000/api';

// ── AUTHENTICATION HELPERS ──────────────────────────────────────
function getAuthHeaders() {
    const token = localStorage.getItem("sm_token");
    const headers = { "Content-Type": "application/json" };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
}

// ── UTILITY FORMATTERS ──────────────────────────────────────────
function fmtNum(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toLocaleString();
}

function fmtReach(num) { return fmtNum(num); }

function pltBadge(platform) {
    const p = (platform || "").toLowerCase();
    if (p.includes('twitter') || p === 'x') return `<span class="plt plt-tw">Twitter/X</span>`;
    if (p.includes('instagram'))            return `<span class="plt plt-ig">Instagram</span>`;
    if (p.includes('facebook'))             return `<span class="plt plt-fb">Facebook</span>`;
    if (p.includes('youtube'))              return `<span class="plt plt-yt">YouTube</span>`;
    return `<span class="plt">${platform}</span>`;
}

function typBadge(type) {
    const t = (type || "text").toLowerCase();
    return `<span class="typ typ-${t}">${t.charAt(0).toUpperCase() + t.slice(1)}</span>`;
}

// ── API ENDPOINTS ───────────────────────────────────────────────
const API = {

    // Auth
    async login(username, password) {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem("sm_token", data.token);
            localStorage.setItem("sm_user",  data.username);
            localStorage.setItem("sm_role",  data.role);
        }
        return data;
    },

    // Dashboard stats cards
    async getGlobalStats() {
        const res = await fetch(`${API_BASE}/posts/stats`);
        return await res.json();
    },

    // Platform breakdown (donut chart)
    async getPlatformDistribution() {
        const res = await fetch(`${API_BASE}/dashboard/platforms`);
        return await res.json();
    },

    // Sentiment bar
    async getSentimentBreakdown() {
        const res = await fetch(`${API_BASE}/posts/sentiment`);
        return await res.json();
    },

    // Engagement over time (line chart)
    async getTimelineData(window = "7d", hashtag = "") {
        let url = `${API_BASE}/posts/timeline?window=${window}`;
        if (hashtag) url += `&hashtag=${encodeURIComponent(hashtag)}`;
        const res = await fetch(url);
        return await res.json();
    },

    // Heatmap 7x24 matrix
    async getHeatmapData() {
        const res = await fetch(`${API_BASE}/posts/heatmap`);
        return await res.json();
    },

    // Trending hashtags with time window
    async getTrendingHashtags(window = "24h", limit = 10) {
        const res = await fetch(`${API_BASE}/hashtags/trending?window=${window}&limit=${limit}`);
        return await res.json();
    },

    // Viral posts ranked by viral coefficient
    async getViralPosts(window = "7d", limit = 20) {
        const res = await fetch(`${API_BASE}/posts/viral?window=${window}&limit=${limit}`);
        return await res.json();
    },

    // Search posts by text, platform, sentiment
    async searchPosts(params = {}) {
        const q = new URLSearchParams();
        if (params.q)         q.append("q",         params.q);
        if (params.platform)  q.append("platform",  params.platform);
        if (params.sentiment) q.append("sentiment", params.sentiment);
        if (params.limit)     q.append("limit",     params.limit);
        const res = await fetch(`${API_BASE}/search/?${q.toString()}`);
        return await res.json();
    },

    // Influencer leaderboard
    async getLeaderboard(limit = 10) {
        const res = await fetch(`${API_BASE}/users/leaderboard?limit=${limit}`);
        return await res.json();
    },

    // Reports page endpoints
    async getReportKPIs() {
        const res = await fetch(`${API_BASE}/reports/kpis`);
        return await res.json();
    },

    async getPlatformSummary() {
        const res = await fetch(`${API_BASE}/reports/platform-summary`);
        return await res.json();
    },

    async getTopHashtags() {
        const res = await fetch(`${API_BASE}/reports/hashtags`);
        return await res.json();
    }
};

// ── SIDEBAR TOGGLE ──────────────────────────────────────────────
function initSidebar() {
    const hamburger = document.getElementById('hamburger');
    const sidebar   = document.getElementById('sidebar');
    const overlay   = document.getElementById('overlay');
    if (hamburger && sidebar && overlay) {
        hamburger.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('open');
        });
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('open');
        });
    }
}

