# Anti-Patterns

Use this file during code review and scaffold review.

## Module Boundaries

- Big-bang architecture rewrites that change structure, behavior, naming, and persistence strategy in one step.
- Splitting classes only because they are long, without a distinct change reason, dependency boundary, or test boundary.
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

- Service methods use `find`, `select`, `insert`, `update`, `delete`, `list`, `create`, or `add`.
- Persistence ports are named `Repository` when they are core ports.
- Store implementation names hide technology, such as `PostStoreImpl`.
- JPA implementation uses Spring Data `JpaRepository` as the standard Store.

## Persistence

- Store write methods mirror database columns as long scalar parameter lists.
- Store write methods reuse read projections, app request DTOs, JPA entities, jOOQ records, Spring Data types, or other adapter entities as write commands.
- `core.port` Store command records are exposed upward through `*:api` service contracts or app controllers.
- DTO, service command, Store command, and entity types are created mechanically for every method even when there is no distinct boundary, validation, policy, or persistence reason.
- Splitting Store write commands only because of a nullable/default field when the write intent and validation are the same.
- Query reads fetch entities and map every row through `toDomain()` by default.
- List/search queries lack stable ordering.
- Store mutates paging result state with `calcPaging` or `setBody`.
- jOOQ-backed Store uses JPA, Spring Data, or `EntityManager` for reads/writes instead of jOOQ DSL.
- jOOQ generated sources come from a manually prepared or stale developer-local database.
- Gradle runs compile/test before Flyway migration and jOOQ code generation are complete.
- jOOQ selection removes JPA entity declarations or Hibernate `ddl-auto: validate` schema verification.
- Flyway migrations are only in app even though a reusable adapter owns the table.
- `ddl-auto` is `create`, `create-drop`, or `update` in the scaffold.

## Web

- Reusable modules expose generic HTTP APIs instead of app-owned host workflow endpoints.
- Controllers inject concrete core implementations such as `*ServiceImpl` instead of `*:api` service contracts.
- Controllers pass app request DTOs directly into reusable domain services, Store contracts, or persistence adapters.
- Controllers bind reusable domain `api` command types directly as request bodies when the HTTP shape has request-only validation, defaults, OpenAPI schema, or client compatibility concerns.
- Controllers or command handlers duplicate enum parsing/default helpers, or push channel-specific aliases, defaults, localization, or user-facing messages into reusable domain enums.
- Common response contains boolean `success`.
- 5xx fallback exposes raw exception messages.
- HTTP-specific response DTOs or web-annotated DTOs are placed in reusable module `api`.

## Tests

- Architecture tests that hard-code exact file paths, helper class names, split interface names, Store command record names, parameter order/count/names, private call order, or proxy/decorator internals when those details are not public contracts.
- Broad reflection/source-scan tests that turn cleanup guidance into a development blocker, such as failing every Store write method with scalar parameters or enforcing exact command record suffixes.
- Service tests verify only Mockito interactions without asserting service output, state changes, or exceptions from the real `*ServiceImpl`.
- Service tests mock stateful `*Store` flows so heavily that count, paging, or saved-then-read behavior is no longer realistic.
- Persistence tests replace the real database with H2 for dialect-sensitive SQL, constraints, ordering, or projection behavior.
- Controller tests duplicate service policy tests instead of staying focused on binding, validation, status, envelope, exception handling, security, filters, or interceptors.

## Skill-Specific Failure Signals

If a proposed answer says "keep controllers inside each feature/domain module", "use JpaRepository for simple CRUD", "service create/find/list", or "put all migrations in app by default", stop and realign with this skill.
