# Data Layer — jOOQ DAO + JPA validate-only + Flyway

## 전체 그림

```
Flyway      → DDL 마이그레이션 (실제 스키마 생성)
JPA Entity  → 스키마 검증만 (ddl-auto: validate)
jOOQ DAO    → 모든 쿼리
```

세 도구가 서로 다른 책임을 가지며 보완.

## application.yml 설정

```yaml
spring:
  jpa:
    open-in-view: false               # 필수. View 단위 트랜잭션 방지
    hibernate:
      ddl-auto: ${DDL_AUTO:validate}  # validate만. create/update 절대 금지
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
```

**중요**: `ddl-auto: validate` — JPA Entity와 실제 DB 스키마(Flyway가 만든 것)가 불일치하면 부팅 실패.
이걸로 Entity 정의 ≠ DDL 변경 시 즉시 발견.

## Flyway Migration 컨벤션

### 파일 명명
```
src/main/resources/db/migration/
├── V202604011001__create_person.sql
├── V202604011010__create_push_log.sql
├── V202604011021__add_email_to_person.sql
└── V202604011051__create_notification.sql
```

- `V{yyyyMMddHHdd}__{설명_snake_case}.sql`
- 버전은 날짜+시간으로 사용(`V202601011530`, `V202601310130`)
- 설명은 영어 snake_case 권장

### 컬럼 명명 + Comment 필수
```sql
CREATE TABLE push_log (
    id              BIGINT          NOT NULL AUTO_INCREMENT          COMMENT 'PK',
    organization    VARCHAR(100)    NOT NULL                         COMMENT '조직명 (GitHub org)',
    project         VARCHAR(100)    NOT NULL                         COMMENT '프로젝트(repo)명',
    branch          VARCHAR(100)    NOT NULL                         COMMENT '브랜치명',
    is_top_branch   BOOLEAN         NOT NULL DEFAULT FALSE           COMMENT '주요 브랜치 여부 (main/master/develop)',
    message         TEXT            NOT NULL                         COMMENT '커밋 메시지',
    commited_at     TIMESTAMP       NOT NULL                         COMMENT '커밋 시각 (KST)',
    commit_url      VARCHAR(500)                                     COMMENT '커밋 GitHub URL',
    committer       VARCHAR(100)    NOT NULL                         COMMENT '커밋한 사람 이름',
    email           VARCHAR(200)    NOT NULL                         COMMENT '커밋한 사람 이메일',
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '레코드 적재 시각',
    PRIMARY KEY (id),
    INDEX idx_committer (committer),
    INDEX idx_commited_at (commited_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Git push 로그';
```

- 컬럼명: snake_case
- **모든 컬럼에 `COMMENT '...'` 필수** (예외 없음)
- 테이블에도 `COMMENT='...'` 권장
- 시간 컬럼: `TIMESTAMP`, `created_at` 같은 audit 필드 일관성
- INDEX는 별도 라인

## JPA Entity (validate-only)

### 기본 구조
```java
import jakarta.persistence.*;

@Entity
@Table
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Person {
    @Id
    @Column(nullable = false, comment = "PK")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Embedded
    private PersonName name;  // comment는 PersonName 내부 @Column에 정의

    @Embedded
    private Age age;          // comment는 Age 내부 @Column에 정의

    private Person(PersonName name, Age age) {
        this.name = name;
        this.age = age;
    }

    public static Person create(String name, int age) {
        return new Person(new PersonName(name), new Age(age));
    }
}
```

### 핵심 규칙
- ✅ `@Entity` + `@Table` (스키마 매핑)
- ✅ `@NoArgsConstructor(PROTECTED)` (JPA reflection용)
- ✅ private 생성자 + 정적 팩토리 (`create`)
- ✅ `@Embedded` + Domain Primitive로 필드 표현
- ✅ **모든 컬럼에 `@Column(comment = "...")` 필수** (Jakarta Persistence 3.2+ 표준)
- ❌ `JpaRepository` 정의 안 함
- ❌ `@SuperBuilder` 또는 public 빌더 안 만듦
- ❌ `dto`, `vo` 패키지 import 안 함

### 컬럼 Comment 규칙 (필수)

모든 컬럼에 의미를 명시한다. Entity 양쪽(JPA), Flyway DDL 양쪽 모두.

**환경 요구사항:**
- Jakarta Persistence 3.2+ (Spring Boot 4.0 / Hibernate 7 이상)
- `@Column.comment` 표준 속성으로 사용
- `org.hibernate.annotations.Comment` 는 **deprecated** — 사용 금지

**JPA 쪽 — `@Column(comment = "...")`**

직접 필드 (Entity의 단순 필드):
```java
@Id
@Column(nullable = false, comment = "PK")
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;

@Column(nullable = false, comment = "잔고 FK")
private Long balanceId;
```

Domain Primitive (`@Embeddable`) — comment는 Embeddable 내부의 `@Column`에:
```java
@Embeddable
public class Age {
    @Column(name = "age", nullable = false, comment = "나이")
    private int value;
}

@Embeddable
public class PersonName {
    @Column(name = "name", nullable = false, comment = "이름")
    private String value;
}
```

→ Entity의 `@Embedded private Age age;` 는 그 자체로 comment 안 붙임.
   Age 내부 `@Column` 의 comment가 자동 적용됨.

**복잡한 케이스 — `@AttributeOverride` 로 재정의**
하나의 Embeddable을 여러 곳에서 다른 컬럼명/comment로 쓰고 싶으면:
```java
@Entity
public class Order {
    @Embedded
    @AttributeOverride(
        name = "value",
        column = @Column(name = "shipping_fee", comment = "배송비")
    )
    private Money shippingFee;

    @Embedded
    @AttributeOverride(
        name = "value",
        column = @Column(name = "total_price", comment = "총 가격")
    )
    private Money totalPrice;
}
```

**Flyway DDL 쪽 — `COMMENT 'xxx'` 절 필수**
```sql
CREATE TABLE person (
    id    BIGINT       NOT NULL AUTO_INCREMENT COMMENT 'PK',
    name  VARCHAR(50)  NOT NULL                COMMENT '이름',
    age   INT          NOT NULL                COMMENT '나이',
    ...
);
```

**왜 필수인가:**
- DB만 보고 컬럼 의미 파악 가능해야 함 (DBA, BI 분석가, 신규 입사자)
- 코드와 DB 사이 의미 전달 채널
- BI 도구(Redash, Metabase)가 자동 표시
- 회사 자산화 — 코드 사라져도 스키마는 남음

## jOOQ DAO

### 표준 구조 (PushLogDao 기준)

```java
package me.example.dao;

import lombok.RequiredArgsConstructor;
import me.example.domain.GitVo;
import me.example.utils.DateUtils;
import org.jooq.Condition;
import org.jooq.DSLContext;
import org.jooq.Query;
import org.jooq.impl.DSL;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;

import static me.example.domain.jooq.Tables.PUSH_LOG;

@Repository
@RequiredArgsConstructor
public class PushLogDao {

    private static final int BATCH_CHUNK_SIZE = 50;

    private final DSLContext dsl;

    // 배치 입력
    public void insertBatch(List<GitVo.InsertVo> list) {
        for (int i = 0; i < list.size(); i += BATCH_CHUNK_SIZE) {
            List<GitVo.InsertVo> chunk = list.subList(i, Math.min(i + BATCH_CHUNK_SIZE, list.size()));
            dsl.batch(chunk.stream().map(vo ->
                    (Query) dsl.insertInto(PUSH_LOG)
                            .set(PUSH_LOG.ORGANIZATION, vo.organization())
                            .set(PUSH_LOG.PROJECT, vo.project())
                            .set(PUSH_LOG.CREATED_AT, DateUtils.nowKst())
            ).toArray(Query[]::new)).execute();
        }
    }

    // 페이징 조회
    public GitVo.SearchVo selectBy(GitVo.SearchVo paging) {
        Condition where = buildCondition(paging);

        int count = dsl.fetchCount(dsl.selectFrom(PUSH_LOG).where(where));

        if (count > 0) {
            paging.calcPaging(count);
            List<GitVo.ListVo> list = dsl.selectFrom(PUSH_LOG)
                    .where(where)
                    .orderBy(PUSH_LOG.COMMITED_AT.desc())
                    .offset(paging.offset())
                    .limit(paging.limit())
                    .fetchInto(GitVo.ListVo.class);
            paging.setBody(list);
        }
        return paging;
    }

    // 동적 조건 빌더 (private)
    private Condition buildCondition(GitVo.SearchVo paging) {
        List<Condition> conditions = new ArrayList<>();

        if (paging.getProject() != null && !paging.getProject().isEmpty()) {
            String pattern = "%" + paging.getProject().toLowerCase() + "%";
            conditions.add(DSL.lower(PUSH_LOG.PROJECT).like(pattern));
        }

        Condition where = DSL.trueCondition();
        for (Condition c : conditions) {
            where = where.and(c);
        }
        return where;
    }
}
```

## DAO 컨벤션

### 메서드 명명
| 동작 | prefix | 예시 |
|------|--------|------|
| 단건 입력 | `insert` | `insert(Person p)` |
| 다건 입력 | `insertBatch` | `insertBatch(List<Person> list)` |
| 단건 조회 | `selectBy` | `selectById(Long id)` |
| 다건 조회 | `selectBy` | `selectByOrganization(String org)` |
| 수정 | `updateBy` | `updateById(Person p)` |
| 삭제 | `deleteBy` | `deleteById(Long id)` |
| 카운트 | `countBy` | `countByCommitter(String c)` |

**금지**: `find*`, `save*`, `get*` (JPA 스타일은 jOOQ DAO에 안 어울림)

### 배치 처리
- `BATCH_CHUNK_SIZE = 50` (또는 100) 청크
- subList로 자르고 `dsl.batch().execute()`

### 동적 조건
- private `buildCondition` 메서드로 분리
- `DSL.trueCondition()` 으로 시작 → `.and()` 누적
- null/empty 체크는 메서드 안에서

### like 검색
- 대소문자 무시: `DSL.lower(컬럼).like(pattern)`
- 패턴: `"%" + value.toLowerCase() + "%"`
- OR 조건: `.or(DSL.lower(다른컬럼).like(pattern))`

### Date/Time
- `DateUtils.nowKst()` (직접 만든 KST 유틸)
- `LocalDateTime` 사용

## jOOQ 코드 생성 — Tables 클래스

```
src/main/java/<base>/domain/jooq/  (자동 생성)
├── Tables.java
├── tables/
│   ├── PushLog.java
│   └── Person.java
└── ...
```

- `static import me.example.domain.jooq.Tables.PUSH_LOG`
- jOOQ Maven/Gradle plugin이 Flyway DDL 보고 자동 생성
- 빌드 시점 강타입 보장 (`PUSH_LOG.NAME` 컴파일 타임 체크)

## fetch* 메서드 선택

| 메서드 | 용도 |
|--------|------|
| `fetchInto(Class)` | List<엔티티> 또는 List<VO> |
| `fetchOptionalInto(Class)` | Optional<단건> |
| `fetchOne()` | 단건 (없으면 null) |
| `fetchCount()` | 카운트만 |
| `fetchExists()` | 존재 여부 boolean |

## DAO 트랜잭션

DAO 자체엔 `@Transactional` 안 붙임. **Service 계층에서 트랜잭션 경계 결정**.

```java
@Service
@RequiredArgsConstructor
public class PersonService {
    @Transactional
    public boolean save(PersonVo vo) {
        return personDao.insert(Person.create(vo.getName(), vo.getAge())) > 0;
    }
}
```

## 멀티 데이터소스

여러 DB 사용 시 jOOQ는 명시적:
- DataSource 별 DSLContext bean 분리
- DAO에 어떤 DSLContext 주입할지 명시

```java
@Repository
@RequiredArgsConstructor
public class PushLogDao {
    @Qualifier("primaryDsl")
    private final DSLContext dsl;
}
```

## 마이그레이션 시 주의

### Entity 변경 ≠ Migration 작성 자동
1. Entity 필드 추가 → Flyway 마이그레이션 SQL 직접 작성 필수
2. 다음 부팅 시 ddl-auto: validate가 일치 여부 검증
3. 불일치면 부팅 실패 → 즉시 발견

### 절대 하지 말 것
- `ddl-auto: create` 또는 `update` (실수로 운영 DB 날림)
- Flyway 없이 Entity만 추가 (검증 실패로 부팅 안 됨)
- 운영 환경에서 마이그레이션 수동 적용 (기록 안 남음)
