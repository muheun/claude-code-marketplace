# Anti-Patterns — 흔한 실수와 회피법

## 1. 같은 검증 룰을 여러 곳에 중복 정의

### ❌ 나쁜 예
```java
// PersonService
if (vo.getName() == null || vo.getName().isEmpty()) throw ...;
if (vo.getAge() <= 0 || vo.getAge() > 200) throw ...;

// PersonVo
public void valid() {
    if (name == null || name.isEmpty()) throw ...;
    if (age <= 0 || age > 200) throw ...;
}

// Person
public void valid() {
    if (name == null || name.isEmpty()) throw ...;
    if (age <= 0 || age > 200) throw ...;
}
```

**문제**: 룰이 3곳. 변경 시 한 곳 까먹을 확률 100%.

### ✅ 좋은 예
Domain Primitive로 룰을 한 곳에:
```java
public class Age {
    public Age(int value) {
        if (value < 1 || value > 200) throw new DomainValidationException(...);
    }
}
// → Person, PersonVo, Service 어디서도 검증 코드 없음. Age 사용만으로 자동.
```

## 2. @SuperBuilder로 검증 우회 가능

### ❌ 나쁜 예
```java
@SuperBuilder
public class Person {
    public static Person from(PersonVo vo) {
        vo.valid();  // 여기서 검증
        return Person.builder()...build();
    }
}
// → 누군가 Person.builder().name(null).age(-1).build() 직접 호출 가능. 검증 우회.
```

### ✅ 좋은 예
빌더 노출 안 함, private 생성자, 정적 팩토리:
```java
public class Person {
    private Person(PersonName name, Age age) {  // private
        this.name = name;
        this.age = age;
    }

    public static Person create(String name, int age) {
        return new Person(new PersonName(name), new Age(age));
    }
}
```

## 3. Entity가 DTO/VO를 import

### ❌ 나쁜 예
```java
// Person.java
import me.example.domain.dto.PersonVo;  // ← 안쪽이 바깥쪽 import. 의존성 역방향.

public class Person {
    public static Person from(PersonVo vo) { ... }  // Entity가 DTO 알게 됨
}
```

**문제**:
- Clean Architecture 의존성 방향 위반
- 다중 진입점 추가 시 `from(KafkaMsg)`, `from(BatchRow)` 가 Entity에 누적됨
- Entity가 N개 어댑터를 알게 됨

### ✅ 좋은 예
Entity는 원시 타입 또는 Domain Primitive만 받음:
```java
public class Person {
    public static Person create(String name, int age) {
        return new Person(new PersonName(name), new Age(age));
    }
}

// Service에서 변환
person = Person.create(vo.getName(), vo.getAge());      // REST
person = Person.create(msg.getName(), msg.getAge());    // Kafka
person = Person.create(row.getName(), row.getAge());    // Batch
```

## 4. RuntimeException 직접 throw

### ❌ 나쁜 예
```java
throw new RuntimeException("나이 범위 1~200");
```

**문제**:
- 시스템 에러(NullPointerException 등)와 도메인 검증 실패 구분 불가
- GlobalExceptionHandler에서 잡기 어려움 (모든 RuntimeException 잡으면 진짜 시스템 에러도 400 응답)

### ✅ 좋은 예
도메인 의미 가진 예외 타입 정의:
```java
public class DomainValidationException extends RuntimeException {
    public DomainValidationException(String message) { super(message); }
}

throw new DomainValidationException("나이 범위 1~200");

// GlobalExceptionHandler에서:
@ExceptionHandler(DomainValidationException.class)
public ResponseEntity<?> handle(DomainValidationException e) {
    return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
}
```

## 5. JpaRepository로 CRUD 처리

### ❌ 나쁜 예
```java
public interface PersonRepository extends JpaRepository<Person, Long> {
    List<Person> findByName(String name);
}
// → JPA가 모든 쿼리 처리. validate-only 원칙 위반.
```

**문제**:
- JPA의 자동 쿼리 생성으로 복잡한 쿼리 추적 어려움
- N+1 문제 잠복
- Native query 섞이면 일관성 깨짐

### ✅ 좋은 예
jOOQ로 명시적 쿼리:
```java
@Repository
@RequiredArgsConstructor
public class PersonDao {
    private final DSLContext dsl;

    public List<Person> selectByName(String name) {
        return dsl.selectFrom(PERSON)
                .where(PERSON.NAME.eq(name))
                .fetchInto(Person.class);
    }
}
// JpaRepository 정의 X. JPA Entity는 ddl-auto: validate 용으로만.
```

## 6. Bean Validation만으로 도메인 무결성 보장 시도

### ❌ 부족한 예
```java
public class PersonVo {
    @NotBlank private String name;
    @Min(1) @Max(200) private int age;
}

public class Person {
    private String name;
    private int age;
    // 불변식 없음
}
```

**문제**:
- Bean Validation은 **DTO 진입점에만** 적용
- Service나 Kafka가 Person 직접 만들면 검증 우회
- "200→150 변경 시 두 곳 다 고쳐야 하는" 중복 문제 잔존

### ✅ 좋은 예
Domain Primitive에 룰을 두고, DTO는 데이터 운반만:
```java
public class PersonVo {
    private String name;  // Bean Validation 안 붙여도 됨
    private int age;
}

public class Person {
    @Embedded private PersonName name;  // 룰 보장
    @Embedded private Age age;           // 룰 보장
}
```

## 7. Service에서 if문으로 검증

### ❌ 나쁜 예
```java
@Service
public class PersonService {
    public boolean save(PersonVo vo) {
        if (vo.getName() == null) throw ...;
        if (vo.getAge() <= 0) throw ...;
        // ... 검증 10줄
        // ... 비즈니스 로직 5줄
        return personDao.save(...);
    }
}
```

**문제**:
- Service가 검증 + 비즈니스를 다 짊어짐
- 비즈니스 로직 가독성 ↓
- 다른 진입점이 같은 검증 코드 반복

### ✅ 좋은 예
Service는 비즈니스 로직만:
```java
@Service
public class PersonService {
    public boolean save(PersonVo vo) {
        return personDao.save(Person.create(vo.getName(), vo.getAge())).getId() > 0;
    }
}
// → 검증은 Person.create 내부의 Domain Primitive에서 자동 발생
```

## 8. DAO 메서드명 컨벤션 위반

### ❌ 일관성 없음
```java
public interface PersonDao {
    Person findById(Long id);          // JPA 스타일
    Person save(Person p);              // JPA 스타일
    List<Person> getByAge(int age);    // 또 다른 스타일
}
```

### ✅ jOOQ 컨벤션 통일
```java
public class PersonDao {
    public Person selectById(Long id) { ... }
    public boolean insert(Person p) { ... }
    public void insertBatch(List<Person> list) { ... }
    public Person updateBy(Person p) { ... }
    public boolean deleteBy(Long id) { ... }
    public List<Person> selectByAge(int age) { ... }
}
```

| 동작 | 메서드명 prefix |
|------|----------------|
| 단일 조회 | `selectBy{조건}` |
| 다건 조회 | `selectBy{조건}` (반환 타입으로 구분) |
| 단건 입력 | `insert` |
| 다건 입력 | `insertBatch` |
| 수정 | `updateBy{조건}` |
| 삭제 | `deleteBy{조건}` |
| 카운트 | `countBy{조건}` |

## 9. Controller에 `@RequestBody` 누락

### ❌ 나쁜 예
```java
@PostMapping
public Map<String, Object> save(PersonVo vo) {  // @RequestBody 없음
    return Map.of("success", personService.save(vo));
}
```

**문제**: JSON body 못 받음. Spring이 query parameter나 form-data로 바인딩 시도.

### ✅ 좋은 예
```java
@PostMapping
public Map<String, Object> save(@RequestBody PersonVo vo) {
    return Map.of("success", personService.save(vo));
}
```

## 10. Domain Primitive 남발

### ❌ 과잉
```java
public class Memo { private String value; ... }       // 검증 없음
public class Description { private String value; ... } // 검증 없음
public class Comment { private String value; ... }     // 검증 없음
// → 그냥 String이면 충분한 필드까지 클래스화. 코드만 늘어남.
```

### ✅ 선별
- 검증 룰 명확하거나 도메인 행동 가능한 필드만 Domain Primitive로
- 단순 데이터는 String/int 그대로 사용

## 11. 컬럼 Comment 누락

### ❌ 나쁜 예
```java
@Entity
public class Person {
    @Id @GeneratedValue
    private Long id;            // ← 무엇의 ID? Comment 없음

    @Embedded
    private PersonName name;     // ← 컬럼 의미 미상

    @Embedded
    private Age age;             // ← 컬럼 의미 미상
}
```

```sql
CREATE TABLE person (
    id    BIGINT       NOT NULL AUTO_INCREMENT,
    name  VARCHAR(50)  NOT NULL,
    age   INT          NOT NULL,
    PRIMARY KEY (id)
);
-- DB 보면 의미 알 수 없음. 코드 찾아봐야 함.
```

**문제**:
- DBA, BI 분석가, 신규 입사자가 코드 안 보고는 컬럼 의미 모름
- BI 도구(Redash, Metabase)가 "id, name, age"만 표시
- 코드 사라지면 DB만 남는데 의미 손실
- 회사 자산화 못 됨

### ❌ deprecated 어노테이션 사용
```java
import org.hibernate.annotations.Comment;  // ← Spring Boot 4 / Hibernate 7 부터 deprecated

@Comment("PK")
private Long id;
```

→ Jakarta Persistence 3.2 표준 등장 이후 비권장.

### ✅ 좋은 예 — 표준 `@Column(comment = ...)` 사용
```java
import jakarta.persistence.Column;

@Entity
public class Person {
    @Id
    @Column(nullable = false, comment = "PK")
    @GeneratedValue
    private Long id;

    @Embedded
    private PersonName name;  // comment는 PersonName 내부 @Column에

    @Embedded
    private Age age;          // comment는 Age 내부 @Column에
}

@Embeddable
public class PersonName {
    @Column(name = "name", nullable = false, length = 50, comment = "이름")
    private String value;
}

@Embeddable
public class Age {
    @Column(name = "age", nullable = false, comment = "나이")
    private int value;
}
```

```sql
CREATE TABLE person (
    id    BIGINT       NOT NULL AUTO_INCREMENT COMMENT 'PK',
    name  VARCHAR(50)  NOT NULL                COMMENT '이름',
    age   INT          NOT NULL                COMMENT '나이',
    PRIMARY KEY (id)
) COMMENT='사람';
```

**원칙**:
- JPA `@Column(comment = "...")` (Jakarta Persistence 3.2+ 표준) + Flyway `COMMENT` **양쪽 모두 필수**
- `@Embedded` 필드는 Embeddable 내부 `@Column` 에 comment (Entity 쪽엔 필요 X)
- `org.hibernate.annotations.Comment` 는 deprecated — 사용 금지

## Quick Validation Checklist

코드 작성 후 빠른 점검:

- [ ] 같은 검증 룰이 두 곳 이상에 있는가? → Domain Primitive로 통합
- [ ] `RuntimeException` 직접 throw하는가? → `DomainValidationException` 등으로
- [ ] Entity가 dto/vo 패키지를 import하는가? → 의존성 방향 수정
- [ ] `@SuperBuilder` 또는 public 빌더가 도메인 객체에 있는가? → 제거 또는 private화
- [ ] `JpaRepository` 정의했는가? → jOOQ DAO로 전환
- [ ] Service에 if문 검증 5줄 이상 있는가? → Domain Primitive로 옮김
- [ ] DAO 메서드명이 `find`, `save` 같은 JPA 스타일인가? → jOOQ 컨벤션으로
- [ ] Controller에 `@RequestBody` 있는가?
- [ ] Domain Primitive에 `@EqualsAndHashCode`, `@JsonValue` 있는가?
- [ ] **모든 Entity 필드에 `@Comment` 있는가?**
- [ ] **모든 Flyway DDL 컬럼에 `COMMENT '...'` 있는가?**
