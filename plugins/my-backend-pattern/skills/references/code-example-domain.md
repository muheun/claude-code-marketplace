# Code Example — Domain (Person + Age + PersonName + PersonVo)

도메인 프리미티브 패턴이 적용된 Person 모듈 표준 코드.
새 도메인 객체 작성 시 이 구조를 그대로 따른다.

## 컨텍스트

- 프로젝트: base_project2
- 도메인: 사람 (Person) — 이름과 나이로 식별
- 적용 패턴: 도메인 프리미티브 (Age, PersonName) + JPA validate-only

## 1. Age (Domain Primitive — 정수)

```java
package kr.co.fixelsoft.baseproject.core.person.domain;

import com.fasterxml.jackson.annotation.JsonValue;
import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import kr.co.fixelsoft.baseproject.core.exception.DomainValidationException;
import lombok.AccessLevel;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Embeddable
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@EqualsAndHashCode
public class Age {
    public static final int MIN = 1;
    public static final int MAX = 200;

    @Column(name = "age", nullable = false, comment = "나이")
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

### 학습 포인트
- `@Embeddable` — JPA Entity의 `@Embedded` 필드로 사용 가능
- `@NoArgsConstructor(PROTECTED)` — JPA reflection 인스턴스화 (외부 호출 차단)
- `@EqualsAndHashCode` — Value Object 핵심 (값 같으면 같은 객체)
- `MIN/MAX` 상수 외부 노출 — Service에서 메시지 생성 시 활용
- **`@Column(name = "age", nullable = false, comment = "나이")`** — DB 컬럼명/제약/의미 한 곳에 (Jakarta Persistence 3.2+ 표준)
- 생성자 검증 — 잘못된 값 인스턴스화 차단
- `@JsonValue` — JSON 직렬화 시 `{"value": 30}` 대신 `30`
- `value()` 메서드 — `getValue()` 대신, records 스타일

## 2. PersonName (Domain Primitive — 문자열)

```java
package kr.co.fixelsoft.baseproject.core.person.domain;

import com.fasterxml.jackson.annotation.JsonValue;
import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import kr.co.fixelsoft.baseproject.core.exception.DomainValidationException;
import lombok.AccessLevel;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Embeddable
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@EqualsAndHashCode
public class PersonName {
    public static final int MAX_LENGTH = 50;

    @Column(name = "name", nullable = false, length = MAX_LENGTH, comment = "이름")
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

### 학습 포인트
- 두 개의 검증 (null/blank + 길이) — 각각 명확한 메시지
- `MAX_LENGTH` 상수 외부 노출
- 그 외 패턴은 Age와 동일

## 3. Person (Entity — JPA validate-only)

```java
package kr.co.fixelsoft.baseproject.core.person.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Entity
@Table
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Person {
    @Id
    @Column(nullable = false, comment = "PK")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Embedded
    private PersonName name;  // comment는 PersonName.value의 @Column에 정의

    @Embedded
    private Age age;          // comment는 Age.value의 @Column에 정의

    private Person(PersonName name, Age age) {
        this.name = name;
        this.age = age;
    }

    public static Person create(String name, int age) {
        return new Person(new PersonName(name), new Age(age));
    }
}
```

### 학습 포인트
- `@Entity` + `@Table` — JPA 스키마 매핑
- `@NoArgsConstructor(PROTECTED)` — JPA용
- `@SuperBuilder` 없음 — 빌더로 검증 우회 차단
- `private` 생성자 — 외부 직접 생성 차단
- **직접 필드는 `@Column(comment = "...")` 필수** (Jakarta Persistence 3.2+ 표준)
- **`@Embedded` 필드는 Embeddable 내부 `@Column` 의 comment 자동 사용** — Entity 측 별도 선언 X
- `Person.create(String, int)` — **원시 타입 받음**. 외부(Service)는 Domain Primitive 타입 몰라도 됨
- 내부에서 `new PersonName(name)`, `new Age(age)` — 검증 자동 발생
- DTO/VO **import 안 함** — 의존성 방향 정상

## 4. PersonVo (DTO — 순수 데이터 운반)

```java
package kr.co.fixelsoft.baseproject.core.person.domain.dto;

import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class PersonVo {
    private Long id;
    private String name;
    private int age;
}
```

### 학습 포인트
- **검증 코드 없음** — Domain Primitive에 위임
- `valid()` 메서드 없음
- Bean Validation 어노테이션 없음 (선택사항)
- `id`는 `Long` (primitive `long` 아님 — null 표현 가능)
- `@NoArgsConstructor(PROTECTED)` + `@AllArgsConstructor(PRIVATE)` — Jackson 역직렬화 지원

## 5. DomainValidationException (도메인 예외)

```java
package kr.co.fixelsoft.baseproject.core.exception;

public class DomainValidationException extends RuntimeException {
    public DomainValidationException(String message) {
        super(message);
    }

    public DomainValidationException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

## 6. GlobalExceptionHandler (선택, 그러나 강력 권장)

```java
package kr.co.fixelsoft.baseproject.core.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(DomainValidationException.class)
    public ResponseEntity<Map<String, Object>> handleDomainValidation(DomainValidationException e) {
        log.warn("Domain validation failed: {}", e.getMessage());
        return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", e.getMessage()
        ));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGeneric(Exception e) {
        log.error("Unexpected error", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "success", false,
                "message", "서버 오류가 발생했습니다"
        ));
    }
}
```

## 7. PersonService (검증 코드 없음)

```java
package kr.co.fixelsoft.baseproject.core.person.service;

import kr.co.fixelsoft.baseproject.core.person.dao.PersonDao;
import kr.co.fixelsoft.baseproject.core.person.domain.Person;
import kr.co.fixelsoft.baseproject.core.person.domain.dto.PersonVo;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class PersonService {

    private final PersonDao personDao;

    public boolean save(PersonVo vo) {
        return personDao.save(Person.create(vo.getName(), vo.getAge())).getId() > 0;
    }
}
```

### 학습 포인트
- 검증 코드 0줄
- 한 줄 짜리 메서드 — 비즈니스 로직만
- `Person.create(vo.getName(), vo.getAge())` — Domain Primitive 자동 생성 + 검증

## 8. PersonController

```java
package kr.co.fixelsoft.baseproject.core.person.controller;

import kr.co.fixelsoft.baseproject.core.person.domain.dto.PersonVo;
import kr.co.fixelsoft.baseproject.core.person.service.PersonService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

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

### 학습 포인트
- `@RequestBody` 필수 — JSON body 받기
- Service 호출 한 줄
- `Map.of("success", ...)` 응답

## 전체 흐름 — 요청부터 저장까지

```
1. 클라이언트가 POST { "name": "김태윤", "age": 30 }
2. PersonController.save()
   → @RequestBody로 PersonVo 바인딩
3. PersonService.save(vo)
   → Person.create(vo.getName(), vo.getAge()) 호출
4. Person.create("김태윤", 30)
   → new PersonName("김태윤") — 검증 통과
   → new Age(30) — 검증 통과
   → Person 인스턴스 생성
5. personDao.save(person)
   → DB에 저장
6. 응답: { "success": true }
```

## 검증 실패 시 흐름

```
클라이언트가 POST { "name": "", "age": 250 }
1. PersonController.save() → @RequestBody 바인딩
2. PersonService.save(vo) → Person.create("", 250)
3. new PersonName("")
   → DomainValidationException("이름은 필수") throw
4. GlobalExceptionHandler 가 잡음
5. 응답: HTTP 400 { "success": false, "message": "이름은 필수" }
```

`age`가 250이어도 PersonName 검증에서 먼저 실패 (호출 순서). 둘 다 잘못이면 첫 번째 실패만 보고됨.
모든 필드 한꺼번에 보고 원하면 Bean Validation을 VO에 추가 (트레이드오프: 룰 중복).

## 새 도메인 객체 작성 시 체크리스트

- [ ] Domain Primitive에 `@Embeddable`, `@NoArgsConstructor(PROTECTED)`, `@EqualsAndHashCode`, `@JsonValue`
- [ ] Domain Primitive 생성자에서 `DomainValidationException` throw
- [ ] Entity에 `@SuperBuilder` 또는 public 빌더 없음
- [ ] Entity 생성자 private + 정적 팩토리 (`create`)
- [ ] Entity의 `create()`는 원시 타입 받음 (Domain Primitive 타입 노출 X)
- [ ] Entity가 dto/vo 패키지 import 안 함
- [ ] VO는 검증 코드 없음 (순수 데이터)
- [ ] Service는 비즈니스 로직만 (검증 코드 없음)
- [ ] Controller에 `@RequestBody`
- [ ] GlobalExceptionHandler 등록 (`DomainValidationException` 처리)
