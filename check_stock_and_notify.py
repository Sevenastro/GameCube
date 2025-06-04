import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime

PRODUCT_URL = "https://www.nintendo.com/us/store/products/nintendo-switch-2-nintendo-gamecube-controller-120833/"
LOG_DIR = "logs"

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
EMAIL_TO = os.getenv('EMAIL_TO')

def check_in_stock():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(PRODUCT_URL, headers=headers, timeout=10)
    except Exception as e:
        return "Check failed"
    if r.status_code != 200:
        return "Check failed"
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()
    if "Out of Stock" in text or "Sold Out" in text:
        return "Out of stock"
    return "In stock"

def send_email(body, subject):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [EMAIL_TO], msg.as_string())

def log_check(status, check_time):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    log_file = os.path.join(LOG_DIR, check_time.strftime("%m-%d-%Y") + ".txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{check_time.strftime('%m-%d-%Y %H:%M:%S')}, {status}\n")

if __name__ == "__main__":
    now = datetime.now()
    status = check_in_stock()
    log_check(status, now)
    print(f"{now.strftime('%m-%d-%Y %H:%M:%S')}: Stock status: {status}")

    # Detect if this run was triggered manually via workflow_dispatch
    github_event = os.getenv("GITHUB_EVENT_NAME", "")
    if github_event == "workflow_dispatch":
        test_subject = "GameCube Controller Stock Check (Test Email: Action Started)"
        test_body = (
            f"[TEST EMAIL]\n"
            f"Time: {now.strftime('%m-%d-%Y %H:%M:%S')}\n"
            f"Stock status: {status}\n"
            f"Link: {PRODUCT_URL}\n"
            f"\nThis is a test email sent because the workflow was manually triggered (Run workflow button). "
            f"The monitoring system is operational and has started running.\n"
        )
        send_email(test_body, test_subject)

    # Still send a separate alert if actually in stock
    if status == "In stock":
        send_email(
            f"{now.strftime('%m-%d-%Y %H:%M:%S')} Item is in stock!\nLink: {PRODUCT_URL}",
            subject="GameCube Controller In Stock Alert"
        )
