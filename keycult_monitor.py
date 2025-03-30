import requests
from bs4 import BeautifulSoup
import time
import schedule
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from discord_webhook import DiscordWebhook, DiscordEmbed
import logging
from logging.handlers import TimedRotatingFileHandler
import asyncio
import sys

# 로깅 설정
def setup_logger():
    logger = logging.getLogger('keycult_monitor')
    logger.setLevel(logging.INFO)
    
    # 로그 포맷 설정
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 파일 핸들러 설정 (7일치 로그 유지)
    file_handler = TimedRotatingFileHandler(
        'keycult_monitor.log',
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setStream(open(os.devnull, 'w', encoding='utf-8'))  # 기본 출력 스트림 대신 파일 스트림 사용
    logger.addHandler(console_handler)
    
    return logger

# 로거 초기화
logger = setup_logger()

# .env 파일에서 환경변수 로드
load_dotenv()

# 알림 설정 확인
USE_EMAIL = bool(os.getenv('EMAIL_ADDRESS') and os.getenv('EMAIL_PASSWORD') and os.getenv('RECEIVER_EMAIL'))
USE_SLACK = bool(os.getenv('SLACK_WEBHOOK_URL'))
USE_DISCORD = bool(os.getenv('DISCORD_WEBHOOK_URL'))

# 이메일 설정
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

# Slack 설정
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
slack_client = WebClient(token=SLACK_WEBHOOK_URL) if USE_SLACK else None

# Discord 설정
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# 마지막 알림 시간 기록
last_notification_time = datetime.now()
last_stock_check_time = datetime.now()  # 마지막 재고 확인 시간 추가

async def send_discord_notification(message):
    try:
        if not DISCORD_WEBHOOK_URL:
            logger.error("Discord Webhook URL이 설정되지 않았습니다.")
            return
            
        logger.info(f"Discord 알림 시도: {message}")
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
        
        # 임베드 생성
        embed = DiscordEmbed(
            title="Keycult 재고 알림",
            description=message,
            color="03b2f8"  # 파란색
        )
        webhook.add_embed(embed)
        
        # 실행
        response = webhook.execute()
        logger.info(f"Discord 알림 발송 성공! 응답: {response}")
    except Exception as e:
        logger.error(f"Discord 발송 실패: {str(e)}")
        logger.error(f"Discord Webhook URL: {DISCORD_WEBHOOK_URL[:10]}...")  # URL의 일부만 로깅

def send_heartbeat(interval_minutes):
    global last_notification_time
    current_time = datetime.now()
    
    # 마지막 알림으로부터 설정된 시간이 지났는지 확인
    if current_time - last_notification_time >= timedelta(minutes=interval_minutes):
        message = f"Keycult 모니터링 서비스가 정상 작동 중입니다. (마지막 재고 확인: {current_time.strftime('%Y-%m-%d %H:%M:%S')})"
        
        if USE_EMAIL:
            send_email_notification("Keycult 모니터링 서비스 생존 알림", message)
        
        if USE_SLACK:
            send_slack_notification(message)
        
        if USE_DISCORD:
            asyncio.run(send_discord_notification(message))
        
        last_notification_time = current_time
        logger.info("생존 알림 발송 완료")

def check_stock():
    global last_notification_time, last_stock_check_time
    url = "https://keycult.com/products/no-2-65-raw-1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Stonewashed / Diagonal Unfinish 옵션의 재고 상태 확인
        target_option = "Stonewashed / Diagonal Unfinish"
        out_of_stock = target_option in response.text and "Out of stock" in response.text
        
        current_time = datetime.now()
        
        # 하루 동안 재고가 없었던 경우 알림
        if out_of_stock and (current_time - last_stock_check_time).days >= 1:
            message = f"Keycult No. 2/65 Raw {target_option} 옵션이 하루 동안 재고가 없었습니다.\n마지막 재고 확인: {last_stock_check_time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            if USE_EMAIL:
                send_email_notification("Keycult No. 2/65 Raw Stonewashed 재고 부족 알림", message)
            
            if USE_SLACK:
                send_slack_notification(message)
            
            if USE_DISCORD:
                asyncio.run(send_discord_notification(message))
            
            logger.info(f"{target_option} 하루 동안 재고 없음 알림 발송 완료.")
            last_stock_check_time = current_time
        
        if not out_of_stock and target_option in response.text:
            message = f"Keycult No. 2/65 Raw {target_option} 옵션이 재고에 입고되었습니다!\n확인하러 가기: {url}"
            
            if USE_EMAIL:
                send_email_notification("Keycult No. 2/65 Raw Stonewashed 재고 입고 알림", message)
            
            if USE_SLACK:
                send_slack_notification(message)
            
            if USE_DISCORD:
                asyncio.run(send_discord_notification(message))
            
            logger.info(f"{target_option} 재고 입고 감지! 알림 발송 완료.")
            last_stock_check_time = current_time  # 재고가 있을 때도 시간 업데이트
        else:
            logger.info(f"{target_option} 재고 없음")
            
        # 재고 확인 후 생존 알림 시간 업데이트
        last_notification_time = current_time
            
    except Exception as e:
        logger.error(f"에러 발생: {str(e)}")

def send_email_notification(subject, body):
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
        logger.info("이메일 알림 발송 성공!")
    except Exception as e:
        logger.error(f"이메일 발송 실패: {str(e)}")

def send_slack_notification(message):
    try:
        response = slack_client.chat_postMessage(
            channel="#keycult-stock",  # 알림을 받을 Slack 채널명
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
        logger.info("Slack 알림 발송 성공!")
    except SlackApiError as e:
        logger.error(f"Slack 발송 실패: {str(e)}")

def main():
    logger.info("Keycult 재고 모니터링 시작...")
    logger.info(f"활성화된 알림: {'이메일' if USE_EMAIL else ''} {'Slack' if USE_SLACK else ''} {'Discord' if USE_DISCORD else ''}")
    
    # 시간 간격 입력 받기
    try:
        if len(sys.argv) == 3:
            # 명령줄 인자에서 시간 간격 받기
            check_interval = int(sys.argv[1])
            heartbeat_interval = int(sys.argv[2])
        else:
            # 사용자 입력 받기
            check_interval = int(input("재고 확인 간격(분): "))
            heartbeat_interval = int(input("생존 알림 간격(분): "))
        
        if check_interval <= 0 or heartbeat_interval <= 0:
            raise ValueError("시간 간격은 1분 이상이어야 합니다.")
            
        logger.info(f"재고 확인 간격: {check_interval}분")
        logger.info(f"생존 알림 간격: {heartbeat_interval}분")
        
        # 초기 알림 발송
        current_time = datetime.now()
        initial_message = f"Keycult 모니터링 서비스가 시작되었습니다.\n재고 확인 간격: {check_interval}분\n생존 알림 간격: {heartbeat_interval}분\n시작 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        if USE_EMAIL:
            send_email_notification("Keycult 모니터링 서비스 시작 알림", initial_message)
        
        if USE_SLACK:
            send_slack_notification(initial_message)
        
        if USE_DISCORD:
            asyncio.run(send_discord_notification(initial_message))
        
        logger.info("초기 알림 발송 완료")
        
        # 재고 확인 스케줄링
        schedule.every(check_interval).minutes.do(check_stock)
        
        # 생존 알림 스케줄링 (재고 확인과 동시에 실행되지 않도록 1분 후에 시작)
        schedule.every(heartbeat_interval).minutes.at(":01").do(lambda: send_heartbeat(heartbeat_interval))
        
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except ValueError as e:
        logger.error(f"입력 오류: {str(e)}")
        return
    except KeyboardInterrupt:
        logger.info("프로그램을 종료합니다.")
        return

if __name__ == "__main__":
    main() 