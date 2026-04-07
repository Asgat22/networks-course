import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, message_text, message_theme="Тема письма", message_type="txt"):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = os.getenv("EMAIL")
    SENDER_PASSWORD = os.getenv("PASSWORD")
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = message_theme
    if message_type == "html":
        msg.attach(MIMEText(message_text, "html"))
    else:
        msg.attach(MIMEText(message_text, "plain"))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("to")
    parser.add_argument("text")
    parser.add_argument("--theme", default="Тема письма")
    parser.add_argument("--type", choices=["txt", "html"], default="txt")
    args = parser.parse_args()
    send_email(args.to, args.text, args.theme, args.type)
