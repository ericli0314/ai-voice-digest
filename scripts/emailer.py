import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send(date_str: str, articles: list[dict], digest: str, site_url: str):
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]
    daily_url = f"{site_url.rstrip('/')}/daily/{date_str}.html"

    top5_html = ""
    for a in articles[:5]:
        summary_html = ""
        if a.get("ai_summary"):
            summary_html = (
                f'<div style="font-size:13px;color:#555;background:#f5f3ff;'
                f'padding:8px 10px;border-radius:5px;margin-top:6px;line-height:1.7;">'
                f'{a["ai_summary"]}</div>'
            )
        top5_html += f"""
        <tr>
          <td style="padding:12px 0;border-bottom:1px solid #eee;">
            <div style="font-size:11px;color:#aaa;margin-bottom:3px;">
              {a.get("source","")} &middot; {a.get("topic","")}
            </div>
            <a href="{a['link']}"
               style="font-size:15px;font-weight:600;color:#1e1b4b;text-decoration:none;">
              {a['title']}
            </a>
            {summary_html}
          </td>
        </tr>"""

    more_line = ""
    if len(articles) > 5:
        more_line = (
            f'<p style="text-align:center;font-size:13px;color:#999;margin:8px 0 0;">'
            f'+ 另有 {len(articles)-5} 篇文章</p>'
        )

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:20px;background:#f0f2f5;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:600px;margin:0 auto;background:white;
              border-radius:14px;overflow:hidden;
              box-shadow:0 4px 20px rgba(0,0,0,0.1);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);
                color:white;padding:32px 24px;text-align:center;">
      <div style="font-size:32px;margin-bottom:8px;">🎙️</div>
      <h1 style="font-size:20px;margin:0 0 5px;font-weight:700;">
        AI語音 &amp; Agent 每日趨勢
      </h1>
      <div style="opacity:0.65;font-size:13px;">{date_str}</div>
    </div>

    <!-- Digest -->
    <div style="padding:24px 24px 0;">
      <div style="background:#f5f3ff;border-left:5px solid #6366f1;
                  padding:16px;border-radius:8px;">
        <div style="font-size:11px;font-weight:700;color:#6366f1;
                    letter-spacing:1px;margin-bottom:8px;">TODAY'S DIGEST</div>
        <p style="font-size:14px;line-height:1.85;color:#444;margin:0;">
          {digest}
        </p>
      </div>
    </div>

    <!-- Articles -->
    <div style="padding:20px 24px;">
      <div style="font-size:11px;font-weight:700;color:#aaa;
                  letter-spacing:1px;margin-bottom:10px;">
        精選文章（共 {len(articles)} 篇）
      </div>
      <table style="width:100%;border-collapse:collapse;">
        {top5_html}
      </table>
      {more_line}
    </div>

    <!-- CTA -->
    <div style="padding:4px 24px 28px;text-align:center;">
      <a href="{daily_url}"
         style="display:inline-block;background:#6366f1;color:white;
                padding:12px 32px;border-radius:8px;text-decoration:none;
                font-size:15px;font-weight:600;">
        查看完整報告 →
      </a>
    </div>

    <!-- Footer -->
    <div style="background:#f8f9fa;padding:14px;text-align:center;
                font-size:12px;color:#bbb;border-top:1px solid #eee;">
      由 DeepSeek AI 自動生成 &nbsp;·&nbsp;
      <a href="{site_url}" style="color:#aaa;">查看所有報告</a>
    </div>
  </div>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎙️ AI語音趨勢 {date_str}（{len(articles)} 篇）"
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient, msg.as_string())

    print(f"[emailer] Sent to {recipient}")
