# Naming Reference

## Java Import Ordering

Sort Java imports alphabetically by the fully qualified name after `import`.

Rules:
- Keep regular imports and static imports in separate groups.
- Sort each group by the complete path, not by a package-type category such as `model`, `event`, or `service`.
- Do not move nested type imports after their enclosing package siblings if the full path sorts earlier.
- Do not add imports for classes from the same package as the current Java file.
- Remove same-package imports only when your own change introduced them or the user explicitly asked for import cleanup.
- Do not use wildcard imports unless the existing project formatter requires them.
- If a file has an established formatter or import layout, follow that layout instead of rewriting unrelated imports.

Example:

```java
import com.fixelsoft.hr.BaseConfigTest;
import com.fixelsoft.hr.leave.api.event.LeaveLifecycleEvent.Shared;
import com.fixelsoft.hr.leave.api.event.LeaveLifecycleProcess;
import com.fixelsoft.hr.leave.api.model.LeaveVo;
import com.fixelsoft.hr.leave.api.model.enums.LeaveType;
import com.fixelsoft.hr.leave.api.service.LeaveApprovalService;
import com.fixelsoft.hr.leave.api.service.LeaveApproverService;
import com.fixelsoft.hr.leave.api.service.LeaveBalanceService;
import com.fixelsoft.hr.leave.api.service.LeaveRequestService;
import com.fixelsoft.hr.leave.api.service.LeaveShareRecipientService;
import com.fixelsoft.hr.people.api.service.PeopleMemberService;
```

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
