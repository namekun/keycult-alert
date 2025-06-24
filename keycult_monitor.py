import requests
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
import socket
import atexit
import signal

# 로그 디렉토리 설정 및 생성
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 로깅 설정 함수
def setup_logger():
    logger = logging.getLogger('keycult_monitor')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, 'keycult_monitor.log'),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

# .env 파일에서 환경변수 로드
load_dotenv()

# 알림 활성화 여부 설정
USE_EMAIL = bool(os.getenv('EMAIL_ADDRESS') and os.getenv('EMAIL_PASSWORD') and os.getenv('RECEIVER_EMAIL'))
USE_SLACK = bool(os.getenv('SLACK_WEBHOOK_URL'))
USE_DISCORD = bool(os.getenv('DISCORD_WEBHOOK_URL'))

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
slack_client = WebClient(token=SLACK_WEBHOOK_URL) if USE_SLACK else None

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# 전역 변수: 마지막 알림 및 재고 확인 시간
last_notification_time = datetime.now()
last_stock_check_time = datetime.now()

# 키워드 모니터링 설정
KEYWORDS = os.getenv('MONITOR_KEYWORDS', '').split(',')  # 쉼표로 구분된 키워드 목록
KEYWORD_CHECK_INTERVAL = int(os.getenv('KEYWORD_CHECK_INTERVAL', '300'))  # 기본 5분

# 공통 알림 전송 함수
def send_notification(subject, message):
    if USE_EMAIL:
        send_email_notification(subject, message)
    if USE_SLACK:
        send_slack_notification(message)
    if USE_DISCORD:
        asyncio.run(send_discord_notification(message))
    logger.info("알림 전송 완료.")

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
        logger.info("Slack 알림 발송 성공!")
    except SlackApiError as e:
        logger.error(f"Slack 발송 실패: {str(e)}")

async def send_discord_notification(message):
    try:
        if not DISCORD_WEBHOOK_URL:
            logger.error("Discord Webhook URL이 설정되지 않았습니다.")
            return
        logger.info(f"Discord 알림 시도: {message}")
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
        embed = DiscordEmbed(
            title="Keycult 재고 알림",
            description=message,
            color="03b2f8"
        )
        webhook.add_embed(embed)
        response = webhook.execute()
        logger.info(f"Discord 알림 발송 성공! 응답: {response}")
    except Exception as e:
        logger.error(f"Discord 발송 실패: {str(e)}")
        logger.error(f"Discord Webhook URL: {DISCORD_WEBHOOK_URL[:10]}...")

# 생존(heartbeat) 알림 전송 함수
def send_heartbeat(heartbeat_interval):
    global last_notification_time
    current_time = datetime.now()
    if current_time - last_notification_time >= timedelta(minutes=heartbeat_interval):
        message = f"Keycult 모니터링 서비스가 정상 작동 중입니다. (마지막 알림: {last_notification_time.strftime('%Y-%m-%d %H:%M:%S')})"
        send_notification("Keycult 모니터링 생존 알림", message)
        last_notification_time = current_time
        logger.info("생존 알림 발송 완료.")
    else:
        logger.info("생존 알림 전송 조건 미충족.")

# 재고 체크 함수
def check_stock():
    global last_notification_time, last_stock_check_time
    url = "https://keycult.com/products/no-2-65-raw-1"
    json_url = f"{url}.js"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    target_option = "Stonewashed / Diagonal Unfinish"
    notification_sent = False
    
    try:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                hostname = url.split("//")[1].split("/")[0]
                socket.gethostbyname(hostname)
                response = requests.get(json_url, headers=headers, timeout=10)
                response.raise_for_status()
                break
            except socket.gaierror as e:
                logger.error(f"DNS resolution failed for {hostname}: {e}")
                if attempt < max_retries:
                    logger.info(f"Retrying DNS resolution ({attempt}/{max_retries})...")
                    time.sleep(1)
                    continue
                else:
                    logger.error("Max DNS resolution retries exceeded.")
                    return
            except Exception as e:
                logger.error(f"HTTP request failed on attempt {attempt}/{max_retries}: {e}")
                if attempt < max_retries:
                    logger.info(f"Retrying HTTP request ({attempt}/{max_retries})...")
                    time.sleep(1)
                    continue
                else:
                    logger.error("Max HTTP request retries exceeded.")
                    return
        else:
            return
        # At this point, `response` is successful and contains product JSON
        product = response.json()
        variants = product.get("variants", [])
        variant = next((v for v in variants if v.get("title") == target_option), None)
        if not variant:
            logger.info(f"{target_option} 옵션이 페이지에 존재하지 않습니다.")
            return

        in_stock = bool(variant.get("available"))
        current_time = datetime.now()

        if in_stock:
            # 재고 입고 알림 전송
            message = (
                f"Keycult No. 2/65 Raw {target_option} 옵션이 재고에 입고되었습니다!\n"
                f"확인하러 가기: {url}"
            )
            for _ in range(10):
                send_notification("Keycult No. 2/65 Raw Stonewashed 재고 입고 알림", message)
            last_stock_check_time = current_time
            notification_sent = True
        else:
            # 하루 이상 재고 없으면 알림 전송
            if (current_time - last_stock_check_time) >= timedelta(days=1):
                message = (
                    f"Keycult No. 2/65 Raw {target_option} 옵션이 하루 동안 재고가 없었습니다.\n"
                    f"마지막 재고 확인: {last_stock_check_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                send_notification("Keycult No. 2/65 Raw Stonewashed 재고 부족 알림", message)
                last_stock_check_time = current_time
                notification_sent = True
            else:
                logger.info(f"{target_option} 재고 없음 - 알림 전송 조건 미충족.")
        
        # 알림 전송이 있었을 때만 마지막 알림 시간 업데이트
        if notification_sent:
            last_notification_time = current_time
        
    except Exception as e:
        logger.error(f"에러 발생: {str(e)}")

def check_keywords():
    """키워드 모니터링 함수"""
    if not KEYWORDS:
        return
        
    try:
        # 여기에 키워드 체크 로직 구현
        # 예: 웹사이트 크롤링, API 호출 등
        for keyword in KEYWORDS:
            if keyword.strip():  # 빈 키워드 제외
                # 키워드 발견 시 알림
                message = f"키워드 '{keyword}' 발견!"
                send_notification("키워드 알림", message)
                logger.info(f"키워드 '{keyword}' 알림 발송")
    except Exception as e:
        logger.error(f"키워드 체크 중 오류 발생: {str(e)}")

def log_exit(msg=None):
    if msg:
        logger.info(f"Keycult 모니터링 서비스 종료: {msg}")
    else:
        logger.info("Keycult 모니터링 서비스 종료")

# atexit 등록
atexit.register(log_exit)

# 시그널 핸들러 등록
def handle_signal(signum, frame):
    log_exit(f"signal {signum} 수신")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)
# macOS에서 SIGQUIT도 처리
if hasattr(signal, 'SIGQUIT'):
    signal.signal(signal.SIGQUIT, handle_signal)

def main():
    try:
        logger.info("Keycult 모니터링 서비스 시작")
        send_notification("Keycult 모니터링 서비스 시작", "Keycult 모니터링 서비스가 정상적으로 시작되었습니다.")

        # 명령줄 인자/환경변수 처리
        check_interval = None
        heartbeat_interval = None
        if len(sys.argv) == 3:
            try:
                check_interval = int(sys.argv[1])
                heartbeat_interval = int(sys.argv[2])
            except Exception:
                logger.error("명령줄 인자 파싱 오류. 환경변수 또는 기본값 사용.")
                check_interval = None
                heartbeat_interval = None
        if check_interval is None or heartbeat_interval is None:
            # 환경변수 시도
            try:
                check_interval = int(os.getenv('CHECK_INTERVAL', ''))
            except Exception:
                check_interval = None
            try:
                heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL', ''))
            except Exception:
                heartbeat_interval = None
        if check_interval is None:
            check_interval = 1  # 기본값: 1분
        if heartbeat_interval is None:
            heartbeat_interval = 30  # 기본값: 30분

        logger.info(f"재고 확인 간격: {check_interval}분, 생존 알림 간격: {heartbeat_interval}시간")
        send_notification("Keycult 모니터링 서비스 시작", f"재고 확인 간격: {check_interval}분, 생존 알림 간격: {heartbeat_interval}시간")

        # 재고 체크는 인자 기반
        schedule.every(check_interval).minutes.do(check_stock)

        # 키워드 모니터링 스케줄 추가
        if KEYWORDS:
            schedule.every(KEYWORD_CHECK_INTERVAL).seconds.do(check_keywords)

        # 생존 알림도 입력받은 간격(분)마다 실행
        schedule.every(heartbeat_interval).hours.do(lambda: send_heartbeat(heartbeat_interval))

        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        log_exit("KeyboardInterrupt")
        sys.exit(0)
    except Exception as e:
        logger.error(f"예외로 인한 서비스 종료: {e}")
        log_exit(f"Exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()