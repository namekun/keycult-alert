# Keycult 재고 모니터링 프로그램

이 프로그램은 Keycult 웹사이트의 No. 2/65 Raw 키보드 재고를 모니터링하고 재고가 입고되면 이메일, Slack, Discord로 알림을 보내는 프로그램입니다.

## 보안 주의사항

- `.env` 파일은 절대로 Git에 커밋하지 마세요.
- 개인정보(이메일, 비밀번호, 토큰 등)는 반드시 `.env` 파일에서 관리하세요.
- `.env` 파일을 다른 사람과 공유하지 마세요.
- GitHub에 푸시하기 전에 `.env` 파일이 포함되지 않았는지 확인하세요.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. `.env` 파일 설정:
- `EMAIL_ADDRESS`: Gmail 주소
- `EMAIL_PASSWORD`: Gmail 앱 비밀번호 (Gmail 계정 설정에서 생성)
- `RECEIVER_EMAIL`: 알림을 받을 이메일 주소
- `SLACK_WEBHOOK_URL`: Slack Webhook URL
- `DISCORD_WEBHOOK_URL`: Discord Webhook URL

## Gmail 앱 비밀번호 생성 방법

1. Google 계정 설정으로 이동
2. 보안 > 2단계 인증 활성화
3. 앱 비밀번호 생성
4. 생성된 비밀번호를 `.env` 파일의 `EMAIL_PASSWORD`에 입력

## Slack Webhook 설정 방법

1. Slack 워크스페이스에서 새로운 앱 생성:
   - [Slack API](https://api.slack.com/apps) 페이지로 이동
   - "Create New App" 클릭
   - "From scratch" 선택
   - 앱 이름과 워크스페이스 선택

2. Bot Token Scopes 설정:
   - "OAuth & Permissions" 메뉴 선택
   - "Scopes" 섹션에서 "Bot Token Scopes" 추가
   - "chat:write" 권한 추가

3. 워크스페이스에 앱 설치:
   - "Install to Workspace" 클릭
   - 권한 승인

4. Webhook URL 복사:
   - "OAuth & Permissions" 페이지에서 "Bot User OAuth Token" 복사
   - 복사한 토큰을 `.env` 파일의 `SLACK_WEBHOOK_URL`에 입력

5. 알림을 받을 채널 생성:
   - Slack에서 "#keycult-stock" 채널 생성
   - 생성한 채널에 앱 초대

## Discord Webhook 설정 방법

1. Discord 서버에서 Webhook 생성:
   - 알림을 받을 채널 설정에서 "연결 통합" 선택
   - "웹후크 생성" 클릭
   - 웹후크 이름 설정 (예: "Keycult Stock")
   - "웹후크 URL 복사" 클릭
   - 복사한 URL을 `.env` 파일의 `DISCORD_WEBHOOK_URL`에 입력

## 실행 방법

### 일반 실행
```bash
python keycult_monitor.py
```

### 백그라운드 서비스로 실행 (macOS)

1. 서비스 설치:
```bash
./install_service.sh
```

2. 서비스 제거:
```bash
./uninstall_service.sh
```

백그라운드 서비스로 실행 시:
- 컴퓨터를 시작할 때마다 자동으로 실행됩니다.
- 백그라운드에서 계속 실행됩니다.
- 로그는 `~/Desktop/DEV/keycult/keycult_monitor.log` 파일에서 확인할 수 있습니다.

## 기능

- 5분마다 자동으로 재고 확인
- 재고 입고 시 이메일, Slack, Discord로 알림 발송
- 콘솔에 모니터링 상태 출력

## 주의사항

- Gmail을 사용하는 경우 "보안 수준이 낮은 앱의 액세스"를 허용하거나 앱 비밀번호를 사용해야 합니다.
- 웹사이트의 HTML 구조가 변경되면 코드 수정이 필요할 수 있습니다.
- Slack 채널명은 "#keycult-stock"으로 설정되어 있습니다. 다른 채널명을 사용하려면 코드를 수정해야 합니다.
- 백그라운드 서비스 설치 전에 `.env` 파일이 올바르게 설정되어 있어야 합니다.
- 서비스 설치 스크립트는 현재 디렉토리에서 실행해야 합니다. 