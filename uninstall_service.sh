#!/bin/bash

# LaunchAgent 언로드
launchctl unload ~/Library/LaunchAgents/com.keycult.monitor.plist

# LaunchAgent 파일 제거
rm ~/Library/LaunchAgents/com.keycult.monitor.plist

echo "Keycult 모니터링 서비스가 제거되었습니다." 