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
- 새로운 feature 브랜치인 경우

### 처리 방법

**에러 감지:**
```bash
git push origin HEAD
# fatal: The current branch feature/auth has no upstream branch.
```

**사용자에게 안내:**
```
⚠️ No upstream branch configured.

Run this to push and set upstream:
git push -u origin feature/auth

Would you like me to execute this? (yes/no)
```

**사용자 승인 시 실행:**
```bash
git push -u origin feature/auth
```

**결과 보고:**
```
✅ Commit completed: abc123
🚀 Pushed to: origin/feature/auth (upstream set)
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
1. Create new branch: git checkout -b <branch-name>
2. Return to branch: git checkout main
3. Cancel commit

Would you like me to create a branch? (yes/no)
```

**사용자 승인 시:**
```bash
git checkout -b feature/temp-branch
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
