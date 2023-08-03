from apscheduler.schedulers.background import BackgroundScheduler
import smtplib as smtp
from email.mime.text import MIMEText

from config import global_settings
from db.database import get_sync_session
from user.models.models import UserModel


def make_emails(users):
    emails = []

    for user in users:
        msg = MIMEText(f' Hello, {user.username}! You want to know a good deal?')

        msg['From'] = global_settings.smtp_user
        msg['To'] = user.email
        msg['Subject'] = 'Advertisement'

        emails.append(msg)

    return emails


def send_ad_email_task():
    with get_sync_session() as session:
        users = session.query(UserModel).all()

    server = smtp.SMTP(global_settings.smtp_host, global_settings.smtp_port)
    server.starttls()
    server.login(global_settings.smtp_user, global_settings.smtp_password)

    for email in make_emails(users):
        server.sendmail(email['From'], email['To'], email.as_string())

    server.quit()


scheduler = BackgroundScheduler()
scheduler.add_job(send_ad_email_task, 'cron', hour=0, minute=0)
