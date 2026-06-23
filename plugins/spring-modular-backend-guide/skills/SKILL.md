---
name: spring-modular-backend-guide
description: Use when working on Java Spring Boot backend architecture, scaffolding, reviewing, or modifying DDD-style multi-module projects that need reusable domain modules, api/core/adapter boundaries, app-owned web composition, QueryDSL/jOOQ persistence rules, Flyway migrations, identifier strategy, Java import ordering, Java test helper formatting, layered service/persistence/app test strategy, Mockito/fake boundaries, Testcontainers DB tests, common response envelopes, or backend-util paging.
---

# Spring Modular Backend Guide

## Overview

Use this skill to build or review Java Spring Boot backends with reusable bounded-context modules. Core rule: domain modules expose public contracts and adapters; the app module owns HTTP endpoints, composition, and cross-domain wiring.

This is an opinionated guideline for new scaffolds and architecture reviews. Do not apply it to non-Spring projects, frontend work, or small throwaway prototypes unless the user explicitly wants this structure.

## Workflow

1. Confirm the project is Java Spring Boot by reading `build.gradle`, `settings.gradle`, or `pom.xml`.
2. Identify the work type and read only the needed references:

| Work type | Required reference |
|---|---|
| New project, scaffold, or module structure | `references/architecture.md`, `references/build-setup.md`, and `references/testing-checklist.md` |
| Architecture design, responsibility separation, or refactoring strategy | `references/architecture.md`, `references/anti-patterns.md`, and `references/testing-checklist.md` |
| Service, Store, SPI, Reader, or Notifier contract granularity | `references/architecture.md` and `references/testing-checklist.md` |
| Store write input design or review | `references/naming.md`, `references/persistence.md`, `references/testing-checklist.md`, and `references/anti-patterns.md` |
| Service, Store, adapter names, Java import ordering, or Java test helper formatting | `references/naming.md` |
| JPA, QueryDSL, jOOQ, Flyway, paging, identifier strategy | `references/persistence.md` |
| Controllers, DTOs, app composition, response envelope | `references/web-and-app.md` |
| Reusable comment/file-like modules or cross-domain validation | `references/spi-and-reuse.md` |
| Gradle dependencies, build plugin placement, or jOOQ codegen setup | `references/build-setup.md` and `references/persistence.md` |
| Architecture test implementation | `references/testing-checklist.md` and `references/architecture-tests.md` |
| Layered service, persistence, or app test strategy | `references/testing-checklist.md` and `references/persistence.md` |
| Code review or readiness check | `references/anti-patterns.md`, `references/testing-checklist.md`, and any changed-area references above |

3. Apply the non-negotiable rules below before writing or reviewing code.
4. Verify with targeted tests first, then the full available build/test command.

## Non-Negotiable Rules

- Domain modules use `api`, `core`, and `adapter:persistence-*`; app owns web controllers and host-specific DTOs.
- Prefer small, verifiable architecture changes: identify mixed responsibilities, split by change reason, and protect the split with tests, architecture rules, module dependency checks, package rules, or focused layer tests; checklist-only notes do not count as protection.
- Split `Service`, `Store`, SPI, Reader, and Notifier contracts by role and change reason, not by method count; avoid one-method interfaces that only add files and wiring.
- Store write methods do not pass app DTOs, adapter entities, JPA/jOOQ/Spring Data types, or read projections as write commands. Non-trivial write inputs should be reviewed and refactored toward purpose-specific domain command/value records instead of long scalar field lists, but do not enforce this style preference with broad reflection/source-scan tests.
- Domain `api/core` modules do not depend on other bounded contexts, app, web-support, persistence adapters, Spring MVC, JPA, or DB technology.
- Domain `api` may expose only DB-neutral paging/search contracts; DB infrastructure bundles stay in app or selected persistence adapters.
- Reusable modules expose SPI contracts from `api`; app or host composition implements them.
- Service contracts are `*Service` interfaces in `api`; concrete core implementations use `*ServiceImpl`.
- Service methods use application verbs: `get`, `save`, `modify`, `remove`, `exists`, plus explicit domain verbs like `attach`.
- Persistence ports use `*Store`; Store methods use query verbs: `select`, `insert`, `update`, `delete`, `upsert`, `exists`, `count`.
- Persistence implementations use technology-explicit names such as `JpaPostStoreAdapter`, `JooqPostStoreAdapter`, `InMemoryPostStoreAdapter`.
- Java imports follow the repository/IntelliJ import layout groups, then sort by fully qualified name inside each group; do not add same-package imports or invent package-type groups such as event/model/service unless the existing formatter already does so.
- Persistence adapters do not self-register with `@Component`; app imports selected configuration holders.
- JPA/Hibernate entities are the relational schema validation model; keep `ddl-auto: validate` and make schema changes through Flyway.
- JPA-backed adapters use QueryDSL projection with stable ordering. Do not make entity fetch plus `toDomain()` the default read pattern.
- jOOQ-backed adapters keep JPA entities only for Hibernate validation; Store reads and writes use jOOQ DSL, not JPA/Spring Data APIs.
- jOOQ generated sources come from a Flyway-migrated schema before compile/test, not from a stale manual database.
- Paging result assembly belongs in service: `countBy`, `calcPaging`, `selectBy`, `setBody`.
- HTTP response envelope has `status`, `code`, `message`, `data`; no boolean `success` field.
- Tests follow module dependency direction: core service tests use the real `*ServiceImpl` with fake or Mockito-controlled external boundaries, persistence tests use real adapters with the target DB via Testcontainers when SQL behavior matters, and app tests verify thin HTTP contracts plus composition.
- Do not skip tests. Use the smallest test that protects the changed behavior or stable boundary; keep ordinary implementation details and refactoring preferences out of architecture tests.
- Architecture tests protect stable module boundaries and forbidden dependency/type rules. They must not police ordinary design cleanup such as exact command record names, Store method parameter counts, scalar-vs-command style migration, helper class names, split interface names, or concrete Java file paths.

## Baseline Failures This Skill Prevents

Without this skill, agents commonly place controllers in domain modules, use `Repository/JpaRepository/find/save/create` as defaults, expose reusable modules as HTTP modules, perform big-bang architecture rewrites, split classes only because they are long, create one-method contracts with no distinct role or change reason, extract abstractions with no protecting test, architecture rule, dependency check, package rule, or focused layer test, over-expand tests into duplicated implementation checks, flatten Java import layout groups into one global alphabetical list, push service field lists down into Store write ports, reuse read projections, app DTOs, JPA entities, jOOQ records, or Spring Data types as write commands, put Flyway migrations only in app, generate jOOQ classes from stale local schemas, drop Hibernate validation when jOOQ is selected, wire compile before codegen, return a boolean `success` field, or put paging mutation inside persistence. Treat those as architecture violations unless the user explicitly overrides the guideline.

## Completion Checklist

- Module boundaries match `api/core/adapter/app`.
- Responsibility splits are small enough to review and are protected by tests, architecture rules, module dependency checks, package rules, or focused layer tests; checklist-only notes do not count as protection.
- Interface granularity follows consumer role and change reason, not "one method per interface" as a default.
- Gradle includes and dependencies match the selected modules and adapters.
- Controllers and HTTP DTOs are in app packages.
- App controllers and workflows depend on `*:api` `*Service` contracts, not `*:core` `*ServiceImpl` classes.
- Cross-domain calls use SPI or app composition, not direct domain dependencies.
- Persistence naming and service naming follow the vocabulary rules.
- Non-trivial Store write inputs are reviewed and refactored toward purpose-specific domain records or value objects where it improves readability and contract stability; domain-contract validation is enforced in those inputs or service policy, and adapter entity annotations are not sufficient alone.
- Java imports remain sorted by fully qualified name within the repository import layout groups, with no new same-package imports added.
- JPA/QueryDSL/jOOQ/Flyway choices match the persistence reference.
- Hibernate validation is configured with `ddl-auto: validate`.
- jOOQ adapters wire Flyway migration, schema verification, code generation, compile, and test in that order.
- Identifier strategy and DDL type mapping match the persistence reference.
- Architecture tests or equivalent checks protect stable boundary rules; behavior tests, compiler contract changes, and review cover ordinary implementation details and Store command cleanup.
- Required tests are present or added as needed, proportional to the changed boundary or behavior, and do not duplicate the same policy across layers.
- Layered tests do not introduce `core -> adapter` or `core -> app` dependencies.
- `./gradlew test` or the project-specific test command passes.
