# Caching (Caffeine / Valkey / Redis)

## Contents

- [Implementation Selection Gate](#implementation-selection-gate)
- [When to Add a Cache](#when-to-add-a-cache)
- [Module Placement and Ownership](#module-placement-and-ownership)
- [Logical Identity and Physical Encoding](#logical-identity-and-physical-encoding)
- [Invalidation and Failure Policy](#invalidation-and-failure-policy)
- [Managed and Commercial Services](#managed-and-commercial-services)
- [Testing](#testing)
- [Common Mistakes](#common-mistakes)

## Implementation Selection Gate

- Default to local Caffeine when each application instance may warm its own working set independently and the overlap-plus-TTL bound (see Invalidation and Failure Policy) is sufficient. A multi-instance deployment alone does not require a remote cache.
- Choose shared Valkey by default only when multiple instances require shared cache state, coordinated cross-instance invalidation, or a shared working set. Dev runs the official `valkey/valkey` image via Docker Compose.
- Redis remains acceptable when it is an established project standard. For a new selection, note that its license changed in 2024 (RSALv2/SSPLv1; Redis 8 added AGPLv3) and verify that the chosen version's license fits.
- Do not select a paid or managed service (AWS ElastiCache, GCP Memorystore, Azure Cache, Redis Enterprise, and similar) by default. Choose one only when the project already runs it or the user explicitly opts in; then apply the Managed and Commercial Services section.
- For a shared cache, use Lettuce via `spring-boot-starter-data-redis` (Boot's default). It speaks RESP, so Valkey and Redis are interchangeable through configuration — keep it that way; do not code against server-specific modules by default.
- Use `<version>` placeholders or the project version catalog; resolve actual versions from the project build.

## When to Add a Cache

Add a cache only when all three hold; otherwise skip it (smallest sufficient change):

- The read is demonstrably hot or expensive (measured, or explicitly stated by the user).
- Bounded staleness is acceptable, a concrete TTL can be named, and the overlap-plus-TTL bound fits the use case (or load completion is bounded or stale fills are fenced).
- Every write has an explicit invalidation scope: affected variants are enumerable, covered by generation/tag/namespace invalidation, or assigned an explicitly accepted TTL-only policy when they cannot be enumerated.

## Module Placement and Ownership

| Concern | Owner |
|---|---|
| Cache port (e.g., `MemberProfileCache`: `get`/`put`/`evict`) | `<domain>:core` `core.port` |
| Cache semantics and logical identity (what is cached, every visibility dimension, read-through, evict-on-write) | `<domain>:core` caching `*ServiceImpl` decorator |
| Physical key encoding and value serialization | `<domain>:adapter:cache-caffeine` or `<domain>:adapter:cache-redis` |
| TTL values and server endpoint per environment | `app` configuration (`@ConfigurationProperties`) |
| Implementation selection (none, Caffeine, Valkey, or established Redis) | `app` composition (`@Import` of the selected adapter configuration) |

- Name the adapter module `cache-redis` after the wire protocol/technology (RESP/Redis), not the selected server product; Valkey is the server behind it and swaps in or out through configuration alone.
- Do not put `@Cacheable` on core services: it drags Spring proxy semantics and a `CacheManager` contract into `core`, and the behavior disappears in plain unit tests. Cache behavior belongs in an explicit decorator composed by `app`.
- The cached value is the technology-neutral result type from `*:api`; serialization (JSON via Jackson) stays inside the adapter.
- The cache port must pass the Interface Split Gate in `architecture.md` (it does when it hides server, serialization, and key format from `core`); the decorator must pass the Class Extraction Gate.

## Logical Identity and Physical Encoding

The use case owns logical cache identity. Include every input or visibility boundary that can change the authorized returned representation, as applicable:

- Resource or domain identity.
- Tenant, organization, or workspace boundary.
- Current authorization/visibility scope or a stable version of it when permissions change fields or results. User identity alone is not a substitute because the same user can remain authorized while losing visible fields.
- Locale when the cached representation is localized.
- Canonical query, filter, sort, page, and projection inputs.
- Representation or schema version when incompatible cached payloads can coexist during a deployment.

The use case supplies these semantic dimensions explicitly; the adapter must not infer authorization, tenancy, locale, or query meaning from ambient framework state. Omitting a varying dimension is a data-isolation or correctness defect, not a serialization preference.

Cached data is never the authority for access control. Evaluate authorization against an authoritative source before returning cached data; a cache hit may accelerate representation lookup but must not grant access that current authoritative state denies. For permission-filtered representations, either include the current visibility scope/version in logical identity and invalidate every affected variant when authorization changes, or cache permission-neutral data and authoritatively reproject it after every hit.

The adapter owns the physical encoding: namespace and version prefixes, delimiters or escaping, canonical byte/string encoding, optional hashing, and value serialization. Encoding must be unambiguous. If hashing is used, hash the canonical logical identity with a sufficiently wide, collision-resistant, domain-separated digest; weak or truncated hashes must not collapse tenant, permission, locale, query, projection, or representation isolation dimensions. Never place passwords, access tokens, session secrets, secret API keys, or other credentials in cache keys. When an identifier is sensitive in operational tooling, encode or hash it according to the project's observability and privacy policy without removing the logical isolation dimension.

## Invalidation and Failure Policy

- Default: cache-aside with delete-on-write. Invalidate after the database transaction commits; a rollback must not publish an invalidation as though the write succeeded. When there is no database transaction, invalidate only after the write succeeds.
- Define a write-to-invalidation-scope mapping before enabling the cache. Every write must invalidate all affected permission, locale, canonical query, page, projection, and representation variants. Use an enumerated key family when finite, generation/tag/namespace invalidation when variants are not safely enumerable, or an explicitly accepted TTL-only policy for remaining variants whose bounded staleness is safe.
- Pre-commit eviction is permitted only as an additional safeguard. It cannot replace post-commit invalidation because a concurrent reader can refill the old value before the transaction commits.
- **Overlap-plus-TTL bound** (canonical definition): after post-commit eviction, a reader whose authoritative load began before the commit can still complete later and refill a stale value. TTL bounds residency from that stale put only when expiry is non-renewing absolute/expire-after-write; reads and hits must not extend its deadline. Unless load completion is bounded or stale fills are fenced, the commit-to-fresh worst case is the remaining duration of the last overlapping load plus TTL; an unbounded load means TTL alone does not bound commit-to-fresh time.
- TTL alone provides no immediate read-your-write guarantee. Bound load completion or fence stale fills only when the use case requires a finite or shorter commit-to-fresh bound; otherwise confirm that the overlap-plus-TTL bound fits the accepted staleness budget.
- Do not re-put the write's view after a write; it races with concurrent writers and can pin a stale value for a full TTL.
- TTL is a required, validated app configuration value, and expiry uses non-renewing absolute/expire-after-write semantics. If the value is absent, zero, negative, or otherwise invalid, fail startup or disable the cache according to an explicit safe policy. A positive adapter default is not universally safe; never cache without a validated expiry contract.
- For ordinary performance caches, `get`/`put` failures log a warning and fall through to the store; those failures do not fail the read path.
- A failed `evict` always logs an error but does not have one unconditional fallback. TTL-only fallback is allowed only where the resulting staleness is explicitly accepted. If stale data could grant access, delay immediate revocation, or violate another correctness-critical contract, apply an explicit safe policy such as bypassing or disabling the affected cache until recovery, or failing closed.
- Require a stronger strategy than post-commit eviction plus TTL when immediate read-your-write, immediate revocation, or another correctness-critical contract requires it. Record the chosen coordination, fencing, bypass, or fail-closed strategy and its failure behavior; do not add stronger coordination preemptively for ordinary bounded-stale reads.

## Managed and Commercial Services

Apply when the project has explicitly opted into a paid or managed cache:

- Keep the adapter on plain RESP through Spring Data Redis so the code ports back to self-hosted Valkey unchanged; provider-specific features (Redis Enterprise modules, provider auth) stay in `app` configuration or a dedicated adapter.
- TLS, AUTH tokens, and endpoints come from app configuration and the secret store, not code.
- State the cost consequence in the change description and get the user's confirmation before adding the dependency.
- Tests still run against the open-source `valkey/valkey` image via Testcontainers; provider behavior is verified in staging.

## Testing

- Shared-cache adapter integration tests use Testcontainers with the `valkey/valkey` image (or the project's actual server image) — never an in-memory map or embedded substitute standing in for the real server. Caffeine adapter tests exercise the real local implementation with controlled expiry where TTL behavior matters.
- Decorator tests in `core` use a hand-written map-backed fake for the cache port (state matters: hit-after-put, evict-then-miss) and a Mockito mock for the delegate service.
- Test that logically distinct tenant, current visibility scope/version, locale, query, projection, and representation-version inputs cannot collide when those dimensions affect visibility. Assert logical isolation and put/get/evict behavior, including hashed encodings, without freezing incidental delimiter, field-order, JSON, digest, or the full physical key.
- Authorization tests prove that a cached representation never bypasses an authoritative denial and that a user who remains authorized but loses fields cannot receive the formerly visible fields after a hit. Exercise either visibility-version invalidation for every affected variant or authoritative reprojection of permission-neutral data.
- Failure-policy tests cover store fallback for ordinary `get`/`put` failures and the selected bypass, disable, or fail-closed behavior when eviction failure could expose unsafe stale data.
- When TTL-only fallback after failed eviction is selected, tests or an explicit use-case assertion establish that the resulting staleness is accepted.
- Namespace, key-version, and isolation dimensions may be asserted when they are deliberate compatibility or data-separation contracts. Keep those assertions at the contract level; do not turn the adapter's entire serialized key string into a golden value.
- Transaction-focused tests prove a committed write invalidates and a rolled-back write does not.
- For each write-to-invalidation-scope mapping, test every affected permission, locale, query, page, projection, and representation variant, or the selected generation/tag/namespace or accepted TTL-only policy.
- Stale-fill tests model a load that overlaps the commit and verify the overlap-plus-TTL bound; repeated-hit tests continue through the expiry deadline and prove reads do not renew it. When load completion is bounded or stale fills are fenced, test that contract without freezing a particular concurrency implementation.
- App configuration tests prove a valid TTL is bound and that absent or invalid TTL follows the selected fail-startup or cache-disabled policy.
- App wiring test asserts the service bean is the caching composition when the adapter is imported.

## Common Mistakes

- `@Cacheable`, `CacheManager`, or client types (`RedisTemplate`, Lettuce) referenced from `api`/`core`.
- Selecting a shared cache merely because the application has multiple instances, despite per-instance bounded staleness being sufficient.
- Treating user identity as current authorization scope, or omitting tenant, visibility-version, locale, query, projection, or representation-version dimensions that change the visible result.
- Letting the adapter invent logical visibility dimensions, or putting credentials in a physical key.
- Using ambiguous physical encoding or a weak/truncated hash that can collapse logical isolation dimensions.
- Caching without a validated app-configured TTL, using a positive adapter default as a universal fallback, or renewing expiry on reads.
- Evicting only before commit, re-putting the write payload instead of invalidating after commit, or invalidating only one key while affected permission, locale, query, page, projection, or representation variants remain.
- Letting `get`/`put` failures escape from an ordinary performance cache, or unconditionally swallowing a failed eviction when stale data could grant access or break a correctness-critical contract.
- Selecting a managed cache service in the design without a project opt-in on record.
- Tests asserting exact serialized key strings when only namespace, version, or isolation is contractual.
