import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from discord_webhook import DiscordWebhook, DiscordEmbed
import asyncio
from dotenv import load_dotenv

load_dotenv()

USE_EMAIL = bool(os.getenv('EMAIL_ADDRESS') and os.getenv('EMAIL_PASSWORD') and os.getenv('RECEIVER_EMAIL'))
USE_SLACK = bool(os.getenv('SLACK_WEBHOOK_URL'))
USE_DISCORD = bool(os.getenv('DISCORD_WEBHOOK_URL'))

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
slack_client = WebClient(token=SLACK_WEBHOOK_URL) if USE_SLACK else None

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def send_notification(subject, message, logger=None):
    if USE_EMAIL:
        send_email_notification(subject, message, logger)
    if USE_SLACK:
        send_slack_notification(message, logger)
    if USE_DISCORD:
        asyncio.run(send_discord_notification(message, logger))
    if logger:
        logger.info("알림 전송 완료.")

def send_email_notification(subject, body, logger=None):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        if logger:
            logger.info("이메일 알림 발송 성공!")
    except Exception as e:
        if logger:
            logger.error(f"이메일 발송 실패: {str(e)}")

def send_slack_notification(message, logger=None):
    try:
        response = slack_client.chat_postMessage(
            channel="#keycult-stock",
            text=message,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Keycult 재고 알림*\n{message}"
                    }
                }
            ]
        )
        if logger:
            logger.info("Slack 알림 발송 성공!")
    except SlackApiError as e:
        if logger:
            logger.error(f"Slack 발송 실패: {str(e)}")

async def send_discord_notification(message, logger=None):
    try:
        if not DISCORD_WEBHOOK_URL:
            if logger:
                logger.error("Discord Webhook URL이 설정되지 않았습니다.")
            return
        if logger:
            logger.info(f"Discord 알림 시도: {message}")
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
        embed = DiscordEmbed(
            title="Keycult 재고 알림",
            description=message,
            color="03b2f8"
        )
        webhook.add_embed(embed)
        response = webhook.execute()
        if logger:
            logger.info(f"Discord 알림 발송 성공! 응답: {response}")
    except Exception as e:
        if logger:
            logger.error(f"Discord 발송 실패: {str(e)}")
            logger.error(f"Discord Webhook URL: {DISCORD_WEBHOOK_URL[:10]}...") 