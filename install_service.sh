#!/bin/bash

# LaunchAgent 디렉토리 생성
mkdir -p ~/Library/LaunchAgents

# LaunchAgent 파일 복사
cp com.keycult.monitor.plist ~/Library/LaunchAgents/

# 권한 설정
chmod 644 ~/Library/LaunchAgents/com.keycult.monitor.plist

# LaunchAgent 로드
launchctl load ~/Library/LaunchAgents/com.keycult.monitor.plist

echo "Keycult 모니터링 서비스가 설치되었습니다."
echo "로그 파일: ~/Desktop/DEV/keycult/keycult_monitor.log" 