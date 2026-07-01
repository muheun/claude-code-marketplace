---
name: spring-modular-backend-guide
description: Use when working on Java Spring Boot DDD-style multi-module architecture, scaffolding, review, or modification involving api/core/adapter boundaries, app-owned web composition, controller DTOs, enum input parsing, QueryDSL/jOOQ/Flyway persistence, identifier strategy, Java import ordering, layered tests, Mockito/fakes, Testcontainers, response envelopes, helper class extraction review, one-consumer Spring bean review, app-local helper review, or backend-util common utilities.
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
| Helper class extraction, one-consumer Spring bean, or app-local helper review | `references/architecture.md`, `references/anti-patterns.md`, and `references/testing-checklist.md` |
| Controller DTO, Service command, or Store command boundary | `references/web-and-app.md`, `references/naming.md`, `references/persistence.md`, `references/testing-checklist.md`, and `references/anti-patterns.md` |
| Store write input design or review | `references/naming.md`, `references/persistence.md`, `references/testing-checklist.md`, and `references/anti-patterns.md` |
| Service, Store, adapter names, Java import ordering, or Java test helper formatting | `references/naming.md` |
| Fixelsoft internal backend-util dependencies, common utilities, `StringUtil`, `NumberUtil`, `DateUtil`, `ListUtil`, or `Params` | `references/build-setup.md` and `references/backend-util.md` |
| JPA, QueryDSL, jOOQ, Flyway, paging, identifier strategy | `references/persistence.md` and `references/build-setup.md` |
| Controllers, DTOs, string enum input parsing, app composition, response envelope | `references/web-and-app.md` |
| Reusable comment/file-like modules or cross-domain validation | `references/spi-and-reuse.md` |
| Gradle dependencies, build plugin placement, or jOOQ codegen setup | `references/build-setup.md` and `references/persistence.md` |
| Architecture test implementation | `references/testing-checklist.md` and `references/architecture-tests.md` |
| Layered service, persistence, or app test strategy | `references/testing-checklist.md` and `references/persistence.md` |
| Code review or readiness check | `references/anti-patterns.md`, `references/testing-checklist.md`, and any changed-area references above |

3. Apply the core guardrails below, then follow the loaded references for detailed judgment.
4. Before writing persistence adapter code, make the selected technology contract explicit from `references/persistence.md` and `references/build-setup.md`. In this guide, choosing JPA means using JPA with QueryDSL for Store reads unless the user explicitly rejects QueryDSL for the project.
5. Verify with focused behavior, wiring, build, layer, or architecture checks that match the changed boundary; then run the full available build/test command.

## Core Guardrails

- Domain modules use `api`, `core`, and `adapter:persistence-*`; app owns web controllers and host-specific DTOs.
- Domain `api/core` modules do not depend on app, web-support, persistence adapters, Spring MVC, JPA, DB technology, or other bounded contexts unless a reference explicitly allows it.
- Reusable modules expose service APIs and SPI contracts; app or host composition owns HTTP endpoints, adapter selection, and cross-domain wiring.
- Controller request DTOs are app-owned HTTP contracts. Service commands live in `*:api`; Store commands live in `core.port`. Share command types only when the boundary and write intent are truly identical.
- Store write methods do not receive app DTOs, adapter entities, JPA/jOOQ/Spring Data types, read projections, or HTTP contracts.
- Persistence choices are explicit: JPA means QueryDSL projection reads by default; jOOQ keeps JPA entities for Hibernate validation but uses jOOQ DSL for reads/writes; schema changes go through Flyway.
- Naming, enum parsing, response envelopes, adapter registration, and import ordering are design/review rules first. Add static enforcement only when the project treats the policy as stable or the task explicitly touches that boundary.
- Tests follow dependency direction. Prefer focused behavior, wiring, layer, and build checks; use architecture tests only for stable boundaries ordinary tests cannot protect cheaply.
- For Fixelsoft internal projects, recommend approved DB-neutral `backend-util` common/json-common utilities when the project opts in, but keep DB/Spring utility bundles out of reusable domain contracts.

## Frequent Failure Signals

If you see controllers in domain modules, app DTOs passed into service/store contracts, one-method interfaces with no distinct role, one-consumer app helper beans extracted from private methods, JPA entity fetch reads used as the default Store read model, direct `Enum.valueOf(...)` parsing at boundaries, broad source scans for review-only preferences, or build checks that blacklist open-ended external coordinates, read `references/anti-patterns.md` plus the changed-area references from the routing table before editing.

## Completion Checklist

- Loaded every reference required by the work type and any changed-area reference.
- Module boundaries, command/DTO ownership, persistence technology, and test scope match the relevant references.
- Extracted helper classes or Spring beans pass the Class Extraction Gate; otherwise keep the logic local.
- New Service, Store, SPI, Reader, or Notifier contracts pass the Interface Split Gate.
- New or changed enforcement checks protect stable boundaries rather than incidental naming, helper shape, or future library coordinates.
- Focused verification passed before the full available build/test command.
