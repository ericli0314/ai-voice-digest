import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import subscribers


def _build_message(gmail_user: str, email: str, confirm_url: str) -> MIMEMultipart:
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:20px;background:#f0f2f5;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:480px;margin:0 auto;background:white;
              border-radius:14px;overflow:hidden;
              box-shadow:0 4px 20px rgba(0,0,0,0.1);">
    <div style="background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);
                color:white;padding:32px 24px;text-align:center;">
      <div style="font-size:32px;margin-bottom:8px;">🎙️</div>
      <h1 style="font-size:18px;margin:0;font-weight:700;">
        確認訂閱 AI語音 &amp; Agent 每日趨勢
      </h1>
    </div>
    <div style="padding:28px 24px;text-align:center;">
      <p style="font-size:14px;color:#555;line-height:1.8;margin:0 0 20px;">
        請點擊下方按鈕確認訂閱，之後每期摘要都會寄到這個信箱。
      </p>
      <a href="{confirm_url}"
         style="display:inline-block;background:#6366f1;color:white;
                padding:12px 32px;border-radius:8px;text-decoration:none;
                font-size:15px;font-weight:600;">
        確認訂閱 →
      </a>
      <p style="font-size:12px;color:#bbb;margin:24px 0 0;">
        不是你本人操作？忽略這封信即可，不會有任何影響。
      </p>
    </div>
  </div>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎙️ 請確認訂閱 AI語音趨勢每日報"
    msg["From"] = gmail_user
    msg["To"] = email
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


def main():
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    pages_url = os.environ.get("PAGES_URL", "").rstrip("/")

    pending = subscribers.get_pending_unconfirmed()
    if not pending:
        print("[confirm_mailer] No pending subscribers.")
        return

    print(f"[confirm_mailer] {len(pending)} pending subscriber(s) to email.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        for sub in pending:
            confirm_url = f"{pages_url}/confirm.html?id={sub['id']}&token={sub['token']}"
            try:
                msg = _build_message(gmail_user, sub["email"], confirm_url)
                server.sendmail(gmail_user, sub["email"], msg.as_string())
                subscribers.mark_confirmation_sent(sub["id"])
                print(f"[confirm_mailer] Sent confirmation to {sub['email']}")
            except Exception as e:
                print(f"[confirm_mailer] Failed for {sub['email']}: {e}")


if __name__ == "__main__":
    main()
