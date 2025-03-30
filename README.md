# Keycult 재고 모니터링 프로그램

Keycult 웹사이트의 특정 키보드 모델의 재고 상태를 모니터링하고, 재고가 입고되면 알림을 보내는 프로그램입니다.

## 기능

- Keycult No. 2/65 Raw (Stonewashed / Diagonal Unfinish) 모델의 재고 상태 모니터링
- 재고 입고 시 이메일, Slack, Discord 알림 발송
- 프로그램 생존 상태 확인을 위한 주기적 알림
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
cd keycult-monitor
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
1. 재고 확인 간격 (분 단위)
2. 생존 알림 간격 (분 단위)

### 직접 시간 간격 지정 실행
```bash
./run_monitor.sh [재고확인간격] [생존알림간격]
```
예시:
```bash
./run_monitor.sh 10 15  # 재고 확인 10분, 생존 알림 15분
```

### 서비스로 실행
```bash
chmod +x install_service.sh
./install_service.sh
```

서비스로 실행하면 컴퓨터를 시작할 때마다 자동으로 실행됩니다.
- 기본 재고 확인 간격: 5분
- 기본 생존 알림 간격: 60분
- 시간 간격을 변경하려면 `config.sh` 파일의 `DEFAULT_CHECK_INTERVAL`과 `DEFAULT_HEARTBEAT_INTERVAL` 값을 수정하세요.

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

- 프로그램 실행 중 발생하는 모든 로그는 `logs` 디렉토리에 저장됩니다.
- 로그 파일은 날짜와 시간이 포함된 이름으로 생성됩니다.
- 서비스 실행 시의 로그는 다음 파일에서 확인할 수 있습니다:
  - `logs/keycult_monitor_output.log`: 일반 출력 로그
  - `logs/keycult_monitor_error.log`: 에러 로그

## 설정 파일

### config.sh
- 기본 설정값 관리
- 환경 변수 설정
- 공통 함수 정의
- 에러 처리 및 로깅 함수

주요 설정값:
```bash
DEFAULT_CHECK_INTERVAL=5      # 기본 재고 확인 간격 (분)
DEFAULT_HEARTBEAT_INTERVAL=60 # 기본 생존 알림 간격 (분)
```

## 주의사항

- Gmail을 사용하는 경우, 앱 비밀번호를 생성하여 사용해야 합니다.
- 너무 짧은 간격으로 설정하면 웹사이트에 과도한 부하를 줄 수 있습니다.
- 프로그램을 종료하려면 Ctrl+C를 누르거나 서비스 제거 스크립트를 실행하세요.
- 서비스 설치 전에 `.env` 파일이 올바르게 설정되어 있어야 합니다.
- 서비스 설치 스크립트는 현재 디렉토리에서 실행해야 합니다.
- macOS의 보안 정책으로 인해 서비스 실행 시 가상환경 접근이 제한될 수 있습니다. 