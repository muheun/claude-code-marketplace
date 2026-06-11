---
name: spring-modular-backend-guide
description: Use when working on Java Spring Boot backend architecture, scaffolding, reviewing, or modifying DDD-style multi-module projects that need reusable domain modules, api/core/adapter boundaries, app-owned web composition, QueryDSL/jOOQ persistence rules, Flyway migrations, identifier strategy, common response envelopes, or backend-util paging.
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
| Service, Store, adapter names | `references/naming.md` |
| JPA, QueryDSL, jOOQ, Flyway, paging, identifier strategy | `references/persistence.md` |
| Controllers, DTOs, app composition, response envelope | `references/web-and-app.md` |
| Reusable comment/file-like modules or cross-domain validation | `references/spi-and-reuse.md` |
| Gradle dependencies or build plugin placement | `references/build-setup.md` |
| Architecture test implementation | `references/testing-checklist.md` and `references/architecture-tests.md` |
| Code review or readiness check | `references/anti-patterns.md`, `references/testing-checklist.md`, and any changed-area references above |

3. Apply the non-negotiable rules below before writing or reviewing code.
4. Verify with targeted tests first, then the full available build/test command.

## Non-Negotiable Rules

- Domain modules use `api`, `core`, and `adapter:persistence-*`; app owns web controllers and host-specific DTOs.
- Domain `api/core` modules do not depend on other bounded contexts, app, web-support, persistence adapters, Spring MVC, JPA, or DB technology.
- Domain `api` may expose only DB-neutral paging/search contracts; DB infrastructure bundles stay in app or selected persistence adapters.
- Reusable modules expose SPI contracts from `api`; app or host composition implements them.
- Service methods use application verbs: `get`, `save`, `modify`, `remove`, `exists`, plus explicit domain verbs like `attach`.
- Persistence ports use `*Store`; Store methods use query verbs: `select`, `insert`, `update`, `delete`, `upsert`, `exists`, `count`.
- Persistence implementations use technology-explicit names such as `JpaPostStoreAdapter`, `JooqPostStoreAdapter`, `InMemoryPostStoreAdapter`.
- Persistence adapters do not self-register with `@Component`; app imports selected configuration holders.
- JPA read side uses QueryDSL projection with stable ordering. Do not make entity fetch plus `toDomain()` the default read pattern.
- jOOQ adapters prefer jOOQ DSL for reads and writes; do not mix jOOQ with JPA/Spring Data inside the same adapter.
- Paging result assembly belongs in service: `countBy`, `calcPaging`, `selectBy`, `setBody`.
- HTTP response envelope has `status`, `code`, `message`, `data`; no boolean `success` field.
- `ddl-auto` defaults to `validate`; schema changes are Flyway migrations.

## Baseline Failures This Skill Prevents

Without this skill, agents commonly place controllers in domain modules, use `Repository/JpaRepository/find/save/create` as defaults, expose reusable modules as HTTP modules, put Flyway migrations only in app, return a boolean `success` field, or put paging mutation inside persistence. Treat those as architecture violations unless the user explicitly overrides the guideline.

## Completion Checklist

- Module boundaries match `api/core/adapter/app`.
- Gradle includes and dependencies match the selected modules and adapters.
- Controllers and HTTP DTOs are in app packages.
- Cross-domain calls use SPI or app composition, not direct domain dependencies.
- Persistence naming and service naming follow the vocabulary rules.
- JPA/jOOQ/Flyway choices match the persistence reference.
- Identifier strategy and DDL type mapping match the persistence reference.
- Architecture tests or equivalent checks protect the important rules.
- `./gradlew test` or the project-specific test command passes.
