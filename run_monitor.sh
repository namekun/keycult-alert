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

# 프로그램 실행 및 로그 저장
python3 keycult_monitor.py 2>&1 | tee "$LOG_FILE" 