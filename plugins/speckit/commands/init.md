---
description: speckit 프로젝트 초기화 및 CLI 설치 확인
allowed-tools: [Bash]
argument-hint: <project-name | 프로젝트명>
---

# Initialize speckit Project

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input is the project name.

**🌐 언어 지시사항**: 이 명령어를 실행할 때는 **사용자의 시스템 언어를 자동으로 감지**하여 해당 언어로 모든 안내, 설치 가이드, 초기화 메시지, 출력을 제공해야 합니다. 시스템 환경 변수(LANG, LC_ALL 등)나 사용자의 이전 대화 패턴을 분석하여 언어를 판단하세요.

GitHub speckit을 사용하여 명세 주도 개발(SDD) 프로젝트를 초기화합니다.

## Step 0: Check Existing Installation

먼저 `.specify/` 디렉토리가 이미 존재하는지 확인:

```bash
ls -la .specify/
```

**이미 초기화된 경우:**

AskUserQuestion 도구를 사용하여 사용자에게 확인:

```json
{
  "questions": [{
    "question": "이미 speckit 프로젝트가 초기화되어 있습니다. 어떻게 하시겠습니까?",
    "header": "재초기화",
    "multiSelect": false,
    "options": [
      {
        "label": "새로 초기화 (기존 데이터 삭제)",
        "description": ".specify/ 폴더를 삭제하고 처음부터 다시 초기화합니다. 기존의 constitution, specification, plan, tasks 파일이 모두 삭제됩니다."
      },
      {
        "label": "취소 (기존 설정 유지)",
        "description": "초기화를 취소하고 기존 speckit 프로젝트를 그대로 사용합니다."
      }
    ]
  }]
}
```

- **"새로 초기화"** 선택 시: Step 1으로 진행
- **"취소"** 선택 시: 아래 "Step 0.1: 기존 프로젝트 상태 확인"으로 진행

**초기화되지 않은 경우:**

바로 Step 1으로 진행

## Step 0.1: 기존 프로젝트 상태 확인

사용자가 "취소"를 선택한 경우, 현재 프로젝트의 상태를 확인하고 다음 작업을 안내합니다.

### 1. 프로젝트 구조 표시

```bash
tree -L 2 .specify/
```

또는 Windows의 경우:

```bash
ls -R .specify/ | head -30
```

### 2. 각 파일 존재 여부 확인

```bash
ls -lh .specify/memory/constitution.md 2>/dev/null && echo "✅ Constitution" || echo "❌ Constitution"
ls -lh .specify/memory/specification.md 2>/dev/null && echo "✅ Specification" || echo "❌ Specification"
ls -lh .specify/memory/plan.md 2>/dev/null && echo "✅ Plan" || echo "❌ Plan"
ls -lh .specify/memory/tasks.md 2>/dev/null && echo "✅ Tasks" || echo "❌ Tasks"
```

### 3. 진행 상태 분석 및 다음 작업 안내

파일 존재 여부에 따라 다음 작업을 안내:

**Constitution이 없는 경우:**
```
📋 현재 상태: speckit이 초기화되었지만 아직 프로젝트 원칙이 정의되지 않았습니다.

🚀 다음 작업:
   /speckit.constitution

   프로젝트의 핵심 원칙과 기준을 정의하세요.
```

**Constitution은 있지만 Specification이 없는 경우:**
```
📋 현재 상태: 프로젝트 원칙이 정의되었습니다.

✅ 완료: Constitution
❌ 대기: Specification → Plan → Tasks → Implementation

🚀 다음 작업:
   /speckit.specify <기능 설명>

   구현할 기능의 요구사항을 정의하세요.
   예: /speckit.specify Add user authentication with OAuth2
```

**Specification은 있지만 Plan이 없는 경우:**
```
📋 현재 상태: 기능 명세가 작성되었습니다.

✅ 완료: Constitution, Specification
❌ 대기: Plan → Tasks → Implementation

🚀 다음 작업:
   /speckit.plan

   명세를 기반으로 기술 구현 계획을 수립하세요.
```

**Plan은 있지만 Tasks가 없는 경우:**
```
📋 현재 상태: 기술 계획이 수립되었습니다.

✅ 완료: Constitution, Specification, Plan
❌ 대기: Tasks → Implementation

🚀 다음 작업:
   /speckit.tasks

   계획을 실행 가능한 작업으로 분해하세요.
```

**Tasks까지 있는 경우:**
```
📋 현재 상태: 모든 계획 단계가 완료되었습니다!

✅ 완료: Constitution, Specification, Plan, Tasks
🎯 준비됨: Implementation

🚀 다음 작업:
   /speckit.implement

   정의된 작업을 기반으로 구현을 시작하세요.

💡 또는 다음 명령어들을 사용할 수 있습니다:
   - /speckit.clarify : 모호한 부분 명확화
   - /speckit.analyze : 프로젝트 상태 분석
   - /speckit.checklist : 품질 게이트 체크리스트 실행
```

### 4. 명령어 종료

기존 프로젝트 상태를 확인하고 안내한 후 초기화 명령어를 종료합니다.

새로 초기화하려면 다시 `/speckit.init`을 실행하고 "새로 초기화"를 선택하세요.

## Step 1: Git Installation & Configuration Check

### 1.1 Git 설치 확인

먼저 Git이 설치되어 있는지 확인합니다:

```bash
git --version
```

**Git이 설치된 경우:**
```
✅ Git: OK (version X.X.X)
→ Step 1.2 (Git 설정 확인)로 진행
```

**Git이 설치되지 않은 경우:**

AskUserQuestion 도구를 사용하여 사용자에게 확인:

```json
{
  "questions": [{
    "question": "Git이 설치되어 있지 않습니다. speckit을 사용하려면 Git이 필요합니다. Git을 설치해드릴까요?",
    "header": "Git 설치",
    "multiSelect": false,
    "options": [
      {
        "label": "설치하기",
        "description": "Claude가 운영체제에 맞게 Git 설치를 도와드립니다 (권장)."
      },
      {
        "label": "직접 설치하기",
        "description": "설치 가이드를 안내받고 직접 설치합니다."
      },
      {
        "label": "Git 없이 진행",
        "description": "Git 없이 speckit만 초기화합니다 (권장하지 않음, 버전 관리 불가)."
      }
    ]
  }]
}
```

**"설치하기" 선택 시:**

운영체제를 감지하고 적절한 설치 명령어 실행:

**Windows:**
```bash
# winget 사용 (Windows 10/11 기본 탑재)
winget install --id Git.Git -e --source winget
```

**macOS:**
```bash
# Homebrew 확인
brew --version 2>/dev/null

# Homebrew 없으면 먼저 설치
if [ $? -ne 0 ]; then
  echo "Homebrew를 설치합니다..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Git 설치
brew install git
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update && sudo apt-get install git -y
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install git -y
```

**Linux (Arch):**
```bash
sudo pacman -S git --noconfirm
```

설치 완료 후:
```bash
# 설치 확인
git --version

# 성공 메시지
echo "✅ Git 설치 완료! (version X.X.X)"
```

→ Step 1.2 (Git 설정 확인)로 진행

**"직접 설치하기" 선택 시:**

운영체제별 설치 가이드 안내:

**Windows:**
```
📥 Git for Windows 다운로드:
https://git-scm.com/download/win

설치 옵션 권장사항:
- Git Bash 포함 설치
- PATH에 Git 추가 선택
- 기본 에디터는 선호하는 것 선택

설치 후 터미널 재시작 → /speckit.init 재실행
```

**macOS:**
```
📥 Git 설치 방법:

방법 1 - Xcode Command Line Tools (권장):
$ xcode-select --install

방법 2 - Homebrew:
$ brew install git

방법 3 - 공식 인스톨러:
https://git-scm.com/download/mac

설치 후 터미널 재시작 → /speckit.init 재실행
```

**Linux:**
```
📥 Git 설치 방법:

Ubuntu/Debian:
$ sudo apt-get update && sudo apt-get install git

Fedora:
$ sudo dnf install git

Arch:
$ sudo pacman -S git

설치 후 터미널 재시작 → /speckit.init 재실행
```

→ 명령어 종료 (사용자가 설치 후 다시 실행해야 함)

**"Git 없이 진행" 선택 시:**

경고 메시지 표시:
```
⚠️  경고: Git 없이 진행합니다.

제한사항:
- 버전 관리 불가
- GitHub 연동 불가
- 협업 기능 제한
- speckit 일부 기능 제한될 수 있음

권장: 나중에라도 Git을 설치하고 git init을 실행하세요.
```

→ Step 3 (Git Repository Initialization) 건너뛰고 Step 2로 진행

### 1.2 Git 설정 확인

**Git이 설치된 경우에만 실행**

Git 사용자 정보가 설정되어 있는지 확인:

```bash
# 이름 확인
git config --global user.name

# 이메일 확인
git config --global user.email
```

**설정이 모두 있는 경우:**
```
✅ Git 설정: OK
   Name: [사용자이름]
   Email: [이메일]
→ Step 2로 진행
```

**설정이 없는 경우:**

AskUserQuestion 도구를 사용하여 사용자에게 확인:

```json
{
  "questions": [{
    "question": "Git 사용자 정보가 설정되지 않았습니다. Git 커밋을 하려면 이름과 이메일이 필요합니다. 지금 설정하시겠습니까?",
    "header": "Git 설정",
    "multiSelect": false,
    "options": [
      {
        "label": "지금 설정하기",
        "description": "이름과 이메일을 입력하여 Git을 설정합니다 (권장)."
      },
      {
        "label": "나중에 설정",
        "description": "첫 커밋 시 다시 설정할 수 있습니다."
      }
    ]
  }]
}
```

**"지금 설정하기" 선택 시:**

사용자에게 정보 요청 (일반 대화로):
```
Git 사용자 정보를 설정합니다.

이름을 입력해주세요 (예: Hong Gildong):
```

사용자 입력 대기 → 이름 저장

```
이메일을 입력해주세요 (예: hong@example.com):
```

사용자 입력 대기 → 이메일 저장

```bash
# Git 설정 적용
git config --global user.name "입력받은이름"
git config --global user.email "입력받은이메일"

# 설정 확인
echo "✅ Git 설정 완료!"
echo "   Name: $(git config --global user.name)"
echo "   Email: $(git config --global user.email)"
```

→ Step 2로 진행

**"나중에 설정" 선택 시:**

안내 메시지:
```
ℹ️  Git 설정을 나중에 하셔도 됩니다.

커밋 시 다음 명령어로 설정하세요:
  git config --global user.name "Your Name"
  git config --global user.email "your@email.com"
```

→ Step 2로 진행

## Step 2: uv & specify CLI Installation Check

필수 도구가 설치되어 있는지 확인:

```bash
uv --version
```

```bash
uv tool list | grep specify
```

**모두 설치됨:**
```
✅ uv: OK (version X.X.X)
✅ specify CLI: OK
   specify-cli v{version}
   - specify.exe

→ 프로젝트 초기화 준비 완료
```

**일부 미설치:**
- `/speckit.check` 명령으로 상세 확인 및 설치 안내를 받으세요

## Step 3: Git Repository Initialization

**Git이 설치된 경우에만 실행** (Step 1에서 "Git 없이 진행"을 선택한 경우 이 단계를 건너뜁니다)

### 3.1 로컬 Git 저장소 확인

현재 디렉토리가 Git 저장소인지 확인:

```bash
git rev-parse --git-dir 2>/dev/null
```

**Git 저장소가 있는 경우:**
```
✅ Git 저장소: 이미 초기화됨
→ Step 3.2 (GitHub 리모트 확인)로 진행
```

**Git 저장소가 없는 경우:**

Git 저장소 초기화:
```bash
git init

echo "✅ Git 저장소 초기화 완료"
```

→ Step 3.2로 진행

### 3.2 GitHub 리모트 확인

GitHub 원격 저장소가 연결되어 있는지 확인:

```bash
git remote -v
```

**리모트가 이미 있는 경우:**
```
✅ GitHub 리모트: 이미 연결됨
   origin: [URL]
→ Step 4로 진행
```

**리모트가 없는 경우:**

AskUserQuestion 도구를 사용하여 사용자에게 확인:

```json
{
  "questions": [{
    "question": "GitHub 리포지토리가 연결되어 있지 않습니다. speckit은 GitHub과 함께 사용하면 더 효과적입니다. 어떻게 하시겠습니까?",
    "header": "GitHub 연동",
    "multiSelect": false,
    "options": [
      {
        "label": "Private 리포지토리 생성",
        "description": "GitHub에 새 Private 리포지토리를 생성하고 자동으로 연결합니다 (권장)."
      },
      {
        "label": "기존 리포지토리 연결",
        "description": "이미 생성된 리포지토리 URL을 입력하여 연결합니다."
      },
      {
        "label": "나중에 설정",
        "description": "로컬에서만 작업하고 나중에 GitHub에 연결합니다."
      }
    ]
  }]
}
```

**"Private 리포지토리 생성" 선택 시:**

#### 3.2.1 GitHub CLI 설치 확인

```bash
gh --version
```

**GitHub CLI가 없는 경우:**

설치 안내 및 자동 설치:

**Windows:**
```bash
winget install --id GitHub.cli
```

**macOS:**
```bash
brew install gh
```

**Linux (Ubuntu/Debian):**
```bash
# 저장소 추가 및 설치
type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y
```

**Linux (Fedora):**
```bash
sudo dnf install gh -y
```

**Linux (Arch):**
```bash
sudo pacman -S github-cli --noconfirm
```

설치 완료:
```bash
gh --version
echo "✅ GitHub CLI 설치 완료"
```

#### 3.2.2 GitHub 로그인 확인

```bash
gh auth status
```

**로그인되지 않은 경우:**

사용자에게 안내:
```
GitHub에 로그인해야 합니다. 브라우저가 열리고 GitHub 인증 페이지로 이동합니다.

다음 단계를 따라주세요:
1. 브라우저에서 GitHub 로그인
2. 인증 코드 확인 및 승인
3. 터미널로 돌아오기

진행하시겠습니까? (Enter를 누르면 로그인이 시작됩니다)
```

사용자 확인 후:

```bash
# GitHub 로그인 시작
gh auth login --web --git-protocol https

# 로그인 성공 확인
gh auth status
echo "✅ GitHub 로그인 완료"
```

#### 3.2.3 Private 리포지토리 생성

프로젝트 이름 확인:
```bash
# 현재 디렉토리명 가져오기
PROJECT_NAME=$(basename "$(pwd)")
echo "프로젝트 이름: $PROJECT_NAME"
```

사용자에게 확인:
```
Private 리포지토리를 생성합니다:
  이름: $PROJECT_NAME
  공개 여부: Private (비공개)

계속하시겠습니까? (y/n)
```

사용자 승인 후:

```bash
# Private 리포지토리 생성 및 연결
gh repo create "$PROJECT_NAME" --private --source=. --remote=origin

echo ""
echo "✅ Private GitHub 리포지토리 생성 완료!"
echo "   Repository: https://github.com/$(gh api user -q .login)/$PROJECT_NAME"
echo "   Visibility: 🔒 Private"
echo ""

# 초기 커밋이 없으면 생성
if [ -z "$(git log --oneline 2>/dev/null)" ]; then
  echo "초기 커밋을 생성합니다..."
  git add .
  git commit -m "Initial commit: speckit initialization

🤖 Generated with speckit and Claude Code"
fi

# 푸시
git push -u origin main 2>/dev/null || git push -u origin master

echo "✅ 초기 코드 푸시 완료"
```

→ Step 4로 진행

**"기존 리포지토리 연결" 선택 시:**

사용자에게 URL 요청:
```
GitHub 리포지토리 URL을 입력해주세요.

형식 예시:
  - HTTPS: https://github.com/username/repo.git
  - SSH: git@github.com:username/repo.git

URL:
```

사용자 입력 대기 → URL 저장

```bash
# 리모트 추가
git remote add origin [입력받은URL]

# 리모트 확인
git remote -v

echo "✅ GitHub 리포지토리 연결 완료"
echo "   origin: [입력받은URL]"

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)

# 초기 커밋이 없으면 생성
if [ -z "$(git log --oneline 2>/dev/null)" ]; then
  echo "초기 커밋을 생성합니다..."
  git add .
  git commit -m "Initial commit: speckit initialization

🤖 Generated with speckit and Claude Code"
fi

# 푸시 시도
echo "원격 리포지토리에 푸시하시겠습니까? (y/n)"
```

사용자 승인 시:
```bash
git push -u origin $CURRENT_BRANCH
echo "✅ 푸시 완료"
```

→ Step 4로 진행

**"나중에 설정" 선택 시:**

안내 메시지:
```
ℹ️  GitHub 리포지토리를 나중에 연결하셔도 됩니다.

나중에 연결하려면:
  1. GitHub에서 리포지토리 생성
  2. git remote add origin [URL]
  3. git push -u origin main

또는 GitHub CLI 사용:
  gh repo create [프로젝트명] --private --source=. --remote=origin --push
```

→ Step 4로 진행

## Step 4: Project Initialization

프로젝트를 초기화합니다. 사용자에게 프로젝트 이름을 물어본 후:

**Git Bash (Windows 권장):**
```bash
# 현재 디렉토리에 초기화 (대화세션 중 사용)
PYTHONIOENCODING=utf-8 specify init --here --force --script ps --ai claude

# 새 디렉토리 생성
PYTHONIOENCODING=utf-8 specify init <project-name> --force --script ps --ai claude
```

**Windows CMD:**
```cmd
# 현재 디렉토리에 초기화 (대화세션 중 사용)
set PYTHONIOENCODING=utf-8 && specify init --here --force --script ps --ai claude

# 새 디렉토리 생성
set PYTHONIOENCODING=utf-8 && specify init <project-name> --force --script ps --ai claude
```

**Windows PowerShell:**
```powershell
# 현재 디렉토리에 초기화 (대화세션 중 사용)
$env:PYTHONIOENCODING="utf-8"; specify init --here --force --script ps --ai claude

# 새 디렉토리 생성
$env:PYTHONIOENCODING="utf-8"; specify init <project-name> --force --script ps --ai claude
```

**macOS/Linux:**
```bash
# 현재 디렉토리에 초기화
PYTHONIOENCODING=utf-8 specify init --here --force --script sh --ai claude

# 새 디렉토리 생성
PYTHONIOENCODING=utf-8 specify init <project-name> --force --script sh --ai claude
```

**주요 옵션 설명:**
- `--here`: 현재 디렉토리에 초기화
- `--force`: **필수** - 대화세션 중 초기화 시 확인 프롬프트 건너뛰기
- `--script ps`: PowerShell 스크립트 사용 (Windows 권장)
- `--script sh`: Shell 스크립트 사용 (Unix/macOS/Git Bash)
- `--ai claude`: Claude Code 사용 (기본)
- `--no-git`: Git 초기화 건너뛰기 (선택)
- `--debug`: 디버그 출력 활성화 (선택)

**중요**: `--force` 없이 실행하면 대화형 확인 프롬프트가 나타나 Claude Code 세션이 중단됩니다.

**성공 시 안내:**

speckit CLI가 초기화 메시지를 출력한 후, 다음과 같이 안내합니다:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 speckit 프로젝트 초기화 완료!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 생성된 구조:
.specify/
├── memory/
│   ├── constitution.md  # 프로젝트 원칙
│   ├── specification.md # 기능 명세
│   ├── plan.md         # 기술 계획
│   └── tasks.md        # 작업 목록
└── config.json

.claude/commands/
├── speckit.constitution.md
├── speckit.specify.md
├── speckit.plan.md
├── speckit.tasks.md
├── speckit.implement.md
├── speckit.clarify.md
├── speckit.analyze.md
└── speckit.checklist.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  중요: Claude Code를 재시작해야 새로운 명령어들이 로드됩니다!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 권장 워크플로우 (재시작 후):

🔰 초보자 / 가이드가 필요한 경우:
   대화형 플러그인을 사용하세요. Claude가 질문하며 단계별로 안내합니다.

   1️⃣  /speckit.constitution  ← 프로젝트 원칙 수립 (Q&A 가이드)
   2️⃣  /speckit.specify       ← 기능 명세 작성 (Q&A 가이드)
   3️⃣  /speckit.plan          ← 기술 계획 수립 (Q&A 가이드)
   4️⃣  /speckit.tasks         ← 작업 분해 (Q&A 가이드)
   5️⃣  /speckit.implement     ← 구현 시작 (Q&A 가이드)

⚡ 숙련자 / 빠른 실행이 필요한 경우:
   speckit 명령어를 직접 사용하세요. 즉시 파일을 생성/수정합니다.

   1️⃣  /speckit.constitution   ← 헌법 파일 직접 생성
   2️⃣  /speckit.specify        ← 명세 파일 직접 생성
   3️⃣  /speckit.plan           ← 계획 파일 직접 생성
   4️⃣  /speckit.tasks          ← 작업 파일 직접 생성
   5️⃣  /speckit.implement      ← 구현 직접 시작

💡 차이점:
   • /speckit.*   = 대화형 가이드 → 정보 수집 → /speckit.* 자동 호출
   • /speckit.*    = 즉시 실행 (가이드 없음)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 추천: 처음이라면 /speckit.constitution 으로 시작하세요!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## If NOT Ready

### uv가 없는 경우

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

설치 후: 터미널 재시작 → `uv --version` 확인 → `/speckit.init` 재실행

### specify CLI가 없는 경우

```bash
uv tool install specify-cli --from git+https://github.com/github/speckit.git
```

설치 후: `uv tool list | grep specify`로 확인 → `/speckit.init` 재실행

**PATH 설정** (선택사항):
```bash
uv tool update-shell
# 터미널 재시작 후 specify 명령 사용 가능
```

## Troubleshooting

### "specify: command not found" 또는 인코딩 오류

**방법 1**: 전체 경로 사용 (가장 확실)

**Windows (CMD):**
```cmd
set PYTHONIOENCODING=utf-8 && "%USERPROFILE%\.local\bin\specify.exe" init --here --force --script ps --ai claude
```

**Windows (PowerShell):**
```powershell
$env:PYTHONIOENCODING="utf-8"; & "$env:USERPROFILE\.local\bin\specify.exe" init --here --force --script ps --ai claude
```

**Git Bash:**
```bash
PYTHONIOENCODING=utf-8 ~/.local/bin/specify init --here --force --script ps --ai claude
```

**macOS/Linux:**
```bash
PYTHONIOENCODING=utf-8 ~/.local/bin/specify init --here --force --script sh --ai claude
```

**방법 2**: PATH 설정

```bash
uv tool update-shell
# 터미널 재시작 후 다시 시도
```

설치 확인:
```bash
uv tool list | grep specify
```

### 다른 AI 사용

Specify는 여러 AI를 지원합니다:
- `--ai claude`: Claude Code (기본 권장)
- `--ai cursor-agent`: Cursor
- `--ai windsurf`: Windsurf
- `--ai copilot`: GitHub Copilot
- `--ai gemini`: Google Gemini

예시:
```bash
PYTHONIOENCODING=utf-8 specify init my-project --ai cursor-agent
```
