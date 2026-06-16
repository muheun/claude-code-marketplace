# Anti-Patterns

Use this file during code review and scaffold review.

## Module Boundaries

- Domain module owns `adapter:web` or `@RestController`.
- Reusable module imports host domain classes such as board/product/notice.
- `api` depends on Spring Web, DB technology, `core`, or `adapter`.
- Domain `api/core` depends on DB infrastructure bundles such as Flyway, p6spy, JDBC drivers, or `fixel-util-spring4-db`.
- `core` depends on Spring MVC, JPA entity, QueryDSL, jOOQ, app, or web-support.
- Cross-domain validation is implemented by direct repository access.

## Naming

- Service methods use `find`, `select`, `insert`, `update`, `delete`, `list`, `create`, or `add`.
- Persistence ports are named `Repository` when they are core ports.
- Store implementation names hide technology, such as `PostStoreImpl`.
- JPA implementation uses Spring Data `JpaRepository` as the standard Store.

## Persistence

- Query reads fetch entities and map every row through `toDomain()` by default.
- List/search queries lack stable ordering.
- Store mutates paging result state with `calcPaging` or `setBody`.
- jOOQ adapter mixes jOOQ DSL with JPA/Spring Data.
- Flyway migrations are only in app even though a reusable adapter owns the table.
- `ddl-auto` is `create`, `create-drop`, or `update` in the scaffold.

## Web

- Reusable modules expose generic HTTP APIs instead of app-owned host workflow endpoints.
- Controllers inject concrete core implementations such as `*ServiceImpl` instead of `*:api` service contracts.
- Common response contains boolean `success`.
- 5xx fallback exposes raw exception messages.
- HTTP response DTOs are placed in reusable module `api`.

## Skill-Specific Failure Signals

If a proposed answer says "keep controllers inside each feature/domain module", "use JpaRepository for simple CRUD", "service create/find/list", or "put all migrations in app by default", stop and realign with this skill.
