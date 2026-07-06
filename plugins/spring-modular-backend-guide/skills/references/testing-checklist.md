# Testing Checklist

## Contents

- [Change Strategy Checks](#change-strategy-checks)
- [Test Scope Checks](#test-scope-checks)
  - [Architecture Test Gate](#architecture-test-gate)
- [Module Boundary Rules](#module-boundary-rules)
- [Naming Rules](#naming-rules)
- [Persistence Rules](#persistence-rules)
- [Layered Test Strategy](#layered-test-strategy)
- [Web Rules](#web-rules)
- [Verification Commands](#verification-commands)

Add tests for changed behavior and stable module boundaries. Keep architecture tests small: selected module existence and dependency direction first. Use `architecture-tests.md` for compact ArchUnit examples.

The skill guides implementation and review judgment. Tests are guardrails for regressions that are cheap and stable to detect; they are not a substitute for reading the guide.

## Change Strategy Checks

- Responsibility splits have a clear reason to change, not only a cosmetic class-length concern.
- Architecture changes are small enough to review without also changing unrelated behavior, naming, and persistence strategy.
- A split leaves a verification point: compilation, behavior test, wiring test, module dependency check, package rule, or focused layer test. Use architecture tests only when they are the smallest stable protection.
- Checklist-only documentation does not count as boundary protection.
- Mixed HTTP, use-case orchestration, domain rule, persistence query, and infrastructure wiring concerns are separated at the appropriate `app`, `api`, `core`, or `adapter` boundary.
- Refactoring does not add direct bounded-context dependencies or make `core` depend on `adapter`/`app`.
- New app-local helper classes or Spring beans pass the Class Extraction Gate in `architecture.md`; otherwise keep the logic as a private method.
- New `Service`, `Store`, SPI, Reader, or Notifier contracts are split by consumer role and change reason, not only because each interface has one method.
- Interface splits either hide concepts a consumer should not know, support realistic implementation/lifecycle differences, or remove unsafe test coupling such as inheritance-based fakes and `null` constructor arguments.

## Test Scope Checks

- Required behavior and boundary tests are present; keeping test scope small is not a reason to skip contract protection.
- Each new test can name the regression it catches in one sentence.
- Prefer one small, sufficient architecture rule, dependency check, or focused layer test over several tests that assert the same boundary.
- Prefer behavior tests for business logic and refactors; use architecture tests only for stable boundaries and forbidden dependencies.
- Validation effort must stay proportional to the change. If an architecture test needs more code than the implementation it protects, first reduce it to the baseline modularization rule or keep the finding as review guidance.
- Do not add tests because the guide could be ignored. The agent using the guide must apply review-only rules during implementation and review.

### Architecture Test Gate

Before adding an ArchUnit or broad source-scan test, pass this gate:

- Classify the check before coding it:
  - Baseline modularization: selected modules exist and dependency direction is correct, including no `api -> core`, no `api/core -> app/adapter/web-support/other bounded context`, and no persistence technology adapter -> `app/web-support/other bounded context`.
  - Opt-in project-policy enforcement: broad static checks for technology bans, adapter registration, naming, jOOQ/Flyway build order, response envelope, enum parsing, and forbidden DTO/entity/persistence types.
  - Review-only guidance: cleanup preferences, exact decomposition names, command-shape preference, scalar-vs-command migration, helper names, and file layout details.
- The rule must protect a stable boundary. Baseline checks are dependency direction and selected module existence. Optional static enforcement needs an existing project standard, a touched boundary, or an explicit user request; it does not make the underlying design rule optional.
- The failure message should describe a regression that would still be invalid if the interface or helper names changed.
- The rule must not force one freshly extracted Reader, SPI, Store, command, helper, or DTO name when another cohesive split would also be valid.
- If compilation, focused wiring tests, behavior tests, or code review can protect the refactor without freezing decomposition, use those instead.
- Do not add focused tests only to make a one-consumer class extraction look justified. Tests protect behavior or stable boundaries; they do not create a boundary by themselves.
- If the rule is about naming, vocabulary, method prefixes, suffixes, helper names, file layout, or decomposition style, enforce it during implementation and review by default. For example, require `remove` instead of `delete` in service APIs during review, but do not add a global architecture test that fails service methods using `delete` unless naming enforcement is an explicit project policy.
- For Gradle/build-file checks, prefer stable internal project boundaries: `api/core` must not depend on `app`, web-support, persistence adapters, or other bounded contexts. Do not maintain broad external Maven-coordinate blacklists for future DB/web libraries. Validate forbidden technology through actual source/bytecode package or type dependencies only when that technology boundary is explicitly in scope.
- Do not add architecture tests that hard-code exact file paths, helper class names, split interface names, command record names, parameter order/count/names, private call order, or proxy/decorator internals unless those are explicit public contracts. Store write boundary checks may still forbid app DTOs, read projections, adapter entities, and persistence technology types, but they must not fail ordinary scalar parameter lists just because a command record would be cleaner.
- Do not convert refactoring guidance into broad reflection/source-scan tests. For example, do not add a test that fails every `*Store` write method with more than N scalar parameters, every command record that lacks a preferred suffix, or every split that uses a different class name than the guide's example.
- Service command and Store command cleanup is verified by compiling the changed contracts and by focused behavior or persistence tests when mapping, validation, SQL, or service behavior can regress. It is not verified by a global style-policing architecture test.
- Do not add a broad test that forces every controller DTO, service command, Store command, and entity to exist as separate types. Also do not add a broad test that forces them to be shared. Use tests to protect stable forbidden dependencies and behavior; use review judgment for whether a mapping or command split is worthwhile.
- Do not add broad reflection/source-scan tests that force every enum to have a `from` method or a lookup map. Protect string enum parsing with focused parser/factory tests and the relevant app or adapter boundary tests. Static checks against direct `Enum.valueOf(...)` should be scoped to known external-input or stored-row mapping boundaries, and must still allow `.name()` serialization where it is the chosen stored-token contract.
- Cross-cutting policy moved to `app` composition is tested by ownership and affected method set, not every annotation attribute.
- Architecture rules apply only to modules included in the current migration scope unless the task explicitly broadens the cleanup.
- Controller tests stay at HTTP contract level; they do not duplicate service policy tests.
- Service tests assert result, state, exception, or side-effect payload from the real `*ServiceImpl`; they do not stop at mock interaction counts.
- Persistence tests assert database behavior that cannot be trusted from unit tests: schema, SQL projection, ordering, paging, constraints, and dialect-sensitive errors.

## Module Boundary Rules

Baseline checks:

- Each migrated bounded context has `*:api` and `*:core`.
- Only selected persistence modules are required. Reusable relational modules usually include `*:adapter:persistence-schema` plus the selected relational technology adapter such as `*:adapter:persistence-jooq`, `*:adapter:persistence-jpa`, or `*:adapter:persistence-mybatis`. Memory-only modules do not need schema resources unless they are paired with a relational runtime.
- `*:core` depends on its own `*:api`.
- `*:api` does not depend on its own `*:core`.
- Persistence technology adapters depend on their own `*:core`.
- `*:adapter:persistence-schema` is resource-only by default and is consumed by app runtime, adapter test runtime, and codegen classpaths.
- `shared:db-schema` is allowed for legacy baseline DDL, strongly cross-domain existing tables, shared foundation tables, or transitional migrations that cannot yet be assigned to one bounded context. Treat it as resource-only and consume it through runtime/test/codegen classpaths.
- `app` depends on selected `*:api`, `*:core`, persistence technology adapters, and schema resource modules for composition.
- Domain `api/core` modules do not depend on `app`, adapters, `shared:web-support`, or other bounded contexts.
- Persistence technology adapters do not depend on `app`, `shared:web-support`, or other bounded contexts.
- Build-file checks that forbid persistence technology adapter sibling dependencies must not classify same-domain `persistence-schema` as a forbidden technology adapter; forbid dependencies on sibling `persistence-jooq`/`persistence-jpa`/`persistence-mybatis` modules instead.
- If the project keeps root-level Flyway migration source lists or code generation migration input lists, verify they include the selected `*:adapter:persistence-schema/src/main/resources/db/migration` locations and `shared/db-schema/src/main/resources/db/migration` when shared or legacy migrations are used.

Conditional static enforcement checks:

The design rules below may be mandatory for this guide or for the project. What is conditional is adding broad source, bytecode, or build-file checks for them; add those checks only when the project standard, touched boundary, or user request justifies the maintenance cost.

- `shared:domain` and `shared:web-support` are separate modules.
- Domain modules do not contain `@RestController`, `@Controller`, or `adapter:web`.
- App packages own web controllers and app-specific DTOs.
- Domain `api/core` source or bytecode does not use DB, Spring Web, Spring Data, JDBC, SQL, transaction, Flyway, jOOQ, QueryDSL, Hibernate, or JPA packages.
- Domain `api/core` modules do not depend on DB infrastructure bundles. Guard this with source/bytecode package rules, not an exhaustive list of external dependency coordinates.

## Naming Rules

Use these as design rules during implementation and review. Do not turn them into global architecture tests unless naming is an explicit project policy.

- Service methods start with application verbs such as `get`, `save`, `modify`, `remove`, `exists`, or explicit domain verbs. Avoid data-access or CRUD prefixes such as `find`, `select`, `insert`, `update`, `delete`, `list`, `create`, and `add` in service interfaces.
- Service contracts are named `*Service`; concrete core implementations, including decorators and variants, are named `*ServiceImpl`.
- Store methods start with persistence verbs such as `select`, `insert`, `update`, `delete`, `upsert`, `exists`, `count`.
- Persistence ports end with `Store`.
- Persistence adapter implementations include the technology, such as `(Jpa|Jooq|Mybatis|InMemory)*StoreAdapter`.

Do not block development with broad architecture tests for these naming rules unless the project explicitly adopts naming enforcement. If a touched name violates the rule, fix it in the change or call it out in review.

## Persistence Rules

Use these when the selected persistence adapter or Store contract is in scope. They are not baseline modularization checks.

- Store write methods do not use app request DTOs, read projections, JPA entities, jOOQ records, Spring Data types, or other adapter entities as write commands.
- Non-trivial Store write inputs should move toward purpose-specific command/value records instead of long scalar parameter lists when the change improves readability, validation, or contract stability.
- Store command granularity is reviewed by write intent, validation, state transition, audit/event behavior, concurrency policy, and caller knowledge. Do not split commands just because one field is nullable, defaulted, or method-specific.
- Write input validation is covered by focused value-object or service tests when validation is part of the domain contract.
- JPA adapters do not depend on `JpaRepository` for standard Store implementation.
- Persistence adapters do not self-register with `@Component`, `@Service`, `@Repository`, or component-scanned `@Configuration`.
- App uses Hibernate `ddl-auto: validate` for relational schema verification.
- Reusable relational modules have Flyway migrations in `*:adapter:persistence-schema`, not duplicated inside `persistence-jpa`, `persistence-jooq`, or `persistence-mybatis`.
- Each consumer's selected schema modules, including `shared:db-schema` when used, are available on app runtime, adapter integration test runtime, and jOOQ code generation migration inputs when present.
- jOOQ adapters wire build tasks so Flyway-migrated schema verification runs before jOOQ code generation, and `compileJava` depends on generated sources before tests run.
- Selected identifier strategy has matching DDL type, public ID `NOT NULL`/`UNIQUE` lookup constraints when used, ID converter, and ordering expectations.
- New table DDL includes table and column comments, including `id`; `ALTER TABLE` DDL comments every introduced or changed schema object. New JPA entities declare matching table/column comments for every mapped object; changed entities declare them for introduced or changed mapped objects. Primary keys are declared explicitly and named when the target DB supports it; foreign keys, unique keys, and indexes use explicit names with `fk_`, `uk_`, and `idx_` role prefixes.
- Already-applied Flyway migrations are not edited to backfill comments or rename keys/indexes. Use a new forward migration when the project accepts the operational change.
- Paged search tests assert count, paging metadata, stable order, and result body.

## Layered Test Strategy

- Core service tests instantiate the real `*ServiceImpl` and replace only external boundaries such as `*Store`, SPI, readers, recorders, notifiers, senders, or publishers.
- Mockito is acceptable in service tests for controlling boundary return values, exceptions, or verifying side-effect calls. The mock is not the test subject.
- Prefer hand-written fakes when state matters: save-then-read, insert-then-select, count-plus-paging, ordering, accumulated changes, multi-step Store interactions, or scenarios where Mockito setup becomes longer than the behavior under test.
- Prefer Mockito mocks when the boundary is stateless, the test only needs one or two methods, a fake would be longer than the test intent, or the scenario is a one-off return value, exception, no-call, or side-effect verification. Core business policy collaborators stay real unless they are the unit under test in a separate focused test.
- Core service tests do not use real persistence adapters and must not add `core -> adapter` or `core -> app` dependencies for testing.
- Persistence adapter tests exercise the real `Jpa*StoreAdapter`, `Jooq*StoreAdapter`, or `InMemory*StoreAdapter`; do not fake the adapter under test.
- jOOQ-backed adapter tests verify JPA entities and Hibernate validation exist, while Store reads/writes go through the real jOOQ adapter.
- SQL, join, projection, unique constraint, ordering, paging, and dialect behavior tests use the real target database product, preferably with Testcontainers.
- Persistence integration tests apply Flyway migrations from the runtime classpath, such as `classpath:db/migration`, so selected `persistence-schema` modules and `shared:db-schema` are included when used. Do not hard-code `app/src/main/resources/db/migration` unless the test is specifically for app-only migrations.
- App tests cover thin controller HTTP contracts, security, common response envelopes, module composition, selected adapter imports, and bean wiring.
- Controller tests may mock service contracts, but they must verify HTTP concerns such as binding, validation, status codes, response envelopes, exception handling, security, filters, or interceptors. Do not retest service business logic through controllers.
- Thin controller HTTP tests may use Mockito for service contracts when they only verify request mapping, binding, validation, status/envelope behavior, or no-call behavior. Thin app workflow forwarding tests may use Mockito when they only verify no-call behavior or a single delegated call. Do not build hand-written fakes for these tests unless stateful behavior is part of the contract.
- Service plus real adapter tests live in an adapter or app test source set and are integration tests, not core unit tests.

Common test-design failures to reject:

- Treating every design rule as an architecture-test rule instead of using review judgment and behavior tests where static enforcement would be brittle.
- Creating tests for a newly extracted helper when the extraction itself failed the class gate; inline the helper instead.
- Adding architecture tests for service method prefixes, Store method prefixes, class suffixes, DTO/command naming, or helper names when the stable issue is only style guidance.
- Blocking normal development with broad tests that enforce cleanup preferences, such as failing all Store write methods with scalar parameter lists or exact command naming rules.
- Blocking normal dependency evolution with external library-coordinate blacklists in architecture tests. New libraries, renamed artifacts, starters, or convention plugins should not require constant test edits when no forbidden type is used by `api/core`.
- Adding production or test dependencies from `core` to a persistence adapter just to run a convenient service test.
- Replacing the target MariaDB/MySQL/PostgreSQL behavior with H2 for SQL, constraint, projection, ordering, or dialect-sensitive tests.
- Hard-coding app migration paths in reusable adapter tests, which hides selected `persistence-schema` migrations.
- Faking the `*StoreAdapter` class in a persistence adapter test instead of testing the real adapter implementation.
- Testing Mockito behavior instead of the real `*ServiceImpl` behavior.
- Freezing cache keys, transaction proxy details, private method order, or other implementation details when ownership and method coverage are the real contract.
- Freezing package/file layout or exact decomposition names when the stable contract is only dependency direction or behavior preservation.
- Broadening an architecture rule to unrelated modules and creating failures outside the current cleanup scope.
- Duplicating one business policy across service, controller, and integration tests without a separate contract at each layer.
- Mocking `*Store` when a simple fake would better preserve state needed by the service scenario.
- Building a hand-written fake for a controller or thin app workflow test when a service-contract mock would express request validation, no-call behavior, or one delegated call more clearly.
- Expanding controller tests into duplicated service policy tests instead of keeping them focused on HTTP contracts.
- Running jOOQ code generation from a stale manual database or after `test` has already started.
- Keeping Flyway DDL only in `persistence-jooq` or another technology adapter, which makes schema ownership depend on the selected adapter.
- Adding only `test.dependsOn(generateJooq)` while leaving `compileJava` free to run before generated sources exist.
- Using JPA, Spring Data, or `EntityManager` for jOOQ-backed Store reads/writes instead of limiting JPA to entity declaration and validation.

## Web Rules

Use these when app/web behavior is in scope. They are not baseline modularization checks except for app ownership of controllers in projects that have previously leaked web code into domain modules.

- Controller success responses follow the project API contract and are not forced into `ApiResponse` unless the project explicitly standardizes a success envelope.
- Controllers and HTTP-facing workflows depend on `*Service` contracts, not concrete `*ServiceImpl` classes.
- App request DTOs stay app-local. Tests may protect against HTTP binding types or request-only shapes leaking into reusable domain service, Store, or persistence contracts, but should not police every mapping method, exact command class name, or whether create/update request DTOs are split or shared.
- String enum input tests verify the app boundary behavior: accepted tokens, invalid input outcome, defaults when the boundary defines them, and no-call behavior when invalid input must stop downstream calls. HTTP controllers verify status and the exception envelope for invalid input; domain enum factory tests stay focused on web-neutral canonical tokens and should exercise the factory instead of raw `Enum.valueOf(...)`.
- Basic exceptions are converted by centralized advice to the common error envelope.
- Tests parse JSON structure instead of only checking string fragments.

## Verification Commands

Use the repository-specific commands. For Gradle projects, prefer:

```bash
./gradlew test
git diff --check
```
