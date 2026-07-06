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
ResponseEntity<BoardPostCommentPageResponse> get(PostId postId, CommentSearch search)
```

Request DTOs should be app-local. Commands/results remain in domain `api`. Use the project's ID value objects and converters instead of hard-coding `UUID` in controller examples.

Controller request DTOs are HTTP contracts, not service or persistence contracts. They may carry web concerns such as binding shape, validation annotations, request defaults, OpenAPI descriptions, string enum inputs, multipart fields, or client compatibility choices. Map them in the controller or app workflow to either scalar service arguments for simple operations or a web-neutral `*:api` command for non-trivial use cases.

Controller search parameters may bind directly to a web-neutral `*:api` `*Search` type when it is only a DB-neutral paging/search contract and the app boundary has no extra parsing, normalization, request-only validation/defaulting, scoping, OpenAPI schema customization, or compatibility policy to apply. Do not create a mapper or request DTO only to mirror fields for ordinary Spring query binding or controller-level OpenAPI metadata that describes the same parameter names, types, optionality, and defaults already present in the web-neutral search contract. Use an app-owned DTO or mapper when OpenAPI metadata changes required flags, defaults, aliases, examples, deprecation, validation, or schema shape.

Use an app-owned mapper or request DTO for search input when the HTTP boundary must parse or normalize values (`String -> enum`, date/time strings, inclusive `from/to` ranges such as start-of-day/end-of-day), apply request-specific validation or defaults, force authenticated user or tenant scope, ignore client-supplied fields, preserve client compatibility aliases, document a different OpenAPI parameter shape, or expose a different HTTP parameter shape from the internal search model. When binding an app-owned DTO-like query object, use the project's OpenAPI support to expose the flattened query parameters in Swagger/OpenAPI, such as springdoc `@ParameterObject` on the controller argument plus app DTO field metadata or explicit controller parameters when needed. Keep that policy in app code; do not push Spring/OpenAPI annotations or channel-specific defaults into reusable domain `api` search classes.

External and persistence boundaries may receive string enum inputs. Do not scatter raw `Enum.valueOf(...)` calls or private `parseXxxOrDefault` helpers across controllers, Slack/LLM command handlers, batch input adapters, or persistence row mappers that read stored strings. Prefer a small boundary-owned parser or mapper when the same policy is reused by multiple entry points. Keep channel-specific aliases, defaults, compatibility tokens, and user-facing messages in app-owned mappers, parsers, request validation, or exception mapping. Call a domain enum factory only when the accepted token is a web-neutral canonical domain code or name, and keep that factory free of Spring, Jackson, OpenAPI, localization, and response-envelope concerns. This rule covers `String -> enum` parsing; it does not forbid `.name()` when an adapter intentionally serializes an enum to the stored canonical token.

Create and update request DTOs may stay separate even when their current fields match if endpoint meaning, OpenAPI schema name, validation/defaulting, client compatibility, allowed/immutable fields, optimistic-lock tokens, or change-reason fields can evolve independently. This split threshold is looser than service or Store command granularity; splitting HTTP request DTOs does not require matching service or Store command types unless their use-case or persistence write intent also differs. Share an app request DTO only when multiple endpoints intentionally expose the same HTTP contract and validation, defaults, schema meaning, and client compatibility are the same. Do not split every request mechanically just to mirror methods.

Do not pass app request DTOs into domain service contracts, Store contracts, or persistence adapters. Do not add Spring MVC, Jackson-only, Swagger/OpenAPI, or servlet concerns to domain `api` command/result types just to avoid a mapping step. A small mapping at the app boundary is cheaper than coupling a reusable module to one HTTP shape.

App workflows may pass an existing public, web-neutral service command after the app boundary has mapped the HTTP request. Do not bind that command directly as the controller request body when the HTTP shape has validation, naming, client compatibility, defaulting, multipart composition, or app-only metadata; keep a separate app request DTO and map explicitly.

Single-item domain `api` result DTOs may be used directly as the success response body when they already match the public response shape and contain no web-only annotations. If a project explicitly uses a success envelope, they may also be used as the `ApiResponse.data` payload. This does not make them HTTP response DTOs; keep them web-neutral. Search/Paging DTOs should usually be converted to app response DTOs. Persistence adapters must not project directly into app response DTOs.

## Exception Response Envelope

Do not force successful controller responses into `ApiResponse` by default. Success response shape follows the project's public API contract: direct DTOs, `ResponseEntity<T>`, or a project-standard success envelope are all acceptable when chosen intentionally.

Exception responses should be centralized through `@RestControllerAdvice`, or `@ControllerAdvice` plus `@ResponseBody` when the project needs broader MVC advice behavior. Put this common error response support in `shared:web-support` or `app`, not in domain modules. Use the project-selected `ApiResponse`-style envelope for exception responses:

```json
{
  "status": 400,
  "message": "invalid request",
  "data": {}
}
```

Rules:

- For new scaffolds, default exception responses to `status`, `message`, and `data`. In existing projects, preserve the established error envelope unless the task explicitly includes a response-contract migration.
- Do not add a boolean `success` field to the common error response. HTTP status expresses success/failure.
- `status` must match the real HTTP status code.
- Add a `code` or message-key field only when the project has an explicit centralized client-code or i18n/message-key strategy. Do not require it by default.
- `message` may be fixed text or a safe exception message.
- For error responses, use `{}` for `data` unless the project has a different established empty payload convention.
- Add `errors` only when validation error handling is intentionally designed.

## Basic Exception Handler

Default mappings:

```text
IllegalArgumentException -> 400 Bad Request
IllegalStateException -> 409 Conflict
Exception -> 500 Internal Server Error
```

4xx exceptions may expose user-safe messages through the centralized error envelope. 5xx fallback must not expose internal exception messages.

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
