# Architecture Overview — 5계층 + 의존성 방향

## 5 Layer 구조

```
┌─────────────────────────────────────────┐
│  Controller (HTTP 진입)                 │  바깥쪽 (변동성 ↑)
├─────────────────────────────────────────┤
│  Service (비즈니스 룰)                  │
├─────────────────────────────────────────┤
│  DAO (jOOQ 쿼리)                        │
├─────────────────────────────────────────┤
│  Entity (JPA validate-only)             │
├─────────────────────────────────────────┤
│  Domain Primitive (타입 + 불변식)       │  안쪽 (안정성 ↑)
└─────────────────────────────────────────┘
```

## 각 계층의 책임

### Controller
**책임**: HTTP 요청 받기, JSON 변환, Service 호출, 응답 반환
**금지**:
- 검증 로직
- 비즈니스 로직
- DB 접근

```java
@RestController
@RequiredArgsConstructor
public class PersonController {
    private final PersonService personService;

    @PostMapping
    public Map<String, Object> save(@RequestBody PersonVo vo) {
        return Map.of("success", personService.save(vo));
    }
}
```

### Service
**책임**: 비즈니스 룰 (중복 체크, 상태 전이, 권한 검증), 트랜잭션 경계
**금지**:
- 형식 검증 (Domain Primitive에 위임)
- SQL/jOOQ 직접 사용 (DAO에 위임)

```java
@Service
@RequiredArgsConstructor
public class PersonService {
    private final PersonDao personDao;

    public boolean save(PersonVo vo) {
        return personDao.save(Person.create(vo.getName(), vo.getAge())).getId() > 0;
    }
}
```

### DAO
**책임**: jOOQ 쿼리, 동적 조건 빌드, 배치 처리
**금지**:
- 비즈니스 로직
- 검증

```java
@Repository
@RequiredArgsConstructor
public class PushLogDao {
    private final DSLContext dsl;

    public void insertBatch(List<GitVo.InsertVo> list) { ... }
    public GitVo.SearchVo selectBy(GitVo.SearchVo paging) { ... }
}
```

### Entity (JPA — validate-only)
**책임**: JPA 스키마 매핑, Flyway DDL과의 일치 검증
**금지**:
- `JpaRepository` 정의
- CRUD 메서드 (모든 쿼리는 jOOQ)
- DTO/VO import (의존성 방향 위반)

```java
@Entity
@Table
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Person {
    @Id @GeneratedValue private Long id;
    @Embedded private PersonName name;
    @Embedded private Age age;

    public static Person create(String name, int age) {
        return new Person(new PersonName(name), new Age(age));
    }
}
```

### Domain Primitive
**책임**: 타입 자체가 룰을 강제. 잘못된 값 인스턴스화 불가능.
**선택**:
- `@Embeddable` 붙이면 JPA에서 직접 사용 가능
- 안 붙이면 순수 POJO (영속성 독립성 ↑)

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
```

## 의존성 방향 — 가장 중요한 원칙

**의존성은 항상 안쪽으로만 흐른다.**

```
Controller ──→ Service ──→ DAO ──→ Entity ──→ Domain Primitive
   ↓             ↓          ↓
 PersonVo     (변환)    (조회 결과)
```

### ✅ 허용
- Controller → PersonVo (당연)
- Service → PersonVo (입력 받음)
- Service → Person (Entity 호출)
- DAO → Entity (DB 매핑)
- Entity → Domain Primitive (필드)

### ❌ 금지 (빨간불)
- **Entity → PersonVo** (안쪽이 바깥쪽 알면 안 됨)
- **Domain Primitive → Entity**
- **Domain Primitive → DAO**
- **DAO → Service**

## 의존성 방향 검증 방법

빠른 체크: 각 계층의 `import` 문 확인.

- Entity의 import에 `dto`, `vo`, `controller`, `service`, `dao` 패키지 있으면 빨간불
- Domain Primitive의 import에 `jakarta.persistence` 외 다른 비즈니스 패키지 있으면 빨간불

## 패키지 구조 권장

```
src/main/java/<base>/<domain>/
├── controller/
│   └── PersonController.java
├── service/
│   └── PersonService.java
├── dao/
│   └── PersonDao.java
└── domain/
    ├── Person.java              # Entity
    ├── Age.java                 # Domain Primitive
    ├── PersonName.java          # Domain Primitive
    └── dto/
        └── PersonVo.java        # DTO
```

도메인별 패키지 분리 (`person/`, `notification/`, `order/` …).
공통 Domain Primitive는 `common/domain/` 같은 곳에 둘 수 있음 (`Email`, `Money` 등).

## 왜 이렇게 나누는가

### 변동성 격리
- 외부 API 변화 → Controller, VO만 영향
- DB 스키마 변화 → Entity, DAO만 영향
- 비즈니스 룰 변화 → Service만 영향
- 도메인 룰 변화 → Domain Primitive만 영향

각 변화가 자기 영역 안에 갇힘.

### 테스트 용이성
- Domain Primitive: 단위 테스트 자명
- Service: DAO mock 후 비즈니스 룰 테스트
- Controller: Service mock 후 HTTP 흐름 테스트

### 영속성 독립성
JPA → MyBatis → MongoDB 갈아타도 Domain Primitive는 그대로.
Entity만 다시 정의. 비즈니스 룰 영향 없음.
