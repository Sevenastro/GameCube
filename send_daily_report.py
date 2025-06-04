import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
EMAIL_TO = os.getenv('EMAIL_TO')
LOG_DIR = "logs"

def send_email(body, subject):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [EMAIL_TO], msg.as_string())

def main():
    today = datetime.now().strftime("%m-%d-%Y")
    log_file = os.path.join(LOG_DIR, today + ".txt")
    if not os.path.exists(log_file):
        body = f"No stock checks were performed on {today}."
    else:
        with open(log_file, encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            body = f"No stock checks were performed on {today}."
        else:
            body = f"Summary of stock checks for {today}:\n" + "".join(lines)
    send_email(body, subject=f"GameCube {today} Stock Check Summary")
    print("Daily summary email sent.")

if __name__ == "__main__":
    main()
