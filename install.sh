#!/bin/bash

# 스크립트의 디렉토리로 이동
cd "$(dirname "$0")"

# Python 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 필요한 패키지 설치
pip install requests beautifulsoup4 schedule python-dotenv slack-sdk discord-webhook

# 로그 디렉토리 생성
mkdir -p logs

# 실행 권한 부여
chmod +x run_monitor.sh

echo "설치가 완료되었습니다."
echo "실행하려면 ./run_monitor.sh를 실행하세요."
echo "실행 시 재고 확인 간격과 생존 알림 간격을 입력하라는 메시지가 표시됩니다." 