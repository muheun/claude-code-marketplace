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

- JPA adapters do not depend on `JpaRepository` for standard Store implementation.
- Persistence adapters do not self-register with `@Component`, `@Service`, `@Repository`, or component-scanned `@Configuration`.
- App uses Hibernate `ddl-auto: validate` for relational schema verification.
- Adapter-local Flyway migrations exist for adapter-owned tables.
- jOOQ adapters wire build tasks so Flyway-migrated schema verification runs before jOOQ code generation, and `compileJava` depends on generated sources before tests run.
- Selected identifier strategy has matching DDL type, public ID `NOT NULL`/`UNIQUE` lookup constraints when used, ID converter, and ordering expectations.
- Paged search tests assert count, paging metadata, stable order, and result body.

## Layered Test Strategy

- Core service tests instantiate the real `*ServiceImpl` and fake only external boundaries such as `*Store`, SPI, readers, or recorders.
- Core service tests do not use real persistence adapters and must not add `core -> adapter` or `core -> app` dependencies for testing.
- Persistence adapter tests exercise the real `Jpa*StoreAdapter`, `Jooq*StoreAdapter`, or `InMemory*StoreAdapter`; do not fake the adapter under test.
- jOOQ-backed adapter tests verify JPA entities and Hibernate validation exist, while Store reads/writes go through the real jOOQ adapter.
- SQL, join, projection, unique constraint, ordering, paging, and dialect behavior tests use the real target database product, preferably with Testcontainers.
- Persistence integration tests apply Flyway migrations from the runtime classpath, such as `classpath:db/migration`, so adapter-owned migrations are included. Do not hard-code `app/src/main/resources/db/migration` unless the test is specifically for app-only migrations.
- App tests cover controllers, security, common response envelopes, module composition, selected adapter imports, and bean wiring.
- Service plus real adapter tests live in an adapter or app test source set and are integration tests, not core unit tests.

Common test-design failures to reject:

- Adding production or test dependencies from `core` to a persistence adapter just to run a convenient service test.
- Replacing the target MariaDB/MySQL/PostgreSQL behavior with H2 for SQL, constraint, projection, ordering, or dialect-sensitive tests.
- Hard-coding app migration paths in reusable adapter tests, which hides adapter-owned Flyway migrations.
- Faking the `*StoreAdapter` class in a persistence adapter test instead of testing the real adapter implementation.
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
