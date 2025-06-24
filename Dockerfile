# Python 3.11 slim 이미지를 사용
FROM python:3.11-slim

# 작업 디렉토리 생성 및 이동
WORKDIR /app

# 시스템 패키지 설치 (필요시)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 의존성 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY keycult_monitor.py ./
COPY config.sh ./
COPY run_monitor.sh ./
COPY install_service.sh ./
COPY uninstall_service.sh ./
COPY com.keycult.monitor.plist ./

# 시간대 설정
RUN apt-get update && apt-get install -y tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo 'Asia/Seoul' > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Seoul

# logs 디렉토리 생성
RUN mkdir -p /app/logs

# .env 파일은 반드시 컨테이너 실행 시 마운트 또는 복사 필요
# 예시: docker run --env-file .env ...

# 실행 권한 부여 (쉘 스크립트)
RUN chmod +x run_monitor.sh install_service.sh uninstall_service.sh

# 기본 실행 명령 (환경 변수로 간격 지정 가능)
# 예: docker run -e CHECK_INTERVAL=1 -e HEARTBEAT_INTERVAL=60 ...
ENV CHECK_INTERVAL=1
ENV HEARTBEAT_INTERVAL=1

CMD sh -c 'python keycult_monitor.py "$CHECK_INTERVAL" "$HEARTBEAT_INTERVAL"'