# Anti-Patterns

Use this file during code review and scaffold review.

## Review Scope

Review findings report design, boundary, contract, behavior, persistence, and test problems — the categories below. Code formatting is the formatter's domain: indentation, whitespace, blank lines, line wrapping, brace placement, and import order/grouping are write-time rules applied while producing code (`naming.md`), enforced by the project formatter or IDE, and they do not appear in review findings. When the user explicitly requests a formatting or import-cleanup review, treat the formatting rules in `naming.md` as the requested review scope.

## Contents

- [Review Scope](#review-scope)
- [Module Boundaries](#module-boundaries)
- [Naming](#naming)
- [Persistence](#persistence)
- [Web](#web)
- [Tests](#tests)
- [Skill-Specific Failure Signals](#skill-specific-failure-signals)

## Module Boundaries

- Big-bang architecture rewrites that change structure, behavior, naming, and persistence strategy in one step.
- Splitting classes only because they are long, without a distinct change reason, dependency boundary, or test boundary.
- Extracting a private helper into a one-method Spring component used by one caller, without a consumer-knowledge, lifecycle, dependency, or reuse boundary.
- Extracting a public or package-visible predicate-like helper that hides side effects such as member provisioning, message sending, persistence, or cache mutation.
- Moving a caller-specific guard, parser, or policy out of a command executor/controller when it is still tightly coupled to that caller's ack/response/error presentation and has no second consumer.
- Splitting every method into a separate `Service`, `Store`, SPI, Reader, or Notifier contract without a distinct consumer role, change reason, or dependency boundary.
- Extracting abstractions that cannot be protected by tests, architecture rules, or clear module dependencies.
- Domain module owns `adapter:web` or `@RestController`.
- Reusable module imports host domain classes such as board/product/notice.
- `api` depends on Spring Web, DB technology, `core`, or `adapter`.
- Domain `api/core` depends on DB infrastructure bundles such as Flyway, p6spy, JDBC drivers, or `fixel-util-spring4-db`.
- Adding `backend-util` everywhere or rewriting local helpers broadly when the Fixelsoft internal Spring project has not opted into it or the change is unrelated.
- `core` depends on Spring MVC, JPA entity, QueryDSL, jOOQ, app, or web-support.
- Cross-domain validation is implemented by direct repository access.

## Naming

- Service interfaces use data-access or CRUD verbs such as `find`, `select`, `insert`, `update`, `delete`, `list`, `create`, or `add` instead of application verbs like `get`, `save`, `modify`, `remove`, `exists`, or explicit domain verbs.
- Persistence ports are named `Repository` when they are core ports.
- Store implementation names hide technology, such as `PostStoreImpl`.
- JPA implementation uses Spring Data `JpaRepository` as the standard Store.

## Persistence

- Store write methods mirror database columns as long scalar parameter lists.
- Store write methods reuse read projections, app request DTOs, JPA entities, jOOQ records, Spring Data types, or other adapter entities as write commands.
- `core.port` Store command records are exposed upward through `*:api` service contracts or app controllers.
- DTO, service command, Store command, and entity types are created mechanically for every method even when there is no distinct boundary, validation, policy, or persistence reason.
- Splitting Store write commands only because of a nullable/default field when the write intent and validation are the same.
- Persistence row mappers call `Enum.valueOf(...)` directly for stored strings; follow "Enum Input Parsing and Factory Names" in `naming.md`.
- Query reads fetch entities and map every row through `toDomain()` by default.
- List/search queries lack stable ordering.
- Store mutates paging result state with `calcPaging` or `setBody`.
- jOOQ-backed Store uses JPA, Spring Data, or `EntityManager` for reads/writes instead of jOOQ DSL.
- jOOQ generated sources come from a manually prepared or stale developer-local database.
- Gradle runs compile/test before Flyway migration and jOOQ code generation are complete.
- jOOQ selection removes JPA entity declarations or Hibernate `ddl-auto: validate` schema verification.
- Flyway migrations are only in app or a technology adapter even though reusable relational schema should live in `*:adapter:persistence-schema`.
- A new Flyway version uses 12-digit `yyyyMMddHHmm`, copies a plan/example timestamp, invents `HHmmss` instead of running `date +%Y%m%d%H%M%S` at file creation, increments a previous version, leaves an unapplied 12-digit file beside new 14-digit files, or changes the version of an already-applied 12-digit file. Already-applied 12-digit history plus new 14-digit files is the expected transition, not a defect.
- New table DDL, changed table DDL, or its matching JPA entity omits table/column comments for introduced or changed schema objects, including the `id` column on new entities.
- Flyway DDL comments and JPA entity comments describe the same table or column differently.
- Primary keys are not declared explicitly, or primary-key constraints are left unnamed when the target DB supports naming them.
- Foreign keys, unique keys, or indexes rely on generated names or explicit names that omit the required `fk_`, `uk_`, or `idx_` role prefix.
- Already-applied Flyway migrations are edited to backfill comments or rename keys/indexes instead of adding a forward migration.
- New domain-owned table DDL is placed in `shared:db-schema` even though a bounded-context `*:adapter:persistence-schema` owner is clear.
- A consumer's selected schema modules are missing from app runtime, adapter integration test runtime, root-level Flyway migration source lists, or jOOQ code generation migration inputs when present.
- `ddl-auto` is `create`, `create-drop`, or `update` in the scaffold.

## Web

- Reusable modules expose generic HTTP APIs instead of app-owned host workflow endpoints.
- Controllers inject concrete core implementations such as `*ServiceImpl` instead of `*:api` service contracts.
- Controllers pass app request DTOs directly into reusable domain services, Store contracts, or persistence adapters.
- Controllers bind reusable domain `api` command types directly as request bodies when the HTTP shape has request-only validation, defaults, OpenAPI schema, or client compatibility concerns.
- Controllers, command handlers, or batch input adapters call `Enum.valueOf(...)` directly for external strings, or duplicate ad-hoc parsing/default helpers; follow "Enum Input Parsing and Factory Names" in `naming.md`.
- Any i18n, localized error, or localized Security response behavior that deviates from `i18n.md`; that file is the canonical policy. Representative signals:
  - Reusable `api/core` injects `MessageSource` or reads `LocaleContextHolder` to format exceptions.
  - `@RestControllerAdvice` localizes MVC errors while Security entry points, access-denied handlers, or filters still emit hard-coded text or raw JSON strings.
  - A custom `LocaleResolver` is registered under a name other than `localeResolver`, so `DispatcherServlet` keeps the default strategy.
  - Batch, scheduled, async, Slack, email, or push rendering uses the current thread/request locale instead of an explicit recipient locale.
- Common error response contains boolean `success`.
- 5xx fallback exposes raw exception messages.
- HTTP-specific response DTOs or web-annotated DTOs are placed in reusable module `api`.

## Tests

- Architecture tests that hard-code exact file paths, helper class names, split interface names, Store command record names, parameter order/count/names, private call order, or proxy/decorator internals when those details are not public contracts.
- Architecture tests whose implementation or maintenance cost is larger than the module boundary or behavior they protect.
- Escalating every code review finding into another global architecture rule instead of classifying it as baseline modularization, opt-in project policy, or review-only guidance.
- Adding architecture tests for service method prefixes, Store method prefixes, class suffixes, helper names, or exact DTO/command names when the issue is only naming or style guidance.
- Adding custom parsers or broad scans whose complexity is larger than the architecture boundary they protect.
- Adding an ArchUnit rule that forbids a cohesive read contract such as `FooRoleReader` only because the current refactor introduced `FooAuthorizationReader`; this freezes a decomposition choice instead of protecting a stable boundary.
- Adding a broad rule that selected app packages must use the exact newly extracted Reader or SPI name, such as `FooDisplayNameReader`, when the stable rule is only avoiding write-capable service dependencies that cross ownership boundaries and expose mutation methods to consumers that should only read or compose.
- Adding focused tests solely to justify a new one-consumer helper bean when a private method would be equally clear.
- Broad reflection/source-scan tests that turn cleanup guidance into a development blocker, such as failing every Store write method with scalar parameters or enforcing exact command record suffixes.
- Broad build-file tests that try to ban every possible external Maven coordinate for web, DB, QueryDSL, jOOQ, Flyway, JDBC drivers, or Spring starters instead of checking stable internal project boundaries and actual forbidden package/type usage.
- Build or architecture tests that treat same-domain `persistence-schema` as a forbidden sibling technology adapter.
- Broad bytecode/source scans for technology packages when the project only asked to verify `api/core/adapter/app` module separation and dependency direction.
- Broad reflection/source-scan tests that force every enum to have a `from` method or lookup map even when the enum has no string parsing contract.
- Service tests verify only Mockito interactions without asserting service output, state changes, or exceptions from the real `*ServiceImpl`.
- Service tests mock stateful `*Store` flows so heavily that count, paging, or saved-then-read behavior is no longer realistic.
- Persistence tests replace the real database with H2 for dialect-sensitive SQL, constraints, ordering, or projection behavior.
- Controller tests duplicate service policy tests instead of staying focused on binding, validation, status, envelope, exception handling, security, filters, or interceptors.

## Skill-Specific Failure Signals

If a proposed answer says "keep controllers inside each feature/domain module", "use JpaRepository for simple CRUD", "service create/find/list", or "put all migrations in app or a technology adapter by default", stop and realign with this skill.
