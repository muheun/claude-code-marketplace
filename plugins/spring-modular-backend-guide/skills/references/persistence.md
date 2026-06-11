# Persistence Reference

## Search And Paging

For internal Fixelsoft projects, Search DTOs may extend a DB-neutral `backend-util` `Paging<T>` only when that artifact is approved as a public API contract. Do not make domain `api` depend on Spring DB bundles, Flyway, p6spy, JDBC drivers, or persistence helper packages. For general or open projects, create a local paging contract instead.

Standard flow:

```text
app request DTO
-> Search DTO
-> service.get(search)
-> service validates target/SPI
-> service calls store.countBy(search)
-> service applies search.calcPaging(count)
-> service calls store.selectBy(search)
-> service applies search.setBody(rows)
-> controller wraps app response DTO in ApiResponse
```

Store executes count and projection queries only. Store must not own paging result mutation.

## JPA And QueryDSL

JPA entities are adapter-internal technology models.

Write side:

- `EntityManager.persist`, `merge`, and `remove` are allowed.
- Entities remain package-private where possible.
- Entities are not returned outside the adapter.

Read side:

- Use QueryDSL projection for single-item reads and list/search reads.
- Add stable ordering for pageable lists.
- Do not use entity fetch plus `toDomain()` as the default read pattern.
- Do not use `JpaRepository` as the standard Store implementation.

Example read shape:

```java
queryFactory.select(Projections.constructor(
        CommentResult.class,
        Projections.constructor(CommentId.class, comment.id),
        Projections.constructor(CommentTarget.class, comment.targetType, comment.targetId),
        comment.content,
        Projections.constructor(AuthorId.class, comment.authorId)))
    .from(comment)
    .where(comment.targetType.eq(target.type())
        .and(comment.targetId.eq(target.id())))
    .orderBy(comment.id.asc())
    .offset(search.offset())
    .limit(search.limit())
    .fetch();
```

## jOOQ

When a jOOQ adapter is selected, prefer jOOQ DSL for reads and writes.

Rules:

- Use `DSLContext` and generated table/record classes.
- Prefer jOOQ DSL for both 조회 and 저장.
- Do not mix jOOQ with JPA/Spring Data inside the same adapter.
- Return domain objects or result DTOs through explicit mapping/projection.
- Keep count query and row query separated for paged searches.

## Flyway And DDL

Default JPA policy:

```yaml
spring:
  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: validate
  flyway:
    enabled: true
    locations: classpath:db/migration
```

Rules:

- Schema changes belong to Flyway migrations.
- Reusable persistence adapters place owned migrations under `src/main/resources/db/migration`.
- App-only composition tables or deployment-only schema changes may live in app migrations.
- Migration versions must be unique across the runtime classpath.
- Prefer `VyyyyMMddHHmm__module_action.sql` style names.

## backend-util

For Spring Boot 4 internal projects:

```kotlin
implementation("com.fixelsoft.util:fixel-util-spring4-db:20260517")
```

Use this for Flyway, p6spy, and related DB infrastructure in `app` or selected persistence adapters. Do not expose this dependency from reusable domain `api/core` modules. For H2 sample projects, exclude MariaDB/MySQL driver modules brought by DB bundles and add H2 explicitly.
