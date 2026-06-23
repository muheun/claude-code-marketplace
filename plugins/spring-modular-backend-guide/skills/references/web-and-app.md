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

Controller request DTOs are HTTP contracts, not service or persistence contracts. They may carry web concerns such as binding shape, validation annotations, request defaults, OpenAPI descriptions, string enum inputs, multipart fields, or client compatibility choices. Map them in the controller or app workflow to either scalar service arguments for simple operations or a web-neutral `*:api` command for non-trivial use cases.

External boundaries may receive string enum inputs. Do not scatter raw `Enum.valueOf(...)` calls or private `parseXxxOrDefault` helpers across controllers, Slack/LLM command handlers, or batch input adapters. Prefer a small app-owned parser or mapper when the same policy is reused by multiple entry points. Keep channel-specific aliases, defaults, compatibility tokens, and user-facing messages in app-owned mappers, parsers, request validation, or exception mapping. Call a domain enum factory only when the accepted token is a web-neutral canonical domain code or name, and keep that factory free of Spring, Jackson, OpenAPI, localization, and response-envelope concerns.

Create and update request DTOs may stay separate even when their current fields match if endpoint meaning, OpenAPI schema name, validation/defaulting, client compatibility, allowed/immutable fields, optimistic-lock tokens, or change-reason fields can evolve independently. This split threshold is looser than service or Store command granularity; splitting HTTP request DTOs does not require matching service or Store command types unless their use-case or persistence write intent also differs. Share an app request DTO only when multiple endpoints intentionally expose the same HTTP contract and validation, defaults, schema meaning, and client compatibility are the same. Do not split every request mechanically just to mirror methods.

Do not pass app request DTOs into domain service contracts, Store contracts, or persistence adapters. Do not add Spring MVC, Jackson-only, Swagger/OpenAPI, or servlet concerns to domain `api` command/result types just to avoid a mapping step. A small mapping at the app boundary is cheaper than coupling a reusable module to one HTTP shape.

App workflows may pass an existing public, web-neutral service command after the app boundary has mapped the HTTP request. Do not bind that command directly as the controller request body when the HTTP shape has validation, naming, client compatibility, defaulting, multipart composition, or app-only metadata; keep a separate app request DTO and map explicitly.

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
