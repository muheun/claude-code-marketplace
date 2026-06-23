# Architecture Reference

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

## Test Scope Calibration

Do not skip tests. Tests should protect the changed responsibility or boundary with the smallest sufficient check, not mirror every implementation detail. Use `testing-checklist.md` as the detailed source for layer-specific test rules.

Quick calibration:

- If a module boundary moved, add one architecture rule or dependency check for that boundary.
- If service policy changed, test the real `*ServiceImpl` through inputs, outputs, state changes, and exceptions.
- If persistence behavior changed, test the real adapter against the target database for projection, ordering, paging, constraints, or dialect-sensitive SQL.
- If controller behavior changed, test HTTP binding, validation, status, response envelope, security, filters, or interceptors.

Architecture tests are for stable rules such as dependency direction, forbidden technologies, controller placement, adapter self-registration, and forbidden Store write input types such as app DTOs, read projections, adapter entities, JPA entities, jOOQ records, and Spring Data types. Behavior tests, compiler contract changes, and review judgment are better for ordinary refactoring choices such as helper names, interface split names, exact command record names, scalar-vs-command migration, parameter order/count/names, and proxy internals.

Store write commands are a design improvement target, not a global test target. Refactor the touched Store contracts when the scalar list is harming readability, validation, or mapping safety, then rely on compilation plus focused service/persistence tests for changed behavior. Do not add a broad architecture test that fails all Store write methods because they have more than a chosen number of parameters.

### Interface Granularity

Split `Service`, `Store`, SPI, Reader, and Notifier contracts by role and change reason, not by method count.

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

## Module Structure

Use this shape for reusable bounded contexts:

```text
shared:domain
shared:web-support

<domain>:api
<domain>:core
<domain>:adapter:persistence-memory
<domain>:adapter:persistence-jpa
<domain>:adapter:persistence-jooq

app
```

Include only the adapter modules actually needed by the project.

## Module Roles

`shared:domain` contains pure shared domain types only. Do not place Spring, Web, JPA, Jackson response types, or persistence helpers here.

`shared:web-support` contains Spring Web common response helpers and basic exception handling. Domain `api/core` and persistence adapters must not depend on it.

`*:api` is the public contract module. Put service interfaces, commands, results, search DTOs, value objects, and SPI contracts here. It must not depend on Spring, Web, DB technology, `core`, or `adapter`.

`*:core` is the default implementation module. Put service implementations, domain models, persistence ports, and core business rules here. It must not contain Spring MVC, JPA, web request/response DTOs, or persistence technology.

`*:adapter:persistence-*` implements core persistence ports with a specific technology. JPA entities, QueryDSL, jOOQ, memory stores, and generated tables stay inside adapters.

`app` is the executable composition module. Put controllers, app request/response DTOs, selected adapter imports, global web behavior, and host-domain SPI implementations here.

## Java Package Convention

Java packages should preserve module boundaries so architecture tests can verify them:

```text
<base>.<domain>.api..
<base>.<domain>.core..
<base>.<domain>.adapter.persistence..
<base>.app.<host-workflow>..
<base>.websupport.. or <base>.web.support..
```

Do not collapse a domain module into only feature packages such as `<base>.board.post` if that hides `api/core/adapter` boundaries. If an existing project uses a different package convention, update the architecture tests and add guards that fail when expected packages are missing.

## Dependency Direction

Arrows point from the depending module to the module it depends on:

```text
*:core -> *:api
*:adapter:persistence-* -> *:core
app -> *:api
app -> *:core
app -> selected *:adapter:persistence-*
app -> shared:web-support
```

`shared:domain` may be used by domain contracts when pure shared domain types are needed. `shared:web-support` is web infrastructure and must stay out of domain `api/core` and persistence adapters.

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
