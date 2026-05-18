# Edge Cases 처리 가이드

Detailed guidance for handling edge cases in commit workflow.

## Case 1: Empty Commit Message Generated

### 상황
- diff 분석이 불명확한 경우
- 변경사항이 너무 다양하여 핵심을 파악하기 어려운 경우
- 설정 파일만 변경된 경우

### 처리 방법

**사용자에게 안내:**
```
⚠️ Unable to generate meaningful commit message.

Please review changes manually:
- file1.kt: [brief description based on diff]
- file2.py: [brief description based on diff]

Suggested message:
🔧 chore: 코드 업데이트

Would you like to proceed or provide custom message?
```

**옵션 제공:**
1. 제안된 메시지로 진행
2. 사용자가 직접 메시지 작성
3. 취소

### 예시

**변경사항:**
- `.gitignore` 업데이트
- `README.md` 오타 수정
- `package.json` 의존성 추가

**생성된 메시지:**
```
🔧 chore: 프로젝트 설정 업데이트

- .gitignore 패턴 추가
- README 오타 수정
- 의존성 업데이트
```

---

## Case 2: Mixed Change Types

### 상황
- 여러 종류의 변경사항이 함께 있는 경우
- 예: 새 기능 + 버그 수정 + 테스트 + 문서

### 처리 방법

**우선순위 적용:**
1. feat (new functionality) > fix (bug) > refactor > perf > others
2. 가장 중요한 변경사항을 Gitmoji로 선택
3. 나머지 변경사항은 bullet point에 언급

### 예시

**변경사항:**
- 사용자 인증 API 구현 (새 기능)
- 관련 테스트 추가
- API 문서 작성

**생성된 메시지:**
```
✨ feat: 사용자 인증 API 구현

- JWT 토큰 기반 인증
- 관련 테스트 추가
- API 문서 업데이트
```

**Gitmoji 선택 이유:**
- Primary: feat (가장 중요)
- Secondary: test + docs (부수적)

---

## Case 3: Large Diff

### 상황
- diff가 500줄 이상인 경우
- 너무 많은 파일이 변경된 경우

### 처리 방법

**경고 메시지 표시:**
```
⚠️ Large changeset detected (500+ lines)

Consider splitting into multiple commits:
1. <logical group 1>
2. <logical group 2>
3. <logical group 3>

Proceed with single commit? (yes/no)
```

**분리 제안 예시:**
```
변경사항 분석:
- 새로운 User 모듈 (300줄)
- Product 모듈 리팩토링 (150줄)
- 테스트 추가 (100줄)

제안:
Commit 1: ✨ feat: User 모듈 구현
Commit 2: ♻️ refactor: Product 모듈 정리
Commit 3: ✅ test: User/Product 테스트 추가
```

**사용자가 단일 커밋 선택 시:**
```
✨ feat: User 및 Product 모듈 구현

- User 모듈 전체 구현
- Product 모듈 리팩토링
- 통합 테스트 추가
```

---

## Case 4: Unstaged Changes

### 상황
- staged 변경사항과 unstaged 변경사항이 동시에 있는 경우

### 처리 방법

**사용자에게 알림:**
```
⚠️ You have unstaged changes:
- src/components/Header.tsx
- src/utils/helper.js

This commit will only include staged changes.

Options:
1. Commit staged only
2. Stage all and commit
3. Cancel
```

**옵션별 처리:**

**Option 1: Commit staged only**
```bash
# staged 파일만 커밋
git commit -m "message"
```

**Option 2: Stage all and commit**
```bash
# 모든 변경사항 stage
git add .
git commit -m "message"
```

**Option 3: Cancel**
- 작업 중단
- 사용자가 수동으로 정리

### 예시

**Staged:**
- `src/api/auth.ts` (인증 API 구현)
- `tests/auth.test.ts` (테스트 추가)

**Unstaged:**
- `src/components/LoginForm.tsx` (진행 중)

**생성된 메시지 (Option 1 선택 시):**
```
✨ feat: 인증 API 구현

- JWT 토큰 기반 인증
- 로그인/로그아웃 엔드포인트
- 관련 테스트 추가
```

---

## Case 5: No Remote Branch

### 상황
- `git push` 실행 시 upstream 브랜치가 설정되지 않음
- 새로운 `feat/` 브랜치인 경우

### 처리 방법

**에러 감지:**
```bash
git push origin HEAD
# fatal: The current branch feat/auth has no upstream branch.
```

**사용자에게 안내:**
```
⚠️ No upstream branch configured.

Run this to push and set upstream:
git push -u origin feat/auth

Would you like me to execute this? (yes/no)
```

**사용자 승인 시 실행:**
```bash
git push -u origin feat/auth
```

**결과 보고:**
```
✅ Commit completed: abc123
🚀 Pushed to: origin/feat/auth (upstream set)
```

---

## Case 6: Pre-commit Hook Failure

### 상황
- pre-commit hook이 실패하여 커밋이 차단됨
- 예: linter 오류, 테스트 실패

### 처리 방법

**에러 감지:**
```bash
git commit -m "message"
# husky - pre-commit hook failed
```

**사용자에게 알림:**
```
❌ Commit failed: Pre-commit hooks blocked

Hook output:
[hook error messages]

Possible causes:
- Linter errors detected
- Tests failed
- Code formatting issues

Please fix the issues and try again.
```

**권장 조치:**
1. Hook 에러 메시지 확인
2. 문제 수정
3. 재시도

**절대 하지 말 것:**
- ❌ `git commit --no-verify` (hook 우회)
- Hook은 코드 품질을 위한 것이므로 우회하지 말 것

---

## Case 7: Merge Conflict

### 상황
- 커밋 시도 중 merge conflict 감지

### 처리 방법

**에러 감지:**
```
❌ Commit failed: Merge conflict detected

Conflicted files:
- src/api/user.ts
- src/components/UserList.tsx

Please resolve conflicts first:
1. Open conflicted files
2. Resolve <<<<< ===== >>>>> markers
3. Stage resolved files
4. Try commit again
```

**사용자 조치 필요:**
1. Conflict 해결
2. `git add <resolved files>`
3. 다시 커밋 시도

---

## Case 8: Empty Changes After Stage

### 상황
- git add 실행 후 실제 변경사항이 없는 경우
- 예: 공백만 변경, 자동 포맷팅으로 원상복구

### 처리 방법

**감지:**
```bash
git diff --cached --stat
# (empty output)
```

**사용자에게 알림:**
```
⚠️ No changes to commit after staging.

Possible causes:
- Only whitespace changes (ignored by git)
- Changes were auto-reverted by formatter
- All changes were already committed

Status: Working tree clean
```

**추천 조치:**
- 커밋 중단
- 사용자가 변경사항 재확인

---

## Case 9: Detached HEAD State

### 상황
- HEAD가 특정 커밋을 가리키고 있음 (브랜치 아님)

### 처리 방법

**감지:**
```bash
git branch --show-current
# (empty output = detached HEAD)
```

**사용자에게 경고:**
```
⚠️ You are in 'detached HEAD' state.

Current: HEAD -> abc123

Committing in this state is not recommended.

Options:
1. Create new branch with Branch Creation Workflow
2. Return to branch: git checkout main
3. Cancel commit

Would you like me to generate a branch name and create it? (yes/no)
```

**사용자 승인 시:**
- `Branch Creation Workflow`를 사용해 현재 작업 의도에 맞는 브랜치 이름을 생성한다.
- 예: `feat/create-items`, `fix/resolve-login-error`, `refactor/modify-member-business`
- 사용자 승인 후 생성한다.

```bash
git switch -c feat/create-items
# 이후 정상 커밋 진행
```

---

## Case 10: Binary Files Detected

### 상황
- Binary 파일 (이미지, 실행 파일 등) 커밋 시도

### 처리 방법

**감지:**
```bash
git diff --cached --numstat | grep '-\t-'
# Binary files will show as '-  -  filename'
```

**사용자에게 확인:**
```
⚠️ Binary files detected:
- assets/logo.png (120 KB)
- dist/app.min.js (500 KB)

Binary files increase repository size.

Are you sure you want to commit these? (yes/no)
```

**권장 사항:**
- 이미지는 필요 시 커밋
- 빌드 파일은 .gitignore 추가 권장
- 대용량 파일은 Git LFS 사용 고려

## Case 11: Repository Initialization Requested Inside Existing Repository

### 상황
- 사용자가 `git init` 또는 저장소 초기화를 요청했지만 현재 디렉토리가 이미 Git 저장소인 경우

### 처리 방법

```bash
git rev-parse --is-inside-work-tree 2>/dev/null
git rev-parse --verify HEAD 2>/dev/null
```

`git rev-parse --is-inside-work-tree`가 성공하면 `git init`을 다시 실행하지 않는다.

- `git rev-parse --verify HEAD`가 성공하면 기존 커밋이 있는 저장소이므로 일반 커밋 워크플로우로 전환하고 현재 diff로 메시지를 생성한다.
- `git rev-parse --verify HEAD`가 실패하면 초기화는 되었지만 아직 커밋이 없는 저장소이므로 `git init` 없이 초기화/초기 커밋 워크플로우를 계속 진행하고 `🎉 init` 메시지 경로를 사용한다.

안내 문구:

```markdown
현재 디렉토리는 이미 Git 저장소입니다. 초기화 대신 현재 변경사항 기준으로 커밋을 진행할 수 있습니다.
```

---

## Case 12: Branch Name Already Exists

### 상황
- 생성하려는 브랜치가 로컬 또는 원격에 이미 존재하는 경우

### 처리 방법

```bash
git show-ref --verify --quiet refs/heads/<candidate-branch>
git ls-remote --heads origin <candidate-branch> 2>/dev/null
```

이미 존재하면 의미 있는 suffix를 먼저 제안한다.

예시:
- `feat/create-items` → `feat/create-items-ui`
- `fix/resolve-login-error` → `fix/resolve-login-error-validation`
- 의미 있는 suffix가 없으면 `-2`를 붙인다.

---

## Case 13: Branch Creation With Dirty Worktree

### 상황
- 커밋되지 않은 변경사항이 있는 상태에서 브랜치 생성을 요청한 경우

### 처리 방법
- 브랜치 생성을 막지 않는다.
- 변경사항을 브랜치 이름 추론의 주요 근거로 사용한다.
- `git switch -c <branch>`는 변경사항을 유지하므로 stash를 요구하지 않는다.
- 단, 충돌이나 checkout 실패가 발생하면 Git 오류를 그대로 설명하고 사용자의 정리를 요청한다.

---

## Case 14: Invalid Branch Name Generated

### 상황
- 사용자 의도 또는 diff 분석에서 공백, 한글, 특수문자, 연속 슬래시가 포함된 이름이 나온 경우

### 처리 방법
- prefix는 허용 목록 중 하나로 제한한다.
- slug는 lowercase kebab-case 영어로 변환한다.
- `a-z`, `0-9`, `-` 외 문자를 제거한다.
- 연속된 hyphen(반복된 하이픈)은 하나로 축약한다.
- 앞뒤 hyphen(앞뒤 하이픈)은 제거한다.
- 빈 slug가 되면 `update-work`를 사용한다.

---

## Case 15: Force Git Operation Seems Necessary

### 상황
- ignored 파일을 추가해야 하거나, hook이 실패하거나, push가 rejected 되어 force 계열 명령이 필요해 보이는 경우

### 처리 방법
- 사용자가 명시적으로 요청하지 않았으면 force 명령을 실행하지 않는다.
- `git add -f`, `git add --force`, `git push --force`, `git push --force-with-lease`, `git commit --no-verify`를 자동으로 사용하지 않는다.
- 실패 원인과 일반적인 해결 방법을 먼저 설명한다.
- 사용자가 정확한 force 동작을 명시적으로 승인한 뒤에만 해당 명령을 실행한다.

---

## 일반 원칙

### 모든 Edge Case 공통
1. **사용자에게 명확히 알림**
2. **옵션 제공** (진행/수정/취소)
3. **절대 자동 우회 금지** (--no-verify, --force 등)
4. **근본 원인 설명**
5. **추천 조치 안내**

### 에러 처리 우선순위
1. 안전 (데이터 손실 방지)
2. 사용자 의사 존중
3. 명확한 안내
4. 복구 가능성 유지
