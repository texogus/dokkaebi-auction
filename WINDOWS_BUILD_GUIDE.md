# Windows 설치파일 생성 방법

이 프로젝트는 Windows 설치파일을 GitHub Actions에서 자동으로 만들 수 있게 준비되어 있습니다.

## 왜 Mac에서 바로 exe를 만들지 않나요?

Windows용 설치파일에는 `auction-monitor.exe`가 포함되어야 합니다. 이 실행파일은 Python 코드를 Windows 실행파일로 묶은 것이고, 안정적으로 만들려면 Windows 환경에서 빌드해야 합니다.

현재 Mac에는 Windows 실행파일 빌드에 필요한 환경이 없으므로, GitHub의 Windows 서버에서 자동 빌드하는 방식을 사용합니다.

## 방법 1: GitHub Actions로 만들기

### 1. GitHub 저장소 만들기

1. GitHub에 로그인합니다.
2. 새 저장소를 만듭니다.
3. 저장소 이름 예시: `dokkaebi-auction`
4. Public 또는 Private은 원하는 대로 선택합니다.

### 2. 이 프로젝트를 GitHub에 올리기

터미널에서 프로젝트 폴더로 이동합니다.

```bash
cd "/Users/te/Documents/도깨비 경매"
```

GitHub 저장소 주소를 연결합니다.

```bash
git remote add origin https://github.com/사용자명/dokkaebi-auction.git
```

파일을 커밋하고 올립니다.

```bash
git add .
git commit -m "Build Windows installer"
git push -u origin main
```

### 3. GitHub Actions 실행

1. GitHub 저장소 페이지로 갑니다.
2. 상단 `Actions` 탭을 누릅니다.
3. `Build Windows Installer` 워크플로를 선택합니다.
4. `Run workflow` 버튼을 누릅니다.
5. 실행이 끝날 때까지 기다립니다.

### 4. 설치파일 다운로드

워크플로 실행 결과 페이지 아래쪽의 `Artifacts`에서 `DokkaebiAuction-Windows-Installer`를 다운로드합니다.

압축을 풀면 다음과 같은 설치파일이 있습니다.

```text
DokkaebiAuction-Setup-0.1.0.exe
```

이 파일을 다른 Windows 컴퓨터에 전달하면 됩니다.

## 방법 2: Windows 컴퓨터에서 직접 만들기

Windows 컴퓨터에 아래 프로그램이 필요합니다.

- Python 3.12 이상
- Node.js 22 이상
- Git

프로젝트 폴더에서 PowerShell을 열고 실행합니다.

```powershell
powershell -ExecutionPolicy Bypass -File packaging/build_windows.ps1
```

완료 후 `release` 폴더에 설치파일이 생깁니다.

```text
release/DokkaebiAuction-Setup-0.1.0.exe
```

## 포함되는 것

Windows 설치파일에는 다음이 포함됩니다.

- Electron 데스크톱 앱
- Python 경매 모니터 실행파일 `auction-monitor.exe`
- YouTube 라이브 채팅 감지 로직
- 엑셀 주문서 생성 로직

사용자는 Python을 따로 설치하지 않아도 됩니다.
