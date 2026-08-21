# Persistence Reference

## Contents

- [Search And Paging](#search-and-paging)
- [Projection And Mapping](#projection-and-mapping)
- [Store Write Inputs](#store-write-inputs)
  - [Command Granularity](#command-granularity)
  - [Service Command vs Store Command](#service-command-vs-store-command)
- [Identifier Strategy](#identifier-strategy)
- [JPA And QueryDSL](#jpa-and-querydsl)
- [jOOQ](#jooq)
- [Flyway And DDL](#flyway-and-ddl)
  - [Migration Version Creation Checklist](#migration-version-creation-checklist)
  - [DDL Comments And Key Names](#ddl-comments-and-key-names)
- [backend-util](#backend-util)

## Search And Paging

For internal Fixelsoft projects, Search DTOs may extend a DB-neutral `backend-util` `Paging<T>` only when the artifact is already exposed with `api` scope in the project build or listed as a public contract in the project's architecture notes. Do not make domain `api` depend on Spring DB bundles, Flyway, p6spy, JDBC drivers, or persistence helper packages. For general or open projects, create a local paging contract instead.

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
-> controller returns an app response DTO, wrapping it only when the project success-response contract requires an envelope
```

Store executes count and projection queries only. Store must not own paging result mutation.

## Projection And Mapping

Persistence adapters project read results into domain `api` result DTOs or adapter-local projection DTOs. Persistence adapters must not depend on app response DTOs.

If QueryDSL or jOOQ can directly create the domain result DTO, do not add service/controller copy methods that only move the same fields again. Add a manual mapping only when the external response shape differs, masking/formatting/permission filtering is required, multiple bounded-context results are composed, or HTTP/app-only metadata is added.

When an app response DTO is needed, map to it in the app controller or a single app assembler. Domain `api` result DTOs may be reused as response payloads only while they remain web-neutral. Keep them free of Spring MVC, Swagger/OpenAPI, Jackson-only response annotations, and other web concerns.

## Store Write Inputs

Store write inputs are persistence-neutral domain commands or value objects. For non-trivial writes, prefer `CommentCreate`, `CommentUpdate`, or similar records over scalar field lists. Keep validation that protects the domain contract in those records or in the service policy; adapter entity annotations may mirror schema constraints but are not sufficient alone.

Do not pass JPA entities, jOOQ records, Spring Data types, app request DTOs, or other adapter entities through `Store` contracts. Do not reuse read projections as write commands. If an existing domain type is intentionally reused as a write model, it must not carry generated IDs, timestamps, derived flags, or fields outside the write intent.

### Command Granularity

Split Store write commands by write intent, policy, and validation differences, not by every optional field. A nullable field, default value, or one method-specific override is not enough reason to create another command type.

Prefer one command when:

- The operation is the same write intent and only a default differs, such as omitted status meaning `PENDING`.
- The same fields are persisted and the same validation rules apply.
- Splitting would only add files, wiring, and fake updates without hiding a concept from callers.

Prefer separate commands when:

- Required fields differ in a way callers must understand.
- Validation, state-transition policy, audit/event behavior, concurrency expectations, or ownership differs.
- One caller should not know or set fields that another caller needs.
- A read projection or persisted row shape would otherwise be reused as a write model.

If a command field is ignored by one Store method, first consider merging the methods and applying a clear default in service/domain policy or a command factory. Adapters should translate already-decided values; only persistence-technical defaults such as generated columns or database timestamps belong in adapter/DDL behavior. Split only when the ignored field signals a genuinely different write intent. Treat command granularity as review judgment, not an architecture-test rule.

### Service Command vs Store Command

Service commands represent caller-facing use-case input and live in domain `api`. Store commands represent persistence write input and live in `core.port`. They often look similar, but they are allowed to change for different reasons.

Keep separate commands when:

- The service applies policy, defaults, actor information, authorization context, audit metadata, generated values, or derived fields before persistence.
- The Store write shape is tied to one table, SQL operation, optimistic-lock version, upsert key, batch behavior, or adapter-specific persistence concern.
- A caller should not know fields that persistence needs, or persistence should not receive fields that belong only to the use case.
- The service command is also consumed by app workflows, batch jobs, or other domain-facing callers and should remain persistence-neutral.

Reusing a service command as Store input is acceptable only when all of these are true:

- The type lives in domain `api`, not in app or `core.port`.
- It is free of HTTP, web, adapter, JPA, jOOQ, Spring Data, and DB-specific concerns.
- The service use case and Store write have the exact same write intent, required fields, validation, and caller knowledge.
- The command does not contain actor-only, audit-only, generated, derived, or response/read-model fields.
- Future changes are expected to evolve together rather than independently.

Do not pass a `core.port` Store command upward into a `*:api` service contract or app controller just to avoid mapping. If the two inputs only differ by naming, consider whether one web-neutral `api` command is enough; if they differ by policy or persistence meaning, keep the mapping explicit.

## Identifier Strategy

Default to database-generated `BIGINT` identity primary keys for ordinary single-primary relational systems unless the project has a clear reason to generate globally unique IDs outside the database.

Recommended defaults:

- Use database-generated `BIGINT` identity primary keys as the default DB PK. They keep PK/FK indexes, joins, and keyset pagination compact.
- MySQL/MariaDB DDL example: `BIGINT AUTO_INCREMENT`. InnoDB clustered primary keys also benefit from compact, increasing values for write locality.
- PostgreSQL DDL example: `BIGINT GENERATED BY DEFAULT AS IDENTITY`.
- Do not expose DB PKs through public APIs, URLs, events, logs, or cross-module contracts when enumeration risk or external coupling matters.
- Add a separate public ID when the DB PK should stay internal. Store it as `NOT NULL`, immutable, and backed by a `UNIQUE` lookup constraint/index.
- Use UUIDv7 or ULID for public IDs, integration IDs, and event IDs.
- Use UUIDv7/ULID as the DB PK only when IDs must be generated before insert, merged across systems, emitted as the primary event identity, or created outside one database node.
- Prefer creating aggregate IDs in application/domain code only when the domain flow benefits from knowing the ID before persistence.

Storage rules:

- PostgreSQL: prefer native `uuid` for UUID identifiers.
- MySQL/MariaDB family: prefer `BINARY(16)` for UUID identifiers; avoid `VARCHAR(36)` as the default primary key shape.
- ULID portable default: use `CHAR(26)` with ASCII/binary collation so canonical ULID strings preserve lexical time order.
- ULID high-volume option: use `BINARY(16)` with an explicit converter, and verify the byte layout preserves expected time ordering before using ID order for pagination or range scans.
- Avoid random UUID v4 as the default indexed primary key when write locality matters.
- MySQL and MariaDB can share broad storage strategy guidance, but do not treat them as identical for DDL, UUID functions, JSON/index behavior, locks, optimizer behavior, jOOQ dialect, or Testcontainers. Validate product-specific SQL against the actual runtime database.

## JPA And QueryDSL

JPA entities are adapter-internal technology models and the default relational schema validation model. Keep Hibernate validation enabled even when a jOOQ-backed Store is selected.

JPA/QueryDSL-backed Store write side:

- `EntityManager.persist`, `merge`, and `remove` are allowed.
- Entities remain package-private where possible.
- Entities are not returned outside the adapter.

JPA/QueryDSL-backed Store read side:

- Choosing JPA for a project that uses this guide means using QueryDSL for Store reads.
- Use QueryDSL projection for single-item reads and list/search reads.
- Add stable ordering for pageable lists.
- Before implementing a `persistence-jpa` module or `Jpa*StoreAdapter`, verify the module build against the QueryDSL baseline in `build-setup.md` (JPA/QueryDSL Adapter Modules) and confirm the adapter can receive or create a `JPAQueryFactory`.
- Criteria API and JPQL string queries are not the default fallback for Store reads. Use them only after the user explicitly rejects QueryDSL for the project; capture the chosen exception in the plan, review response, or project architecture note instead of source-code comments.
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

When a jOOQ-backed Store is selected, JPA entities still exist for Hibernate schema validation, but Store reads and writes use jOOQ DSL.

Rules:

- Use `DSLContext` and generated table/record classes.
- Prefer jOOQ DSL for both reads and writes.
- Do not use JPA, Spring Data, `JpaRepository`, or `EntityManager` for Store reads/writes in the jOOQ-backed Store.
- JPA entities in a jOOQ-backed adapter are for entity declaration and `ddl-auto: validate` only.
- Return domain objects or result DTOs through explicit mapping/projection.
- Keep count query and row query separated for paged searches.

Code generation lifecycle:

- Generate jOOQ sources from a Flyway-migrated schema, not from a manually prepared developer-local database.
- Keep the codegen database separate from the integration-test runtime database where practical.
- Build order should be: prepare codegen DB -> apply Flyway migrations -> verify expected tables exist -> generate jOOQ sources -> compile -> test.
- Integration tests still start or connect to their own runtime DB and apply Flyway migrations before exercising the real adapter.
- If generated jOOQ sources are committed, CI must still verify they are current by running the same migration and codegen path or a generated-source drift check.

## Flyway And DDL

Default schema policy:

```yaml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: validate
```

jOOQ projects use Flyway migrations as the schema source for both code generation and persistence integration tests. They still keep JPA entity declarations and Hibernate `ddl-auto: validate` as schema verification, but jOOQ-backed Stores do not use JPA/Spring Data for reads or writes.

Rules:

- Schema changes belong to Flyway migrations.
- Reusable relational bounded contexts own migrations in `*:adapter:persistence-schema/src/main/resources/db/migration` by default, even when only one persistence technology exists today.
- If existing or shared schema cannot be assigned to one bounded context, keep those migrations in a shared schema resource module such as `shared:db-schema`, with files under `shared/db-schema/src/main/resources/db/migration`. Use it for legacy baseline DDL, strongly cross-domain existing tables, shared foundation tables, or transitional migrations; do not make it the default for new domain-owned tables.
- Use `persistence-schema`, not `persistence-flyway`: the module owns schema resources; Flyway is the current migration tool.
- Technology adapters such as `persistence-jpa`, `persistence-jooq`, and `persistence-mybatis` consume the schema module and must not duplicate table DDL migrations.
- App-only composition tables or deployment-only schema changes may live in app migrations.
- Migration versions must be unique across the runtime classpath.
- Every new versioned migration uses `VyyyyMMddHHmmss__module_action.sql`. The version is always 14 digits. That is this guide's timestamp version, not an optional extra for collisions.
- Do not create new 12-digit `VyyyyMMddHHmm` files, including to match already-applied 12-digit history. Never change the version of an already-applied file. If a 12-digit file in this change has not been applied, replace its whole version with a new `date +%Y%m%d%H%M%S` output; do not append seconds to the old prefix.
- Flyway compares an undotted version as one number. `V202412312359` (12-digit) is a smaller integer than `V20240101000000` (14-digit), so mixed lengths are not calendar order. New 14-digit versions still sort after existing 12-digit history, which is the safe forward path for already-applied files.
- The 14-digit value is the machine clock at file-creation time. Session date, `user_info` date, "today", plan samples, nearby filenames, and review comments supply a calendar day at most. They are not a clock and must not be combined with a chosen hour, minute, or second.
- Before creating the file, run `date +%Y%m%d%H%M%S` in the environment that will write it and use that exact output as the version. If that command is unavailable, use an equivalent local clock that prints `yyyyMMddHHmmss`. If neither can print a 14-digit clock, do not create the file; ask for the output of `date +%Y%m%d%H%M%S`. Do not skip the clock because the date is already known, and do not compose `yyyyMMdd` with a chosen time.
- Do not invent, round, pad, or pick `HHmmss`. Forbidden sources include `000000`, `120000`, `090000`, "a unique time", the next second, previous version plus one, and any timestamp copied from a plan, example, or nearby file.
- If two files would share the same 14-digit version, wait until the clock changes and run `date +%Y%m%d%H%M%S` again. Do not increment the previous version to manufacture uniqueness.
- Persistence integration tests should apply migrations from the runtime classpath, such as `classpath:db/migration`, so selected schema modules are included. Adapter module tests, app tests, and jOOQ code generation must include the matching `persistence-schema` resources and `shared:db-schema` when shared or legacy migrations are used. Avoid hard-coding `app/src/main/resources/db/migration` unless the test is specifically for app-only migrations.

### Migration Version Creation Checklist

- Run `date +%Y%m%d%H%M%S` immediately before creating the file. The conversation date is not a substitute. If the clock cannot be printed, stop and ask for that output.
- Use that exact 14-digit string in `V<timestamp>__module_action.sql`.
- Treat timestamps in implementation plans, examples, review comments, and nearby files as placeholders. Ignore them and run the clock at file creation.
- Before adding the file, search all runtime migration source directories for the candidate version and reject duplicates.
- On a duplicate, wait and re-run `date +%Y%m%d%H%M%S`. Do not add one second or one minute to the previous version.
- If this change still contains an unapplied 12-digit file, replace its whole version with a new `date +%Y%m%d%H%M%S` output. Do not append seconds to the old prefix. Do not change the version of an already-applied file.
- If a work-in-progress migration was already applied to a local codegen or test database and then edited, reset only that local work-in-progress schema/history or recreate the migration with a new clock timestamp. Do not leave a checksum-mismatched Flyway history state and do not use `repair` as a way to bless an arbitrary edited timestamp.

### DDL Comments And Key Names

Every new table DDL must document the table and every column it introduces. Add table and column comments in the Flyway migration, including `id`, public IDs, audit columns, foreign-key columns, status/type columns, and nullable business fields. For `ALTER TABLE`, document each introduced or changed schema object in the same migration instead of requiring unrelated legacy columns to be backfilled in that change.

Every new JPA entity must declare comments for its mapped table and every mapped column with the project's selected annotation mechanism, such as Hibernate `@Comment`. When changing an existing entity, declare comments for each introduced or changed mapped schema object. Entity comments and Flyway DDL comments must match in meaning. The entity is the Hibernate validation model, but Flyway remains the schema source, so do not put a required comment only on one side.

Declare primary keys explicitly, and name the primary-key constraint with the project convention or a `pk_` prefix when the target database supports custom primary-key constraint names. Name foreign keys, unique keys, and indexes explicitly. Do not rely on database, Hibernate, or migration-tool generated names for foreign keys, unique keys, or indexes. Follow the project's existing naming convention only when it preserves the role prefix; otherwise use stable lowercase `fk_`, `uk_`, and `idx_` prefixes with enough table/column context to identify the purpose. Prefer `uk_<table>_<columns>` for unique constraints and `idx_<table>_<columns>` for non-unique indexes.

When the target database supports comments on constraints or indexes, add comments for non-obvious keys and indexes as well. When it does not, the explicit key/index name must carry the operational meaning clearly enough for schema review, error diagnostics, and migration diff inspection.

Do not edit an already-applied Flyway migration to add comments or rename keys/indexes. Preserve Flyway history and checksum integrity. If a released migration is missing comments or explicit names, add a new forward migration for the comment or rename operation when the project accepts that operational change; otherwise report the gap instead of rewriting history.

## backend-util

For `backend-util` adoption, dependency snippets, and scope rules, see `backend-util.md`, the canonical source.

For Spring Boot 4 internal projects, use `com.fixelsoft.util:fixel-util-spring4-db:<approved-version>` for Flyway, p6spy, and related DB infrastructure in `app` or selected persistence technology adapters; resolve `<approved-version>` from the project version catalog or existing usage. Do not expose this dependency from reusable domain `api/core` modules or resource-only `persistence-schema` modules. For H2 sample projects, exclude MariaDB/MySQL driver modules brought by DB bundles and add H2 explicitly.
