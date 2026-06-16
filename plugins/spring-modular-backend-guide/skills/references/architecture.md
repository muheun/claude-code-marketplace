# Architecture Reference

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

`app -> *:core` exists for composition and configuration, such as constructing `*ServiceImpl` default service implementations or importing selected adapter configurations. Controllers and HTTP-facing app services should depend on `*:api` service contracts, not concrete `*ServiceImpl` core classes.

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
