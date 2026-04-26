---
name: my-backend-pattern
description: Apply muheun's opinionated Java Spring Boot backend patterns. ACTIVATE when both conditions met (1) current project is Java/Spring Boot (build.gradle or pom.xml exists with spring-boot-starter dependencies, .java files in controller/service/dao/domain packages) AND (2) user requests creating, modifying, or reviewing backend layer code. CONCRETE TRIGGER PHRASES (Korean) "도메인 추가", "DAO 만들어", "DAO에 select 추가", "Entity 검증 어떻게", "Service 패턴 맞아", "Controller에 RequestBody", "도메인 프리미티브로 리팩토링", "Age 타입 만들어", "jOOQ 쿼리 짜줘", "DSLContext로 select", "Flyway 마이그레이션", "백엔드 코드 리뷰", "@Column comment 빠진", "@Embeddable 어떻게", "ddl-auto validate". (English) "create a controller", "add a service", "spring boot dao", "domain primitive validation", "jooq query", "jpa entity pattern". WHAT IT ENFORCES 5-layer architecture (Controller/Service/DAO/Entity/Domain Primitive), jOOQ for all queries, JPA validate-only (no JpaRepository CRUD), Flyway DDL with COMMENT clauses, Domain Primitive pattern (Age/PersonName/Email) with type-driven validation, DomainValidationException for domain errors, @Column(comment="...") on every column, @SuperBuilder forbidden on domain objects, Entity must not import dto/vo packages. DO NOT ACTIVATE for frontend (React/Vue/Flutter/Svelte/native mobile), Kotlin .kt files even in Spring Boot project (Java only), Non-Spring backends (Node.js/Python/Go/Rust), pure DevOps tasks (Docker/Kubernetes/CI/CD), generic code questions without backend context.
---

# 무흔의 Spring Boot 백엔드 패턴

## Overview

Java + Spring Boot 기반 백엔드 개발 시 일관되게 적용할 5계층 아키텍처와 패턴 가이드.
**검증 룰을 위치가 아니라 타입에 새기는** 도메인 프리미티브 패턴이 핵심.

---

## When to Use This Skill

### 강한 활성화 신호 (반드시 활성화)

다음 phrase 패턴 등장 시:

**도메인 모듈 작업:**
- "Notification 도메인 추가해줘", "Order 모듈 만들어줘"
- "User Entity 만들어줘"

**DAO/쿼리 작업:**
- "PushLog DAO에 selectByCommitter 추가"
- "jOOQ 쿼리 짜줘", "DSLContext로 select"
- "buildCondition 만들어줘", "동적 쿼리"

**Controller/Service 작업:**
- "Controller에 @RequestBody 필요해?"
- "Service 패턴 맞게 짜줘"

**검증/리팩토링:**
- "Entity 검증 패턴 맞아?", "도메인 프리미티브로 리팩토링"
- "Age/Email 같은 타입 만들어줘"
- "@Column comment 빠진 거 찾아줘"

**Flyway/DDL:**
- "Flyway 마이그레이션 작성", "V{N}__create_xxx.sql"

**코드 리뷰:**
- "이 Spring Boot 코드 패턴 맞아?", "anti-pattern 있어?"

영문도 동일: "create a controller", "add a service", "spring boot dao", "domain primitive validation"

### 활성화 컨텍스트 (다음 중 2개 이상 해당 시 강함)

- 현재 디렉토리에 `build.gradle` 또는 `pom.xml` 존재
- `.java` 파일이 `controller/`, `service/`, `dao/`, `domain/` 패키지에 있음
- `spring-boot-starter` 의존성 포함
- 사용자가 `@Entity`, `@RestController`, `@Service`, `@Repository` 어노테이션 언급
- 사용자가 `.java` 파일 경로(`@C:\...\xxx.java`) 첨부

### 활성화 거부 신호 (절대 활성화 X)

- ❌ Frontend 코드 (React, Vue, Flutter, Svelte, native mobile)
- ❌ **Kotlin `.kt` 파일** (이 plugin은 Java 전용. Kotlin은 별도 룰)
- ❌ Non-Spring 백엔드 (Node.js, Python, Go, Rust)
- ❌ DevOps만 (Docker, Kubernetes, CI/CD, Terraform)
- ❌ DB 쿼리만 (Java 코드 무관)
- ❌ 일반 질문 ("코드란?", "어떤 언어 추천?")

---

## Activation Confirmation (자기 검증)

활성화 후 **첫 응답 시작 전 자기 점검**:

```
□ 현재 프로젝트가 Java Spring Boot인가? (build.gradle/pom.xml 직접 확인)
□ 사용자가 백엔드 코드 작업 의도를 명확히 표현했는가?
□ 작업 종류 식별 가능한가? (Controller/Service/DAO/Entity/Domain 중 어느 것)
```

3개 모두 YES일 때만 패턴 적용 진행.
하나라도 NO면 일반 어시스턴트 모드로 (skill 적용 보류).

---

## Core Philosophy

### 1. 검증은 타입 시스템에 새긴다

같은 룰이 여러 곳에 있으면 빨간불. **잘못된 값은 인스턴스화 자체가 불가능**해야 한다.

```java
public final class Age {
    public static final int MIN = 1;
    public static final int MAX = 200;
    private int value;

    public Age(int value) {
        if (value < MIN || value > MAX)
            throw new DomainValidationException("나이 범위 " + MIN + "~" + MAX);
        this.value = value;
    }
}
// → new Age(-1) 호출 자체가 실패. 잘못된 Age는 존재 불가능.
```

### 2. Persistence Ignorance — 도메인은 영속성을 모른다

JPA → MyBatis → MongoDB 갈아타도 도메인 객체는 그대로 살아남는다.
검증은 영속성 기술과 독립.

### 3. 의존성 방향: 안쪽으로만

Entity는 DTO/VO를 모른다. 어댑터(바깥)가 도메인(안쪽)을 알지, 그 반대 X.
Entity가 PersonVo를 import하기 시작하면 설계 빨간불.

### 4. jOOQ가 쿼리, JPA는 스키마 검증만

- JPA: `ddl-auto: validate` 만. JpaRepository 사용 X.
- jOOQ: 모든 쿼리. DSLContext 직접 사용.
- Flyway: DDL 마이그레이션.

### 5. 같은 검증 룰 = 한 곳에만

3곳 검증 = 3곳 동기화 부담. 룰 변경 시 까먹을 확률 100%.

---

## 5 Layer Responsibility

| 계층 | 책임 | 안 하는 것 |
|------|------|-----------|
| **Controller** | HTTP 진입, JSON 변환, Service 호출 | 검증, 비즈니스 로직 |
| **Service** | 비즈니스 룰 (중복 체크, 상태 전이) | 형식 검증, SQL |
| **DAO** | jOOQ 쿼리, 동적 조건 | 비즈니스 로직, 검증 |
| **Entity** | JPA 스키마 매핑 (validate-only) | JpaRepository, CRUD |
| **Domain Primitive** | 타입 + 불변식 + 도메인 행동 | (옵션) 영속성 어노테이션 |

---

## How to Use This Skill

### Step 1: 환경 확인 (필수, 코드 작성 전)

⚠️ **`build.gradle` 또는 `pom.xml` 먼저 Read 도구로 읽기.** 일반론 답 금지.

특히 확인:
- **Spring Boot 버전** (3.x vs 4.x — Jakarta Persistence 3.2 지원 여부)
- **Hibernate 버전** (6.x vs 7.x — `org.hibernate.annotations.Comment` deprecated 여부)
- **Java 버전** (17/21/25 — records, pattern matching, sealed)
- **jOOQ 버전, Flyway 버전, Lombok 사용 여부**

→ AI 학습 데이터 시점 ≠ 사용자 환경. **환경이 답을 결정.**
→ Spring Boot 4.0 이상이면 `@Column(comment = "...")` 사용. `@Comment` 금지.

### Step 2: 작업 종류 식별 + Reference Read (필수)

⚠️ **반드시 Read 도구로 해당 reference를 직접 읽고 시작.** 표는 카탈로그일 뿐, 실제 내용을 Read해야 적용 가능.

| 작업 | Read 명령 |
|------|----------|
| 전체 구조 파악 / 새 모듈 풀세트 | `Read references/architecture-overview.md` |
| 도메인 객체 (Entity, Embeddable) 설계 | `Read references/domain-primitive.md` |
| DAO / jOOQ 쿼리 작성 | `Read references/data-layer.md` |
| Controller / Service 작성 | `Read references/web-layer.md` |
| DTO/VO 작성 / 페이징 패턴 | `Read references/vo-pattern.md` |
| 예외 처리 / GlobalExceptionHandler | `Read references/exception-handling.md` |
| 코드 리뷰 / 패턴 위반 검증 | `Read references/anti-patterns.md` |

여러 영역 겹치면 **여러 파일 모두 Read** (예: 새 모듈 = architecture + domain + data + web 4개).

### Step 3: 표준 코드 참조 (코드 작성 작업 시)

작성 시 다음 표준 예시도 함께 Read:

| 작성하는 것 | 추가로 Read할 표준 예시 |
|------------|----------------------|
| DAO | `Read references/code-example-dao.md` (PushLogDao 기준) |
| Entity / Domain Primitive | `Read references/code-example-domain.md` (Person/Age/PersonName 기준) |

### Step 4: 작성 후 anti-pattern 검증 (필수)

작성 완료 후 **반드시** `references/anti-patterns.md` 의 11가지 anti-pattern 모두 점검.
체크리스트 통과 못 하면 수정.

---

## 사용자와 작업 시 메타 행동

⚠️ **사용자가 hesitation 표현 시 즉시 한 발 물러서기:**
- "흠.. 애매하다"
- "오버 엔지니어링 같다"
- "이거 진짜 필요한가?"
- "비용 대비 이득이 모호한데"

이런 표현은 사용자의 직감 신호. 이론적 정합성 추구 멈추고 **실용 관점 재평가**.
거창한 개념(Persistence Ignorance, DRY, SOLID 등)으로 보일러플레이트 정당화 금지.
입장 변경 시 명확하게: "내가 틀렸다. [이유]. [정정안]." (양다리 금지)

---

## Quick Decision Tree

```
사용자 요청 받음
│
├─ Step 0: Activation Confirmation 통과? (YES/NO)
│   └─ NO → skill 적용 보류, 일반 응답
│   └─ YES → 계속
│
├─ Step 1: build.gradle/pom.xml Read → 버전 확인
│
├─ Step 2: 작업 종류 식별 → 해당 reference Read
│   ├─ 새 모듈 → architecture-overview.md
│   ├─ 도메인 객체 → domain-primitive.md
│   ├─ DAO → data-layer.md
│   ├─ Controller/Service → web-layer.md
│   ├─ VO/DTO → vo-pattern.md
│   └─ 예외 처리 → exception-handling.md
│
├─ Step 3: 작성 작업이면 표준 코드도 Read
│   ├─ DAO 작성 → code-example-dao.md
│   └─ 도메인 작성 → code-example-domain.md
│
└─ Step 4: 작성 완료 후 anti-patterns.md 체크리스트 적용
```

---

## Validation Checklist

작성한 코드가 다음 모두 만족하는지 확인:

- [ ] Entity가 DTO/VO를 import하지 않는다
- [ ] `@SuperBuilder`로 검증 우회 가능한 도메인 객체 없다
- [ ] `RuntimeException` 직접 throw 안 한다 (`DomainValidationException` 등 사용)
- [ ] 같은 검증 룰이 2곳 이상에 정의되지 않는다
- [ ] DAO는 jOOQ 사용 (`JpaRepository` 아님)
- [ ] Domain Primitive는 생성자 검증 + 외부에서 우회 불가능
- [ ] `@Embeddable` 클래스에 `@NoArgsConstructor(PROTECTED)` + `@EqualsAndHashCode`
- [ ] `@JsonValue`로 직렬화 형태 명시
- [ ] Controller에 `@RequestBody` 사용
- [ ] DAO 메서드명: `insertBatch`, `selectBy`, `updateBy` (find/save 아님)
- [ ] **모든 컬럼에 `@Column(comment = "...")` 명시** (Jakarta Persistence 3.2+ 표준)
- [ ] **`@Embedded` 필드의 comment는 Embeddable 내부 `@Column`에 정의**
- [ ] **`org.hibernate.annotations.Comment` 사용 금지** (deprecated)
- [ ] **Flyway DDL의 모든 컬럼에 `COMMENT '...'` 명시**

---

## Resources

### references/

- **architecture-overview.md** — 5계층 책임 + 의존성 방향
- **domain-primitive.md** — Age/PersonName 패턴 (핵심)
- **data-layer.md** — jOOQ DAO + JPA validate-only + Flyway + @Column 규칙
- **web-layer.md** — Controller + Service 컨벤션
- **vo-pattern.md** — DTO/VO with records, inner class grouping
- **exception-handling.md** — DomainValidationException + GlobalExceptionHandler
- **anti-patterns.md** — 11가지 흔한 실수와 회피법
- **code-example-dao.md** — PushLogDao 표준 예시
- **code-example-domain.md** — Person/Age/PersonName/PersonVo 표준 예시

---

## Example: 새 도메인 모듈 추가 흐름

User: "Notification 도메인 모듈 추가해줘"

Steps:
0. **Activation Confirmation** — Java Spring Boot 프로젝트 확인 ✓
1. **환경 확인** — `build.gradle` Read → Spring Boot 버전 확인
2. **Reference Read** (4개 동시):
   - `Read references/architecture-overview.md`
   - `Read references/domain-primitive.md`
   - `Read references/data-layer.md`
   - `Read references/web-layer.md`
3. **표준 코드 Read**:
   - `Read references/code-example-domain.md`
   - `Read references/code-example-dao.md`
4. **작성**:
   - Domain Primitive 식별 — `NotificationTitle`, `NotificationContent` 등
   - Entity 정의 — `@Embedded` 로 Domain Primitive 사용
   - Flyway Migration — `V{N}__create_notification.sql` (모든 컬럼 `COMMENT '...'`)
   - DAO 작성 — jOOQ 기반. `insertBatch`, `selectBy`, `updateBy`
   - VO 정의 — 도메인별 inner class 그룹 (`NotificationVo.InsertVo`, `SearchVo`, `ListVo`)
   - Service — 비즈니스 로직만. 변환은 `Entity.create(vo.field())` 호출
   - Controller — `@RestController`, `@RequestBody`, Service 호출 후 `Map.of` 반환
5. **검증**: `Read references/anti-patterns.md` → 11개 체크리스트 통과 확인

---

## Origin

이 패턴은 muheun이 2026-04-26 깊은 토론을 통해 정립한 백엔드 개발 방법론을 코드화한 것이다.
검증 위치 고민에서 출발해, **"룰을 위치가 아닌 타입에 새겨라"** 는 깨달음에 도달.
관련 학습 기록(자전적): muheun의 자아 위키 `learning/2026-04-26-도메인-프리미티브-패턴.md`
