from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime
import pytz

PRODUCT_URL = "https://www.nintendo.com/us/store/products/nintendo-switch-2-nintendo-gamecube-controller-120833/"
LOG_DIR = "logs"
CHICAGO_TZ = pytz.timezone('America/Chicago')

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
EMAIL_TO = os.getenv('EMAIL_TO')

def check_in_stock():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(PRODUCT_URL)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        text = driver.find_element(By.TAG_NAME, "body").text
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        with open(os.path.join(LOG_DIR, "last_body_text.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        with open(os.path.join(LOG_DIR, "last_page.html"), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        try:
            driver.find_element(By.XPATH, '//span[contains(@class,"ZovBS") and contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"), "sold out")]')
            return "Out of stock"
        except NoSuchElementException:
            return "In stock"
    finally:
        driver.quit()

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
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    now_chicago = now_utc.astimezone(CHICAGO_TZ)

    status = check_in_stock()
    log_check(status, now_chicago)
    print(f"{now_chicago.strftime('%m-%d-%Y %H:%M:%S')}: Stock status: {status}")

    github_event = os.getenv("GITHUB_EVENT_NAME", "")
    if github_event == "workflow_dispatch":
        test_subject = f"[{status}] GameCube Controller Stock Check (Test Email: Action Started)"
        test_body = (
            f"[TEST EMAIL]\n"
            f"Time: {now_chicago.strftime('%m-%d-%Y %H:%M:%S')} (America/Chicago)\n"
            f"Stock status: {status}\n"
            f"Link: {PRODUCT_URL}\n"
            f"\nThis is a test email sent because the workflow was manually triggered (Run workflow button). "
            f"The monitoring system is operational and has started running.\n"
        )
        send_email(test_body, test_subject)

    if status == "In stock":
        send_email(
            f"{now_chicago.strftime('%m-%d-%Y %H:%M:%S')} (America/Chicago) Item is in stock!\nLink: {PRODUCT_URL}",
            subject=f"[{status}] GameCube Controller In Stock Alert"
        )
