# Exception Handling — DomainValidationException + GlobalExceptionHandler

## 예외 타입 계층

```
RuntimeException (java)
└── DomainValidationException        # 도메인 검증 실패 (400)
    ├── DuplicateException            # 중복 데이터
    ├── NotFoundException             # 존재하지 않음
    ├── ForbiddenException            # 권한 없음
    └── ... (도메인별 의미 가진 예외)
```

## DomainValidationException 정의

```java
package me.example.exception;

public class DomainValidationException extends RuntimeException {
    public DomainValidationException(String message) {
        super(message);
    }

    public DomainValidationException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

### 왜 `RuntimeException` 직접 throw 금지인가

```java
// ❌ 나쁜 예
throw new RuntimeException("나이 범위 1~200");
```

**문제:**
- DB 연결 실패도 RuntimeException
- NPE도 RuntimeException
- `@ExceptionHandler(RuntimeException.class)` 로 잡으면 진짜 시스템 에러도 400 응답
- 도메인 검증 실패 ≠ 시스템 에러

```java
// ✅ 좋은 예
throw new DomainValidationException("나이 범위 1~200");
```

→ GlobalExceptionHandler에서 도메인 검증만 골라 400 응답.

## Domain Primitive에서 사용

```java
public class Age {
    public static final int MIN = 1;
    public static final int MAX = 200;

    public Age(int value) {
        if (value < MIN || value > MAX)
            throw new DomainValidationException("나이 범위는 " + MIN + "~" + MAX);
        this.value = value;
    }
}
```

## GlobalExceptionHandler

### 기본 구조

```java
package me.example.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 도메인 검증 실패 → 400
    @ExceptionHandler(DomainValidationException.class)
    public ResponseEntity<Map<String, Object>> handleDomainValidation(DomainValidationException e) {
        log.warn("Domain validation failed: {}", e.getMessage());
        return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", e.getMessage()
        ));
    }

    // Bean Validation 실패 → 400
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleBeanValidation(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(err -> err.getField() + ": " + err.getDefaultMessage())
                .collect(Collectors.joining(", "));
        return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "message", message
        ));
    }

    // 데이터 없음 → 404
    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleNotFound(NotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of(
                "success", false,
                "message", e.getMessage()
        ));
    }

    // 권한 없음 → 403
    @ExceptionHandler(ForbiddenException.class)
    public ResponseEntity<Map<String, Object>> handleForbidden(ForbiddenException e) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of(
                "success", false,
                "message", e.getMessage()
        ));
    }

    // 그 외 시스템 에러 → 500 (마지막 fallback)
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

## 예외 응답 형식

### 표준 응답
```json
{
    "success": false,
    "message": "나이 범위는 1~200"
}
```

### 필드별 에러 (Bean Validation 시)
```json
{
    "success": false,
    "message": "name: 필수, age: 1~200 범위"
}
```

또는 더 상세하게:
```json
{
    "success": false,
    "message": "검증 실패",
    "errors": {
        "name": "필수",
        "age": "1~200 범위"
    }
}
```

## 도메인별 예외 정의 패턴

### NotFoundException
```java
public class NotFoundException extends RuntimeException {
    public NotFoundException(String entityName, Object id) {
        super(String.format("%s를 찾을 수 없습니다 (id=%s)", entityName, id));
    }
}

// 사용
public Person getById(Long id) {
    Person person = personDao.selectById(id);
    if (person == null) throw new NotFoundException("Person", id);
    return person;
}
```

### DuplicateException
```java
public class DuplicateException extends RuntimeException {
    public DuplicateException(String fieldName, Object value) {
        super(String.format("이미 존재하는 %s입니다: %s", fieldName, value));
    }
}

// 사용
if (personDao.existsByEmail(email)) {
    throw new DuplicateException("이메일", email);
}
```

### ForbiddenException
```java
public class ForbiddenException extends RuntimeException {
    public ForbiddenException(String message) {
        super(message);
    }
}

// 사용
if (!post.isOwnedBy(userId)) {
    throw new ForbiddenException("작성자만 삭제할 수 있습니다");
}
```

## 로깅 정책

| 예외 타입 | 로그 레벨 | 이유 |
|----------|----------|------|
| `DomainValidationException` | `WARN` 또는 안 함 | 사용자 입력 실수. 시스템 문제 아님 |
| `Bean Validation` | `WARN` 또는 안 함 | 사용자 입력 실수 |
| `NotFoundException` | `INFO` 또는 안 함 | 일상적 |
| `DuplicateException` | `INFO` 또는 안 함 | 일상적 |
| `Exception` (시스템) | `ERROR` (스택트레이스) | 진짜 문제 |

### 안티 패턴
- ❌ DomainValidationException 마다 ERROR 로그 → 알림 노이즈
- ❌ 시스템 예외에 스택트레이스 안 찍기 → 디버그 불가능

## 트랜잭션 롤백과의 상호작용

Spring 기본:
- `RuntimeException` (`DomainValidationException` 포함) → 자동 롤백
- 체크 예외 → 롤백 X (별도 설정 필요)

도메인 예외는 모두 `RuntimeException` 상속하므로 롤백 자동.

## 클라이언트와의 약속

API 응답 일관성:
- HTTP 상태 코드: 400/403/404/500 명확
- Body 형식: 항상 `success`, `message` 포함
- 클라이언트는 `success: false` 체크 + `message` 표시 가능

이 약속이 깨지면 클라이언트 코드가 `try-catch` 지옥. GlobalExceptionHandler가 그 약속 강제.

## 안티 패턴

### ❌ Controller에서 try-catch
```java
@PostMapping
public Map<String, Object> save(@RequestBody PersonVo vo) {
    try {
        return Map.of("success", personService.save(vo));
    } catch (DomainValidationException e) {
        return Map.of("success", false, "message", e.getMessage());
    }
}
// → GlobalExceptionHandler가 처리할 일을 Controller마다 반복
```

### ❌ Service에서 generic catch
```java
public boolean save(PersonVo vo) {
    try {
        return personDao.insert(Person.create(...)) > 0;
    } catch (Exception e) {
        return false;  // 무슨 에러인지 모름. 트랜잭션도 안 됨.
    }
}
```

### ❌ 의미 없는 메시지
```java
throw new DomainValidationException("Invalid");  // 무엇이 invalid?
throw new DomainValidationException("Error");    // 무슨 에러?
```

### ✅ 명확한 메시지
```java
throw new DomainValidationException("나이 범위는 " + MIN + "~" + MAX);
throw new DomainValidationException("이메일 형식이 올바르지 않습니다");
throw new DuplicateException("이메일", email);
```
