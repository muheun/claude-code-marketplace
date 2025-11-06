---
name: smart-git-commit
description: Execute git commit operations when user requests to commit or push code changes. Use this skill to generate recommended commit messages, perform local commits, or push to remote repositories. Auto-activates for Korean keywords ("커밋", "푸시") and English keywords ("commit", "push"). Always uses Bash tool for git operations and Claude's natural language processing for message generation.
---

# Smart Git Commit

Automatically generate high-quality Gitmoji-based Korean commit messages by analyzing code changes, then execute commits and pushes after user approval.

## When to Use This Skill

**Auto-activate when users request commit actions:**

Korean triggers:
- "커밋해줘" / "커밋해" / "커밋"
- "저장해줘" / "저장해"
- "푸시해줘" / "푸시해" / "푸시"

English triggers:
- "commit" / "commit this" / "create commit"
- "push" / "push changes" / "commit and push"
- "save" / "save changes"

**Do NOT activate for:**
- General git questions or explanations
- Browsing commit history
- Code review without commit intent

## Workflow

Follow these steps sequentially for every commit request:
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

**If AI files detected:**
```
⚠️ AI-related files are staged:
- claudedocs/analysis.md
- src/component.ai.md

These are typically not committed to version control.

Options:
1. ✅ Proceed with commit (include AI files)
2. 🚫 Exclude AI files from this commit
3. ❌ Cancel

Choose an option:
```

**Handle user choice:**
- **Choice 1**: Continue with all files (user intentionally wants to commit AI files)
- **Choice 2**: Remove AI files from staging, continue with remaining files
  ```bash
  git restore --staged claudedocs/ src/component.ai.md
  ```
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
4. **Semantic relationships**: Analyze diff content to detect related changes (e.g., Service imports Repository)

**1.5.3 Present grouping to user:**

```
🔍 Large changeset detected (15 files)

Suggested grouping:
📦 Group 1: User 모듈 구현 (5 files)
   - src/user/User.kt
   - src/user/UserService.kt
   - src/user/UserRepository.kt
   - src/user/UserDto.kt
   - src/user/UserMapper.kt

📦 Group 2: Product 모듈 구현 (4 files)
   - src/product/Product.kt
   - src/product/ProductService.kt
   - src/product/ProductRepository.kt
   - src/product/ProductDto.kt

📦 Group 3: 테스트 추가 (3 files)
   - tests/UserTest.kt
   - tests/ProductTest.kt
   - tests/IntegrationTest.kt

📦 Group 4: 문서 업데이트 (3 files)
   - README.md
   - docs/api.md
   - docs/setup.md

Options:
1. ✅ Create 4 separate commits (recommended)
2. ⚠️ Create 1 combined commit
3. ✏️ Modify grouping
4. ❌ Cancel

Choose an option:
```

**1.5.4 Handle user choice:**

- **Choice 1**: Generate separate commit message for each group (proceed to Step 2 for each group)
- **Choice 2**: Combine all files into single commit (skip grouping, proceed to Step 2)
- **Choice 3**: Ask user to specify custom grouping, then proceed
- **Choice 4**: Stop workflow

**1.5.5 Execute grouped commits:**

For each group, execute Step 2 → Step 3 → Step 4 sequentially:

```bash
# Group 1
git add src/user/*.kt
git commit -m "$(cat <<'EOF'
✨ feat: User 모듈 구현

- User 엔티티 및 DTO 정의
- UserService 비즈니스 로직
- UserRepository 데이터 접근
EOF
)"

# Group 2
git add src/product/*.kt
git commit -m "$(cat <<'EOF'
✨ feat: Product 모듈 구현

- Product 엔티티 및 DTO 정의
- ProductService 비즈니스 로직
- ProductRepository 데이터 접근
EOF
)"

# Continue for remaining groups...
```

**Edge cases:**
- If grouping is unclear or ambiguous → fallback to single commit (Choice 2)
- If user requests custom grouping → accept user's grouping logic
- Files <10 → skip grouping, proceed directly to Step 2

*Detailed grouping strategies: `references/grouping_strategies.md`*

### Step 2: Generate Commit Message

Use Claude's natural language processing to generate message from diff analysis.

**2.1 Analyze diff semantically:**

Read the actual code changes from `git diff --cached` output:
- What functionality was added/changed?
- What bugs were fixed?
- What was refactored?

**2.2 Select Gitmoji:**

Based on change type, refer to `references/gitmoji_rules.md` for complete guidelines.

**Quick reference (most common):**

| Gitmoji | Type | When to Use |
|---------|------|-------------|
| ✨ | feat | New feature, API, component |
| 🐛 | fix | Bug fix, error handling |
| ♻️ | refactor | Code restructure, no feature change |
| ⚡ | perf | Performance optimization |
| ✅ | test | Unit/integration tests |
| 📝 | docs | Documentation, README |
| 🔧 | chore | Build, config, dependencies |

*Full list with 20+ Gitmoji: `references/gitmoji_rules.md`*

**Priority when multiple types:**
1. feat > fix > refactor > perf > others
2. Choose the most significant change

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
- Korean-first (title and body)
- Imperative form ("추가" not "추가했습니다")
- Under 300 characters total
- 3-4 bullet points (each 1 line)
- Production code changes only

❌ **MUST NOT include:**
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

**2.5 Example:**

**✅ GOOD:**
```
✨ feat: JWT 토큰 기반 인증 API 구현

- 토큰 생성 및 검증 로직
- 자동 갱신 기능 (만료 30분 전)
- 로그인/로그아웃 엔드포인트
```

**❌ BAD:**
```
✨ feat: TASK-1234 사용자 인증 구현

- JIRA-456: JWT 토큰 생성
- SC-003: 로그인 시나리오 검증 완료
- 34개 테스트 통과, 2개 실패
```

**Problems:** Task IDs, Scenario IDs, Test statistics

*More examples: `references/commit_examples.md`*

### Step 3: User Approval

Use AskUserQuestion tool to show message and get approval.

**Present message:**

```markdown
📋 Generated commit message:

<full message>

Choose an action:
```

**Options:**

1. **Commit only** - Execute local commit
2. **Commit + Push** - Commit and push to remote
3. **Modify message** - Let user edit message
4. **Cancel** - Abort commit

**Handle user choice:**

- **Choice 1**: Proceed to Step 4 with `do_push=false`
- **Choice 2**: Proceed to Step 4 with `do_push=true`
- **Choice 3**: Ask user for new message, then go to Step 4
- **Choice 4**: Stop workflow

**Never commit without explicit approval.**

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

**Large diff (>500 lines):**
- Warn user to consider splitting commits
- Ask for confirmation before proceeding

**Unstaged changes:**
- Inform user about unstaged files
- Offer options: commit staged only, stage all, or cancel

**No remote branch:**
- Detect push failure due to no upstream
- Offer to run `git push -u origin <branch>`

*Full edge case handling: `references/edge_cases.md`*

## Checklist

Before each commit:

- [ ] User explicitly requested commit
- [ ] Git repository verified
- [ ] Changes detected (not empty)
- [ ] AI-related files confirmed by user (if any)
- [ ] Correct Gitmoji selected
- [ ] Korean message (imperative form)
- [ ] Under 300 characters total
- [ ] No AI signature, tracking codes, or test statistics
- [ ] User approved message

## References

Detailed reference materials:

- **`references/gitmoji_rules.md`** - Complete Gitmoji mapping (20+ entries) and selection guidelines
- **`references/commit_examples.md`** - Extensive good/bad examples with explanations
- **`references/edge_cases.md`** - Detailed edge case scenarios and solutions
- **`references/grouping_strategies.md`** - Advanced grouping algorithms and project-specific patterns

## Integration with MY_RULES.md

This skill implements MY_RULES.md Git workflow rules:

✅ **Enforced:**
- Git 커밋 시 smart-git-commit 스킬 사용
- Bash 직접 처리 금지
- 한글 커밋 메시지
- AI 서명 절대 금지

✅ **Triggers:**
- "커밋", "커밋해줘", "commit", "push", "푸시"

✅ **Quality:**
- Gitmoji + 한글 메시지 자동 생성
- 300자 제한 준수
- 사용자 승인 필수
