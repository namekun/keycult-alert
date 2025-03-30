#!/bin/bash

# 스크립트의 디렉토리로 이동
cd "$(dirname "$0")"

# 환경 변수 설정
export PYTHONIOENCODING=utf-8
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8

# 명령줄 인자 확인
if [ $# -ne 2 ]; then
    echo "사용법: $0 <재고확인간격> <생존알림간격>"
    exit 1
fi

# Python 스크립트 실행
python3 "$(pwd)/keycult_monitor.py" "$1" "$2" 