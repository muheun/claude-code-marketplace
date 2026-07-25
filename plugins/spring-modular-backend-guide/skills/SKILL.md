---
name: spring-modular-backend-guide
description: Use when designing, scaffolding, reviewing, or modifying Java Spring Boot DDD-style multi-module backends involving api/core/adapter boundaries, app-owned Servlet MVC composition, controller DTOs, enum input parsing, i18n/MessageSource/localized errors or notifications, QueryDSL/jOOQ/Flyway persistence, identifier strategy, Kafka messaging/event publishing/outbox, Caffeine/Valkey/Redis caching, Java imports, Java test helper formatting, layered tests, Mockito/fakes/Testcontainers, response envelopes, helper extraction, Spring bean granularity, or backend-util utilities.
---

# Spring Modular Backend Guide

## Overview

Use this skill to build or review Java Spring Boot backends with reusable bounded-context modules. Core rule: domain modules expose public contracts and adapters; the app module owns HTTP endpoints, composition, and cross-domain wiring. HTTP and Security guidance targets the Servlet MVC stack; do not transplant its resolver, filter, or handler contracts into WebFlux.

This is an opinionated guideline for new scaffolds and architecture reviews. Do not apply it to non-Spring projects, frontend work, or small throwaway prototypes unless the user explicitly wants this structure.

## Workflow

1. Confirm the project is Java Spring Boot from the applicable build descriptors. For Gradle, read `settings.gradle[.kts]`, the relevant root and module `build.gradle[.kts]`, and any version catalog or convention plugin. For Maven, read the relevant `pom.xml`, parent POM, and imported BOM.
2. Before applying version-sensitive guidance, record the configured Java toolchain/release, the JDK actually used by build and test commands, and the resolved Spring Boot, Spring Framework, Spring Security, and touched Spring extension versions. Use dependency insight, a dependency tree, or the effective POM when a BOM or plugin controls transitive versions. Verify API behavior against matching official documentation or tagged source; do not substitute documentation from another JDK or Spring generation without proving compatibility. If an exact version cannot be resolved, state the uncertainty and do not present a version-specific conclusion as confirmed.
3. Identify the work type and read only the needed references. Use the most specific row and combine rows only when the task crosses work types:

| Work type | Required reference |
|---|---|
| New project, scaffold, or module structure | `references/architecture.md`, `references/build-setup.md`, and `references/testing-checklist.md` |
| Architecture design, responsibility separation, or refactoring strategy | `references/architecture.md`, `references/anti-patterns.md`, and `references/testing-checklist.md` |
| Service, Store, SPI, Reader, or Notifier contract granularity | `references/architecture.md` and `references/testing-checklist.md` |
| Helper class extraction, one-consumer Spring bean, or app-local helper review | `references/architecture.md`, `references/anti-patterns.md`, and `references/testing-checklist.md` |
| Controller DTO, Service command, or Store command boundary | `references/web-and-app.md`, `references/naming.md`, `references/persistence.md`, `references/testing-checklist.md`, and `references/anti-patterns.md` |
| Store write input design or review | `references/naming.md`, `references/persistence.md`, `references/testing-checklist.md`, and `references/anti-patterns.md` |
| Service, Store, adapter names, Java import ordering, or Java test helper formatting | `references/naming.md` |
| Fixelsoft internal backend-util dependencies, common utilities, `StringUtil`, `NumberUtil`, `DateUtil`, `ListUtil`, or `Params` | `references/build-setup.md` and `references/backend-util.md` |
| JPA, QueryDSL, jOOQ, Flyway, paging, identifier strategy | `references/persistence.md` and `references/build-setup.md` |
| Controllers, DTOs, string enum input parsing, app composition, response envelope | `references/web-and-app.md` and `references/naming.md` |
| Kafka, messaging, event publishing or consuming, outbox, topic contracts | `references/messaging.md`, `references/architecture.md`, and `references/testing-checklist.md` |
| Caffeine/Valkey/Redis caching, cache selection, cache keys, TTL, cache invalidation | `references/caching.md`, `references/architecture.md`, and `references/testing-checklist.md` |
| Internationalization/i18n, localization, `MessageSource`, message keys, or non-HTTP notifications | `references/i18n.md` |
| Servlet MVC locale selection, localized HTTP errors, or localized Spring Security responses | `references/i18n.md` and `references/web-and-app.md` |
| Internationalization test strategy | `references/i18n.md` and `references/testing-checklist.md` |
| Reusable comment/file-like modules or cross-domain validation | `references/spi-and-reuse.md` |
| Gradle dependencies, build plugin placement, or jOOQ codegen setup | `references/build-setup.md` and `references/persistence.md` |
| Architecture test implementation | `references/testing-checklist.md` and `references/architecture-tests.md` |
| Layered service, persistence, or app test strategy | `references/testing-checklist.md` and `references/persistence.md` |
| Code review or readiness check | `references/anti-patterns.md`, `references/testing-checklist.md`, and any changed-area references above |

4. Apply the core guardrails below, then follow the loaded references for detailed judgment.
5. Before writing persistence adapter code, make the selected technology contract explicit from `references/persistence.md` and `references/build-setup.md`. In this guide, choosing JPA means using JPA with QueryDSL for Store reads unless the user explicitly rejects QueryDSL for the project.
6. Verify with focused behavior, wiring, build, layer, or architecture checks that match the changed boundary; then run the full available build/test command.

## Core Guardrails

- Domain modules use `api`, `core`, and technology adapters (`adapter:persistence-*`, `adapter:messaging-*`, `adapter:cache-*`); app owns web controllers and host-specific DTOs.
- Domain `api/core` modules do not depend on app, web-support, technology adapters, Spring MVC, JPA, DB technology, or other bounded contexts unless a reference explicitly allows it.
- Reusable modules expose service APIs and SPI contracts; app or host composition owns HTTP endpoints, adapter selection, and cross-domain wiring.
- Controller request DTOs are app-owned HTTP contracts. Service commands live in `*:api`; Store commands live in `core.port`. Share command types only when the boundary and write intent are truly identical.
- Store write methods do not receive app DTOs, adapter entities, JPA/jOOQ/Spring Data types, read projections, or HTTP contracts.
- Persistence choices are explicit: JPA means QueryDSL projection reads by default; jOOQ keeps JPA entities for Hibernate validation but uses jOOQ DSL for reads/writes; schema changes go through Flyway.
- Naming, enum parsing, response envelopes, adapter registration, and import ordering are design/review rules first. Add static enforcement only when the project treats the policy as stable or the task explicitly touches that boundary.
- Domain modules own error and event meaning; app or outbound presentation boundaries select locale and render user-facing text. Keep `MessageSource`, `LocaleContextHolder`, translated sentences, and channel-specific templates out of reusable `api/core` modules.
- Keep logical messaging and cache contracts framework-neutral in `api/core`. Kafka producer/client types stay in messaging adapters and cache-client types in cache adapters. Outbound messaging adapters may implement their bounded context's `core` ports; reusable inbound messaging adapters may call that context's framework-neutral `api`; neither depends on app, web-support, or another bounded context. App may own host-specific inbound listeners, and implementation selection follows the documented messaging and cache selection gates.
- Tests follow dependency direction. Prefer focused behavior, wiring, layer, and build checks; use architecture tests only for stable boundaries ordinary tests cannot protect cheaply.
- For Fixelsoft internal projects, recommend approved DB-neutral `backend-util` common/json-common utilities when the project opts in, but keep DB/Spring utility bundles out of reusable domain contracts.

## Frequent Failure Signals

If you see any of the following, read `references/anti-patterns.md` plus the changed-area references from the routing table before editing:

- Controllers in domain modules; app DTOs passed into service/store contracts.
- One-method interfaces with no distinct role; one-consumer app helper beans extracted from private methods.
- `MessageSource` or `LocaleContextHolder` in reusable domain logic; translated exception sentences used as service contracts.
- JPA entity fetch reads used as the default Store read model; direct `Enum.valueOf(...)` parsing at boundaries.
- `KafkaTemplate`/`@KafkaListener`/cache client types or `@Cacheable` in `api/core` modules.
- One unacknowledged Kafka record treated as a partition barrier; processed-event uniqueness shared across independent subscriptions.
- User identity treated as current visibility scope; incomplete cache invalidation; read-renewed expiry; weak/truncated hashed cache keys.
- Paid managed brokers or caches selected without a project opt-in.
- Broad source scans for review-only preferences; build checks that blacklist open-ended external coordinates.

## Completion Checklist

- Loaded every reference required by the work type and any changed-area reference.
- For version-sensitive work, recorded the configured Java toolchain/release, the JDK used by verification commands, and resolved versions for the touched Spring stack; version-sensitive claims use matching official documentation or tagged source.
- Module boundaries, command/DTO ownership, persistence technology, and test scope match the relevant references.
- Extracted helper classes or Spring beans pass the Class Extraction Gate; otherwise keep the logic local.
- New Service, Store, SPI, Reader, or Notifier contracts pass the Interface Split Gate.
- Localized behavior declares its supported locales, default and fallback policy, message ownership, focused locale tests, and a non-HTTP rendering boundary when async or outbound messages exist.
- When messaging is in scope, state the explicit delivery policy, per-aggregate ordering, partition-barrier behavior, logical-consumer/subscription idempotency scope, and implementation-selection policy.
- When caching is in scope, state current visibility identity or authoritative reprojection, complete write-to-invalidation scope, non-renewing expiry, validated TTL configuration policy, unambiguous collision-resistant encoding, and implementation-selection policy.
- New or changed enforcement checks protect stable boundaries rather than incidental naming, helper shape, or future library coordinates.
- Focused verification passed before the full available build/test command.
