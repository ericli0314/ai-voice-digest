import os
import json
from datetime import date as Date

DOCS = "docs"


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


def generate_daily(date_str: str, articles: list[dict], digest: str):
    cards = ""
    for a in articles:
        summary_block = ""
        if a.get("ai_summary"):
            summary_block = f'<p class="ai-sum">{a["ai_summary"]}</p>'
        cards += f"""
        <div class="card">
            <div class="meta">{a.get("source", "")} · {a.get("topic", "")}</div>
            <h3><a href="{a["link"]}" target="_blank" rel="noopener noreferrer">{a["title"]}</a></h3>
            {summary_block}
            <div class="pub">{a.get("published", "")}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI語音 &amp; Agent 趨勢 | {date_str}</title>
    <style>
        {_base_styles()}
        .back {{ display:inline-block; margin-top:1rem; color:#a5b4fc;
                 text-decoration:none; font-size:0.85rem; }}
        .back:hover {{ text-decoration:underline; }}
        .digest-box {{ background:white; border-radius:12px; padding:1.5rem;
                       margin-bottom:1.8rem; border-left:5px solid #6366f1;
                       box-shadow:0 2px 10px rgba(0,0,0,0.07); }}
        .digest-box h2 {{ font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;
                          color:#6366f1; margin-bottom:0.8rem; }}
        .digest-box p {{ color:#444; font-size:0.95rem; line-height:1.9; }}
        .count {{ color:#888; font-size:0.85rem; margin-bottom:1rem; }}
        .card {{ background:white; border-radius:12px; padding:1.2rem;
                 margin-bottom:0.8rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                 transition:transform 0.15s, box-shadow 0.15s; }}
        .card:hover {{ transform:translateY(-2px); box-shadow:0 4px 14px rgba(0,0,0,0.1); }}
        .meta {{ font-size:0.72rem; color:#aaa; text-transform:uppercase;
                 letter-spacing:0.5px; margin-bottom:0.4rem; }}
        .card h3 {{ font-size:0.97rem; font-weight:600; margin-bottom:0.4rem; }}
        .card h3 a {{ text-decoration:none; color:#1e1b4b; }}
        .card h3 a:hover {{ color:#6366f1; text-decoration:underline; }}
        .ai-sum {{ font-size:0.87rem; color:#555; background:#f5f3ff;
                   padding:0.7rem 0.9rem; border-radius:6px; margin:0.5rem 0; }}
        .pub {{ font-size:0.72rem; color:#bbb; margin-top:0.4rem; }}
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
        <div class="count">今日共收錄 {len(articles)} 篇相關文章</div>
        {cards}
    </div>
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

    # Remove duplicate for today if re-running
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
        <div class="hero-sub">每日自動追蹤產業最新動態</div>
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
