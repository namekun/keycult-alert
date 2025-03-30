#!/bin/bash

# 서비스 언로드
launchctl unload ~/Library/LaunchAgents/com.keycult.monitor.plist

# 서비스 파일 제거
rm ~/Library/LaunchAgents/com.keycult.monitor.plist

echo "서비스가 제거되었습니다."
echo "로그 파일은 logs 디렉토리에 남아있습니다." 