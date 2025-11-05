---
name: smart-git-commit
description: Execute git commit operations when user requests to commit or push code changes. Use this skill to generate recommended commit messages, perform local commits, or push to remote repositories. If the request type is ambiguous (message generation vs. local commit vs. remote push), confirm with the user before proceeding.
---

# Smart Git Commit

## Overview

Automatically generate Gitmoji-based Korean commit messages by analyzing project changes, then execute commits and pushes after user approval.

**Core capabilities**:
- 📊 Analyze git changes and check .gitignore violations
- 🎨 Generate Gitmoji + Korean commit messages
- ✅ Require user approval before committing
- 🚀 Execute commits and pushes with one click

## When to Use This Skill

Use this skill when users request commit actions:
- "커밋해줘" / "커밋해" / "commit"
- "저장해줘" / "git commit"
- "푸시해줘" (commit + push)

## Workflow

### Step 1: Analyze Changes

Execute `scripts/analyze_changes.py`:

```bash
python3 scripts/analyze_changes.py
```

Checks:
- Modified/added/deleted files
- .gitignore violations
- Sensitive information (API keys, .env, credentials)
- Temporary/build files (node_modules, dist, *.log)

**If violations detected**: Warn user and stop.

### Step 2: Generate Commit Message

Generate message using analysis result:

```bash
python3 scripts/analyze_changes.py | python3 scripts/generate_message.py
```

**Message rules**:
- Gitmoji selection based on file types
- Korean-first (title and body)
- Under 300 characters
- No AI signatures
- **No tracking codes** (Phase 4, T032-1, SC-003 등 절대 금지)
- **Maximum conciseness** (각 bullet point 1줄, 핵심만 전달)

**Format**:
```
<gitmoji> <type>: Korean summary (max 50 chars)

- Key change 1
- Key change 2
- Key change 3
```

**Improve generic messages** by:
- Reading actual diffs with `git diff`
- Identifying key functionality changes
- Using domain-specific terms
- Referencing `references/commit_examples.md`

### Step 3: User Approval

Show message and ask:

```
📋 Generated commit message:

<message>

✅ Commit with this message?
🚀 Push as well?

(1) Commit only
(2) Commit + Push
(3) Modify message
(4) Cancel
```

**Never commit without explicit approval.**

### Step 4: Execute

Based on user choice:

```bash
# Commit only
python3 scripts/execute_commit.py "message" false

# Commit + Push
python3 scripts/execute_commit.py "message" true
```

Report results:
- ✅ "Commit completed: <hash>"
- 🚀 "Pushed to: <branch>"
- ❌ "Failed: <error>"

## Gitmoji Selection

Refer to `references/gitmoji_rules.md` for detailed rules.

**Quick reference**:

| Situation | Gitmoji | Type |
|-----------|---------|------|
| Test files | ✅ | test |
| Bug fix | 🐛 | fix |
| New feature | ✨ | feat |
| Refactoring | ♻️ | refactor |
| Performance | ⚡ | perf |
| Documentation | 📝 | docs |
| Configuration | 🔧 | chore |

## Message Quality Standards

Refer to `references/commit_examples.md` for examples.

**Good**:
- ✅ Imperative form ("add" not "added")
- ✅ **Extremely concise** (1줄 = 1 bullet point, 핵심만)
- ✅ Under 300 characters
- ✅ Production files only
- ✅ No AI signatures
- ✅ **No tracking codes** (외부 문서 참조 금지)

**Bad**:
- ❌ AI signatures (🤖 Generated with...)
- ❌ **Tracking codes** (Phase 4, T032-1, SC-003 등)
- ❌ Over 300 characters
- ❌ File-by-file details
- ❌ Configuration file changes
- ❌ Past tense
- ❌ Verbose explanations (기술 용어 과다, 장황한 설명)

## Prohibitions

### Absolutely Forbidden

1. **Tracking codes**:
   - `Phase 4`, `T032-1`, `SC-003` 등 문서 참조 코드
   - 외부 이슈 트래커나 문서 시스템 참조
   - 커밋 메시지는 독립적이고 자체 완결적이어야 함

2. **AI signatures**:
   - `🤖 Generated with Claude Code`
   - `Co-Authored-By: Claude`
   - Any AI attribution

3. **Force commits**:
   - No `git add --force`
   - No ignoring .gitignore rules

4. **Sensitive information**:
   - `.env`, credentials, API keys
   - `*.pem`, `*.key`, `*.cert`

5. **Temporary/build files**:
   - `node_modules/`, `dist/`, `build/`
   - `*.log`, `*.tmp`, `__pycache__/`
   - `.DS_Store`, `Thumbs.db`

### User Approval Required

- Never commit without approval
- Always show message before committing
- Respect user choice

## Scripts

### analyze_changes.py

Analyzes git status and checks violations.

**Output**:
```json
{
  "success": true,
  "modified": ["file1.kt"],
  "added": ["file2.py"],
  "gitignore_violations": [],
  "diff_summary": "2 files changed, 10 insertions(+)"
}
```

### generate_message.py

Generates commit message from analysis.

**Output**:
```json
{
  "success": true,
  "message": "✨ feat: User auth API\n\n- JWT authentication\n- Token refresh\n- Login/logout",
  "emoji": "✨",
  "type": "feat"
}
```

### execute_commit.py

Executes git commit and optional push.

**Usage**:
```bash
python3 scripts/execute_commit.py "message" false  # commit only
python3 scripts/execute_commit.py "message" true   # commit + push
```

## Example Scenarios

### Scenario 1: Test File Modified

**User**: "커밋해줘"

**Workflow**:
1. Detect `PostEmbeddingRepositoryTest.kt` modified
2. Generate ✅ test message
3. Show message, ask approval
4. Execute commit

### Scenario 2: New Feature

**User**: "푸시해줘"

**Workflow**:
1. Analyze new API files
2. Generate ✨ feat message
3. Ask for commit + push approval
4. Execute and report

### Scenario 3: .gitignore Violation

**User**: "커밋해줘"

**Result**:
```
⚠️ .gitignore violation detected:
- .env (sensitive info)

Cannot commit these files.
Add to .gitignore or use git restore.
```

## Checklist

Before each commit:
- [ ] User requested commit
- [ ] Analysis completed
- [ ] No violations
- [ ] No sensitive info
- [ ] Correct Gitmoji
- [ ] Korean message
- [ ] Under 300 chars
- [ ] No AI signature
- [ ] User approved
