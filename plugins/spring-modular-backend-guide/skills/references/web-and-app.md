# Web And App Reference

## Contents

- [Controller Placement](#controller-placement)
- [App DTOs](#app-dtos)
- [Search Binding](#search-binding)
- [Exception Response Envelope](#exception-response-envelope)
- [Basic Exception Handler](#basic-exception-handler)
- [Adapter Selection](#adapter-selection)

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

Keep reusable module Search DTOs out of HTTP responses. Return one directly only when it is web-neutral and already field-for-field identical to the public response contract; otherwise convert it to an app response DTO:

```java
ResponseEntity<BoardPostCommentPageResponse> get(PostId postId, CommentSearch search)
```

Paged list input binding is in [Search Binding](#search-binding). Search type, `Paging` inheritance, and param-bag storage are in `persistence.md` (Search And Paging).

Request DTOs should be app-local. Commands/results remain in domain `api`. Use the project's ID value objects and converters instead of hard-coding `UUID` in controller examples.

Controller request DTOs are HTTP contracts, not service or persistence contracts. They may carry web concerns such as binding shape, validation annotations, request defaults, OpenAPI descriptions, string enum inputs, multipart fields, or client compatibility choices. Map them in the controller or app workflow to either scalar service arguments for simple operations or a web-neutral `*:api` command for non-trivial use cases.

External and persistence boundaries may receive string enum inputs. The canonical `String -> enum` parsing policy is "Enum Input Parsing and Factory Names" in `naming.md`. For request DTO enum fields, choose the binding by this rule:

- Use a `String` field plus an app-boundary parser when lenient parsing, aliases, or defaults are needed.
- Bind an enum field directly only when exact-match semantics are acceptable. Spring MVC binds query/form/path enum parameters through a case-sensitive built-in converter (effectively `Enum.valueOf`); JSON request-body enum fields follow the project's Jackson deserialization policy instead. In both cases verify that the resulting binding failure maps to the project's 400 response contract.
- Register a `Converter` or an `@InitBinder` editor when one global parsing policy must apply across endpoints.

Create and update request DTOs may stay separate even when their current fields match if endpoint meaning, OpenAPI schema name, validation/defaulting, client compatibility, allowed/immutable fields, optimistic-lock tokens, or change-reason fields can evolve independently. This split threshold is looser than service or Store command granularity; splitting HTTP request DTOs does not require matching service or Store command types unless their use-case or persistence write intent also differs. Share an app request DTO only when multiple endpoints intentionally expose the same HTTP contract and validation, defaults, schema meaning, and client compatibility are the same. Do not split every request mechanically just to mirror methods.

Do not pass app request DTOs into domain service contracts, Store contracts, or persistence adapters. Do not add Spring MVC, Jackson-only, Swagger/OpenAPI, or servlet concerns to domain `api` command/result types just to avoid a mapping step. A small mapping at the app boundary is cheaper than coupling a reusable module to one HTTP shape.

App workflows may pass an existing public, web-neutral service command after the app boundary has mapped the HTTP request. Do not bind that command directly as the controller request body when the HTTP shape has validation, naming, client compatibility, defaulting, multipart composition, or app-only metadata; keep a separate app request DTO and map explicitly.

Single-item domain `api` result DTOs may be used directly as the success response body when they already match the public response shape and contain no web-only annotations. If a project explicitly uses a success envelope, they may also be used as the `ApiResponse.data` payload. This does not make them HTTP response DTOs; keep them web-neutral. Convert Search/Paging DTOs to app response DTOs unless the type is web-neutral and field-for-field identical to the public response contract, including paging metadata. Persistence adapters must not project directly into app response DTOs.

## Search Binding

Paged list endpoints bind a web-neutral `*:api` `*Search` that extends `Paging`. The Search type, param-bag storage, and service/store flow are in `persistence.md` (Search And Paging).

Recipe:

1. If the query parameter names and types match `*Search` accessors, the controller argument is that Search object, annotated `@ModelAttribute`. `page`, `pageSize`, and bindable filters live on Search, not as individual `@RequestParam` values. A controller-parameter `@ParameterObject` may sit next to `@ModelAttribute` so OpenAPI flattens query fields; do not put Spring/OpenAPI annotations on the domain `api` Search class, and do not invent an app DTO only to host those annotations. `@ModelAttribute` binds every public setter; `body` and totals are not query parameters — see `persistence.md` (Search And Paging). An `@InitBinder` allowed-fields list is optional and is not an architecture-test rule.
2. If a value cannot bind as a Search accessor, or must not come from the client, declare it as an extra controller parameter and assign it with `search.set...`. Typical cases: `@AuthenticationPrincipal`, an HTTP-only alias, a value implied by the request path, or a few HTTP-only conversions (enum aliases, date-range expansion, request defaults). Enum token policy is in `naming.md`.
3. If the public HTTP query schema differs from Search accessors in names, types, or conversion, bind an app-owned query object and map to Search. That app object must not redeclare `page`, `pageSize`, or filters whose names and types already match Search. When binding it, flatten query parameters with the project's OpenAPI support, such as springdoc `@ParameterObject` plus app DTO field metadata. Keep Spring/OpenAPI annotations off reusable domain `api` search classes.

```java
CommentPageResponse mine(
        @AuthenticationPrincipal AuthorId authorId,
        @ParameterObject @ModelAttribute CommentSearch search,
        @RequestParam(defaultValue = "false") boolean onlyMine) {
    search.setAuthorId(authorId);
    if (onlyMine) {
        search.setMine(true);
    }
    return CommentPageResponse.from(commentService.get(search));
}
```

Do not create a mapper or request DTO whose fields only repeat Search accessors for ordinary Spring query binding or for controller-level OpenAPI metadata that already matches those accessors.

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

When a Servlet MVC API localizes user-facing text, follow `i18n.md`. Keep error meaning and stable arguments in the owning domain contract, but resolve locale and render the HTTP message in `app` or `shared:web-support`. Report the selected representation with `Content-Language`; include every request-visible locale selector in effective cache keys and ensure validators distinguish localized representations. For a server-side preference that cannot participate in `Vary`, require `private, no-cache` with representation-specific revalidation or use `no-store`. Do not create an `HttpSession` only to persist locale in a stateless application.

Apply the app-owned response policy to ordinary JSON Security handlers because filter-chain failures do not pass through controller advice. Preserve each authentication scheme's status, challenge headers, redirect behavior, media type, and protocol-owned structured error body; OAuth2/OIDC protocol endpoints keep or delegate to their framework handlers instead of using the common application envelope. Each handler calls the shared locale policy directly. If a filter precomputes a request-only selector, use exactly one placement from `i18n.md`: a side-effect-free container filter before the Security `DelegatingFilterProxy`, or a side-effect-free filter inside each affected `SecurityFilterChain` before its earliest relevant failure-producing filter. Never register the same filter in both places. Persist a valid selector only in the final accepted MVC or app-owned Security response handler, because `HttpFirewall` may reject lazily when a wrapped header or parameter is accessed; being merely inside `springSecurityFilterChain` or before `DispatcherServlet` is insufficient.

Treat firewall rejection as a separate global boundary: `FilterChainProxy` invokes one `RequestRejectedHandler` (Spring Security 5.4+), and a rejection may occur before chain selection or later while the firewalled request is accessed. No in-chain locale filter is therefore a reliable prerequisite. Prefer a fixed generic response. If the product explicitly requires localization, use only a bounded, allowlisted selector precomputed by the side-effect-free container filter or the deterministic default; never inspect or echo rejected raw request data, expose the firewall exception, or persist locale in this handler.

## Basic Exception Handler

Default mappings:

```text
IllegalArgumentException -> 400 Bad Request
IllegalStateException -> 409 Conflict
Exception -> 500 Internal Server Error
```

The `IllegalArgumentException -> 400` mapping is a scaffold default only: it can misclassify internal or framework-thrown `IllegalArgumentException` as client errors, so prefer introducing domain exception types for intentional 4xx responses.

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

Default: annotate adapter configuration holders with `@Configuration(proxyBeanMethods = false)` and keep them outside component-scan reach so unselected adapters cannot activate; the app imports the selected holder explicitly. Both under `proxyBeanMethods = false` and in a plain class used via `@Import` (bean lite mode), `@Bean` methods must not call each other directly: singleton semantics are not proxied in either mode, so each direct call creates a new instance. Pass the dependency as a method parameter instead.
