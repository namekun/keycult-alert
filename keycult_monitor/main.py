import os
import sys
import time
from datetime import datetime
import schedule
from dotenv import load_dotenv
from keycult_monitor.logging_config import setup_logger
from keycult_monitor.notifier import send_notification
from keycult_monitor.monitor import (
    setup_exit_handlers, send_heartbeat, check_stock, check_keywords
)

def main():
    load_dotenv()
    logger = setup_logger()
    setup_exit_handlers(logger)
    logger.info("Keycult 모니터링 서비스 시작")
    send_notification("Keycult 모니터링 서비스 시작", "Keycult 모니터링 서비스가 정상적으로 시작되었습니다.", logger)

    # 인자/환경변수 파싱
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
        try:
            check_interval = int(os.getenv('CHECK_INTERVAL', ''))
        except Exception:
            check_interval = None
        try:
            heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL', ''))
        except Exception:
            heartbeat_interval = None
    if check_interval is None:
        check_interval = 1
    if heartbeat_interval is None:
        heartbeat_interval = 30

    logger.info(f"재고 확인 간격: {check_interval}분, 생존 알림 간격: {heartbeat_interval}시간")
    send_notification("Keycult 모니터링 서비스 시작", f"재고 확인 간격: {check_interval}분, 생존 알림 간격: {heartbeat_interval}시간", logger)

    # 환경 변수
    KEYWORDS = os.getenv('MONITOR_KEYWORDS', '').split(',')
    KEYWORD_CHECK_INTERVAL = int(os.getenv('KEYWORD_CHECK_INTERVAL', '300'))

    last_notification_time = datetime.now()
    last_stock_check_time = datetime.now()

    # 스케줄 등록
    def stock_job():
        nonlocal last_notification_time, last_stock_check_time
        last_notification_time, last_stock_check_time = check_stock(
            logger, last_notification_time, last_stock_check_time)
    schedule.every(check_interval).minutes.do(stock_job)

    if KEYWORDS:
        schedule.every(KEYWORD_CHECK_INTERVAL).seconds.do(lambda: check_keywords(logger, KEYWORDS))

    def heartbeat_job():
        nonlocal last_notification_time
        last_notification_time = send_heartbeat(logger, heartbeat_interval, last_notification_time)
    schedule.every(heartbeat_interval).hours.do(heartbeat_job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt로 종료")
        sys.exit(0)
    except Exception as e:
        logger.error(f"예외로 인한 서비스 종료: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 