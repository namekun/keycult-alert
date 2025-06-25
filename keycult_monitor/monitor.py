import os
import sys
import time
import schedule
from datetime import datetime, timedelta
import socket
import atexit
import signal
from .notifier import send_notification

def log_exit(logger, msg=None):
    if msg:
        logger.info(f"Keycult 모니터링 서비스 종료: {msg}")
        send_notification("Keycult 모니터링 서비스 종료", f"Keycult 모니터링 서비스가 종료되었습니다. {msg}", logger)
    else:
        logger.info("Keycult 모니터링 서비스 종료")
        send_notification("Keycult 모니터링 서비스 종료", "Keycult 모니터링 서비스가 종료되었습니다.", logger)

# atexit/signal 등록 함수
def setup_exit_handlers(logger):
    def handle_signal(signum, frame):
        log_exit(logger, f"signal {signum} 수신")
        sys.exit(0)
    atexit.register(lambda: log_exit(logger))
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    if hasattr(signal, 'SIGQUIT'):
        signal.signal(signal.SIGQUIT, handle_signal)

def send_heartbeat(logger, heartbeat_interval, last_notification_time):
    current_time = datetime.now()
    if current_time - last_notification_time >= timedelta(minutes=heartbeat_interval):
        message = f"Keycult 모니터링 서비스가 정상 작동 중입니다. (마지막 알림: {last_notification_time.strftime('%Y-%m-%d %H:%M:%S')})"
        send_notification("Keycult 모니터링 생존 알림", message, logger)
        last_notification_time = current_time
        logger.info("생존 알림 발송 완료.")
    else:
        logger.info("생존 알림 전송 조건 미충족.")
    return last_notification_time

def check_stock(logger, last_notification_time, last_stock_check_time):
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
                import requests
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
                    return last_notification_time, last_stock_check_time
            except Exception as e:
                logger.error(f"HTTP request failed on attempt {attempt}/{max_retries}: {e}")
                if attempt < max_retries:
                    logger.info(f"Retrying HTTP request ({attempt}/{max_retries})...")
                    time.sleep(1)
                    continue
                else:
                    logger.error("Max HTTP request retries exceeded.")
                    return last_notification_time, last_stock_check_time
        else:
            return last_notification_time, last_stock_check_time
        product = response.json()
        variants = product.get("variants", [])
        variant = next((v for v in variants if v.get("title") == target_option), None)
        if not variant:
            logger.info(f"{target_option} 옵션이 페이지에 존재하지 않습니다.")
            return last_notification_time, last_stock_check_time
        in_stock = bool(variant.get("available"))
        current_time = datetime.now()
        if in_stock:
            message = (
                f"Keycult No. 2/65 Raw {target_option} 옵션이 재고에 입고되었습니다!\n"
                f"확인하러 가기: {url}"
            )
            for _ in range(10):
                send_notification("Keycult No. 2/65 Raw Stonewashed 재고 입고 알림", message, logger)
            last_stock_check_time = current_time
            notification_sent = True
        else:
            if (current_time - last_stock_check_time) >= timedelta(days=1):
                message = (
                    f"Keycult No. 2/65 Raw {target_option} 옵션이 하루 동안 재고가 없었습니다.\n"
                    f"마지막 재고 확인: {last_stock_check_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                send_notification("Keycult No. 2/65 Raw Stonewashed 재고 부족 알림", message, logger)
                last_stock_check_time = current_time
                notification_sent = True
            else:
                logger.info(f"{target_option} 재고 없음 - 알림 전송 조건 미충족.")
        if notification_sent:
            last_notification_time = current_time
        return last_notification_time, last_stock_check_time
    except Exception as e:
        logger.error(f"에러 발생: {str(e)}")
        return last_notification_time, last_stock_check_time

def check_keywords(logger, KEYWORDS):
    if not KEYWORDS:
        return
    try:
        for keyword in KEYWORDS:
            if keyword.strip():
                message = f"키워드 '{keyword}' 발견!"
                send_notification("키워드 알림", message, logger)
                logger.info(f"키워드 '{keyword}' 알림 발송")
    except Exception as e:
        logger.error(f"키워드 체크 중 오류 발생: {str(e)}") 