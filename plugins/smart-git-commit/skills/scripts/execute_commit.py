#!/usr/bin/env python3
"""
커밋 실행 스크립트

승인된 커밋 메시지로 git commit 및 push를 수행합니다.
"""

import subprocess
import sys
import json
import os

def run_command(cmd, check=True):
    """명령 실행"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )

        if check and result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr or result.stdout,
                "returncode": result.returncode
            }

        return {
            "success": True,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.stderr else None,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def stage_files(files=None):
    """
    파일을 스테이징

    Args:
        files: 스테이징할 파일 목록 (None이면 모든 변경사항)
    """
    if files:
        # 특정 파일만 스테이징
        files_str = ' '.join(f'"{f}"' for f in files)
        cmd = f"git add {files_str}"
    else:
        # 모든 변경사항 스테이징
        cmd = "git add -A"

    return run_command(cmd)

def commit(message):
    """
    커밋 수행

    Args:
        message: 커밋 메시지
    """
    # 메시지를 heredoc으로 전달 (특수문자 처리)
    escaped_message = message.replace("'", "'\\''")
    cmd = f"git commit -m '{escaped_message}'"

    return run_command(cmd)

def push(remote='origin', branch=None):
    """
    푸시 수행

    Args:
        remote: 리모트 이름 (기본: origin)
        branch: 브랜치 이름 (None이면 현재 브랜치)
    """
    if branch:
        cmd = f"git push {remote} {branch}"
    else:
        cmd = f"git push {remote} HEAD"

    return run_command(cmd)

def get_current_branch():
    """현재 브랜치 이름 가져오기"""
    result = run_command("git rev-parse --abbrev-ref HEAD", check=False)
    if result['success']:
        return result['output']
    return None

def execute_commit(commit_message, do_push=False, files=None):
    """
    커밋 실행 메인 함수

    Args:
        commit_message: 커밋 메시지
        do_push: 푸시 여부
        files: 스테이징할 파일 목록 (None이면 모든 변경사항)

    Returns:
        dict: 실행 결과
    """
    results = {
        "success": True,
        "steps": []
    }

    # 1. 파일 스테이징
    stage_result = stage_files(files)
    results['steps'].append({
        "step": "stage",
        "success": stage_result['success'],
        "output": stage_result.get('output'),
        "error": stage_result.get('error')
    })

    if not stage_result['success']:
        results['success'] = False
        results['error'] = f"스테이징 실패: {stage_result.get('error')}"
        return results

    # 2. 커밋
    commit_result = commit(commit_message)
    results['steps'].append({
        "step": "commit",
        "success": commit_result['success'],
        "output": commit_result.get('output'),
        "error": commit_result.get('error')
    })

    if not commit_result['success']:
        results['success'] = False
        results['error'] = f"커밋 실패: {commit_result.get('error')}"
        return results

    # 3. 푸시 (선택적)
    if do_push:
        branch = get_current_branch()
        push_result = push(branch=branch)
        results['steps'].append({
            "step": "push",
            "success": push_result['success'],
            "output": push_result.get('output'),
            "error": push_result.get('error'),
            "branch": branch
        })

        if not push_result['success']:
            results['success'] = False
            results['error'] = f"푸시 실패: {push_result.get('error')}"
            # 푸시 실패는 warning으로 처리 (커밋은 성공)
            results['warning'] = "커밋은 완료되었으나 푸시에 실패했습니다."
            results['success'] = True  # 커밋은 성공했으므로

    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: execute_commit.py <message> [push:true|false]"
        }, ensure_ascii=False))
        sys.exit(1)

    commit_message = sys.argv[1]
    do_push = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else False

    result = execute_commit(commit_message, do_push)
    print(json.dumps(result, ensure_ascii=False, indent=2))
