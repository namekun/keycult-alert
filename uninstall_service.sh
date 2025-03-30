#!/bin/bash

# 스크립트의 디렉토리로 이동
cd "$(dirname "$0")"

echo "Keycult 모니터링 서비스를 종료합니다..."

# 실행 중인 프로세스 찾기 및 종료
PROCESS_ID=$(ps aux | grep "keycult_monitor.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$PROCESS_ID" ]; then
    echo "실행 중인 프로세스(PID: $PROCESS_ID)를 종료합니다..."
    kill $PROCESS_ID
    echo "프로세스가 종료되었습니다."
else
    echo "실행 중인 프로세스가 없습니다."
fi

# 서비스 언로드
echo "서비스를 언로드합니다..."
launchctl unload ~/Library/LaunchAgents/com.keycult.monitor.plist

# 서비스 파일 제거
echo "서비스 파일을 제거합니다..."
rm -f ~/Library/LaunchAgents/com.keycult.monitor.plist

echo "모든 작업이 완료되었습니다."
echo "로그 파일은 logs 디렉토리에 남아있습니다." 