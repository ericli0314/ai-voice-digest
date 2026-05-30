import os
import json
from datetime import date as Date

DOCS = "docs"

FIREBASE_DB_URL = os.environ.get("FIREBASE_DB_URL", "")
FIREBASE_USER_KEY = os.environ.get("FIREBASE_USER_KEY", "")


def _ensure_dirs():
    os.makedirs(f"{DOCS}/daily", exist_ok=True)


def _base_styles() -> str:
    return """
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans TC', sans-serif;
               background: #f0f2f5; color: #333; line-height: 1.6; }
        a { color: inherit; }
        .header { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                  color: white; padding: 2.5rem 1.5rem; text-align: center; }
        .header h1 { font-size: 1.7rem; margin-bottom: 0.4rem; }
        .header .sub { opacity: 0.65; font-size: 0.9rem; }
        .container { max-width: 860px; margin: 2rem auto; padding: 0 1rem; }
    """


def _interactive_js(firebase_db_url: str, firebase_user_key: str) -> str:
    return f"""
<script>
const DB_URL   = "{firebase_db_url}";
const USER_KEY = "{firebase_user_key}";
const DATA_URL = DB_URL
    ? `${{DB_URL}}/users/${{USER_KEY}}.json`
    : null;

let state = {{ favorites: {{}}, notes: {{}} }};
let saveTimer = null;

/* ── Firebase / localStorage I/O ── */
async function loadData() {{
    setStatus('loading');
    if (DATA_URL) {{
        try {{
            const res = await fetch(DATA_URL);
            if (res.ok) {{
                const data = await res.json();
                if (data) state = {{ favorites: {{}}, notes: {{}}, ...data }};
            }}
            setStatus('synced');
        }} catch(e) {{
            loadLocal();
            setStatus('offline');
        }}
    }} else {{
        loadLocal();
        setStatus('local');
    }}
    applyToUI();
}}

function loadLocal() {{
    try {{
        const raw = localStorage.getItem('digest_data');
        if (raw) state = JSON.parse(raw);
    }} catch(e) {{}}
}}

async function saveToCloud() {{
    setStatus('saving');
    localStorage.setItem('digest_data', JSON.stringify(state));
    if (!DATA_URL) {{ setStatus('local'); return; }}
    try {{
        await fetch(DATA_URL, {{
            method: 'PUT',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(state)
        }});
        setStatus('synced');
    }} catch(e) {{
        setStatus('offline');
    }}
}}

function scheduleSync() {{
    clearTimeout(saveTimer);
    setStatus('pending');
    saveTimer = setTimeout(saveToCloud, 1200);
}}

/* ── UI apply ── */
function applyToUI() {{
    document.querySelectorAll('.card').forEach(card => {{
        const id = card.dataset.id;
        const starBtn  = card.querySelector('.btn-star');
        const noteArea = card.querySelector('.note-area');
        const noteText = card.querySelector('.note-text');
        const noteBadge = card.querySelector('.note-badge');

        if (state.favorites[id]) {{
            card.classList.add('is-fav');
            starBtn.textContent = '⭐';
            starBtn.title = '取消最愛';
        }} else {{
            card.classList.remove('is-fav');
            starBtn.textContent = '☆';
            starBtn.title = '加入最愛';
        }}

        const note = state.notes[id] || '';
        noteText.value = note;
        noteBadge.style.display = note ? 'inline' : 'none';
    }});
    updateFavCount();
    applyFilter();
}}

/* ── Favorites ── */
function toggleFav(btn) {{
    const card = btn.closest('.card');
    const id   = card.dataset.id;
    if (state.favorites[id]) {{
        delete state.favorites[id];
        card.classList.remove('is-fav');
        btn.textContent = '☆';
        btn.title = '加入最愛';
    }} else {{
        state.favorites[id] = true;
        card.classList.add('is-fav');
        btn.textContent = '⭐';
        btn.title = '取消最愛';
    }}
    updateFavCount();
    applyFilter();
    scheduleSync();
}}

function updateFavCount() {{
    const n = Object.keys(state.favorites).length;
    const el = document.getElementById('fav-count');
    if (el) el.textContent = n > 0 ? ` (${{n}})` : '';
}}

/* ── Notes ── */
function toggleNote(btn) {{
    const card     = btn.closest('.card');
    const noteArea = card.querySelector('.note-area');
    const isOpen   = noteArea.style.display !== 'none';
    noteArea.style.display = isOpen ? 'none' : 'block';
    if (!isOpen) card.querySelector('.note-text').focus();
}}

function onNoteChange(textarea) {{
    const card  = textarea.closest('.card');
    const id    = card.dataset.id;
    const val   = textarea.value;
    const badge = card.querySelector('.note-badge');
    if (val.trim()) {{
        state.notes[id] = val;
        badge.style.display = 'inline';
    }} else {{
        delete state.notes[id];
        badge.style.display = 'none';
    }}
    scheduleSync();
}}

/* ── Filter ── */
let currentFilter = 'all';
function setFilter(f) {{
    currentFilter = f;
    document.querySelectorAll('.filter-btn').forEach(b =>
        b.classList.toggle('active', b.dataset.filter === f)
    );
    applyFilter();
}}

function applyFilter() {{
    document.querySelectorAll('.card').forEach(card => {{
        if (currentFilter === 'fav') {{
            card.style.display = state.favorites[card.dataset.id] ? '' : 'none';
        }} else {{
            card.style.display = '';
        }}
    }});
}}

/* ── Sync status badge ── */
function setStatus(s) {{
    const el = document.getElementById('sync-status');
    if (!el) return;
    const MAP = {{
        loading: ['⟳ 載入中',   '#a78bfa'],
        saving:  ['⟳ 儲存中',   '#f59e0b'],
        synced:  ['✓ 已雲端同步', '#10b981'],
        offline: ['✗ 離線模式',  '#ef4444'],
        pending: ['● 待儲存',   '#6366f1'],
        local:   ['◎ 本機儲存',  '#94a3b8'],
    }};
    const [text, color] = MAP[s] || ['', '#aaa'];
    el.textContent = text;
    el.style.color  = color;
}}

window.addEventListener('load', loadData);
</script>
"""


def _interactive_styles() -> str:
    return """
        /* toolbar */
        .toolbar { display:flex; align-items:center; gap:0.6rem;
                   margin-bottom:1rem; flex-wrap:wrap; }
        .filter-btn { border:1.5px solid #d1d5db; background:white; border-radius:20px;
                      padding:5px 14px; font-size:0.82rem; cursor:pointer;
                      transition:all 0.15s; color:#555; }
        .filter-btn.active { background:#6366f1; border-color:#6366f1;
                             color:white; font-weight:600; }
        #sync-status { margin-left:auto; font-size:0.78rem; font-weight:500;
                       transition:color 0.3s; }
        /* cards */
        .card { background:white; border-radius:12px; padding:1.2rem;
                margin-bottom:0.8rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                transition:transform 0.15s, box-shadow 0.15s, border-color 0.2s;
                border-left:4px solid transparent; }
        .card:hover { transform:translateY(-2px); box-shadow:0 4px 14px rgba(0,0,0,0.1); }
        .card.is-fav { border-left-color:#f59e0b; }
        .card-header { display:flex; align-items:flex-start; gap:0.5rem; }
        .card-body { flex:1; min-width:0; }
        .meta { font-size:0.72rem; color:#aaa; text-transform:uppercase;
                letter-spacing:0.5px; margin-bottom:0.3rem; }
        .card h3 { font-size:0.97rem; font-weight:600; margin-bottom:0.3rem; }
        .card h3 a { text-decoration:none; color:#1e1b4b; }
        .card h3 a:hover { color:#6366f1; text-decoration:underline; }
        .ai-sum { font-size:0.87rem; color:#555; background:#f5f3ff;
                  padding:0.7rem 0.9rem; border-radius:6px; margin:0.5rem 0; }
        .pub { font-size:0.72rem; color:#bbb; margin-top:0.3rem; }
        /* action buttons */
        .card-actions { display:flex; flex-direction:column; gap:0.3rem;
                        flex-shrink:0; }
        .btn-star, .btn-note-toggle { border:none; background:transparent;
                       cursor:pointer; font-size:1.1rem; padding:2px 4px;
                       border-radius:6px; transition:transform 0.1s;
                       line-height:1; }
        .btn-star:hover, .btn-note-toggle:hover { transform:scale(1.2); }
        .note-badge { font-size:0.6rem; background:#6366f1; color:white;
                      border-radius:4px; padding:1px 4px; vertical-align:top;
                      margin-left:2px; }
        /* notes area */
        .note-area { margin-top:0.8rem; display:none; }
        .note-label { font-size:0.72rem; color:#6366f1; font-weight:600;
                      margin-bottom:0.3rem; text-transform:uppercase;
                      letter-spacing:0.5px; }
        .note-text { width:100%; min-height:80px; border:1.5px solid #e0e0ff;
                     border-radius:8px; padding:0.6rem 0.8rem; font-size:0.88rem;
                     font-family:inherit; resize:vertical; color:#333;
                     line-height:1.6; outline:none; }
        .note-text:focus { border-color:#6366f1;
                           box-shadow:0 0 0 3px rgba(99,102,241,0.12); }
        /* digest box */
        .digest-box { background:white; border-radius:12px; padding:1.5rem;
                      margin-bottom:1.4rem; border-left:5px solid #6366f1;
                      box-shadow:0 2px 10px rgba(0,0,0,0.07); }
        .digest-box h2 { font-size:0.82rem; text-transform:uppercase;
                         letter-spacing:1px; color:#6366f1; margin-bottom:0.8rem; }
        .digest-box p { color:#444; font-size:0.95rem; line-height:1.9; }
        .count { color:#888; font-size:0.85rem; margin-bottom:0.8rem; }
        .back { display:inline-block; margin-top:1rem; color:#a5b4fc;
                text-decoration:none; font-size:0.85rem; }
        .back:hover { text-decoration:underline; }
    """


def generate_daily(date_str: str, articles: list[dict], digest: str):
    cards = ""
    for a in articles:
        aid = a.get("id", "")
        summary_block = (
            f'<p class="ai-sum">{a["ai_summary"]}</p>'
            if a.get("ai_summary") else ""
        )
        cards += f"""
        <div class="card" data-id="{aid}">
            <div class="card-header">
                <div class="card-body">
                    <div class="meta">{a.get("source","")} · {a.get("topic","")}</div>
                    <h3>
                        <a href="{a["link"]}" target="_blank" rel="noopener noreferrer">{a["title"]}</a>
                    </h3>
                    {summary_block}
                    <div class="pub">{a.get("published","")}</div>
                </div>
                <div class="card-actions">
                    <button class="btn-star" title="加入最愛"
                            onclick="toggleFav(this)">☆</button>
                    <button class="btn-note-toggle" title="開啟筆記"
                            onclick="toggleNote(this)">📝<span class="note-badge" style="display:none">✎</span></button>
                </div>
            </div>
            <div class="note-area">
                <div class="note-label">✏️ 我的筆記</div>
                <textarea class="note-text"
                          placeholder="輸入你的想法、摘要或備註..."
                          oninput="onNoteChange(this)"></textarea>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI語音 &amp; Agent 趨勢 | {date_str}</title>
    <style>
        {_base_styles()}
        {_interactive_styles()}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎙️ AI語音 &amp; Agent 每日趨勢</h1>
        <div class="sub">{date_str}</div>
        <a href="../index.html" class="back">← 返回總覽</a>
    </div>
    <div class="container">
        <div class="digest-box">
            <h2>📋 今日趨勢摘要</h2>
            <p>{digest}</p>
        </div>

        <div class="toolbar">
            <button class="filter-btn active" data-filter="all"
                    onclick="setFilter('all')">全部文章</button>
            <button class="filter-btn" data-filter="fav"
                    onclick="setFilter('fav')">⭐ 我的最愛<span id="fav-count"></span></button>
            <span id="sync-status"></span>
        </div>

        <div class="count">今日共收錄 {len(articles)} 篇相關文章</div>
        {cards}
    </div>
    {_interactive_js(FIREBASE_DB_URL, FIREBASE_USER_KEY)}
</body>
</html>"""

    path = f"{DOCS}/daily/{date_str}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[site] Written {path}")


def update_index(date_str: str, article_count: int, digest: str):
    history_path = f"{DOCS}/history.json"
    if os.path.exists(history_path):
        with open(history_path, encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []

    history = [h for h in history if h["date"] != date_str]
    preview = digest[:160] + ("…" if len(digest) > 160 else "")
    history.insert(0, {"date": date_str, "count": article_count, "preview": preview})
    history = history[:90]

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    entries = ""
    for i, h in enumerate(history):
        badge = '<span class="badge">最新</span>' if i == 0 else ""
        entries += f"""
        <a href="daily/{h['date']}.html" class="entry">
            <div class="entry-head">
                <span class="entry-date">{h['date']}</span>
                {badge}
                <span class="entry-count">{h['count']} 篇</span>
            </div>
            <div class="entry-preview">{h['preview']}</div>
        </a>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI語音 &amp; Agent 趨勢每日報</title>
    <style>
        {_base_styles()}
        .hero-sub {{ opacity:0.65; font-size:0.88rem; margin-top:0.5rem; }}
        .tags {{ margin-top:1rem; display:flex; flex-wrap:wrap; gap:0.4rem;
                 justify-content:center; }}
        .tag {{ background:rgba(255,255,255,0.15); border-radius:20px;
                padding:3px 12px; font-size:0.78rem; }}
        .section-label {{ font-size:0.78rem; color:#999; text-transform:uppercase;
                          letter-spacing:1px; margin-bottom:0.8rem; }}
        .entry {{ display:block; background:white; border-radius:12px;
                  padding:1.1rem 1.2rem; margin-bottom:0.8rem; text-decoration:none;
                  color:inherit; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                  transition:all 0.15s; border-left:4px solid transparent; }}
        .entry:hover {{ transform:translateY(-2px); box-shadow:0 5px 15px rgba(0,0,0,0.1);
                        border-left-color:#6366f1; }}
        .entry-head {{ display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem; }}
        .entry-date {{ font-weight:700; font-size:1rem; color:#1e1b4b; }}
        .entry-count {{ margin-left:auto; font-size:0.78rem; color:#aaa; }}
        .badge {{ background:#6366f1; color:white; font-size:0.68rem;
                  padding:2px 8px; border-radius:10px; }}
        .entry-preview {{ font-size:0.87rem; color:#666; line-height:1.65; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎙️ AI語音 &amp; Agent 趨勢每日報</h1>
        <div class="hero-sub">每日自動追蹤產業最新動態，由 DeepSeek AI 摘要整理</div>
        <div class="tags">
            <span class="tag">Voice AI</span>
            <span class="tag">Voice Bot</span>
            <span class="tag">AI Agent</span>
            <span class="tag">Agentic AI</span>
            <span class="tag">AI客服</span>
            <span class="tag">Contact Center AI</span>
            <span class="tag">UCC / CCaaS</span>
        </div>
    </div>
    <div class="container">
        <div class="section-label">歷史報告（共 {len(history)} 天）</div>
        {entries}
    </div>
</body>
</html>"""

    with open(f"{DOCS}/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[site] Index updated ({len(history)} entries)")


def generate(date_str: str, articles: list[dict], digest: str):
    _ensure_dirs()
    generate_daily(date_str, articles, digest)
    update_index(date_str, len(articles), digest)
