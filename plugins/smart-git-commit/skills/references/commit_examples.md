# 커밋 메시지 예시

Comprehensive good and bad examples for commit message generation.

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

```
✨ feat: 파일 업로드 기능 추가

- 다중 파일 업로드 지원
- 파일 타입 검증 (이미지만 허용)
- 최대 크기 제한 (10MB)
```

### 🐛 버그 수정

```
🐛 fix: 토큰 만료 처리 오류 수정

- UTC 기준 만료 시간 비교로 변경
- 만료 30분 전 자동 갱신
- 타임존 불일치 문제 해결
```

```
🐛 fix: 검색 결과 중복 제거

- Set 자료구조로 중복 필터링
- 정렬 순서 유지 로직 추가
```

```
🐛 fix: 로그인 실패 시 무한 로딩 해결

- 에러 상태 처리 추가
- 사용자 피드백 메시지 표시
```

### ♻️ 리팩토링

```
♻️ refactor: DB 연결 풀 관리 개선

- HikariCP 설정 분리
- 동적 연결 수 조정
- 연결 풀 상태 모니터링 추가
```

```
♻️ refactor: API 클라이언트 모듈화

- 공통 HTTP 클라이언트 분리
- 에러 핸들링 중앙화
- 타입 안정성 개선
```

```
♻️ refactor: 사용자 서비스 계층 분리

- 비즈니스 로직과 데이터 접근 분리
- 의존성 주입 패턴 적용
- 테스트 용이성 향상
```

### ⚡ 성능 개선

```
⚡ perf: 검색 쿼리 최적화

- 복합 인덱스 적용 (user_id, created_at)
- Redis 캐시 추가 (TTL 5분)
- 응답시간 200ms→50ms 개선
```

```
⚡ perf: 이미지 로딩 속도 개선

- WebP 포맷 변환
- Lazy loading 적용
- CDN 캐싱 설정
```

```
⚡ perf: 대용량 데이터 처리 최적화

- 배치 처리 도입 (1000건 단위)
- 메모리 사용량 70% 감소
- 처리 시간 10분→2분 단축
```

### ✅ 테스트

```
✅ test: PostEmbedding 테스트 안정성 개선

- 벡터 유사도 검증 로직 강화
- 트랜잭션 동기화 보장
- 간헐적 실패 원인 제거
```

```
✅ test: API 예외 처리 테스트 추가

- 타임아웃 시나리오 검증
- 네트워크 오류 처리 확인
- 인증 실패 케이스 테스트
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

```
📝 docs: README 설치 가이드 업데이트

- Docker 환경 설정 추가
- 환경 변수 설명
- 트러블슈팅 섹션 추가
```

### 🔧 Chore

```
🔧 chore: 의존성 업데이트

- Spring Boot 3.2.0 → 3.2.1
- QueryDSL 5.0.0 → 5.1.0
- 보안 패치 적용
```

```
🔧 chore: 빌드 설정 개선

- Gradle 캐싱 활성화
- 빌드 시간 5분→2분 단축
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

**문제점:**
- AI 서명 절대 금지
- 메시지가 너무 간략함

**개선안:**
```
✨ feat: 사용자 프로필 편집 기능 추가

- 이름, 이메일 수정 지원
- 프로필 이미지 업로드
- 변경 이력 저장
```

---

### ❌ 태스크/시나리오 ID 포함

```
✨ feat: TASK-1234 사용자 인증 구현

- JIRA-456: JWT 토큰 생성
- SC-003: 로그인 시나리오 검증 완료
- Phase 2 마일스톤 달성
```

**문제점:**
- Task/Issue IDs (TASK-1234, JIRA-456)
- Scenario IDs (SC-003)
- Phase tracking (작업 리포트용)
- 실제 구현 내용 설명 부족

**개선안:**
```
✨ feat: JWT 토큰 기반 인증 구현

- 토큰 생성 및 검증 로직
- 자동 갱신 기능 (만료 30분 전)
- 로그인/로그아웃 엔드포인트
```

---

### ❌ 테스트 통계 포함

```
✅ test: API 테스트 안정화

- 34개 테스트 추가
- 32개 통과, 2개 실패
- 커버리지 85% 달성
- Phase 3 검증 완료
```

**문제점:**
- 테스트 통계 (CI report용 정보)
- Coverage numbers (코드 변경 설명 없음)
- Phase tracking
- 실제 테스트 내용 설명 부족

**개선안:**
```
✅ test: API 예외 처리 테스트 추가

- 타임아웃 시나리오 검증
- 네트워크 오류 처리 확인
- 인증 실패 케이스 테스트
```

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

**문제점:**
- 파일별 상세 설명 (git diff로 볼 수 있음)
- Configuration files 언급 (불필요)
- 실제 기능 설명 부족

**개선안:**
```
✨ feat: 사용자 관리 CRUD API 구현

- 사용자 생성/조회/수정/삭제
- JPA 기반 데이터 접근
- 입력 값 검증 로직
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

**문제점:**
- 300자 초과
- 파일별 상세 설명 불필요
- 장황한 서술

**개선안:**
```
✨ feat: 사용자 관리 CRUD API 구현

- 생성/조회/수정/삭제 기능
- JPA 기반 영속성 계층
- 입력 값 검증 및 변환
```

---

### ❌ 영어 사용

```
✨ feat: Add user authentication API

- JWT token based auth
- Refresh token auto-renewal
- Login/logout endpoints
```

**문제점:**
- 한글 우선 원칙 위반

**개선안:**
```
✨ feat: 사용자 인증 API 구현

- JWT 토큰 기반 인증
- 리프레시 토큰 자동 갱신
- 로그인/로그아웃 엔드포인트
```

---

### ❌ 과거형 사용

```
✨ feat: 사용자 인증 API를 구현했습니다

- JWT 토큰 기반 인증을 추가했습니다
- 리프레시 토큰 자동 갱신 기능을 구현했습니다
- 로그인/로그아웃 엔드포인트를 만들었습니다
```

**문제점:**
- 명령형이 아닌 과거형 사용

**개선안:**
```
✨ feat: 사용자 인증 API 구현

- JWT 토큰 기반 인증
- 리프레시 토큰 자동 갱신
- 로그인/로그아웃 엔드포인트
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

### 6. WHAT/WHY/HOW 집중
- WHAT: 무엇을 만들었는가 (필수)
- WHY: 왜 필요했는가 (선택적)
- HOW: 어떻게 구현했는가 (핵심만)

### 7. 추적 정보 제외
- ❌ Task IDs, Scenario IDs
- ❌ Test statistics
- ❌ Phase/Milestone tracking
- ✅ 코드 변경 내용만 설명

### 8. 구현 세부사항 제외
- ❌ "Step 1.4", "Step 1.5" (내부 구조 언급)
- ❌ "참조 문서 확장", "문서 작업" (코드 아닌 문서 작업)
- ❌ "SKILL.md 수정", "references/ 추가" (파일명 나열)
- ✅ 실제 개발/개선/해결한 기능만 설명

**예시:**
```
❌ BAD:
✨ feat: Step 1.5 추가 및 참조 문서 확장

- Step 1.5: 논리적 커밋 분리
- references/grouping_strategies.md 추가
- SKILL.md 업데이트

✅ GOOD:
✨ feat: 대규모 변경사항 논리적 커밋 분리 기능 추가

- 10개 이상 파일 변경 시 자동 그룹핑 제안
- 디렉토리, 파일명, 변경 타입 기반 분석
- 그룹별 순차 커밋 실행 지원
```

---

## 9. 코드 참조 제거 규칙 (CRITICAL)

**핵심 원칙**: 커밋 메시지는 **비즈니스 기능 중심**이어야 하며, **코드 구조 중심**이 아니어야 합니다.

### 절대 금지 항목

❌ **클래스명 언급 금지**:
- `UserService`, `ProductRepository`, `AuthController`
- `VectorEntityType`, `TokenValidator`, `SearchService`
→ 대신: "사용자 서비스", "상품 데이터 접근", "인증 컨트롤러"

❌ **메서드명 언급 금지**:
- `extractVectorFields()`, `getUserById()`, `calculateDiscount()`
- `search()`, `validate()`, `save()`
→ 대신: "벡터 필드 추출", "사용자 조회", "할인 계산"

❌ **변수명/필드명 언급 금지**:
- `userId`, `productList`, `searchQuery`
- `expiresAt`, `createdAt`, `isActive`
→ 대신: "사용자 ID", "상품 목록", "검색어"

❌ **파일명 언급 금지**:
- `UserService.kt`, `auth.controller.ts`, `product.dto.py`
→ 대신: "사용자 서비스 계층", "인증 컨트롤러", "상품 데이터 모델"

### 변환 공식

```
구체적 코드 참조 → 일반화된 도메인 기능 설명

VectorEntityType enum
→ 엔티티 타입 enum

extractVectorFields()
→ 벡터 필드 추출

UserRepository.findByEmail()
→ 이메일 기반 사용자 조회

ProductService.calculateDiscount()
→ 상품 할인 계산

AuthController.login()
→ 로그인 API
```

### 예시 1: 리팩토링 (벡터화 아키텍처)

**❌ BAD (코드 중심)**:
```
♻️ refactor: 벡터화 아키텍처 개선

- VectorEntityType enum으로 타입 안전성 보장
- extractVectorFields() 통합으로 중복 코드 제거
- OAuth2 사용자 생성 시 벡터화 누락 해결
- E5 모델 Query/Passage prefix로 검색 정확도 향상
```

**문제점**:
- `VectorEntityType` 클래스명 노출
- `extractVectorFields()` 메서드명 노출
- 코드 구조 중심 설명

**✅ GOOD (도메인 중심)**:
```
♻️ refactor: 벡터화 아키텍처 개선 및 E5 모델 최적화

- 엔티티 타입 enum으로 타입 안전성 보장
- 벡터 필드 추출 중복 코드 리팩토링
- OAuth2 사용자 생성 시 벡터화 누락 해결
- 임베딩 모델 Query/Passage prefix로 검색 정확도 향상
```

**개선 이유**:
- 일반화된 도메인 용어 사용
- 기능 중심 설명
- 코드 리팩토링 후에도 메시지 의미 유지

---

### 예시 2: 기능 추가 (데이터 계층)

**❌ BAD**:
```
✨ feat: User 및 Product 리포지토리 구현

- UserRepository.findByEmail() 추가
- ProductRepository.searchByKeyword() 구현
- BaseRepository 추상 클래스 생성
```

**✅ GOOD**:
```
✨ feat: 사용자 및 상품 데이터 접근 계층 구현

- 이메일 기반 사용자 조회
- 키워드 기반 상품 검색
- 공통 데이터 접근 추상화
```

---

### 예시 3: 성능 개선 (캐싱)

**❌ BAD**:
```
⚡ perf: SearchService 쿼리 최적화

- PostRepository.findByKeyword() 인덱스 추가
- RedisCacheManager.set() TTL 5분 설정
- SearchController.search() 응답시간 개선
```

**✅ GOOD**:
```
⚡ perf: 검색 성능 최적화

- 게시물 검색 인덱스 추가
- Redis 캐시 TTL 설정
- 검색 API 응답 시간 75% 단축
```

---

### 예시 4: 버그 수정 (토큰 검증)

**❌ BAD**:
```
🐛 fix: TokenValidator.isExpired() 타임존 버그

- ZonedDateTime.now(ZoneOffset.UTC) 사용
- TokenEntity.expiresAt 필드 UTC 저장
```

**✅ GOOD**:
```
🐛 fix: 토큰 만료 시간 타임존 버그 수정

- UTC 기준 시간 비교로 변경
- 만료 시간 저장 로직 개선
```

---

### 예시 5: 테스트 추가

**❌ BAD**:
```
✅ test: UserServiceTest 예외 처리 케이스 추가

- createUser_whenEmailExists_throwsException()
- validatePassword_whenTooShort_throwsException()
```

**✅ GOOD**:
```
✅ test: 사용자 서비스 예외 처리 테스트 추가

- 이메일 중복 예외 처리
- 비밀번호 검증 예외 처리
```

---

### 허용되는 기술 용어

✅ **기술 개념/패턴은 OK**:
- `enum`, `interface`, `abstract class` (개념)
- `Redis`, `JWT`, `OAuth2` (기술 스택)
- `Query/Passage prefix` (기술 용어)
- `타입 안전성`, `불변성`, `캐싱` (아키텍처 개념)

✅ **도메인 용어는 OK**:
- "사용자 인증", "게시물 검색", "상품 필터링"
- "벡터 필드", "엔티티 타입", "토큰 검증"
- "데이터 계층", "비즈니스 로직", "API 엔드포인트"

---

### 변환 연습

| ❌ 피해야 할 표현 | ✅ 선호하는 표현 |
|-----------------|----------------|
| `VectorEntityType enum` | `엔티티 타입 enum` |
| `extractVectorFields()` | `벡터 필드 추출` |
| `OAuth2UserService.createUser()` | `OAuth2 사용자 생성` |
| `UserRepository.findByEmail()` | `이메일 기반 사용자 조회` |
| `ProductDto` | `상품 데이터 모델` |
| `searchQuery.toLowerCase()` | `검색어 소문자 변환` |
| `TokenValidator.isExpired()` | `토큰 만료 검증` |
| `PostRepository` | `게시물 데이터 접근` |
| `AuthController.login()` | `로그인 API` |
| `UserService.kt` | `사용자 서비스 계층` |

---

### 왜 이 규칙이 중요한가?

**1. 코드 리팩토링에 강건함**:
- 클래스명 변경 (`UserService` → `UserServiceImpl`)
- 메서드명 변경 (`getUser` → `findUser`)
→ 커밋 메시지 의미는 여전히 유효

**2. 비개발자 가독성**:
- PM, 디자이너, QA도 대략적 변경 이해 가능
- "사용자 인증 추가" (이해 O) vs "AuthService.authenticate() 추가" (이해 X)

**3. 기술 스택 독립성**:
- 기술 변경 (`JPA` → `MyBatis`) 후에도 메시지 재사용 가능
- "데이터 접근 개선" (기술 독립) vs "JPA 쿼리 개선" (기술 종속)

**4. 장기 유지보수**:
- 6개월 후 코드 구조 변경되어도 커밋 의미 명확
- 히스토리 검색 시 기능 기반 검색 가능

---

### 자가 검증 체크리스트

커밋 메시지 작성 후 체크:

- [ ] 클래스명 (PascalCase 패턴) 없음
- [ ] 메서드명 (`()` 포함) 없음
- [ ] 변수명 (camelCase 패턴) 없음
- [ ] 파일명 (확장자 포함) 없음
- [ ] 도메인 용어로 대체됨
- [ ] 기능 중심 설명임
