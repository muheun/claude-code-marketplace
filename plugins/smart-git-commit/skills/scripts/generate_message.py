#!/usr/bin/env python3
"""
커밋 메시지 생성 스크립트

분석된 변경사항을 기반으로 Gitmoji + 한글 커밋 메시지를 생성합니다.
"""

import json
import sys
import subprocess

# Gitmoji 매핑 (파일 확장자/패턴 기반)
GITMOJI_MAP = {
    # 테스트 파일
    'test': {'emoji': '✅', 'type': 'test'},
    'spec': {'emoji': '✅', 'type': 'test'},

    # 문서
    'md': {'emoji': '📝', 'type': 'docs'},
    'txt': {'emoji': '📝', 'type': 'docs'},

    # 설정 파일
    'yml': {'emoji': '🔧', 'type': 'chore'},
    'yaml': {'emoji': '🔧', 'type': 'chore'},
    'json': {'emoji': '🔧', 'type': 'chore'},
    'toml': {'emoji': '🔧', 'type': 'chore'},
    'gradle': {'emoji': '🔧', 'type': 'chore'},

    # CI/CD
    'github': {'emoji': '👷', 'type': 'ci'},
    '.gitlab-ci': {'emoji': '👷', 'type': 'ci'},

    # 코드 (기본)
    'default': {'emoji': '✨', 'type': 'feat'}
}

def infer_gitmoji(files):
    """
    파일 목록으로부터 Gitmoji 추론

    우선순위:
    1. 테스트 파일 → ✅ test
    2. 문서 파일 → 📝 docs
    3. 설정 파일 → 🔧 chore
    4. 기타 코드 → ✨ feat (기본)
    """
    has_test = any('test' in f.lower() or 'spec' in f.lower() for f in files)
    if has_test:
        return '✅', 'test'

    has_docs = any(f.endswith('.md') or f.endswith('.txt') for f in files)
    if has_docs:
        return '📝', 'docs'

    has_config = any(
        f.endswith(('.yml', '.yaml', '.json', '.toml', '.gradle'))
        for f in files
    )
    if has_config:
        return '🔧', 'chore'

    # 기본: 기능 추가로 가정
    return '✨', 'feat'

def generate_summary(files, diff_summary):
    """
    변경사항으로부터 요약 생성

    간단한 휴리스틱:
    - 파일명에서 주요 키워드 추출
    - 변경 라인 수 기반 중요도 판단
    """
    # 파일 확장자별 그룹핑
    by_ext = {}
    for f in files:
        ext = f.split('.')[-1] if '.' in f else 'other'
        by_ext.setdefault(ext, []).append(f)

    # 주요 변경 사항 추출 (최대 3개)
    changes = []

    for ext, file_list in sorted(by_ext.items(), key=lambda x: len(x[1]), reverse=True):
        if ext in ['kt', 'java', 'py', 'js', 'ts', 'go', 'rs']:
            # 소스 코드: 파일명에서 클래스/함수명 추출
            base_names = [f.split('/')[-1].replace(f'.{ext}', '') for f in file_list]
            if len(base_names) == 1:
                changes.append(f"{base_names[0]} 구현")
            else:
                changes.append(f"{ext.upper()} 파일 {len(base_names)}개 수정")
        elif ext == 'md':
            changes.append("문서 업데이트")
        elif ext in ['yml', 'yaml', 'json']:
            changes.append("설정 파일 수정")
        else:
            changes.append(f"{ext} 파일 수정")

        if len(changes) >= 3:
            break

    return changes[:3]

def format_message(emoji, type_name, summary, details, max_length=300):
    """
    커밋 메시지 포맷팅

    형식:
    <gitmoji> <타입>: 한글 요약 (50자 이내)

    - 변경사항 1
    - 변경사항 2
    - 변경사항 3
    """
    title = f"{emoji} {type_name}: {summary}"

    # 제목이 50자를 넘으면 축약
    if len(title) > 50:
        title = title[:47] + "..."

    # 본문 생성
    body_lines = [f"- {d}" for d in details]
    body = "\n".join(body_lines)

    # 전체 메시지
    message = f"{title}\n\n{body}"

    # 300자 제한 체크
    if len(message) > max_length:
        # 본문을 줄여서 300자 맞추기
        available = max_length - len(title) - 2  # \n\n
        truncated_body = []
        current_length = 0

        for line in body_lines:
            if current_length + len(line) + 1 <= available:
                truncated_body.append(line)
                current_length += len(line) + 1
            else:
                break

        body = "\n".join(truncated_body)
        message = f"{title}\n\n{body}"

    return message

def generate_message(analysis_result):
    """
    분석 결과로부터 커밋 메시지 생성

    Args:
        analysis_result: analyze_changes.py의 출력 JSON

    Returns:
        dict: {
            "message": "생성된 커밋 메시지",
            "emoji": "사용된 Gitmoji",
            "type": "커밋 타입"
        }
    """
    if not analysis_result.get('success'):
        return {
            "success": False,
            "error": "분석 결과가 유효하지 않습니다."
        }

    modified = analysis_result.get('modified', [])
    added = analysis_result.get('added', [])
    all_files = modified + added

    if not all_files:
        return {
            "success": False,
            "error": "변경된 파일이 없습니다."
        }

    # Gitmoji 추론
    emoji, type_name = infer_gitmoji(all_files)

    # 요약 생성
    summary_parts = generate_summary(all_files, analysis_result.get('diff_summary', ''))

    # 제목 생성 (첫 번째 요약을 제목으로)
    if summary_parts:
        summary = summary_parts[0]
    else:
        summary = "코드 업데이트"

    # 상세 내용 (나머지 요약들)
    details = summary_parts[1:] if len(summary_parts) > 1 else summary_parts

    # 메시지 포맷팅
    message = format_message(emoji, type_name, summary, details)

    return {
        "success": True,
        "message": message,
        "emoji": emoji,
        "type": type_name,
        "file_count": len(all_files)
    }

if __name__ == "__main__":
    # stdin으로부터 분석 결과 읽기
    if len(sys.argv) > 1:
        # 파일 경로로부터 읽기
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            analysis_result = json.load(f)
    else:
        # stdin으로부터 읽기
        analysis_result = json.load(sys.stdin)

    result = generate_message(analysis_result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
