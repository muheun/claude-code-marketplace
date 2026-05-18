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
- Branch: "create branch" / "new branch" / "checkout branch" / "make a branch"

**Do NOT activate for:**
- General git questions or explanations
- Browsing commit history
- Code review without intent to write Git state
- Branch naming discussion without a request to create or switch branches

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
- `*.ai.md`, `*.claude.md` - AI-generated markdown
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
- **AI signatures** (`🤖 Generated with...`, `Co-Authored-By: Claude`)
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

## Edge Cases

Common edge cases and how to handle them. For complete details, see `references/edge_cases.md`.

**Quick Reference:**
- Empty commit → Suggest generic message
- Mixed types → Priority: feat > fix > refactor
- Large diff (>500 lines) → Warn and suggest split
- Unstaged changes → Offer options: staged only / stage all / cancel
- Pre-commit hook failure → Never bypass with --no-verify
- No remote branch → Offer `git push -u origin <branch>`
- Merge conflict → Request resolution before commit
- Detached HEAD → Suggest creating branch

*Full edge case handling: `references/edge_cases.md`*

## Commit/Push Checklist

Before each commit or push workflow:

- [ ] User explicitly requested commit
- [ ] Git repository verified
- [ ] Changes detected (not empty)
- [ ] AI-related files confirmed by user (if any)
- [ ] Correct Gitmoji selected
- [ ] Korean message (imperative form)
- [ ] Domain-centric language (no class/method/variable names)
- [ ] Under 300 characters total
- [ ] No AI signature, tracking codes, or test statistics
- [ ] User approved message

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
