# Testing Checklist

Add architecture tests or equivalent checks when this guideline is used for a scaffold. Use `architecture-tests.md` for compact ArchUnit examples.

## Change Strategy Checks

- Responsibility splits have a clear reason to change, not only a cosmetic class-length concern.
- Architecture changes are small enough to review without also changing unrelated behavior, naming, and persistence strategy.
- A split leaves a verification point: architecture test, module dependency check, package rule, or focused layer test.
- Checklist-only documentation does not count as boundary protection.
- Mixed HTTP, use-case orchestration, domain rule, persistence query, and infrastructure wiring concerns are separated at the appropriate `app`, `api`, `core`, or `adapter` boundary.
- Refactoring does not add direct bounded-context dependencies or make `core` depend on `adapter`/`app`.
- New `Service`, `Store`, SPI, Reader, or Notifier contracts are split by consumer role and change reason, not only because each interface has one method.
- Interface splits either hide concepts a consumer should not know, support realistic implementation/lifecycle differences, or remove unsafe test coupling such as inheritance-based fakes and `null` constructor arguments.

## Test Scope Checks

- Required tests are present; keeping test scope small is not a reason to skip contract protection.
- Each new test can name the regression it catches in one sentence.
- Prefer one small, sufficient architecture rule, dependency check, or focused layer test over several tests that assert the same boundary.
- Cross-cutting policy moved to `app` composition is tested by ownership and affected method set, not every annotation attribute.
- Architecture rules apply only to modules included in the current migration scope unless the task explicitly broadens the cleanup.
- Controller tests stay at HTTP contract level; they do not duplicate service policy tests.
- Service tests assert result, state, exception, or side-effect payload from the real `*ServiceImpl`; they do not stop at mock interaction counts.
- Persistence tests assert database behavior that cannot be trusted from unit tests: schema, SQL projection, ordering, paging, constraints, and dialect-sensitive errors.

## Module Boundary Rules

- `shared:domain` and `shared:web-support` are separate modules.
- Domain `api/core` modules do not depend on `shared:web-support`.
- Domain `api/core` modules do not depend on DB infrastructure bundles.
- Domain `api/core` modules do not depend on app or adapter packages.
- Persistence adapters do not depend on `shared:web-support`.
- `api/core` modules do not directly depend on other bounded contexts.
- Domain modules do not contain `@RestController` or `@Controller`.
- App packages own web controllers and app-specific DTOs.

## Naming Rules

- Service methods start with allowed application prefixes.
- Service contracts are `*Service`; concrete core implementations, including decorators and variants, are `*ServiceImpl`.
- Store methods start with allowed persistence prefixes.
- Persistence ports end with `Store`.
- Persistence adapter implementations match `(Jpa|Jooq|InMemory)*StoreAdapter`.

## Persistence Rules

- Store write methods do not use app request DTOs, read projections, JPA entities, jOOQ records, Spring Data types, or other adapter entities as write commands.
- Non-trivial Store write inputs use purpose-specific command/value records instead of long scalar parameter lists.
- Write input validation is covered by focused value-object or service tests when validation is part of the domain contract.
- JPA adapters do not depend on `JpaRepository` for standard Store implementation.
- Persistence adapters do not self-register with `@Component`, `@Service`, `@Repository`, or component-scanned `@Configuration`.
- App uses Hibernate `ddl-auto: validate` for relational schema verification.
- Adapter-local Flyway migrations exist for adapter-owned tables.
- jOOQ adapters wire build tasks so Flyway-migrated schema verification runs before jOOQ code generation, and `compileJava` depends on generated sources before tests run.
- Selected identifier strategy has matching DDL type, public ID `NOT NULL`/`UNIQUE` lookup constraints when used, ID converter, and ordering expectations.
- Paged search tests assert count, paging metadata, stable order, and result body.

## Layered Test Strategy

- Core service tests instantiate the real `*ServiceImpl` and replace only external boundaries such as `*Store`, SPI, readers, recorders, notifiers, senders, or publishers.
- Mockito is acceptable in service tests for controlling boundary return values, exceptions, or verifying side-effect calls. The mock is not the test subject.
- Prefer hand-written fakes when state matters: storing then reading, count plus paging, accumulated changes, or scenarios where Mockito setup becomes longer than the behavior under test.
- Prefer Mockito mocks for stateless external-boundary readers, validators, policies, notifiers, senders, publishers, and one-off exception paths. Core business policy collaborators stay real unless they are the unit under test in a separate focused test.
- Core service tests do not use real persistence adapters and must not add `core -> adapter` or `core -> app` dependencies for testing.
- Persistence adapter tests exercise the real `Jpa*StoreAdapter`, `Jooq*StoreAdapter`, or `InMemory*StoreAdapter`; do not fake the adapter under test.
- jOOQ-backed adapter tests verify JPA entities and Hibernate validation exist, while Store reads/writes go through the real jOOQ adapter.
- SQL, join, projection, unique constraint, ordering, paging, and dialect behavior tests use the real target database product, preferably with Testcontainers.
- Persistence integration tests apply Flyway migrations from the runtime classpath, such as `classpath:db/migration`, so adapter-owned migrations are included. Do not hard-code `app/src/main/resources/db/migration` unless the test is specifically for app-only migrations.
- App tests cover thin controller HTTP contracts, security, common response envelopes, module composition, selected adapter imports, and bean wiring.
- Controller tests may mock service contracts, but they must verify HTTP concerns such as binding, validation, status codes, response envelopes, exception handling, security, filters, or interceptors. Do not retest service business logic through controllers.
- Service plus real adapter tests live in an adapter or app test source set and are integration tests, not core unit tests.

Common test-design failures to reject:

- Adding production or test dependencies from `core` to a persistence adapter just to run a convenient service test.
- Replacing the target MariaDB/MySQL/PostgreSQL behavior with H2 for SQL, constraint, projection, ordering, or dialect-sensitive tests.
- Hard-coding app migration paths in reusable adapter tests, which hides adapter-owned Flyway migrations.
- Faking the `*StoreAdapter` class in a persistence adapter test instead of testing the real adapter implementation.
- Testing Mockito behavior instead of the real `*ServiceImpl` behavior.
- Freezing cache keys, transaction proxy details, private method order, or other implementation details when ownership and method coverage are the real contract.
- Broadening an architecture rule to unrelated modules and creating failures outside the current cleanup scope.
- Duplicating one business policy across service, controller, and integration tests without a separate contract at each layer.
- Mocking `*Store` when a simple fake would better preserve state needed by the service scenario.
- Expanding controller tests into duplicated service policy tests instead of keeping them focused on HTTP contracts.
- Running jOOQ code generation from a stale manual database or after `test` has already started.
- Adding only `test.dependsOn(generateJooq)` while leaving `compileJava` free to run before generated sources exist.
- Using JPA, Spring Data, or `EntityManager` for jOOQ-backed Store reads/writes instead of limiting JPA to entity declaration and validation.

## Web Rules

- Controller success responses use common envelope.
- Controllers and HTTP-facing workflows depend on `*Service` contracts, not concrete `*ServiceImpl` classes.
- Basic exceptions are converted to the common envelope.
- Tests parse JSON structure instead of only checking string fragments.

## Verification Commands

Use the repository-specific commands. For Gradle projects, prefer:

```bash
./gradlew test
git diff --check
```
