# Web Layer — Controller + Service

## Controller

### 기본 구조

```java
package me.example.controller;

import lombok.RequiredArgsConstructor;
import me.example.domain.dto.PersonVo;
import me.example.service.PersonService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/persons")
@RequiredArgsConstructor
public class PersonController {

    private final PersonService personService;

    @PostMapping
    public Map<String, Object> save(@RequestBody PersonVo vo) {
        return Map.of("success", personService.save(vo));
    }

    @GetMapping("/{id}")
    public PersonVo getById(@PathVariable Long id) {
        return personService.getById(id);
    }
}
```

### 컨벤션

| 요소 | 규칙 |
|------|------|
| 클래스 어노테이션 | `@RestController` + `@RequiredArgsConstructor` + (옵션) `@RequestMapping` |
| 의존성 주입 | `private final` 필드 (생성자 주입은 Lombok이 처리) |
| Body 받기 | `@RequestBody` 필수 (POST/PUT) |
| Path 변수 | `@PathVariable` |
| Query 파라미터 | `@RequestParam` 또는 객체 바인딩 |
| 응답 형식 | `Map.of("key", value)` 또는 DTO 직접 반환 |
| HTTP 상태 코드 | 정상은 자동 200. 실패는 GlobalExceptionHandler에 위임 |

### 금지사항
- ❌ Controller에 검증 로직 (Bean Validation 안 쓰면 Domain Primitive로 위임)
- ❌ Controller에 비즈니스 로직 (조건문, 계산)
- ❌ Controller에 DAO 직접 호출
- ❌ `ServletRequest` 받지 마라 (필요 시 `@RequestHeader`, `@CookieValue`로 명시)
- ❌ try-catch로 예외 처리 (GlobalExceptionHandler에서 일괄)

### 응답 형식 패턴

#### 패턴 1: Map.of (간단한 액션 결과)
```java
@PostMapping
public Map<String, Object> save(@RequestBody PersonVo vo) {
    return Map.of("success", personService.save(vo));
}
```

#### 패턴 2: DTO 직접 반환 (조회)
```java
@GetMapping("/{id}")
public PersonVo getById(@PathVariable Long id) {
    return personService.getById(id);
}
```

#### 패턴 3: 페이징 결과 (SearchVo 자체)
```java
@GetMapping
public PersonVo.SearchVo search(PersonVo.SearchVo paging) {
    return personService.search(paging);
}
```

## Service

### 기본 구조

```java
package me.example.service;

import lombok.RequiredArgsConstructor;
import me.example.dao.PersonDao;
import me.example.domain.Person;
import me.example.domain.dto.PersonVo;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class PersonService {

    private final PersonDao personDao;

    @Transactional
    public boolean save(PersonVo vo) {
        Person person = Person.create(vo.getName(), vo.getAge());
        return personDao.insert(person) > 0;
    }

    @Transactional(readOnly = true)
    public PersonVo getById(Long id) {
        return personDao.selectById(id);
    }
}
```

### 컨벤션

| 요소 | 규칙 |
|------|------|
| 클래스 어노테이션 | `@Service` + `@RequiredArgsConstructor` |
| 트랜잭션 | 메서드 단위 `@Transactional`. 조회만은 `readOnly = true` |
| 검증 | Domain Primitive에 위임 (`Person.create()` 호출만 하면 자동) |
| 변환 | `Entity.create(vo.field1(), vo.field2())` 패턴 |
| DAO 호출 | 1~2개. 많아지면 Service 분리 또는 Aggregate 재설계 검토 |

### 금지사항
- ❌ if문 검증 (5줄 이상 검증 코드는 Domain Primitive로 옮기라는 신호)
- ❌ DAO 우회 (DataSource, JdbcTemplate 직접 사용)
- ❌ Controller 호출 (양방향 의존)
- ❌ 다른 Service 호출 사슬 (3단계 이상은 설계 재검토)

### 비즈니스 로직 예시

#### 중복 체크
```java
@Transactional
public boolean save(PersonVo vo) {
    if (personDao.existsByEmail(vo.getEmail())) {
        throw new DuplicateEmailException("이미 등록된 이메일");
    }
    Person person = Person.create(vo.getName(), vo.getAge(), vo.getEmail());
    return personDao.insert(person) > 0;
}
```

#### 상태 전이
```java
@Transactional
public boolean approve(Long orderId) {
    Order order = orderDao.selectById(orderId);
    order.approve();  // Domain 메서드. 상태 전이 가능 여부 자체 검증.
    return orderDao.updateById(order) > 0;
}
```

#### 권한 검증
```java
@Transactional
public boolean delete(Long postId, Long userId) {
    Post post = postDao.selectById(postId);
    if (!post.isOwnedBy(userId)) {
        throw new ForbiddenException("작성자만 삭제 가능");
    }
    return postDao.deleteById(postId) > 0;
}
```

## Controller-Service 통신 데이터 형식

### 입력 (Controller → Service)
- 작은 입력: 원시 타입 (`Long id`, `String email`)
- 복잡한 입력: VO (`PersonVo`)

### 출력 (Service → Controller)
- 단건 조회: VO 또는 단순 타입
- 다건 조회: `List<VO>` 또는 SearchVo (페이징 포함)
- 액션 결과: `boolean` 또는 ID

## Service 트랜잭션 전략

### 기본
- 쓰기 메서드: `@Transactional`
- 읽기 메서드: `@Transactional(readOnly = true)`

### 격리 레벨
- 기본 (DB default 사용)
- 명시 필요 시: `@Transactional(isolation = Isolation.SERIALIZABLE)` 같이

### 롤백 정책
- RuntimeException 자동 롤백 (Spring 기본)
- 체크 예외 롤백: `@Transactional(rollbackFor = Exception.class)`

### 주의
- `open-in-view: false` 환경에서 LazyInitializationException 주의
- Service 메서드 안에서 모든 lazy 로딩 끝내기

## 의존성 주입 패턴

### ✅ 권장 (Lombok 생성자 주입)
```java
@Service
@RequiredArgsConstructor
public class PersonService {
    private final PersonDao personDao;
    private final NotificationService notificationService;
}
```

### ❌ 비권장
- `@Autowired` 필드 주입 (테스트 어려움)
- Setter 주입
- `@RequiredArgsConstructor` 없이 수동 생성자 작성 (보일러플레이트)

## REST API URL 컨벤션

| 동작 | HTTP | 경로 |
|------|------|------|
| 목록 조회 | GET | `/persons` |
| 단건 조회 | GET | `/persons/{id}` |
| 생성 | POST | `/persons` |
| 전체 수정 | PUT | `/persons/{id}` |
| 부분 수정 | PATCH | `/persons/{id}` |
| 삭제 | DELETE | `/persons/{id}` |
| 검색 | GET | `/persons?keyword=...` |
| 액션 | POST | `/persons/{id}/approve` |

복수형 명사 + 식별자. 동사는 액션에만.
