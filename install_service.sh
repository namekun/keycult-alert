#!/bin/bash

# 스크립트의 디렉토리로 이동
cd "$(dirname "$0")"

# 실행 권한 부여
chmod +x run_monitor.sh
chmod +x uninstall_service.sh

# 기본 시간 간격 설정 (분 단위)
DEFAULT_CHECK_INTERVAL=1
DEFAULT_HEARTBEAT_INTERVAL=60

echo "실행 권한이 부여되었습니다."
echo "이제 ./run_monitor.sh를 실행하여 프로그램을 시작할 수 있습니다."

# 로그 디렉토리 생성
mkdir -p logs

# 서비스 파일 생성
cat > ~/Library/LaunchAgents/com.keycult.monitor.plist << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.keycult.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/run_monitor.sh</string>
        <string>$DEFAULT_CHECK_INTERVAL</string>
        <string>$DEFAULT_HEARTBEAT_INTERVAL</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>$(pwd)/logs/keycult_monitor_error.log</string>
    <key>StandardOutPath</key>
    <string>$(pwd)/logs/keycult_monitor_output.log</string>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
</dict>
</plist>
EOL

# 서비스 로드
launchctl load ~/Library/LaunchAgents/com.keycult.monitor.plist

echo "서비스가 설치되었습니다."
echo "재고 확인 간격: $DEFAULT_CHECK_INTERVAL분"
echo "생존 알림 간격: $DEFAULT_HEARTBEAT_INTERVAL분"
echo "로그 파일은 $(pwd)/logs 디렉토리에서 확인할 수 있습니다."
echo "서비스를 제거하려면 ./uninstall_service.sh를 실행하세요." 