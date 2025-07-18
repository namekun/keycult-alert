# Keycult 재고 모니터링 프로그램

Keycult 웹사이트의 특정 키보드 모델의 재고 상태를 모니터링하고, 재고가 입고되면 알림을 보내는 프로그램입니다.
ReadMe는 mac 기반으로 작성하였습니다.

## 기능

- Keycult No. 2/65 Raw (Stonewashed / Diagonal Unfinish) 모델의 재고 상태 모니터링
- DNS 해상도 실패 시 최대 3회 재시도 및 HTTP 요청 타임아웃(10초) 적용
- 재고 입고 시 10회 반복 알림 전송 (이메일, Slack, Discord)
- 프로그램 생존 상태 확인을 위한 주기적 알림 (설정 간격마다 정확히 전송)
- 자세한 로그 기록
- 사용자 설정 가능한 모니터링 간격
- 안정적인 백그라운드 서비스 지원

## 보안 주의사항

- `.env` 파일은 절대로 Git에 커밋하지 마세요.
- 개인정보(이메일, 비밀번호, 토큰 등)는 반드시 `.env` 파일에서 관리하세요.
- `.env` 파일을 다른 사람과 공유하지 마세요.
- GitHub에 푸시하기 전에 `.env` 파일이 포함되지 않았는지 확인하세요.

## 설치 방법

1. 저장소를 클론합니다:
```bash
git clone [repository-url]
cd keycult-alert
```

2. 설치 스크립트를 실행합니다:
```bash
chmod +x install.sh
./install.sh
```

3. `.env` 파일을 생성하고 필요한 환경변수를 설정합니다:
```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
RECEIVER_EMAIL=receiver@example.com
SLACK_WEBHOOK_URL=your-slack-webhook-url
DISCORD_WEBHOOK_URL=your-discord-webhook-url
```

## 실행 방법

### 일반 실행
```bash
./run_monitor.sh
```
실행 시 다음 정보를 입력하라는 메시지가 표시됩니다:
1. 재고 확인 간격 (분 단위, 예: 1)
2. 생존 알림 간격 (시간 단위, 예: 1)

- **재고 확인**: 입력한 간격(분)마다 실행됩니다.
- **생존 알림**: 입력한 간격(시간)마다 주기적으로 울리며, 메시지에 입력한 생존 알림 간격이 함께 표시됩니다.

### 직접 시간 간격 지정 실행
```bash
./run_monitor.sh [재고확인간격] [생존알림간격]
```
예시:
```bash
./run_monitor.sh 1 2  # 재고 확인 1분, 생존 알림 2시간마다
```

### 서비스로 실행
```bash
chmod +x install_service.sh
./install_service.sh
```
- 서비스로 실행하면 컴퓨터를 시작할 때마다 자동으로 실행됩니다.
- 기본 재고 확인 간격: 1분
- 기본 생존 알림 간격: 1시간
- 시간 간격을 변경하려면 `config.sh` 파일의 `DEFAULT_CHECK_INTERVAL`과 `DEFAULT_HEARTBEAT_INTERVAL` 값을 수정하세요.

### run_monitor.sh와 install_service.sh의 차이

- `run_monitor.sh`: 즉시 모니터링을 시작하며, 실행 시 또는 명령줄 인자로 시간 간격을 지정할 수 있습니다. 로그 파일은 실행 시점의 타임스탬프를 포함한 이름으로 `logs` 폴더에 저장됩니다.
- `install_service.sh`: macOS LaunchAgent 서비스를 생성하여 백그라운드에서 모니터링을 실행합니다. 기본 간격을 사용하며 컴퓨터를 재시작해도 자동으로 동작합니다.

## 서비스 관리

### 서비스 상태 확인
```bash
launchctl list | grep keycult
```

### 서비스 제거
```bash
./uninstall_service.sh
```

이 명령어는 다음 작업을 수행합니다:
1. 실행 중인 모니터링 프로세스를 찾아 종료
2. 서비스를 언로드
3. 서비스 설정 파일 제거

## 로그 관리

- 모든 로그는 `logs` 디렉토리에 저장됩니다.
- 로그 파일은 `TimedRotatingFileHandler`로 매일 회전되며, 파일명은 `keycult_monitor_YYYY-MM-DD.log` 형식입니다.
- INFO 및 ERROR 레벨 로그가 하나의 통합 로그 파일에 기록되며, DNS 해상도 시도, HTTP 요청/응답, 재시도, 알림 전송 이벤트 등이 포함됩니다.
- 필요 시 로깅 설정을 `config.sh`에서 조정할 수 있습니다.

## 설정 파일

### config.sh
- 기본 설정값 관리
- 환경 변수 설정
- 공통 함수 정의
- 에러 처리 및 로깅 함수

주요 설정값:
```bash
DEFAULT_CHECK_INTERVAL=1      # 기본 재고 확인 간격 (분)
DEFAULT_HEARTBEAT_INTERVAL=12 # 기본 생존 알림 간격 (시간)
```

## 주의사항

- Gmail을 사용하는 경우, 앱 비밀번호를 생성하여 사용해야 합니다.
- 너무 짧은 간격으로 설정하면 웹사이트에 과도한 부하를 줄 수 있습니다.
- 프로그램을 종료하려면 Ctrl+C를 누르거나 서비스 제거 스크립트를 실행하세요.
- 서비스 설치 전에 `.env` 파일이 올바르게 설정되어 있어야 합니다.
- 서비스 설치 스크립트는 현재 디렉토리에서 실행해야 합니다.
- macOS의 보안 정책으로 인해 서비스 실행 시 가상환경 접근이 제한될 수 있습니다. 

## 최근 변경 및 주요 안내

### 2024-06 업데이트

- **Docker 지원**: Dockerfile, docker-compose.yml 추가. 컨테이너에서 바로 실행 가능
- **시간대 자동 설정**: 컨테이너에서 한국 시간(Asia/Seoul)으로 로그 및 시간 동작
- **환경변수 기반 설정**: CHECK_INTERVAL, HEARTBEAT_INTERVAL을 .env 또는 docker 환경변수로 지정 가능
- **서비스 시작 알림**: 서비스가 시작될 때 알림(이메일/슬랙/디스코드) 자동 전송
- **로그 실시간 확인**: docker compose logs -f keycult-monitor 등으로 실시간 로그 확인 가능
- **stdout 로그 출력**: 모든 로그가 파일과 동시에 콘솔에도 출력되어 도커 로그에서 바로 확인 가능

---

## Docker로 실행하기

### 1. 이미지 빌드 및 실행
```bash
docker compose build
docker compose up -d
```

### 2. 환경변수(.env) 예시
```
CHECK_INTERVAL=1
HEARTBEAT_INTERVAL=60
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
RECEIVER_EMAIL=receiver@example.com
SLACK_WEBHOOK_URL=your-slack-webhook-url
DISCORD_WEBHOOK_URL=your-discord-webhook-url
```

### 3. 로그 확인
```bash
docker compose logs -f keycult-monitor
```

### 4. 시간대 문제 해결
- 컨테이너는 자동으로 Asia/Seoul(한국) 시간대가 적용됩니다.
- 로그 및 알림의 시간이 한국 기준으로 표시됩니다.

### 5. 컨테이너 이름 지정 실행 예시
```bash
docker run --name keycult-monitor --env-file .env -v $(pwd)/logs:/app/logs keycult-monitor
```

---
