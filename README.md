# 만물도깨비 유튜브 경매 자동화

YouTube 라이브 채팅을 모니터링해 경매와 `[N개한정]` 선착순 주문을 자동으로 판별하고, 낙찰 결과를 엑셀 주문서로 저장하는 프로젝트입니다.

## 주요 기능

- YouTube 라이브 채팅 실시간 폴링
- 호스트 메시지 기반 경매 시작/낙찰선 감지
- 경매: 낙찰선 이전 사용자별 최고가 기준 낙찰
- 선착순: 먼저 입력한 순서와 요청 수량 기준 낙찰
- 회원 명단과 차단 목록 엑셀 대조
- 중복 낙찰 표시
- 주문서 저장 시 고객명 가나다 순 정렬

## 설치

```bash
pip install -r requirements.txt
```

Mac 앱 개발/빌드까지 할 때는 Node 패키지도 설치합니다.

```bash
npm install
```

## 실행

```bash
YOUTUBE_API_KEY="발급받은_API_KEY" YOUTUBE_VIDEO_ID="영상ID" python -m auction
```

환경변수로 설정을 바꿀 수 있습니다.

| 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `YOUTUBE_API_KEY` | `YOUR_YOUTUBE_API_KEY` | YouTube Data API v3 API 키 |
| `YOUTUBE_VIDEO_ID` | `qxv6hXXFdXA` | 방송 영상 ID |
| `MEMBER_FILE` | `회원명단.xlsx` | 회원 명단 파일 |
| `BLOCKED_FILE` | `차단목록.xlsx` | 차단 목록 파일 |
| `COL_ID` | `아이디` | YouTube 표시이름 컬럼 |
| `COL_NAME` | `고객명` | 고객명 컬럼 |
| `COL_PHONE` | `연락처` | 연락처 컬럼 |
| `COL_ADDRESS` | `주소` | 주소 컬럼 |
| `HOST_KEYWORD` | `만물도깨비` | 호스트 채널명 키워드 |
| `POLL_SEC` | `6` | 최소 폴링 간격(초) |
| `SORT_BY_NAME` | `true` | 저장 전 고객명 정렬 여부 |

## 파일 구조

```text
.
├── .github
│   └── workflows
│       └── build-windows.yml
├── .gitignore
├── README.md
├── WINDOWS_BUILD_GUIDE.md
├── auction
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py
│   ├── config.py
│   ├── detector.py
│   ├── identity.py
│   ├── members.py
│   ├── monitor.py
│   ├── parser.py
│   ├── run_monitor.py
│   ├── winner.py
│   ├── workbook.py
│   └── youtube_client.py
├── dist-electron
│   ├── 도깨비경매-darwin-x64
│   └── 도깨비경매-electron-mac-test.zip
├── electron
│   ├── index.html
│   ├── main.js
│   ├── preload.js
│   ├── renderer.js
│   └── styles.css
├── monitor_entry.py
├── node_modules
├── packaging
│   ├── build_mac_app.sh
│   └── build_windows.ps1
├── package-lock.json
├── package.json
├── requirements.txt
├── tests
    ├── __init__.py
    └── test_parser.py
├── dokkaebi-auction-windows-build-source.zip
└── 도깨비경매-windows-build-source.zip
```

## 모듈 책임

- `auction/app.py`: 실행 흐름과 상태 관리
- `auction/config.py`: 환경변수 기반 설정
- `auction/detector.py`: 경매 시작, 낙찰선, 기준가 감지
- `auction/identity.py`: YouTube 표시이름 정규화
- `auction/members.py`: 회원/차단 엑셀 로드
- `auction/monitor.py`: CLI와 Mac 앱이 공유하는 실시간 모니터링 엔진
- `auction/parser.py`: 입찰 금액과 선착순 수량 파싱
- `auction/run_monitor.py`: Electron 앱에서 실행하는 JSON 설정 기반 모니터
- `auction/winner.py`: 낙찰자 산정
- `auction/workbook.py`: 주문서 엑셀 생성, 행 작성, 정렬
- `auction/youtube_client.py`: YouTube API 호출
- `electron/index.html`: Mac 앱 화면 구조
- `electron/main.js`: Electron 메인 프로세스와 Python 모니터 실행
- `electron/preload.js`: 화면과 메인 프로세스 사이의 안전한 API
- `electron/renderer.js`: 화면 이벤트와 상태 관리
- `electron/styles.css`: Mac 앱 화면 스타일
- `monitor_entry.py`: Windows 설치파일에 포함할 모니터 실행파일 진입점
- `packaging/build_mac_app.sh`: Mac 앱 빌드 스크립트
- `packaging/build_windows.ps1`: Windows 설치파일 빌드 스크립트
- `.github/workflows/build-windows.yml`: Windows 설치파일 자동 빌드 워크플로
- `.gitignore`: 빌드 산출물과 의존성 폴더 제외 설정
- `dist-electron/도깨비경매-darwin-x64/도깨비경매.app`: 테스트용 Mac 앱
- `dist-electron/도깨비경매-electron-mac-test.zip`: 앱 전달용 압축 파일
- `package.json`, `package-lock.json`, `node_modules`: Electron 앱 의존성
- `tests/test_parser.py`: 입찰 금액/수량 파싱 회귀 테스트
- `WINDOWS_BUILD_GUIDE.md`: Windows 설치파일 생성 상세 안내
- `dokkaebi-auction-windows-build-source.zip`: GitHub 업로드/Windows 빌드용 영문 경로 소스 압축본
- `도깨비경매-windows-build-source.zip`: 이전 한글 경로 소스 압축본

## Mac 앱 테스트

이미 만든 테스트 앱은 `dist-electron/도깨비경매-darwin-x64/도깨비경매.app`에 있습니다.

다시 빌드하려면 아래 명령을 실행합니다.

```bash
npm run build:mac
```

전달용 압축 파일은 `dist-electron/도깨비경매-electron-mac-test.zip`입니다.

## Windows 설치파일 만들기

Windows 설치파일은 Windows 환경에서 빌드합니다. Windows PC 또는 GitHub Actions의 `windows-latest` 러너에서 아래 스크립트를 실행합니다.

```powershell
powershell -ExecutionPolicy Bypass -File packaging/build_windows.ps1
```

빌드가 끝나면 `release/DokkaebiAuction-Setup-0.1.0.exe` 형태의 설치파일이 생성됩니다. 이 파일을 다른 Windows 컴퓨터에 전달하면 Python을 따로 설치하지 않아도 실행할 수 있습니다.

GitHub에 올려두면 `.github/workflows/build-windows.yml` 워크플로가 같은 과정을 자동으로 수행하고, 결과 설치파일을 `DokkaebiAuction-Windows-Installer` 아티팩트로 제공합니다.

자세한 단계는 `WINDOWS_BUILD_GUIDE.md`에 정리되어 있습니다.

## 테스트

```bash
PYTHONPYCACHEPREFIX=/private/tmp/auction_pycache python3 -m unittest
```
