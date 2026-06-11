# Testing Checklist

Add architecture tests or equivalent checks when this guideline is used for a scaffold. Use `architecture-tests.md` for compact ArchUnit examples.

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
- Store methods start with allowed persistence prefixes.
- Persistence ports end with `Store`.
- Persistence adapter implementations match `(Jpa|Jooq|InMemory)*StoreAdapter`.

## Persistence Rules

- JPA adapters do not depend on `JpaRepository` for standard Store implementation.
- Persistence adapters do not self-register with `@Component`, `@Service`, `@Repository`, or component-scanned `@Configuration`.
- App uses `ddl-auto: validate`.
- Adapter-local Flyway migrations exist for adapter-owned tables.
- Selected identifier strategy has matching DDL type, public ID `NOT NULL`/`UNIQUE` lookup constraints when used, ID converter, and ordering expectations.
- Paged search tests assert count, paging metadata, stable order, and result body.

## Web Rules

- Controller success responses use common envelope.
- Basic exceptions are converted to the common envelope.
- Tests parse JSON structure instead of only checking string fragments.

## Verification Commands

Use the repository-specific commands. For Gradle projects, prefer:

```bash
./gradlew test
git diff --check
```
