# Architecture Reference

## Contents

- [Change Strategy](#change-strategy)
- [Extraction and Split Gates](#extraction-and-split-gates)
  - [Interface Split Gate](#interface-split-gate)
  - [Class Extraction Gate](#class-extraction-gate)
- [Test Scope Calibration](#test-scope-calibration)
- [Module Structure](#module-structure)
- [Module Roles](#module-roles)
- [Java Package Convention](#java-package-convention)
- [Dependency Direction](#dependency-direction)
- [App Package Shape](#app-package-shape)

## Change Strategy

Prefer small, verifiable architecture changes over one large redesign.

When an area mixes multiple responsibilities, identify the reasons it changes before extracting anything. HTTP representation, use-case orchestration, domain rules, persistence queries, and infrastructure wiring should not be moved as one undifferentiated block.

Separate responsibilities only when the split can be validated. A good split can be protected by module dependencies, package rules, naming rules, persistence rules, web response rules, architecture tests, or focused layer tests. Prefer checks that protect stable boundaries and behavior without freezing incidental implementation details.

Good change units:

- Have one primary reason to change.
- Do not add direct dependencies between bounded contexts.
- Do not make `core` depend on `adapter` or `app`.
- Leave a test, architecture rule, module dependency check, package rule, or focused layer test that would catch the old mixed responsibility.
- Avoid changing structure, behavior, naming, and persistence strategy in the same step unless the user explicitly asks for a larger migration.

A checklist item may record the decision, but it does not protect a boundary by itself.

Small changes do not mean creating many classes by default. Split when change reasons, test boundaries, dependency direction, or reuse boundaries differ.

## Extraction and Split Gates

Split `Service`, `Store`, SPI, Reader, and Notifier contracts by role and change reason, not by method count. Apply the gates below before creating any new contract, class, or Spring bean.

### Interface Split Gate

Before introducing a new contract or moving consumers to it, pass this gate:

- Name the consumer knowledge being hidden, or the dependency direction, reuse boundary, lifecycle, exception policy, cache policy, or implementation possibility the split protects.
- Name the real change reason that makes this boundary useful now.
- Confirm the split protects a dependency direction, reuse boundary, or consumer knowledge boundary, not only a shorter method list.
- Check whether the existing contract would still be cohesive enough; if yes, keep it unless a clearer boundary is needed now.
- Prefer compiler contract changes, focused wiring tests, or behavior tests over architecture rules that freeze the exact new interface name.

A small interface is useful when it hides knowledge a consumer should not have. A new interface name alone does not create a stable boundary.

Prefer separate contracts when:

- Consumers belong to different use cases.
- External concepts differ. For example, Google Calendar attendee email and Slack user id can come from the same member source but should not leak into the same consumer.
- Change reasons, implementations, exception policy, cache behavior, or lifecycle can realistically differ.
- The split hides concepts a consumer should not know.
- Tests get a clearer fake boundary and no longer need inheritance-based fakes or `null` constructor arguments.

Prefer one contract when:

- Methods query the same source in the same way.
- Inputs, lifecycle, and exception policy are the same.
- The methods always move with the same implementation and separate implementations are unlikely.
- The only reason to split is "one method per interface" or test convenience.
- Extra files and wiring increase without protecting a module boundary or dependency direction.

Small interfaces are useful when they protect consumers from unnecessary knowledge. They are over-split when method-level separation only increases files and wiring.

### Class Extraction Gate

Before extracting a private/helper block into a new class or Spring bean, pass this gate:

- Name the concrete second consumer. If there is only the current consumer, extraction must be justified by a non-reuse boundary below; otherwise keep a private method.
- Name the dependency direction, lifecycle, exception policy, cache/transaction policy, implementation possibility, or consumer-knowledge boundary the class protects. "Cleaner file" or "shorter executor/service" is not enough.
- Confirm the extracted method name does not hide side effects. A public or package-visible predicate such as `canExecute`, `hasRole`, or `isAllowed` must not secretly provision members, send messages, write data, or mutate state unless the name makes the side effect explicit.
- Check whether presentation/transport details remain with the caller. If a helper is tightly coupled to one Slack ack flow, controller response, modal update, or batch adapter error message, keep it local unless another consumer needs the same policy without that presentation.
- Prefer package-private app-local classes over public components when extraction is justified only inside `app`. Do not add an interface for a single implementation unless it protects a real consumer boundary.
- Use compilation, focused wiring, or behavior tests only for the stable boundary being created. Do not add tests merely to justify a class extraction.

Extract when the new class has one primary reason to change after these checks. Keep a private method when a single-consumer extraction has no dependency, lifecycle, policy, or consumer-knowledge boundary, remains tightly coupled to caller flow, or only moves code into a one-method bean.

## Test Scope Calibration

Do not skip tests. Tests should protect the changed responsibility or boundary with the smallest sufficient check, not mirror every implementation detail. Use `testing-checklist.md` as the detailed source for layer-specific test rules.

Quick calibration:

- If a module boundary moved, add one architecture rule or dependency check for that boundary.
- If service policy changed, test the real `*ServiceImpl` through inputs, outputs, state changes, and exceptions.
- If persistence behavior changed, test the real adapter against the target database for projection, ordering, paging, constraints, or dialect-sensitive SQL.
- If controller behavior changed, test HTTP binding, validation, status, response envelope, security, filters, or interceptors.

Classify each proposed architecture check into one of three groups:

Included in baseline (stable modularization rules):

- Selected `api/core`, technology adapter (persistence, messaging, cache), and schema resource modules exist and dependency direction is correct.
- Technology adapters such as `persistence-jpa`, `persistence-jooq`, `persistence-mybatis`, `persistence-memory`, `messaging-kafka`, `cache-caffeine`, and `cache-redis` depend inward only on their own `api` and/or `core` contracts as their role requires. Persistence, outbound messaging, and cache port implementations normally depend on `core`; a reusable inbound messaging adapter may depend on `api` to call a framework-neutral service contract.
- `persistence-schema` is resource-only by default and is consumed through app runtime, adapter test runtime, or codegen classpaths.
- No `api -> core`, no `api/core -> app/adapter/web-support/other bounded context`, and no technology adapter -> `app/web-support/other bounded context`.

Conditional opt-in (mandatory design rules whose broad static enforcement is an opt-in project-policy check, not the default baseline):

- Technology bans, controller placement, adapter self-registration, jOOQ/Flyway build order, response envelope, enum parsing, and forbidden DTO/entity/persistence-type rules.

Review-only (behavior tests, compiler contract changes, and review judgment are better than architecture rules):

- Ordinary refactoring choices such as helper names, interface split names, exact command record names, scalar-vs-command migration, parameter order/count/names, and proxy internals.

If a proposed architecture test needs a broad source scan, bytecode scan, dependency-coordinate blacklist, or many helper methods, stop and classify it before coding it: baseline modularization, opt-in project policy, or review-only guidance. The validation should not cost more to build or maintain than the boundary it protects.

Store write commands are a design improvement target, not a global test target. Refactor the touched Store contracts when the scalar list is harming readability, validation, or mapping safety, then rely on compilation plus focused service/persistence tests for changed behavior. Do not add a broad architecture test that fails all Store write methods because they have more than a chosen number of parameters.

For contract and class extraction decisions, apply the [Interface Split Gate](#interface-split-gate) and [Class Extraction Gate](#class-extraction-gate) in [Extraction and Split Gates](#extraction-and-split-gates).

## Module Structure

Use this shape for reusable bounded contexts:

```text
shared:domain
shared:web-support

<domain>:api
<domain>:core
<domain>:adapter:persistence-schema
<domain>:adapter:persistence-memory
<domain>:adapter:persistence-jpa
<domain>:adapter:persistence-jooq
<domain>:adapter:persistence-mybatis
<domain>:adapter:messaging-kafka
<domain>:adapter:cache-caffeine
<domain>:adapter:cache-redis

app
```

Include only the schema resource modules and technology adapters actually needed by the project.

## Module Roles

`shared:domain` contains pure shared domain types only. Do not place Spring, Web, JPA, Jackson response types, or persistence helpers here.

`shared:web-support` contains Spring Web common response helpers and basic exception handling. Domain `api/core` and technology adapters must not depend on it.

`*:api` is the public contract module. Put service interfaces, commands, results, search DTOs, value objects, and SPI contracts here. It must not depend on Spring, Web, persistence, messaging, cache-client technology, `core`, or `adapter`.

`*:core` is the default implementation module. Put service implementations, domain models, technology-neutral ports, and core business rules here. It must not contain Spring MVC, JPA, Kafka, cache-client types, web request/response DTOs, or other adapter technology.

`*:adapter:persistence-schema` owns reusable relational schema resources such as Flyway migrations. It is resource-only by default and should not depend on `*:core` unless a project-specific schema convention explicitly requires code.

Technology adapters such as `*:adapter:persistence-jpa`, `*:adapter:persistence-jooq`, `*:adapter:persistence-mybatis`, and `*:adapter:persistence-memory` implement core persistence ports. JPA entities, QueryDSL, jOOQ, memory stores, and generated tables stay inside technology adapters.

`*:adapter:messaging-kafka`, `*:adapter:cache-caffeine`, and `*:adapter:cache-redis` follow the same inward dependency rules: they depend only on their own `api` and/or `core` contracts as their role requires, keep client types inside the adapter, and are selected by app composition. Outbound messaging and cache adapters normally implement `core` ports; a reusable inbound Kafka adapter may instead call its bounded context's framework-neutral `api` service contract. See `messaging.md` and `caching.md`.

`app` is the executable composition module. Put controllers, app request/response DTOs, selected adapter imports, global web behavior, and host-domain SPI implementations here.

## Java Package Convention

Java packages should preserve module boundaries so architecture tests can verify them:

```text
<base>.<domain>.api..
<base>.<domain>.core..
<base>.<domain>.adapter.persistence..
<base>.<domain>.adapter.messaging..
<base>.<domain>.adapter.cache..
<base>.app.<host-workflow>..
<base>.websupport.. or <base>.web.support..
```

Do not collapse a domain module into only feature packages such as `<base>.board.post` if that hides `api/core/adapter` boundaries. If an existing project uses a different package convention, update the architecture tests and add guards that fail when expected packages are missing.

## Dependency Direction

Arrows point from the depending module to the module it depends on:

```text
*:core -> *:api
*:adapter:persistence-jpa|jooq|mybatis|memory -> *:core
*:adapter:messaging-kafka -> *:api and/or *:core (selected roles only)
*:adapter:cache-caffeine|redis -> *:core (port implementation only)
app -> *:api
app -> *:core
app -> selected *:adapter:persistence-schema
app -> selected *:adapter:persistence-jpa|jooq|mybatis|memory
app -> selected *:adapter:messaging-kafka
app -> selected *:adapter:cache-caffeine|redis
app -> shared:web-support
```

`shared:domain` may be used by domain contracts when pure shared domain types are needed. `shared:web-support` is web infrastructure and must stay out of domain `api/core` and every technology adapter.

`app -> *:core` exists for composition and configuration, such as constructing selected `*ServiceImpl` service implementations or importing selected adapter configurations. Controllers and HTTP-facing app services should depend on `*:api` service contracts, not concrete `*ServiceImpl` core classes.

Do not let bounded-context `api/core` modules depend on each other. For example, `comment:core` must not know `board`. The app implements a `CommentTargetPolicy` or similar SPI to connect them.

## App Package Shape

Within app, group web and composition code by host workflow:

```text
app/.../board/web/post
app/.../board/web/comment
app/.../board/web/attachment
app/.../board/support
```

Do not use a generic `integration` package when a domain workflow package communicates intent more clearly.
