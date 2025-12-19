import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (
    MAIL_HOST,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM
)


def send_email(to_email, subject, html_content):
    """
    Gửi email HTML
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = MAIL_FROM
        msg["To"] = to_email
        msg["Subject"] = subject

        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        server = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, to_email, msg.as_string())
        server.quit()

        return True, "Email sent successfully"

    except Exception as e:
        print("MAIL ERROR:", e)
        return False, str(e)
