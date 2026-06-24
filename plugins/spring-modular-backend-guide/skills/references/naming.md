# Naming Reference

## Java Import Ordering

Follow the IntelliJ import layout used by the project, then sort alphabetically
inside each layout group.

Default IntelliJ layout:

```text
import module imports
import all other imports

import javax.*
import java.*

import static all other imports
```

Rules:
- Keep the IntelliJ layout order exactly as configured, including adjacent entries that render without a blank line in Java source.
- Sort imports alphabetically by the complete path after `import` only inside each layout entry.
- Do not invent extra package-type groups such as `model`, `event`, or `service`.
- Nested type imports stay in the sorted position for their full path within the current layout group.
- Do not add imports for classes from the same package as the current Java file.
- Remove same-package imports only when your own change introduced them or the user explicitly asked for import cleanup.
- Do not use wildcard imports unless the existing project formatter requires them.
- If a repository has an established formatter or import layout, follow that layout instead of rewriting unrelated imports.

## Java Test Helper Formatting

When adding or changing Java tests, keep existing multiline helper method parameter alignment unless the helper signature itself is part of the requested change.

Do not re-align existing helper parameters while trying to remove unrelated diffs. If a test change only adds a new case, the final diff should not contain parameter alignment changes in existing helper methods.

## Service Method Names

Service interfaces use application/use-case vocabulary.

Allowed default prefixes:

```text
get*
save*
modify*
remove*
exists*
```

Allowed when they are explicit domain actions:

```text
attach*
publish*
close*
approve*
```

Avoid these in service interfaces:

```text
find*
select*
insert*
update*
delete*
list*
create*
add*
```

Example:

```java
BoardPostService.save(command)
BoardPostService.get(postId)
BoardPostService.exists(postId)

CommentService.save(command)
CommentService.get(search)

FileAttachmentService.attach(command)
FileAttachmentService.get(search)
```

## Service Input Names

Service contracts live in domain `api`, so their inputs must describe use-case intent instead of HTTP request shape or database columns.

Scalar parameters are fine for simple reads, existence checks, deletes, and tiny state changes when the meaning is obvious:

```java
AlertScheduleService.get(id)
AlertScheduleService.exists(name)
AlertScheduleService.remove(id)
AlertScheduleService.modifyStatus(id, status)
```

Use a `*:api` command/value record for non-trivial write use cases, especially when a method has several fields, repeats primitive/String types, owns validation/defaulting, is likely to grow, or would otherwise pass controller request fields straight through the service layer:

```java
AlertScheduleService.save(AlertScheduleSave command)
AlertScheduleService.modify(AlertScheduleModify command)
```

Service command names should express the use case, not the adapter action. Prefer `LeaveApprovalRequest`, `AlertScheduleSave`, or `MemberInvite` over names that mirror one SQL table or persistence method. Keep service commands web-neutral: no Spring MVC, servlet, Jackson-only, Swagger/OpenAPI, JPA, jOOQ, or Spring Data dependencies.

Do not expose `core.port` Store command records from service contracts. A Store command belongs to persistence write intent; a service command belongs to caller-facing use-case intent. Sharing one input type is acceptable only when that type lives in `api`, is web-neutral and persistence-neutral, and the service use case and Store write have the exact same required fields, validation, and caller knowledge.

Do not create command records mechanically for every one-field or two-field service method. The goal is to make contracts harder to misuse, not to add a DTO layer for every call.

## Enum Input Parsing and Factory Names

Do not call `Enum.valueOf(...)` directly when converting a `String` from a user, API, database row, file, Slack/LLM command, batch job, or integration payload into a domain enum. Route that conversion through a boundary-owned parser/mapper or a domain enum factory so trimming, case policy, invalid-token errors, and compatibility aliases stay centralized.

Use a reusable domain enum factory only when the enum owns a stable web-neutral token such as code, name, or canonical name. Name the factory by the accepted token when ambiguity matters, such as `fromCode` or `fromName`. Use a generic `from` only when the input contract is obvious and domain-neutral.

Internal-only enums do not need factories just because they exist. Add a domain enum factory when parsing a stable domain-owned canonical code or name is repeated, case-insensitive by domain contract, or part of a stable domain input contract. Keep channel aliases, compatibility tokens, and defaults in app-owned parsers. Lookup maps are optional for tiny one-off internal checks; prefer a `private static final` immutable lookup map when parsing is repeated, the enum is large enough that scanning hurts readability, or the factory accepts explicit codes/aliases that would otherwise become scattered conditionals.

`enum -> String` serialization is a separate decision. Calling `.name()` in a persistence adapter or event mapper is acceptable when the stored token is intentionally the enum constant name. Use an explicit `code` plus `fromCode` when stored or public tokens must remain stable across enum renames.

## Service Implementation Names

Service contracts live in domain `api` modules as `*Service` interfaces.

Concrete service implementations live in the matching domain `core` module and use `*ServiceImpl`:

```text
BoardPostService
BoardPostServiceImpl
CachedBoardPostServiceImpl
TenantAwareBoardPostServiceImpl
```

Use extra qualifiers before `ServiceImpl` for non-default decorators, tenant-aware implementations, or cache-aware implementations. Do not name concrete implementations `*Service` without the `Impl` suffix because that makes them look like contracts.

App controllers, command handlers, schedulers, and workflows depend on the `*Service` contract. Direct references to `*ServiceImpl` are limited to app composition/configuration and implementation-focused unit tests.

## Persistence Port Names

Persistence ports live in `core.port` and use `*Store`.

In this guideline, `Store` is the repository-like persistence port owned by `core`. Do not name core ports `*Repository`, and do not expose Spring Data `JpaRepository` as the Store contract or standard Store implementation.

Store methods use persistence/query vocabulary:

```text
select*
insert*
update*
delete*
upsert*
exists*
count*
```

Example:

```java
interface CommentStore {
    Comment insert(CommentCreate command);
    void update(CommentUpdate command);
    long countBy(CommentSearch search);
    List<CommentResult> selectBy(CommentSearch search);
}
```

Store write methods should communicate write intent through the input type, not a long column-shaped parameter list. Use a purpose-specific command/value record such as `CommentCreate` or `CommentUpdate` when an `insert`, `update`, or `upsert` needs more than a few fields, repeats primitive/String types, or has validation rules.

Do not split command records only because one field is nullable, has a default, or is used by only one overload. Split by meaning: different required fields, validation, state transition, audit/event behavior, concurrency policy, or caller knowledge. When the write intent is the same, prefer one command and make defaults explicit.

Do not use app request DTOs, read projections, adapter entities, JPA entities, jOOQ records, or Spring Data types as Store write commands. A domain model may be reused only when it is explicitly the write model and does not carry generated IDs, timestamps, derived flags, or fields outside the write intent; this exception does not apply to app request DTOs, read projections, adapter entities, JPA entities, jOOQ records, or Spring Data types.

## Adapter Names

Adapter implementations include the technology and end in `StoreAdapter`:

```text
PostStore
JpaPostStoreAdapter
JooqPostStoreAdapter
InMemoryPostStoreAdapter
```

Adapter configuration holders use:

```text
<Domain><Technology>PersistenceConfiguration
```

Examples:

```text
BoardJpaPersistenceConfiguration
CommentMemoryPersistenceConfiguration
FileJooqPersistenceConfiguration
```

Do not name persistence implementations `*Repository`, `*Dao`, or `*StoreImpl` in this guideline. Those names hide technology choice or pull the design back toward DB-centric layering.
