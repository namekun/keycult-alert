#!/bin/bash

# 스크립트의 디렉토리로 이동
cd "$(dirname "$0")"

# Python 가상환경 활성화
source venv/bin/activate

# 로그 디렉토리 생성
mkdir -p logs

# 현재 시간을 로그 파일명에 포함
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/keycult_monitor_${TIMESTAMP}.log"

# 환경 변수 설정
export PYTHONIOENCODING=utf-8
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8

# 명령줄 인자에서 시간 간격을 받아서 Python 스크립트에 전달
if [ $# -eq 2 ]; then
    CHECK_INTERVAL=$1
    HEARTBEAT_INTERVAL=$2
    python3 keycult_monitor.py $CHECK_INTERVAL $HEARTBEAT_INTERVAL 2>&1 | tee "$LOG_FILE"
else
    # 인자가 없으면 사용자 입력 받기
    python3 keycult_monitor.py 2>&1 | tee "$LOG_FILE"
fi 