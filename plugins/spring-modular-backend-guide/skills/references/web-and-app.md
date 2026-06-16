# Web And App Reference

## Controller Placement

HTTP controllers and HTTP request/response DTOs belong in `app`, not in domain modules.

Good:

```text
app/.../board/web/post/PostController
app/.../board/web/comment/BoardPostCommentController
app/.../board/web/attachment/BoardPostFileAttachmentController
```

Avoid:

```text
comment/adapter/web/PostCommentController
file/adapter/web/PostFileAttachmentController
```

Reusable modules should expose service APIs and SPI contracts, not HTTP adapters.

## App DTOs

Keep reusable module Search DTOs out of HTTP responses when practical. Convert them to app response DTOs:

```java
ResponseEntity<ApiResponse<BoardPostCommentPageResponse>> get(PostId postId, CommentSearch search)
```

Request DTOs should be app-local. Commands/results remain in domain `api`. Use the project's ID value objects and converters instead of hard-coding `UUID` in controller examples.

Single-item domain `api` result DTOs may be used directly as the `ApiResponse.data` payload when they already match the public response shape and contain no web-only annotations. This does not make them HTTP response DTOs; keep them web-neutral. Search/Paging DTOs should usually be wrapped in app response DTOs. Persistence adapters must not project directly into app response DTOs.

## Response Envelope

Use `shared:web-support` for a common envelope:

```json
{
  "status": 200,
  "code": "common.ok",
  "message": "success",
  "data": {}
}
```

Rules:

- No boolean `success` field. HTTP status expresses success/failure.
- `status` must match the real HTTP status code.
- `code` is for client branching and future message keys.
- `message` may be fixed text or a safe exception message.
- `data` is the success payload. For empty or error responses, use `{}`.
- Add `errors` only when validation error handling is intentionally designed.

## Basic Exception Handler

Default mappings:

```text
IllegalArgumentException -> 400 Bad Request
IllegalStateException -> 409 Conflict
Exception -> 500 Internal Server Error
```

4xx exceptions may expose user-safe messages. 5xx fallback must not expose internal exception messages.

## Adapter Selection

Persistence adapters must not self-register with `@Component`.

Each adapter module provides a configuration holder with `@Bean` methods. The app imports only selected holders:

```java
@Import({
    BoardJpaPersistenceConfiguration.class,
    CommentJpaPersistenceConfiguration.class,
    FileMemoryPersistenceConfiguration.class
})
class ApplicationComposition {
}
```

Do not annotate adapter configuration holders with `@Configuration` if component scanning could activate unselected adapters. App imports the selected holder explicitly.
