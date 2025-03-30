#!/bin/bash

# 에러 처리 설정
set -e
trap 'handle_error ${LINENO}' ERR

# 설정 파일 로드
source "$(dirname "$0")/config.sh"

# 환경 확인
check_environment

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 현재 시간을 로그 파일명에 포함
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/keycult_monitor_${TIMESTAMP}.log"

# 명령줄 인자에서 시간 간격을 받아서 Python 스크립트에 전달
if [ $# -eq 2 ]; then
    CHECK_INTERVAL=$1
    HEARTBEAT_INTERVAL=$2
    log_info "재고 확인 간격: $CHECK_INTERVAL분"
    log_info "생존 알림 간격: $HEARTBEAT_INTERVAL분"
    "$VENV_DIR/bin/python3" "$SCRIPT_DIR/keycult_monitor.py" "$CHECK_INTERVAL" "$HEARTBEAT_INTERVAL" 2>&1 | tee "$LOG_FILE"
else
    # 인자가 없으면 사용자 입력 받기
    log_info "시간 간격을 입력해주세요:"
    "$VENV_DIR/bin/python3" "$SCRIPT_DIR/keycult_monitor.py" 2>&1 | tee "$LOG_FILE"
fi 