#!/bin/bash

# 에러 처리 설정
set -e
trap 'handle_error ${LINENO}' ERR

# 설정 파일 로드
source "$(dirname "$0")/config.sh"

log_info "Keycult 모니터링 서비스 제거 시작..."

# 실행 중인 프로세스 찾기 및 종료
PROCESS_ID=$(ps aux | grep "keycult_monitor.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$PROCESS_ID" ]; then
    log_info "실행 중인 프로세스(PID: $PROCESS_ID) 종료 중..."
    kill $PROCESS_ID
    sleep 2
    if ps -p $PROCESS_ID > /dev/null; then
        log_info "프로세스 강제 종료 중..."
        kill -9 $PROCESS_ID
    fi
    log_info "프로세스가 종료되었습니다."
else
    log_info "실행 중인 프로세스가 없습니다."
fi

# 서비스 언로드
if check_service_status; then
    log_info "서비스 언로드 중..."
    launchctl unload "$PLIST_PATH"
    log_info "서비스가 언로드되었습니다."
else
    log_info "서비스가 이미 중지되어 있습니다."
fi

# 서비스 파일 제거
if [ -f "$PLIST_PATH" ]; then
    log_info "서비스 설정 파일 제거 중..."
    rm -f "$PLIST_PATH"
    log_info "서비스 설정 파일이 제거되었습니다."
else
    log_info "서비스 설정 파일이 이미 제거되어 있습니다."
fi

log_info "모든 작업이 완료되었습니다."
log_info "로그 파일은 $LOG_DIR 디렉토리에 남아있습니다." 