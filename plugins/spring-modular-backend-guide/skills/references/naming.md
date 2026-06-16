# Naming Reference

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
    Comment insert(Comment comment);
    long countBy(CommentSearch search);
    List<CommentResult> selectBy(CommentSearch search);
}
```

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
