# 커밋 메시지 예시

## 좋은 예시 ✅

### ✨ 기능 추가

```
✨ feat: ONNX 임베딩 모델 통합

- MiniLM-L12-v2 모델 로딩 (벡터 384차원)
- DJL Criteria 패턴 적용
- 리소스 자동 정리 구현
```

```
✨ feat: 사용자 인증 API 구현

- JWT 토큰 기반 인증
- 리프레시 토큰 자동 갱신
- 로그인/로그아웃 엔드포인트
```

### 🐛 버그 수정

```
🐛 fix: 토큰 만료 처리 오류 수정

- UTC 기준 만료 시간 비교로 변경
- 만료 30분 전 자동 갱신
```

```
🐛 fix: 검색 결과 중복 제거

- Set 자료구조로 중복 필터링
- 정렬 순서 유지 로직 추가
```

### ♻️ 리팩토링

```
♻️ refactor: DB 연결 풀 관리 개선

- HikariCP 설정 분리
- 동적 연결 수 조정
- 연결 풀 상태 모니터링
```

```
♻️ refactor: API 클라이언트 모듈화

- 공통 HTTP 클라이언트 분리
- 에러 핸들링 중앙화
- 타입 안정성 개선
```

### ⚡ 성능 개선

```
⚡ perf: 검색 쿼리 최적화

- 복합 인덱스 적용
- Redis 캐시 추가 (TTL 5분)
- 응답시간 200ms→50ms 개선
```

```
⚡ perf: 이미지 로딩 속도 개선

- WebP 포맷 변환
- Lazy loading 적용
- CDN 캐싱 설정
```

### ✅ 테스트

```
✅ test: PostEmbedding limit 테스트 안정화

- 벡터 유사도 1.0 보장
- 트랜잭션 커밋 보장
- 34개 테스트 통과
```

```
✅ test: 사용자 인증 통합 테스트 추가

- 로그인/로그아웃 시나리오 검증
- 토큰 갱신 플로우 테스트
- 권한 검증 테스트
```

### 📝 문서

```
📝 docs: API 엔드포인트 문서 작성

- REST API 명세 추가
- 요청/응답 예시 포함
- 에러 코드 설명
```

### 🔧 Chore

```
🔧 chore: 의존성 업데이트

- Spring Boot 3.2.0 → 3.2.1
- QueryDSL 5.0.0 → 5.1.0
- 보안 패치 적용
```

---

## 나쁜 예시 ❌

### ❌ AI 서명 포함

```
✨ feat: 새로운 기능 추가

기능 구현 완료

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

**문제점**: AI 서명 절대 금지

---

### ❌ 추적 코드 포함

```
✅ test: Phase 4 검색 API 통합 테스트 완성 (T032)

- T032-1: 필드별 가중치 검증 (SC-003)
- T032-2: 임계값 경계 필터링 검증 (SC-006)
- T032-3: 빈 결과 처리 검증
- T032-4: 인증 실패 검증 (401 Unauthorized)
```

**문제점**: Phase 4, T032, SC-003 같은 추적 코드 절대 금지

**개선안**:
```
✅ test: API 통합 테스트 추가

- 필드별 가중치 검증
- 임계값 경계 필터링
- 빈 결과 및 인증 실패 처리
```

---

### ❌ 300자 초과

```
✨ feat: 사용자 관리 시스템 구현

이번 커밋에서는 사용자 관리 시스템의 전체 기능을 구현하였습니다.
먼저 UserController.kt 파일에 사용자 생성, 조회, 수정, 삭제 API를 추가하였고,
UserService.kt에는 비즈니스 로직을 구현하였습니다.
UserRepository.kt는 JPA를 사용하여 데이터베이스 접근 계층을 구현하였으며,
UserDto.kt에는 요청/응답 데이터 전송 객체를 정의하였습니다.
또한 UserValidator.kt에는 입력 값 검증 로직을 추가하였고,
UserMapper.kt에는 Entity와 DTO 간 변환 로직을 구현하였습니다.
```

**문제점**: 300자 초과, 파일별 상세 설명 불필요

---

### ❌ 영어 사용

```
✨ feat: Add user authentication API

- JWT token based auth
- Refresh token auto-renewal
- Login/logout endpoints
```

**문제점**: 한글 우선 원칙 위반

---

### ❌ 과거형 사용

```
✨ feat: 사용자 인증 API를 구현했습니다

- JWT 토큰 기반 인증을 추가했습니다
- 리프레시 토큰 자동 갱신 기능을 구현했습니다
```

**문제점**: 명령형이 아닌 과거형 사용

---

### ❌ 파일별 상세 설명

```
✨ feat: 사용자 관리 기능 추가

- UserController.kt에 CRUD API 추가
- UserService.kt에 비즈니스 로직 구현
- UserRepository.kt에 JPA 쿼리 추가
- UserDto.kt에 데이터 전송 객체 정의
- application.yml에 DB 설정 추가
- build.gradle.kts에 의존성 추가
```

**문제점**: Production 파일이 아닌 설정 파일 포함, 파일별 설명 불필요

**개선안**:
```
✨ feat: 사용자 관리 CRUD API 구현

- 사용자 생성/조회/수정/삭제
- JPA 기반 데이터 접근
- 입력 값 검증
```

---

## 커밋 메시지 작성 팁

### 1. 핵심만 추출
- ✅ "사용자 인증 API 구현"
- ❌ "UserController, UserService, UserRepository 파일을 수정하여 사용자 인증 기능을 구현"

### 2. 명령형 사용
- ✅ "버그 수정"
- ❌ "버그를 수정했습니다"
- ❌ "버그 수정함"

### 3. 3-4개 bullet point
- 너무 많으면 → 커밋 분리 고려
- 너무 적으면 → 구체성 추가

### 4. Production 파일만
- ✅ 실제 기능 코드 변경
- ❌ .gitignore, package.json, README.md 등 설정 파일

### 5. 300자 엄수
- 제목 + 본문 합쳐서 300자
- 초과 시 불필요한 설명 제거
