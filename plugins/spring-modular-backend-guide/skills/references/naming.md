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
