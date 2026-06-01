# Gitmoji 규칙 및 매핑

Complete Gitmoji reference for commit message generation.

## 전체 Gitmoji 테이블

| Gitmoji | 타입 | 설명 | 사용 시점 |
|---------|------|------|----------|
| ✨ | feat | 새로운 기능 추가 | 새로운 API, 컴포넌트, 기능 구현 |
| 🐛 | fix | 버그 수정 | 오류 수정, 예외 처리 개선 |
| ♻️ | refactor | 리팩토링 | 코드 구조 개선 (기능 변경 없음) |
| ⚡ | perf | 성능 개선 | 쿼리 최적화, 캐싱, 응답 시간 개선 |
| 📝 | docs | 문서 변경 | README, 가이드, 주석 업데이트 |
| ✅ | test | 테스트 추가/수정 | 단위 테스트, 통합 테스트 작성 |
| 🔧 | chore | 빌드/설정 변경 | 의존성 업데이트, 설정 파일 수정 |
| 🔒 | security | 보안 이슈 수정 | 취약점 패치, 인증/권한 개선 |
| 💄 | style | UI/스타일 변경 | CSS, 레이아웃, 디자인 수정 |
| 🚀 | deploy | 배포 관련 | CI/CD, 환경 설정 |
| 🎨 | style | 코드 포맷팅 | Prettier, Linter 적용 |
| 🔥 | remove | 코드/파일 제거 | 사용하지 않는 코드 삭제 |
| 🚧 | wip | 작업 진행 중 | 미완성 기능 (WIP 커밋, 권장하지 않음) |
| 💚 | fix | CI 빌드 수정 | CI/CD 파이프라인 수정 |
| ⬆️ | upgrade | 의존성 업그레이드 | 패키지 버전 업데이트 |
| ⬇️ | downgrade | 의존성 다운그레이드 | 호환성 문제로 버전 다운 |
| 📌 | pin | 의존성 버전 고정 | 특정 버전으로 핀 |
| 👷 | ci | CI 설정 추가/변경 | GitHub Actions, Jenkins |
| 🔀 | merge | 브랜치 병합 | PR 병합 |
| 🎉 | init | 프로젝트 시작 | 초기 커밋 |
| 🔖 | release | 버전 태그/릴리스 | v1.0.0 릴리스 |

## 선택 가이드

### 파일 유형별 Gitmoji

**Backend (Kotlin/Java/Python/Go)**
- 새로운 API → ✨ feat
- 버그 수정 → 🐛 fix
- 리팩토링 → ♻️ refactor
- 테스트 추가 → ✅ test

**Frontend (React/Vue/Angular)**
- 새로운 컴포넌트 → ✨ feat
- UI 디자인 변경 → 💄 style
- 상태 관리 리팩토링 → ♻️ refactor

**Database**
- 마이그레이션 → ✨ feat
- 쿼리 최적화 → ⚡ perf
- 인덱스 추가 → ⚡ perf

**Infrastructure**
- Docker 설정 → 🔧 chore
- CI/CD 파이프라인 → 👷 ci
- 배포 스크립트 → 🚀 deploy

### 변경 범위별 Gitmoji

**단일 파일**
- 파일의 주요 변경 유형에 맞는 Gitmoji 선택

**여러 파일 (관련된 변경)**
- 가장 중요한 변경 사항의 Gitmoji 선택
- 예: 기능 추가 + 테스트 → ✨ feat (기능이 주요)

**여러 파일 (무관한 변경)**
- 커밋을 분리하는 것이 권장됨
- 불가피한 경우 ♻️ refactor 또는 🔧 chore 사용

## 우선순위 규칙

변경사항이 여러 타입에 해당할 때:

1. **feat (✨)** - 새로운 기능이 가장 높은 우선순위
2. **fix (🐛)** - 버그 수정이 두 번째
3. **refactor (♻️)** - 리팩토링
4. **perf (⚡)** - 성능 개선
5. **test (✅)** - 테스트
6. **docs (📝)** - 문서
7. **chore (🔧)** - 기타

**예시:**

```
변경사항: 새로운 API + 관련 테스트 + API 문서
→ ✨ feat: API 구현 (feat이 우선)

변경사항: 버그 수정 + 테스트 추가
→ 🐛 fix: 버그 수정 (fix가 우선)

변경사항: 코드 리팩토링 + 성능 개선
→ ⚡ perf: 성능 개선 (perf가 더 중요)
```

## 특수 케이스

### 초기 프로젝트 설정
```
🎉 init: 프로젝트 초기 설정

- 기본 디렉토리 구조
- 의존성 설정
- README 작성
```

### 릴리스/버전 태깅
```
🔖 release: v1.0.0 릴리스

- 주요 기능 완성
- 프로덕션 배포 준비
```

### 긴급 핫픽스
```
🐛 fix: 프로덕션 결제 오류 긴급 수정

- 트랜잭션 롤백 로직 추가
- 오류 알림 강화
```

### WIP 커밋 (권장하지 않음)
```
🚧 wip: 사용자 인증 작업 중

- 기본 구조만 구현
- 검증 로직 미완성
```

**주의:** WIP 커밋은 로컬 개발용으로만 사용하고, PR에는 포함하지 마세요.

## 참고

- 하나의 커밋에는 하나의 Gitmoji만 사용
- 명확하지 않은 경우 가장 중요한 변경 사항에 맞춰 선택
- 공식 사이트: https://gitmoji.dev

## 브랜치 Prefix 매핑

브랜치 생성 시에는 Gitmoji를 사용하지 않고 타입 prefix만 사용한다.
새 기능 작업은 항상 `feat/`를 사용한다. `feature/`는 같은 의미의 legacy prefix로 보고 새 브랜치에는 사용하지 않는다.

| 변경 유형 | Commit 타입 | Branch prefix | 예시 |
|----------|-------------|---------------|------|
| 새로운 기능 | feat | `feat/` | `feat/create-items` |
| 버그 수정 | fix | `fix/` | `fix/resolve-login-error` |
| 구조 개선 | refactor | `refactor/` | `refactor/modify-member-business` |
| 성능 개선 | perf | `perf/` | `perf/improve-search-speed` |
| 테스트 | test | `test/` | `test/add-payment-coverage` |
| 문서 | docs | `docs/` | `docs/update-install-guide` |
| 유지보수 | chore | `chore/` | `chore/update-build-tooling` |

`init`은 초기 커밋 메시지에만 사용한다. 일반 작업 브랜치에는 `init/` prefix를 사용하지 않는다. 사용자가 명시적으로 초기화 작업 브랜치를 요청하면 `chore/initialize-repository`처럼 작업 목적이 드러나는 이름을 우선한다.
