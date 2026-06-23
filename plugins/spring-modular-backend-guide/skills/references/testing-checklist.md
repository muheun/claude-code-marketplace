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
- Prefer behavior tests for business logic and refactors; use architecture tests only for stable boundaries and forbidden dependencies.
- Do not add architecture tests that hard-code exact file paths, helper class names, split interface names, command record names, parameter order/count/names, private call order, or proxy/decorator internals unless those are explicit public contracts. Store write boundary checks may still forbid app DTOs, read projections, adapter entities, and persistence technology types, but they must not fail ordinary scalar parameter lists just because a command record would be cleaner.
- Do not convert refactoring guidance into broad reflection/source-scan tests. For example, do not add a test that fails every `*Store` write method with more than N scalar parameters, every command record that lacks a preferred suffix, or every split that uses a different class name than the guide's example.
- Service command and Store command cleanup is verified by compiling the changed contracts and by focused behavior or persistence tests when mapping, validation, SQL, or service behavior can regress. It is not verified by a global style-policing architecture test.
- Do not add a broad test that forces every controller DTO, service command, Store command, and entity to exist as separate types. Also do not add a broad test that forces them to be shared. Use tests to protect stable forbidden dependencies and behavior; use review judgment for whether a mapping or command split is worthwhile.
- Do not add broad reflection/source-scan tests that force every enum to have a `from` method, a lookup map, or no direct `valueOf` calls. Where enum parsing policy exists, protect it with focused parser/factory tests and app boundary tests.
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
- Non-trivial Store write inputs should move toward purpose-specific command/value records instead of long scalar parameter lists when the change improves readability, validation, or contract stability.
- Store command granularity is reviewed by write intent, validation, state transition, audit/event behavior, concurrency policy, and caller knowledge. Do not split commands just because one field is nullable, defaulted, or method-specific.
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
- Prefer hand-written fakes when state matters: save-then-read, insert-then-select, count-plus-paging, ordering, accumulated changes, multi-step Store interactions, or scenarios where Mockito setup becomes longer than the behavior under test.
- Prefer Mockito mocks when the boundary is stateless, the test only needs one or two methods, a fake would be longer than the test intent, or the scenario is a one-off return value, exception, no-call, or side-effect verification. Core business policy collaborators stay real unless they are the unit under test in a separate focused test.
- Core service tests do not use real persistence adapters and must not add `core -> adapter` or `core -> app` dependencies for testing.
- Persistence adapter tests exercise the real `Jpa*StoreAdapter`, `Jooq*StoreAdapter`, or `InMemory*StoreAdapter`; do not fake the adapter under test.
- jOOQ-backed adapter tests verify JPA entities and Hibernate validation exist, while Store reads/writes go through the real jOOQ adapter.
- SQL, join, projection, unique constraint, ordering, paging, and dialect behavior tests use the real target database product, preferably with Testcontainers.
- Persistence integration tests apply Flyway migrations from the runtime classpath, such as `classpath:db/migration`, so adapter-owned migrations are included. Do not hard-code `app/src/main/resources/db/migration` unless the test is specifically for app-only migrations.
- App tests cover thin controller HTTP contracts, security, common response envelopes, module composition, selected adapter imports, and bean wiring.
- Controller tests may mock service contracts, but they must verify HTTP concerns such as binding, validation, status codes, response envelopes, exception handling, security, filters, or interceptors. Do not retest service business logic through controllers.
- Thin controller HTTP tests may use Mockito for service contracts when they only verify request mapping, binding, validation, status/envelope behavior, or no-call behavior. Thin app workflow forwarding tests may use Mockito when they only verify no-call behavior or a single delegated call. Do not build hand-written fakes for these tests unless stateful behavior is part of the contract.
- Service plus real adapter tests live in an adapter or app test source set and are integration tests, not core unit tests.

Common test-design failures to reject:

- Treating every design preference as an architecture-test rule instead of using review judgment and behavior tests.
- Blocking normal development with broad tests that enforce cleanup preferences, such as failing all Store write methods with scalar parameter lists or exact command naming rules.
- Adding production or test dependencies from `core` to a persistence adapter just to run a convenient service test.
- Replacing the target MariaDB/MySQL/PostgreSQL behavior with H2 for SQL, constraint, projection, ordering, or dialect-sensitive tests.
- Hard-coding app migration paths in reusable adapter tests, which hides adapter-owned Flyway migrations.
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
- Adding only `test.dependsOn(generateJooq)` while leaving `compileJava` free to run before generated sources exist.
- Using JPA, Spring Data, or `EntityManager` for jOOQ-backed Store reads/writes instead of limiting JPA to entity declaration and validation.

## Web Rules

- Controller success responses use common envelope.
- Controllers and HTTP-facing workflows depend on `*Service` contracts, not concrete `*ServiceImpl` classes.
- App request DTOs stay app-local. Tests may protect against HTTP binding types or request-only shapes leaking into reusable domain service, Store, or persistence contracts, but should not police every mapping method, exact command class name, or whether create/update request DTOs are split or shared.
- String enum input tests verify the app boundary behavior: accepted tokens, invalid input outcome, defaults when the boundary defines them, and no-call behavior when invalid input must stop downstream calls. HTTP controllers verify status/envelope; domain enum factory tests stay focused on web-neutral canonical tokens.
- Basic exceptions are converted to the common envelope.
- Tests parse JSON structure instead of only checking string fragments.

## Verification Commands

Use the repository-specific commands. For Gradle projects, prefer:

```bash
./gradlew test
git diff --check
```
