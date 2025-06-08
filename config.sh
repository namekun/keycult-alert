#!/bin/bash

# 기본 설정
DEFAULT_CHECK_INTERVAL=1
DEFAULT_HEARTBEAT_INTERVAL=60

# 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
LOG_DIR="$SCRIPT_DIR/logs"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$PLIST_DIR/com.keycult.monitor.plist"

# Ensure required directories exist
mkdir -p "$LOG_DIR" "$PLIST_DIR"

# 환경 변수
export PYTHONIOENCODING=utf-8
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8

# 로깅 함수
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

# 에러 처리 함수
handle_error() {
    local exit_code=$?
    local line_number=$1
    log_error "스크립트 실행 중 오류 발생 (라인: $line_number, 종료 코드: $exit_code)"
    exit $exit_code
}

# 환경 확인 함수
check_environment() {
    if [ ! -d "$VENV_DIR" ]; then
        log_error "가상환경이 존재하지 않습니다. install.sh를 먼저 실행해주세요."
        exit 1
    fi

    if [ ! -f "$SCRIPT_DIR/keycult_monitor.py" ]; then
        log_error "keycult_monitor.py 파일을 찾을 수 없습니다."
        exit 1
    fi

    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        log_error ".env 파일을 찾을 수 없습니다."
        exit 1
    fi
}

# 서비스 상태 확인 함수
check_service_status() {
    if launchctl list | grep -q "com.keycult.monitor"; then
        return 0  # 서비스 실행 중
    else
        return 1  # 서비스 중지됨
    fi
} 
