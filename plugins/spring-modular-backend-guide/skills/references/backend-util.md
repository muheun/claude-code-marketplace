# backend-util Reference

For Fixelsoft internal Spring backend projects, recommend DB-neutral `backend-util` common/json-common utilities, but keep adoption a project choice. When the project opts in, check the utility first before adding repeated local helper methods for common null/default/parsing/list/json behavior.

## Dependencies

Prefer `fixel-util-json-common` for reusable modules that opt into common utilities, `Params`, or DB-neutral paging/search contracts. Use `implementation` for helper-only usage:

```kotlin
dependencies {
    implementation("com.fixelsoft.util:fixel-util-json-common:<approved-version>")
}
```

Use `api` only when the module intentionally exposes `backend-util` public contract types — the artifact is already exposed with `api` scope elsewhere in the project build, or the contract is listed in the project's architecture notes:

```kotlin
dependencies {
    api("com.fixelsoft.util:fixel-util-json-common:<approved-version>")
}
```

Do not add Spring/DB bundles such as `fixel-util-spring4-db` to reusable domain `api/core` modules.

## Common Utilities

When a project uses `backend-util`, actively check these utilities before writing equivalent repeated local code:

| Utility | Prefer for | Avoid using for |
|---|---|---|
| `StringUtil` | null-safe blank checks, trim/default handling, prefix/suffix helpers | replacing clear domain validation messages or one-off string assembly |
| `NumberUtil` | null/default numeric conversion, string/object numeric parsing, number formatting helpers | replacing straightforward domain arithmetic such as `BigDecimal` calculations |
| `DateUtil` | string-to-date/time conversion, date/time formatting, shared conversion exception policy | wrapping already-typed `LocalDate`/`LocalDateTime` domain calculations |
| `ListUtil` | null-safe list creation, mutable list helpers, common filtering/collection setup | replacing simple `List.of(...)`, `List.copyOf(...)`, or readable stream pipelines mechanically |
| `Params` | dynamic JSON, webhook payloads, audit details, metadata, loose key-value payloads | replacing typed request/response DTOs, service commands, domain models, or Store commands |

Examples:

```java
if (StringUtil.isNotBlank(request.halfDayType())) {
    halfDayType = appHalfDayTypeParser.parse(request.halfDayType());
}

String normalized = StringUtil.trimToEmpty(value);
LocalDate date = DateUtil.toLocalDate(dateText);
Params<Object> detail = Params.obj("memberId", memberId)
        .putParam("reason", reason);
```

## Boundary Rules

- Domain `api` may expose DB-neutral `backend-util` types only for explicitly approved public contracts, commonly paging/search. Utility helper classes should remain implementation details.
- Do not use `Params` to avoid designing explicit DTOs or commands. If the payload has a stable public shape, use a typed record/class. Typed `*Search` getters/setters that store filters in `Paging.getParams()` are the approved paging use of that bag, not this prohibition; see `persistence.md` (Search And Paging).
- Do not convert ordinary style preferences into architecture tests that ban all direct Java standard-library use. Review repeated helper code and changed code instead.
- When existing code already uses project-local helpers, prefer incremental cleanup near the changed code over broad rewrites.

## Internationalization Extraction Gate

For i18n utility extraction criteria, `MessageSource` usage boundaries, and bundle ownership rules, see `i18n.md`, the canonical source.
