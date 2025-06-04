import smtplib
from email.mime.text import MIMEText
import os

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER', 'sevenastros@gmail.com')
EMAIL_PASS = os.getenv('EMAIL_PASS', 'kfhkgutevzeacvrd')
EMAIL_TO = os.getenv('EMAIL_TO', 'sevenastros@gmail.com')

def send_email(body, subject="Test Email"):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [EMAIL_TO], msg.as_string())

if __name__ == "__main__":
    send_email("这是一封测试邮件。如果你看到这封邮件，说明邮件发送功能正常！", subject="GameCube 邮件发送测试")
    print("测试邮件已发送")
