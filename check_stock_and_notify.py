import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

PRODUCT_URL = "https://www.nintendo.com/us/store/products/nintendo-switch-2-nintendo-gamecube-controller-120833/"
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER', 'sevenastros@gmail.com')
EMAIL_PASS = os.getenv('EMAIL_PASS', 'kfhkgutevzeacvrd')
EMAIL_TO = os.getenv('EMAIL_TO', 'sevenastros@gmail.com')

def check_in_stock():
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(PRODUCT_URL, headers=headers, timeout=10)
    if resp.status_code != 200:
        print(f"Failed to fetch page: {resp.status_code}")
        return False
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text()
    # Checks for common out-of-stock phrases
    if "Out of Stock" in text or "Sold Out" in text:
        return False
    return True

def send_email():
    body = f"The product may be in stock! Check: {PRODUCT_URL}"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "GameCube Controller Restock Alert"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [EMAIL_TO], msg.as_string())

if __name__ == "__main__":
    if check_in_stock():
        send_email()
        print("In stock! Email sent.")
    else:
        print("Still out of stock.")
