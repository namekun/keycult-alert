# Python 3.11 slim 이미지를 사용
FROM python:3.11-slim

# 작업 디렉토리 생성 및 이동
WORKDIR /app

# 시스템 패키지 설치 (필요시)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime \
    && echo 'Asia/Seoul' > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Seoul

# 파이썬 의존성 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사 (패키지 전체)
COPY keycult_monitor/ ./keycult_monitor/
COPY com.keycult.monitor.plist ./

# logs 디렉토리 생성
RUN mkdir -p /app/logs

# .env 파일은 반드시 컨테이너 실행 시 마운트 또는 복사 필요
# 예시: docker run --env-file .env ...

# 기본 실행 명령 (환경 변수로 간격 지정 가능)
ENV CHECK_INTERVAL=1
ENV HEARTBEAT_INTERVAL=1

CMD ["python", "-m", "keycult_monitor.main"]