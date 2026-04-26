# VO/DTO Pattern — Records + Inner Class Grouping

## 핵심 컨셉

VO/DTO는 **데이터 운반만**. 검증·로직 없음. (검증은 Domain Primitive가 담당)

도메인별로 **inner class로 그룹화**:
```java
public class GitVo {
    public record InsertVo(...) {}
    public record SearchVo(...) {}
    public record ListVo(...) {}
}
```

용도(Insert/Search/List)별로 별도 VO 가짐. 한 VO로 모든 걸 처리하지 않음.

## 두 가지 표기 — Records vs Lombok Class

### Pattern A: Java Records (권장 — Java 16+)

```java
public class GitVo {
    public record InsertVo(
            String organization,
            String project,
            String branch,
            boolean isTopBranch,
            String message,
            LocalDateTime commitedAt,
            String commitUrl,
            String committer,
            String email
    ) {}
}
```

**사용**: `vo.organization()`, `vo.committer()` (getter 없이 메서드 직접)

**장점**:
- 자동 final, equals, hashCode, toString
- 불변 객체
- 보일러플레이트 0
- 명확한 데이터 운반 의도

### Pattern B: Lombok Class (Records 못 쓸 때)

```java
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class PersonVo {
    private Long id;
    private String name;
    private int age;
}
```

**사용**: `vo.getName()`, `vo.getAge()` (getter 명시)

**언제**: 페이징 VO처럼 mutable 필요 시 (paging.setBody, paging.calcPaging)

## 도메인별 VO 그룹화

### 단일 클래스, inner record 패턴

```java
public class PersonVo {

    // 입력용 (POST /persons)
    public record InsertVo(
            String name,
            int age
    ) {}

    // 검색용 (GET /persons?...)
    public static class SearchVo {
        // 검색 조건
        private String name;
        private Integer minAge;
        private Integer maxAge;

        // 페이징 상태
        private int page = 1;
        private int size = 20;
        private int totalCount;
        private List<ListVo> body;

        // ... getters, setters, calcPaging, setBody, offset, limit
    }

    // 목록 응답용 (GET /persons - 행)
    public record ListVo(
            Long id,
            String name,
            int age,
            LocalDateTime createdAt
    ) {}

    // 상세 응답용 (GET /persons/{id})
    public record DetailVo(
            Long id,
            String name,
            int age,
            LocalDateTime createdAt,
            LocalDateTime updatedAt
    ) {}
}
```

### 왜 분리하는가

**InsertVo ≠ ListVo ≠ DetailVo:**
- `InsertVo`: id, createdAt 없음 (서버가 생성)
- `ListVo`: 목록에 필요한 최소 필드만 (성능)
- `DetailVo`: 상세 조회용 모든 필드

한 VO로 다 쓰면:
- 입력 시 id 받는 척 (보안 문제)
- 목록 조회 시 불필요한 필드 다 담음 (성능)
- 필드 의미가 모호

## 페이징 VO 표준 패턴

### 구조

```java
@Getter
@Setter
public static class SearchVo {
    // 검색 조건
    private String project;
    private String branch;
    private String committer;

    // 페이징 입력
    private int page = 1;
    private int size = 20;

    // 페이징 결과
    private int totalCount;
    private int totalPage;
    private List<ListVo> body;

    public void calcPaging(int totalCount) {
        this.totalCount = totalCount;
        this.totalPage = (int) Math.ceil((double) totalCount / size);
    }

    public int offset() {
        return (page - 1) * size;
    }

    public int limit() {
        return size;
    }

    public void setBody(List<ListVo> body) {
        this.body = body;
    }
}
```

### 사용

```java
// Controller
@GetMapping
public PersonVo.SearchVo search(PersonVo.SearchVo paging) {
    return personService.search(paging);
}

// Service
public PersonVo.SearchVo search(PersonVo.SearchVo paging) {
    return personDao.selectBy(paging);
}

// DAO
public PersonVo.SearchVo selectBy(PersonVo.SearchVo paging) {
    int count = dsl.fetchCount(...);
    if (count > 0) {
        paging.calcPaging(count);
        List<PersonVo.ListVo> list = dsl.selectFrom(PERSON)
                .offset(paging.offset())
                .limit(paging.limit())
                .fetchInto(PersonVo.ListVo.class);
        paging.setBody(list);
    }
    return paging;
}
```

페이징 VO가 자기 상태(검색 조건 + 결과)를 다 담음 → 한 객체가 왔다 갔다 함.

## VO에 Bean Validation을 붙일까?

### 안 붙이는 경우 (권장)
- 검증은 Domain Primitive가 책임
- VO는 순수 데이터 운반

### 붙이는 경우
- 진입점에서 빠른 실패 원할 때
- 도메인 도달 전 차단 (네트워크/JSON 파싱 비용 절감)
- 단, **룰 중복 발생** 의식 (Domain Primitive와 VO Bean Validation 양쪽에 같은 룰)

### 절충안 — 상수 공유
```java
public class PersonVo {
    public record InsertVo(
            @NotBlank String name,
            @Min(Age.MIN) @Max(Age.MAX) int age   // ← 상수 참조
    ) {}
}
```

`Age.MIN`, `Age.MAX` 가 단일 진실 원천. VO는 그 값을 참조만.

## 패키지 위치

```
domain/
├── Person.java              # Entity
├── Age.java                 # Domain Primitive
├── PersonName.java          # Domain Primitive
└── dto/
    └── PersonVo.java        # 도메인 VO 그룹
```

또는 도메인 공유:
```
domain/
└── git/
    └── GitVo.java           # Insert + Search + List 통합
```

## VO 명명 컨벤션

| 용도 | 이름 | 예시 |
|------|------|------|
| 입력 (생성) | `{Name}Vo.InsertVo` | `PersonVo.InsertVo` |
| 입력 (수정) | `{Name}Vo.UpdateVo` | `PersonVo.UpdateVo` |
| 검색 (조건+페이징) | `{Name}Vo.SearchVo` | `PersonVo.SearchVo` |
| 목록 응답 | `{Name}Vo.ListVo` | `PersonVo.ListVo` |
| 상세 응답 | `{Name}Vo.DetailVo` | `PersonVo.DetailVo` |
| 또는 단순 통합 | `{Name}Vo` | `PersonVo` (단일 사용) |

## 안티 패턴

### ❌ 만능 VO
```java
public class PersonVo {
    private Long id;          // 입력에선 불필요
    private String name;
    private int age;
    private LocalDateTime createdAt;  // 입력에선 불필요
    private List<PersonVo> children;  // 응답에서만 필요
    // → 어떤 컨텍스트에선 일부만 의미 있음. 혼란.
}
```

### ❌ Entity를 VO로 사용
```java
@PostMapping
public Person save(@RequestBody Person person) { ... }
// → Entity를 외부에 노출. 의존성 방향 위반. JPA 어노테이션이 클라이언트에 보임.
```

### ❌ VO에 비즈니스 로직
```java
public class PersonVo {
    public boolean isAdult() {
        return age >= 19;
    }
    public PersonVo withIncrementedAge() {
        return new PersonVo(name, age + 1);
    }
}
// → VO는 데이터 운반만. 행동은 Domain Primitive 또는 Entity에.
```

### ❌ Insert/Update/Search/List 한 VO로
```java
public class PersonVo {
    private Long id;          // Insert엔 null, Update/Search/List엔 값
    private String name;
    private Integer age;      // List엔 값, Search엔 조건 (혼동)
}
// → 같은 필드가 다른 의미. 분리 필요.
```
