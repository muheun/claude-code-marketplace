# Domain Primitive Pattern — 핵심

## 핵심 아이디어

**"검증 룰을 코드 위치(Service/DTO/Entity)가 아니라 타입 시스템에 새긴다."**

`Age`, `Email`, `Money` 같은 타입 자체가 룰을 가짐. 잘못된 값으로는 **인스턴스화 자체가 불가능**.

## 왜 만드는가

### 검증 위치 문제 해결

같은 룰이 여러 위치에 중복되는 문제 (Service if문 + DTO valid + Entity invariant) 를 단번에 해결.
타입을 사용하는 모든 곳이 자동으로 검증됨.

### Persistence Ignorance

JPA Entity가 사라져도 Domain Primitive는 살아남음. 영속성 기술 변화에 강건.

### 컴파일러 강제

`int age` 대신 `Age age` → 다른 int (productId 등)와 혼동 불가능. 컴파일 타임 보호.

## 표준 코드 패턴

### 기본 구조 (Age 예시)

```java
package me.example.domain;

import com.fasterxml.jackson.annotation.JsonValue;
import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.AccessLevel;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Embeddable
@NoArgsConstructor(access = AccessLevel.PROTECTED)  // JPA용
@EqualsAndHashCode                                   // Value Object 핵심
public class Age {
    public static final int MIN = 1;
    public static final int MAX = 200;

    @Column(name = "age")
    private int value;

    public Age(int value) {
        if (value < MIN || value > MAX)
            throw new DomainValidationException("나이 범위는 " + MIN + "~" + MAX);
        this.value = value;
    }

    @JsonValue
    public int value() { return value; }
}
```

### 핵심 요소

| 요소 | 이유 |
|------|------|
| `@Embeddable` | JPA Entity의 `@Embedded` 필드로 사용 가능 |
| `@NoArgsConstructor(PROTECTED)` | JPA reflection 인스턴스화용 (외부 호출 차단) |
| `@EqualsAndHashCode` | Value Object — 값 같으면 같은 객체 |
| `public static final MIN/MAX` | 룰 상수 외부 노출 (Service에서 메시지 만들 때 활용) |
| `@Column(name = "age")` | DB 컬럼명 명시 (필드명 `value`와 다름) |
| 생성자 검증 | 잘못된 값 인스턴스화 차단 |
| `@JsonValue` | JSON 직렬화 시 `{"value": 30}` 대신 `30` |
| `value()` 메서드 | `getValue()` 대신. records 스타일 |

## String 기반 Domain Primitive (PersonName 예시)

```java
@Embeddable
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@EqualsAndHashCode
public class PersonName {
    public static final int MAX_LENGTH = 50;

    @Column(name = "name")
    private String value;

    public PersonName(String name) {
        if (name == null || name.isBlank())
            throw new DomainValidationException("이름은 필수");
        if (name.length() > MAX_LENGTH)
            throw new DomainValidationException("이름 최대 " + MAX_LENGTH + "자");
        this.value = name;
    }

    @JsonValue
    public String value() { return value; }
}
```

## Entity에서 사용

```java
@Entity
@Table
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Person {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Embedded
    private PersonName name;

    @Embedded
    private Age age;

    private Person(PersonName name, Age age) {
        this.name = name;
        this.age = age;
    }

    public static Person create(String name, int age) {
        return new Person(new PersonName(name), new Age(age));
    }
}
```

핵심:
- `Person.create()` 가 원시 타입(`String`, `int`) 받아서 내부에서 Domain Primitive 생성
- 외부(Service)는 Domain Primitive 타입 몰라도 됨 (캡슐화)
- 잘못된 값이 들어오면 Domain Primitive 생성자에서 즉시 예외

## 언제 만들고 언제 안 만드는가 — 선별 기준

### ✅ 만들어야 함
- 검증 룰이 명확함 (range, format, length)
- 도메인 행동 메서드를 가질 수 있음 (`age.isAdult()`, `email.domain()`)
- 다른 원시 타입과 혼동 위험 (`Long userId` vs `Long productId`)
- 비즈니스적 의미 강함 (`Money`, `Coordinate`, `IpAddress`)

### ❌ 만들지 마라
- 단순 String/Long으로 충분, 검증 X (`description`, `memo` 같은 필드)
- 그냥 식별자 (`@Id Long id` 같은)
- 외부 시스템 ID (변환 책임 없음)

**원칙**: 모든 필드에 적용은 과잉. 의미 있는 필드만 골라서.

## 다중 진입점 시나리오

진입점 4개 추가될 때:
- REST POST → PersonVo
- Kafka message → PersonEventMessage
- Batch CSV → PersonCsvRow
- Internal API → PersonInternalRequest

각 어댑터는 자기 형식 검증 후 **원시 타입(`String`, `int`)으로** `Person.create()` 호출.
**Entity는 어떤 어댑터도 모름.** Domain Primitive 생성자에서 결국 동일하게 검증됨.

```java
// REST
person = Person.create(vo.getName(), vo.getAge());

// Kafka
person = Person.create(msg.getName(), msg.getAge());

// Batch
person = Person.create(row.getName(), row.getAge());
```

→ 4개 어댑터, **검증 룰은 단 하나**. (Age, PersonName 안에)

## JPA 통합 시 주의사항

### final 필드 못 씀
JPA가 reflection으로 객체 생성 → setter 또는 field 직접 set 필요.
`final` 빼고 `protected` 생성자로 외부 우회 막음. 트레이드오프 받아들임.

### no-args 생성자 필수
`@NoArgsConstructor(access = AccessLevel.PROTECTED)` 로 외부엔 노출 안 하되 JPA만 사용 가능.

### equals/hashCode 필수
Value Object의 본질. JPA Embedded 비교, 컬렉션 동작에 영향.
`@EqualsAndHashCode` (Lombok) 또는 직접 구현.

### @JsonValue 권장
없으면 `{"name": {"value": "김태윤"}}` 같이 직렬화됨. `@JsonValue` 붙이면 `{"name": "김태윤"}`.

## Persistence Ignorance — JPA 제거 시뮬레이션

JPA → MyBatis로 갈아탄다고 가정:

```java
// Age.java — 한 글자도 안 바뀜
@Embeddable                    // ← 이것만 빼면 됨
public final class Age {
    public Age(int value) {
        if (value < MIN || value > MAX)
            throw new DomainValidationException(...);
        this.value = value;
    }
}

// PersonRecord.java (MyBatis 결과 매핑용 POJO)
public class PersonRecord {
    private Long id;
    private PersonName name;     // 그대로 사용
    private Age age;              // 그대로 사용

    public static PersonRecord create(PersonName name, Age age) { ... }
}
```

**검증 코드 한 줄도 안 바뀜.** 영속성 독립성 확보.

## 안티 패턴 — Domain Primitive로 위장하지만 망친 경우

### ❌ 검증 없는 단순 wrapper
```java
public class Age {
    private int value;
    public Age(int value) { this.value = value; }  // 검증 없음
    public int getValue() { return value; }
}
```
→ 그냥 `int` 보다 나쁨. 클래스만 늘림. 의미 없음.

### ❌ Setter 노출
```java
public class Age {
    private int value;
    public void setValue(int value) {
        if (value < 1) throw ...;
        this.value = value;
    }
}
```
→ `new Age()` 후 setter 안 부르고 사용하면 잘못된 상태로 존재. 불변식 깨짐.

### ❌ public 생성자 + 외부에서 builder 노출
```java
@Builder  // ← public builder 노출
public class Age {
    private int value;
    public Age(int value) { /* 검증 */ }
}
// → Age.builder().value(-1).build();  검증 우회 가능
```

## Origin

이 패턴은 검증 위치 고민에서 출발한 토론을 통해 정립.
"검증을 어디에 둘 것인가?"가 잘못된 질문이고, **"어떤 타입이 잘못된 값을 거부하는가?"** 가 올바른 질문임을 발견.
