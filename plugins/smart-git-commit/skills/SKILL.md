---
name: smart-git-commit
description: Execute smart Git operations when users request commit, push, repository initialization, or branch creation. Use semantic change analysis to generate Korean Gitmoji commit messages and conventional branch names such as feat/create-items, fix/resolve-login-error, or refactor/modify-member-business.
---

# Smart Git Commit

Generate high-quality Gitmoji-based Korean commit messages and safe Git workflow commands by analyzing the user's current repository state. This skill supports commit, push, repository initialization, and branch creation.

## When to Use This Skill

**Auto-activate when users request Git write actions:**

Korean triggers:
- Commit/push: "커밋해줘" / "커밋해" / "커밋" / "저장해줘" / "저장해" / "푸시해줘" / "푸시해" / "푸시"
- Init: "초기화해줘" / "깃 초기화" / "git init" / "저장소 초기화" / "초기 커밋"
- Branch: "브랜치 만들어줘" / "브랜치 생성" / "새 브랜치" / "작업 브랜치 만들어줘"

English triggers:
- Commit/push: "commit" / "commit this" / "create commit" / "push" / "push changes" / "commit and push" / "save"
- Init: "initialize git" / "git init" / "initial commit" / "initialize repository"
- Branch: "create branch" / "new branch" / "make a branch"

**Do NOT activate for:**
- General git questions or explanations
- Browsing commit history
- Code review without intent to write Git state
- Branch naming discussion without a request to create a branch

## Shared Semantic Analysis

Use this analysis for commit messages, initial commit messages, and branch names.

**Repository state commands:**

```bash
git rev-parse --is-inside-work-tree 2>/dev/null
git status --porcelain=v1
git diff --cached --stat
git diff --cached
git diff --stat
git diff
```

If the repository is not initialized yet, inspect files without staging ignored content:

```bash
git status --porcelain=v1 2>/dev/null || true
rg --files -g '!.git' -g '!node_modules' -g '!dist' -g '!build' -g '!coverage'
# If rg is unavailable before repository initialization:
find . -type f \
  -not -path './.git/*' \
  -not -path './node_modules/*' \
  -not -path './dist/*' \
  -not -path './build/*' \
  -not -path './coverage/*'
```

**Semantic classification:**

1. `feat` - new user-facing capability, new workflow, new integration, or meaningful new behavior
2. `fix` - bug correction, broken behavior recovery, validation correction, or error handling correction
3. `refactor` - structure improvement without behavior change
4. `perf` - measurable performance improvement
5. `test` - test-only change
6. `docs` - documentation-only change
7. `chore` - tooling, dependency, formatting, or maintenance change
8. `init` - first repository commit only

**Priority when multiple types apply:**

`feat` > `fix` > `refactor` > `perf` > `test` > `docs` > `chore`

Use `init` only for the first commit created by the initialization workflow.

**Naming language rules:**

- Commit titles and bodies remain Korean-first.
- Branch slugs use lowercase English words separated by hyphens.
- Branch slugs describe the domain or workflow, not file names, class names, method names, variables, issue IDs, or tracking numbers.
- Prefer verb-object branch slugs: `create-items`, `modify-member-business`, `resolve-login-error`.
- Keep branch names under 48 characters when possible.

## Force Operation Safety

Never run force-style Git operations unless the user explicitly requests the exact force action.

Forbidden unless explicitly requested:

- `git add -f`
- `git add --force`
- `git push --force`
- `git push --force-with-lease`
- `git commit --no-verify`
- Any command that bypasses ignore rules, hooks, branch protection, or normal Git safety checks

If a normal Git operation fails because a force action might be needed, stop and explain the cause. Ask the user for explicit approval before running any force command.

## Shell Portability

Command blocks are intended for Codex agents running a Bash-compatible shell.

On Windows, prefer Git Bash or WSL. PowerShell and CMD require adaptation for shell-specific syntax such as `2>/dev/null`, `|| true`, pipes, line continuations, and heredocs; the examples are not native PowerShell/CMD support promises.

For file listing, prefer `rg --files` when ripgrep is installed. If `rg` is unavailable, choose the fallback based on repository state.

Inside an initialized Git repository, use Git's ignore-aware listing:

```bash
git ls-files --cached --others --exclude-standard
```

Before repository initialization, use a Bash-compatible `find` fallback that excludes common generated or dependency directories:

```bash
find . -type f \
  -not -path './.git/*' \
  -not -path './node_modules/*' \
  -not -path './dist/*' \
  -not -path './build/*' \
  -not -path './coverage/*'
```

## Commit/Push Workflow

Follow these steps sequentially for every commit or push request. For repository initialization, use `Repository Initialization Workflow`. For branch creation, use `Branch Creation Workflow`.
- **Step 1**: Analyze changes (with optional grouping for large changesets)
- **Step 2**: Generate commit message (for each group if grouped)
- **Step 3**: User approval
- **Step 4**: Execute commit (single or multiple commits)

### Step 1: Analyze Changes

Use Bash tool to analyze git repository and detect violations.

**1.1 Check if git repository:**

```bash
git rev-parse --git-dir 2>/dev/null
```

If fails → "현재 디렉토리가 Git 저장소가 아닙니다."

**1.2 Check changes:**

```bash
git status --porcelain
```

If empty → "변경사항이 없습니다."

**1.3 Get detailed diff:**

```bash
# Staged changes
git diff --cached

# Unstaged changes (if needed)
git diff

# Statistics
git diff --cached --stat
```

**1.4 Check AI-related files:**

**Principle**: Respect user's .gitignore configuration. Files that passed .gitignore are trusted. Only verify AI-related files require user confirmation.

```bash
git diff --cached --name-only
```

**AI-related file patterns (⚠️ User confirmation required):**
- `claudedocs/` - Claude Code analysis/reports
- `.claude/` - Claude Code configuration
- `*.ai.md`, `*.claude.md` - AI-authored markdown
- `.cursor/` - Cursor IDE configuration
- `*.copilot.md` - GitHub Copilot files
- `.aider*`, `aider.*.md` - Aider AI files
- `*.gpt.md` - ChatGPT related files

**If AI files detected:** Present options and handle user choice.

**Options:**
1. ✅ Proceed with commit (include AI files)
2. 🚫 Exclude AI files from this commit
3. ❌ Cancel

**Handle user choice:**
- **Choice 1**: Continue with all files
- **Choice 2**: Remove AI files from staging (`git restore --staged <files>`)
- **Choice 3**: Stop workflow

**Important**: Do NOT block or warn about other file types (.env, node_modules, etc.). User manages these via .gitignore/.gitignore_global.

### Step 1.5: Logical Grouping (Optional)

**Activation trigger**: Large changeset (10+ files) OR user explicitly requests commit splitting.

**1.5.1 Analyze for grouping potential:**

```bash
# Count changed files
git diff --cached --name-only | wc -l
```

If ≥10 files, analyze for logical grouping.

**1.5.2 Grouping analysis criteria:**

Analyze file relationships using:

1. **Directory structure**: `src/user/`, `src/product/` → module-based groups
2. **File naming patterns**: `User*.kt`, `Product*.kt`, `*Test.kt` → domain-based groups
3. **Change types**:
   - Implementation files: `*.kt`, `*.py`, `*.ts`, `*.java`
   - Test files: `*Test.kt`, `*_test.py`, `*.test.ts`, `*.spec.js`
   - Documentation: `README.md`, `*.md` in `docs/`
   - Configuration: `package.json`, `build.gradle`, `*.toml`, `*.yml`
4. **Semantic relationships**: Analyze diff content to detect related changes

*Detailed grouping strategies: `references/grouping_strategies.md`*

**1.5.3 Present grouping to user:**

Present suggested grouping with file counts and domain names.

**Options:**
1. ✅ Create separate commits (recommended)
2. ⚠️ Create 1 combined commit
3. ✏️ Modify grouping
4. ❌ Cancel

**1.5.4 Handle user choice and execute grouped commits:**

For each group, execute Step 2 → Step 3 → Step 4 sequentially.

**Edge cases:**
- If grouping is unclear or ambiguous → fallback to single commit
- If user requests custom grouping → accept user's grouping logic
- Files <10 → skip grouping, proceed directly to Step 2

### Step 2: Generate Commit Message

Use Claude's natural language processing to generate message from diff analysis.

**2.1 Analyze diff semantically:**

Read the actual code changes from `git diff --cached` output:
- What functionality was added/changed?
- What bugs were fixed?
- What was refactored?

**2.2 Select Gitmoji:**

Based on change type, refer to `references/gitmoji_rules.md` for complete guidelines.

**Quick Reference:** ✨ feat | 🐛 fix | ♻️ refactor | ⚡ perf | ✅ test | 📝 docs | 🔧 chore

**Priority when multiple types:**
1. feat > fix > refactor > perf > others
2. Choose the most significant change

*Complete Gitmoji mapping: `references/gitmoji_rules.md`*

**2.3 Generate Korean summary:**

**Format:**
```
<gitmoji> <type>: 한글 핵심 요약 (max 50 chars)

- 핵심 변경사항 1 (1줄, 간결)
- 핵심 변경사항 2 (1줄, 간결)
- 핵심 변경사항 3 (1줄, 간결)
```

**2.4 Quality rules:**

✅ **MUST follow:**
- **Focus on WHAT, WHY, HOW - not tracking info**
  - WHAT: 무엇을 개발/개선/해결했는가 (필수)
  - WHY: 왜 필요했는가 (선택적)
  - HOW: 어떻게 구현했는가 (핵심만)
- **Domain-centric language** (not code-centric)
  - Use general terms: "사용자 인증", "검색 기능", "데이터 계층"
  - Avoid specific names: class/method/variable names, file names
- Korean-first (title and body)
- Imperative form ("추가" not "추가했습니다")
- Under 300 characters total
- 3-4 bullet points (each 1 line)
- Production code changes only

❌ **MUST NOT include:**
- **Code references**:
  - Class names: `UserService`, `VectorEntityType`
  - Method names: `extractVectorFields()`, `getUserById()`
  - Variable names: `userId`, `searchQuery`
  - File names: `UserService.kt`, `auth.controller.js`
- **AI signatures** (generator banners, automated co-author trailers)
- **Tracking codes** (`Phase 4`, `T032-1`, `SC-003`)
- **Task/Issue IDs** (`TASK-123`, `JIRA-456`, `#789`)
- **Scenario IDs** (`SC-003`, `SCENARIO-45`)
- **Test statistics** (`34개 통과`, `2개 실패`, `커버리지 85%`)
- **Work report info** (작업 리포트용 정보)
- Past tense (했습니다, 했음)
- File-by-file descriptions
- Configuration file details (`.gitignore`, `package.json`)
- Verbose explanations

*Complete examples with transformations: `references/commit_examples.md`*

### Step 3: Show Message and Get User Approval

⚠️ **CRITICAL RULE - NEVER SKIP THIS STEP**

This step is **mandatory** and must **never** be skipped under any circumstances. Always show the generated commit message to the user and wait for explicit approval before proceeding to commit execution.

**3.1 Display the generated message:**

**MUST use AskUserQuestion tool** to present the commit message to the user. Do not proceed to Step 4 without completing this interaction.

**Message format:**

```markdown
📋 Generated commit message:

<full message>

Choose an action:
```

**3.2 Provide exactly 4 options:**

1. **Commit only** - Execute local commit
2. **Commit + Push** - Commit and push to remote
3. **Modify message** - Let user edit message
4. **Cancel** - Abort commit

**3.3 Handle user choice:**

Wait for user selection. Do not assume or skip this step.

- **Choice 1**: User approved → Proceed to Step 4 with `do_push=false`
- **Choice 2**: User approved with push → Proceed to Step 4 with `do_push=true`
- **Choice 3**: User requests modification → Ask user for new message, then proceed to Step 4
- **Choice 4**: User cancelled → Stop workflow entirely

⚠️ **Enforcement**: If you proceed to Step 4 without completing Step 3, you are violating the core workflow. The user must see the message and make an explicit choice.

### Step 4: Execute Commit

Use Bash tool to execute git operations.

**4.1 Stage files:**

```bash
# Stage all changes
git add .

# Or stage specific files (if user specified)
git add "file1.kt" "file2.py"
```

**4.2 Commit with heredoc:**

Use heredoc to safely handle special characters:

```bash
git commit -m "$(cat <<'EOF'
✨ feat: 사용자 인증 API 구현

- JWT 토큰 기반 인증
- 리프레시 토큰 자동 갱신
- 로그인/로그아웃 엔드포인트
EOF
)"
```

**4.3 Push (optional):**

If user chose "Commit + Push":

```bash
git push origin HEAD
```

**4.4 Report results:**

Success:
```
✅ Commit completed: <commit hash>
🚀 Pushed to: origin/<branch>
```

Failure:
```
❌ Commit failed: <error message>

Possible causes:
- Pre-commit hooks blocked
- Merge conflict detected
- No changes staged
```

Push failure (after successful commit):
```
✅ Commit completed: <commit hash>
⚠️ Push failed: <error message>

Your changes are committed locally.
Try: git push origin HEAD
```

## Repository Initialization Workflow

Use this workflow when the user asks to initialize Git, create an initial commit, or prepare the current directory as a repository.

### Init Step 1: Inspect Current Directory

Check whether the current directory is already a Git repository:

```bash
git rev-parse --is-inside-work-tree 2>/dev/null
git rev-parse --verify HEAD 2>/dev/null
```

If `git rev-parse --is-inside-work-tree` succeeds, do not run `git init` again.

- If `git rev-parse --verify HEAD` succeeds, continue with the normal commit workflow and use the current diff to generate the message.
- If `git rev-parse --verify HEAD` fails, the repository is initialized but has no commits. Continue this initialization/initial-commit workflow without running `git init` again, and use the `🎉 init` message path.

If it fails, inspect candidate files:

```bash
pwd
rg --files -g '!.git' -g '!node_modules' -g '!dist' -g '!build' -g '!coverage'
# If rg is unavailable before repository initialization:
find . -type f \
  -not -path './.git/*' \
  -not -path './node_modules/*' \
  -not -path './dist/*' \
  -not -path './build/*' \
  -not -path './coverage/*'
```

If no files are found, ask the user whether to create an empty repository. Do not create an empty commit unless the user explicitly asks.

### Init Step 2: Initialize Repository

Run `git init` only when `git rev-parse --is-inside-work-tree` failed in Init Step 1:

```bash
git init
git status --porcelain=v1
```

If already inside a repository but `git rev-parse --verify HEAD` failed, skip `git init` and continue to staging and initial commit message generation.

### Init Step 3: Stage Initial Files

Stage files using the user's ignore rules:

```bash
git add .
git status --porcelain=v1
git diff --cached --stat
```

Never use `git add -f` or `git add --force` unless the user explicitly requested the exact `git add -f` or `git add --force` action.

### Init Step 4: Generate Initial Commit Message

Reuse the same semantic message-generation rules from `Step 2: Generate Commit Message`, with this required title format:

```markdown
🎉 init: 프로젝트 초기 설정

- 기본 작업 구조 구성
- 핵심 설정 파일 추가
- 초기 문서와 실행 기반 정리
```

Adjust the bullets to match the staged content. Keep the message Korean-first, imperative, under 300 characters, and free of AI signatures.

### Init Step 5: Ask for Approval

Show the generated initial commit message and provide exactly 3 options:

1. **Initialize + Commit** - Create the initial commit
2. **Modify message** - Let user edit message
3. **Cancel** - Abort after leaving repository initialized if `git init` already ran

Do not create the initial commit without explicit user approval.

If the user cancels after staging files, explain that the index may contain staged files. Offer to clean up the index with `git restore --staged .`, but run it only after explicit user approval.

### Init Step 6: Execute Initial Commit

After approval, run:

```bash
git commit -m "$(cat <<'EOF'
🎉 init: 프로젝트 초기 설정

- 기본 작업 구조 구성
- 핵심 설정 파일 추가
- 초기 문서와 실행 기반 정리
EOF
)"
git rev-parse --short HEAD
```

Report the commit hash and current branch:

```bash
git branch --show-current
```

## Branch Creation Workflow

Use this workflow when the user asks to create a new branch for the current work.

### Branch Step 1: Verify Repository State

Run:

```bash
git rev-parse --is-inside-work-tree 2>/dev/null
git status --porcelain=v1
git branch --show-current
```

If the directory is not a Git repository, offer to run `Repository Initialization Workflow` first.

If the worktree has uncommitted changes, do not block branch creation. Use those changes as the primary context for naming unless the user provided a clearer branch purpose.

### Branch Step 2: Analyze Work Intent

Use the shared semantic analysis. Prefer user-provided intent over diff inference.

If the user only says something like "브랜치 생성해줘" or "create a branch" without a branch name or topic:

1. Review the current conversation for the active work topic.
2. Review the current diff and status for implementation context.
3. Generate a branch name from the inferred topic if the intent is clear.
4. If the intent is still unclear, brainstorm with the user before creating anything:
   - Suggest 1-2 candidate branch names based on the best available context.
   - Let the user choose one candidate or provide a custom branch name.
   - Do not create a branch until the user confirms the name.

Examples:

- User says "아이템 생성 기능 작업 브랜치 만들어줘" → `feat/create-items`
- User says "멤버 비즈니스 로직 정리 브랜치" → `refactor/modify-member-business`
- User says "로그인 오류 수정 브랜치" → `fix/resolve-login-error`
- Diff only changes docs → `docs/update-guide`
- Diff only changes tests → `test/add-coverage`
- Diff only changes tooling → `chore/update-tooling`

### Branch Step 3: Generate Branch Name

Use this format:

```markdown
<type>/<slug>
```

Allowed prefixes:

- `feat/` for new behavior
- `fix/` for bug fixes
- `refactor/` for behavior-preserving structure changes
- `perf/` for performance work
- `test/` for test-only work
- `docs/` for documentation-only work
- `chore/` for tooling or maintenance

Slug rules:

- Use lowercase English.
- Replace spaces and underscores with hyphens.
- Remove characters outside `a-z`, `0-9`, and `-`.
- Collapse repeated hyphens.
- Trim leading and trailing hyphens.
- Prefer 2 to 5 words.
- Do not include issue IDs, dates, user names, file names, class names, method names, or variables.

### Branch Step 4: Check for Conflicts

Before creating the branch, run:

```bash
git show-ref --verify --quiet refs/heads/<candidate-branch>
git remote get-url origin
git ls-remote --heads origin <candidate-branch> 2>/dev/null
```

If `git remote get-url origin` fails, the repository has no `origin` remote. Do not offer or run upstream push. Explain that only local branch creation is available unless the user configures a remote.

If the local or remote branch already exists, append a short semantic suffix instead of a number when possible:

- `feat/create-items` → `feat/create-items-ui`
- `fix/resolve-login-error` → `fix/resolve-login-error-validation`
- If no meaningful suffix is available, append `-2`.

### Branch Step 5: Ask for Approval

Show the generated branch name. If `origin` exists, provide exactly 4 options:

1. **Create branch** - Run `git switch -c <branch>`
2. **Create + push upstream** - Run `git switch -c <branch>` and `git push -u origin <branch>`
3. **Modify branch name** - Let user provide a branch name, then validate the format and conflict checks again
4. **Cancel** - Abort branch creation

If `origin` does not exist, provide exactly 3 options:

1. **Create local branch** - Run `git switch -c <branch>`
2. **Modify branch name** - Let user provide a branch name, then validate the format and conflict checks again
3. **Cancel** - Abort branch creation

Do not create or push the branch without explicit user approval.

### Branch Step 6: Execute Branch Creation

For local branch creation:

```bash
git switch -c <branch>
git branch --show-current
```

For branch creation with upstream push:

```bash
git switch -c <branch>
git push -u origin <branch>
git branch --show-current
```

If `git switch -c` fails because the branch exists, do not overwrite it. Ask whether to switch to the existing branch or choose a new name.

## Edge Cases

Common edge cases and how to handle them. For complete details, see `references/edge_cases.md`.

**Quick Reference:**
- Empty commit → Suggest generic message
- Mixed types → Priority: feat > fix > refactor
- Large diff (>500 lines) → Warn and suggest split
- Unstaged changes → Offer options: staged only / stage all / cancel
- Pre-commit hook failure → Never bypass automatically; use `--no-verify` only after the user explicitly requests that exact bypass action
- No remote branch → Offer `git push -u origin <branch>`
- Merge conflict → Request resolution before commit
- Detached HEAD → Suggest creating branch

*Full edge case handling: `references/edge_cases.md`*

## Commit/Push Checklist

Before each commit or push workflow:

- [ ] User explicitly requested commit or push
- [ ] Git repository verified
- [ ] Changes detected (not empty)
- [ ] AI-related files confirmed by user (if any)
- [ ] Correct Gitmoji selected
- [ ] Korean message (imperative form)
- [ ] Domain-centric language (no class/method/variable names)
- [ ] Under 300 characters total
- [ ] No AI signature, tracking codes, or test statistics
- [ ] User approved message

Before repository initialization:

- [ ] User explicitly requested initialization or initial commit
- [ ] Existing Git repository check completed
- [ ] Candidate files inspected with ignore rules respected
- [ ] Force operations avoided unless explicitly requested
- [ ] Initial commit message generated with `🎉 init`
- [ ] User approved initial commit

Before branch creation:

- [ ] User explicitly requested branch creation
- [ ] Git repository verified
- [ ] Current work intent analyzed from user request, conversation context, and diff
- [ ] Ambiguous branch topic resolved with 1-2 suggestions or custom user input
- [ ] Branch prefix selected from allowed list
- [ ] Branch slug normalized to lowercase kebab-case
- [ ] Local and remote branch conflicts checked
- [ ] `origin` remote verified before offering upstream push
- [ ] Force push avoided unless explicitly requested
- [ ] User approved branch creation

## References

Detailed reference materials:

- **`references/gitmoji_rules.md`** - Complete Gitmoji mapping (20+ entries) and selection guidelines
- **`references/commit_examples.md`** - Extensive good/bad examples with code reference transformations
- **`references/edge_cases.md`** - Detailed edge case scenarios and solutions
- **`references/grouping_strategies.md`** - Advanced grouping algorithms and project-specific patterns

## Integration with MY_RULES.md

This skill implements MY_RULES.md Git workflow rules:

✅ **Enforced:**
- Git 커밋 시 smart-git-commit 스킬 사용
- Bash 직접 처리 금지
- 한글 커밋 메시지
- AI 서명 절대 금지
- 클래스/메서드/변수명 직접 언급 금지

✅ **Triggers:**
- Commit/push: "커밋", "커밋해줘", "commit", "push", "푸시"
- Init: "초기화", "깃 초기화", "initialize git", "initial commit"
- Branch: "브랜치", "브랜치 만들어줘", "create branch", "new branch"

✅ **Quality:**
- Gitmoji + 한글 메시지 자동 생성
- 도메인 중심 언어 사용
- 300자 제한 준수
- 사용자 승인 필수
