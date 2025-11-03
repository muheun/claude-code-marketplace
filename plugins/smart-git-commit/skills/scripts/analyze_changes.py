#!/usr/bin/env python3
"""
Git 변경사항 분석 스크립트

현재 저장소의 변경사항을 분석하여 JSON 형식으로 반환합니다.
- git status 확인
- 변경된 파일 목록
- .gitignore 위반 여부
- 민감 정보 포함 여부
"""

import subprocess
import json
import sys
import os
from pathlib import Path

def run_command(cmd):
    """Git 명령 실행"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_git_repo():
    """Git 저장소인지 확인"""
    stdout, stderr, returncode = run_command("git rev-parse --git-dir 2>/dev/null")
    return returncode == 0

def get_git_status():
    """Git status 확인"""
    stdout, stderr, returncode = run_command("git status --porcelain")
    if returncode != 0:
        return None, stderr
    return stdout, None

def parse_status(status_output):
    """Git status 출력 파싱"""
    modified = []
    added = []
    deleted = []

    for line in status_output.split('\n'):
        if not line.strip():
            continue

        status = line[:2]
        filepath = line[3:].strip()

        # 상태 코드 분석 (https://git-scm.com/docs/git-status)
        if 'M' in status:  # Modified
            modified.append(filepath)
        elif 'A' in status:  # Added
            added.append(filepath)
        elif 'D' in status:  # Deleted
            deleted.append(filepath)
        elif '?' in status:  # Untracked
            added.append(filepath)

    return modified, added, deleted

def check_gitignore_violations(files):
    """
    .gitignore 위반 파일 확인

    주의: git check-ignore는 이미 추적 중인 파일에 대해서는
    .gitignore를 무시하므로, 패턴 기반 휴리스틱도 사용합니다.
    """
    violations = []

    # 민감 정보 패턴
    sensitive_patterns = [
        '.env', '.env.local', '.env.production',
        'credentials', 'secrets', 'api_key',
        '*.pem', '*.key', '*.cert',
        'id_rsa', 'id_dsa'
    ]

    # 임시/빌드 파일 패턴
    temp_patterns = [
        '__pycache__', '*.pyc', '.pytest_cache',
        'node_modules', 'dist', 'build', 'target',
        '*.log', '*.tmp',
        '.DS_Store', 'Thumbs.db'
    ]

    for file in files:
        file_lower = file.lower()

        # 민감 정보 체크
        if any(pattern in file_lower for pattern in sensitive_patterns):
            violations.append(file)
            continue

        # 임시/빌드 파일 체크
        if any(pattern in file_lower for pattern in temp_patterns):
            violations.append(file)

    return violations

def get_diff_summary():
    """변경사항 요약 (git diff --stat)"""
    stdout, stderr, returncode = run_command("git diff --cached --stat")
    if returncode != 0:
        return ""
    return stdout

def analyze_changes():
    """변경사항 종합 분석"""
    # Git 저장소 확인
    if not check_git_repo():
        return {
            "success": False,
            "error": "현재 디렉토리가 Git 저장소가 아닙니다."
        }

    # Git status 확인
    status_output, error = get_git_status()
    if error:
        return {
            "success": False,
            "error": f"git status 실패: {error}"
        }

    if not status_output:
        return {
            "success": True,
            "status": "clean",
            "message": "변경사항이 없습니다.",
            "modified": [],
            "added": [],
            "deleted": []
        }

    # 파일 목록 파싱
    modified, added, deleted = parse_status(status_output)
    all_files = modified + added

    # .gitignore 위반 확인
    violations = check_gitignore_violations(all_files)

    # diff 요약
    diff_summary = get_diff_summary()

    return {
        "success": True,
        "status": status_output,
        "modified": modified,
        "added": added,
        "deleted": deleted,
        "diff_summary": diff_summary,
        "gitignore_violations": violations
    }

if __name__ == "__main__":
    result = analyze_changes()
    print(json.dumps(result, ensure_ascii=False, indent=2))
