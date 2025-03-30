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

# 실행 권한 부여
chmod +x "$SCRIPT_DIR/run_monitor.sh"
chmod +x "$SCRIPT_DIR/uninstall_service.sh"
chmod +x "$SCRIPT_DIR/run_service.sh"

# 서비스 파일 생성
log_info "서비스 설정 파일 생성 중..."
cat > "$PLIST_PATH" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.keycult.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd "$SCRIPT_DIR" && PYTHONIOENCODING=utf-8 LANG=ko_KR.UTF-8 LC_ALL=ko_KR.UTF-8 "$VENV_DIR/bin/python3" "$SCRIPT_DIR/keycult_monitor.py" $DEFAULT_CHECK_INTERVAL $DEFAULT_HEARTBEAT_INTERVAL</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/keycult_monitor_error.log</string>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/keycult_monitor_output.log</string>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
</dict>
</plist>
EOL

# 기존 서비스 제거
if check_service_status; then
    log_info "기존 서비스 제거 중..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
fi

# 서비스 로드
log_info "서비스 로드 중..."
launchctl load "$PLIST_PATH"

# 서비스 상태 확인
if check_service_status; then
    log_info "서비스가 성공적으로 설치되었습니다."
    log_info "재고 확인 간격: $DEFAULT_CHECK_INTERVAL분"
    log_info "생존 알림 간격: $DEFAULT_HEARTBEAT_INTERVAL분"
    log_info "로그 파일: $LOG_DIR/keycult_monitor_*.log"
    log_info "서비스 제거: ./uninstall_service.sh"
else
    log_error "서비스 설치 실패"
    exit 1
fi 