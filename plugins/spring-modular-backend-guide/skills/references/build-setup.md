# Build Setup Reference

## Contents

- [settings.gradle.kts](#settingsgradlekts)
- [Root build.gradle.kts](#root-buildgradlekts)
- [Dependency Shape](#dependency-shape)
  - [Persistence Schema Modules](#persistence-schema-modules)
  - [JPA/QueryDSL Adapter Modules](#jpaquerydsl-adapter-modules)
  - [jOOQ Adapter Modules](#jooq-adapter-modules)
  - [jOOQ Codegen Order](#jooq-codegen-order)
  - [App Module Dependencies](#app-module-dependencies)
- [Plugin Placement](#plugin-placement)
- [Migration Resources](#migration-resources)

Use Gradle Kotlin DSL for new scaffolds unless the existing project already uses another build style.

## settings.gradle.kts

Include only the bounded contexts and adapters selected by the project:

```kotlin
rootProject.name = "sample-backend"

include(
    "shared:domain",
    "shared:web-support",
    "board:api",
    "board:core",
    "board:adapter:persistence-schema",
    "board:adapter:persistence-jpa",
    // "board:adapter:persistence-jooq",
    "comment:api",
    "comment:core",
    "comment:adapter:persistence-schema",
    "comment:adapter:persistence-jpa",
    // "comment:adapter:persistence-jooq",
    "file:api",
    "file:core",
    "file:adapter:persistence-memory",
    "app"
)
```

Do not include `adapter:web` under domain modules. Web belongs to `app`.

## Root build.gradle.kts

Versionless Spring dependencies in submodules require a shared dependency management rule. New scaffolds should import the Spring Boot BOM from the root build:

```kotlin
plugins {
    id("org.springframework.boot") version "4.0.6" apply false
}

val springBootVersion = "4.0.6"

subprojects {
    if (!projectDir.resolve("build.gradle.kts").isFile) {
        return@subprojects
    }

    pluginManager.apply("java")

    repositories {
        mavenCentral()
    }

    dependencies {
        add("implementation", platform("org.springframework.boot:spring-boot-dependencies:$springBootVersion"))
        add("annotationProcessor", platform("org.springframework.boot:spring-boot-dependencies:$springBootVersion"))
        add("testImplementation", platform("org.springframework.boot:spring-boot-dependencies:$springBootVersion"))
    }

    pluginManager.withPlugin("java-library") {
        dependencies.add("api", platform("org.springframework.boot:spring-boot-dependencies:$springBootVersion"))
    }
}
```

Use a Spring Boot 3.x or 4.x version that matches the target project. If the project uses the Spring dependency-management plugin instead, apply the same BOM consistently to every submodule configuration that declares versionless dependencies.

Internal projects may add `mavenLocal()` or a company repository, but `mavenCentral()` should remain the default public repository for Spring, QueryDSL, ArchUnit, and test dependencies.

## Dependency Shape

Domain `api` modules:

```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":shared:domain"))
}
```

If an internal project uses a shared `Paging<T>`, keep the dependency DB-neutral. Do not add `fixel-util-spring4-db` or other DB infrastructure bundles to domain `api`.

For Fixelsoft internal Spring projects, `backend-util` common/json-common usage is recommended but not required; use it only when the user or project chooses it. When the project opts in and a module only calls common utilities or JSON map helpers internally, keep the dependency non-transitive:

```kotlin
dependencies {
    implementation("com.fixelsoft.util:fixel-util-json-common:<approved-version>")
}
```

Use `api` only when the module intentionally exposes approved `backend-util` public contract types, such as shared paging/search contracts:

```kotlin
dependencies {
    api("com.fixelsoft.util:fixel-util-json-common:<approved-version>")
}
```

`fixel-util-json-common` exposes common utilities such as `StringUtil`, `NumberUtil`, `DateUtil`, and `ListUtil`, plus `Params` for dynamic JSON/key-value payloads. Do not depend directly on the internal `fixel-util-common` module from consuming projects unless that project explicitly publishes and approves it.

Domain `core` modules:

```kotlin
plugins {
    `java-library`
}

dependencies {
    api(project(":board:api"))
}
```

Shared `web-support` module:

```kotlin
plugins {
    `java-library`
}

dependencies {
    api("org.springframework:spring-web")
    api("org.springframework:spring-context")
    // api("org.springframework.boot:spring-boot-starter-webmvc") // Spring Boot 4 starter option
    // api("org.springframework.boot:spring-boot-starter-web") // Spring Boot 3.x starter option
}
```

Use granular Spring Framework dependencies when this module only provides `ApiResponse`, `ResponseEntity` helpers, and `@RestControllerAdvice`. Use a Boot starter only when the project intentionally standardizes shared web infrastructure on starter dependencies.

### Persistence Schema Modules

For reusable relational bounded contexts, create `*:adapter:persistence-schema` by default. This module owns Flyway migrations under `src/main/resources/db/migration` and keeps schema ownership independent from JPA, jOOQ, MyBatis, or any later adapter swap. Adapter count is not the ownership criterion; use this module even when the project has only one relational technology adapter today. Use `persistence-schema`, not `persistence-flyway`, because the responsibility is schema resources and Flyway is only the migration mechanism.

```kotlin
plugins {
    `java-library`
}
```

Do not put duplicate table DDL migrations in `persistence-jpa`, `persistence-jooq`, or `persistence-mybatis`. App modules, adapter integration tests, and jOOQ code generation must include the selected schema module resources.

Do not declare consumer dependencies in `persistence-schema` itself. Add the schema module to each consumer classpath that must see Flyway migrations. In Spring Boot apps, `runtimeOnly` keeps schema resources off the compile classpath while `bootJar` still packages the schema jar under `BOOT-INF/lib`; plain `jar` deployments must carry the runtime classpath.

```kotlin
// app/build.gradle.kts
dependencies {
    runtimeOnly(project(":board:adapter:persistence-schema"))
}

// board:adapter:persistence-jpa or board:adapter:persistence-jooq build.gradle.kts
dependencies {
    testRuntimeOnly(project(":board:adapter:persistence-schema"))
}

// jOOQ code generation convention; use the project's actual configuration name.
dependencies {
    jooqCodegenMigration(project(":board:adapter:persistence-schema"))
}
```

Treat `persistence-schema` as a schema resource module, not as a sibling technology adapter. Architecture or build-file checks that forbid `persistence-jooq`/`persistence-jpa`/`persistence-mybatis` from depending on sibling adapters must still allow the same-domain schema module on test or codegen configurations. Continue to forbid dependencies on sibling technology adapters, app/web-support modules, and other bounded contexts.

If the root build keeps a manual Flyway migration source list or code generation migration input list, verify that it stays in sync with the selected schema modules. Every selected relational adapter should have its corresponding `*:adapter:persistence-schema/src/main/resources/db/migration` location available to each consumer that needs it: app runtime, adapter integration test runtime, and jOOQ code generation when present.

### JPA/QueryDSL Adapter Modules

```kotlin
plugins {
    `java-library`
}

dependencies {
    implementation(project(":board:core"))
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("io.github.openfeign.querydsl:querydsl-jpa:7.4.0")
    annotationProcessor("io.github.openfeign.querydsl:querydsl-apt:7.4.0:jakarta")
    annotationProcessor("jakarta.persistence:jakarta.persistence-api")
    annotationProcessor("jakarta.annotation:jakarta.annotation-api")
}
```

Treat this as the required JPA adapter baseline for projects using this guide, not an optional embellishment. Use the OpenFeign-maintained QueryDSL artifacts under `io.github.openfeign.querydsl`; do not use legacy `com.querydsl` coordinates for new scaffolds. When scaffolding a `persistence-jpa` module or `Jpa*StoreAdapter`, include QueryDSL dependencies and annotation processors before writing read-side adapter code. If the user explicitly rejects QueryDSL for the project, stop and ask for the selected persistence-read alternative instead of silently falling back to Criteria, JPQL string queries, entity fetch mapping, or `JpaRepository`.

### jOOQ Adapter Modules

```kotlin
plugins {
    `java-library`
    // Apply the project's selected jOOQ code generation convention here.
}

dependencies {
    implementation(project(":board:core"))
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-jooq")
    // Add the target JDBC driver, Flyway, and jOOQ codegen dependencies through the project convention.
    // Keep JPA entities for Hibernate schema validation; Store reads/writes still use jOOQ DSL.
}
```

jOOQ-backed adapters still keep JPA entity declarations and `ddl-auto: validate` for schema verification. Do not add Spring Data repositories or use `EntityManager` for Store reads/writes in the jOOQ-backed Store.

### jOOQ Codegen Order

jOOQ adapters must generate sources from a Flyway-migrated schema before Java compilation and tests. Use project-specific task names, but keep this dependency order:

```text
prepareJooqCodegenDb
-> flywayMigrateJooqCodegen
-> verifyJooqCodegenSchema
-> generateJooq
-> compileJava
-> test
```

Gradle wiring must make `generateJooq` depend on the migration and schema verification tasks, and `compileJava` depend on `generateJooq`. `compileJava.dependsOn(generateJooq)` is the required contract. `test` will then depend on generated sources through compilation; an explicit `test.dependsOn(generateJooq)` is only a supplemental clarity check.

`verifyJooqCodegenSchema` should fail when:

- Flyway migrations were not applied to the codegen database.
- The expected schema is empty.
- Required schema-module tables are missing.
- The codegen database product or dialect differs from the target runtime database.

Do not generate jOOQ classes from a manually prepared developer-local database. Keep the codegen database separate from integration-test runtime databases where practical.

### App Module Dependencies

The `app` module selects schema resources and concrete technology adapters. Schema modules are runtime dependencies; technology adapters remain compile/runtime dependencies:

```kotlin
plugins {
    id("org.springframework.boot")
}

dependencies {
    implementation(project(":shared:web-support"))
    implementation(project(":board:api"))
    implementation(project(":board:core"))
    runtimeOnly(project(":board:adapter:persistence-schema"))
    implementation(project(":board:adapter:persistence-jpa"))
    implementation(project(":comment:api"))
    implementation(project(":comment:core"))
    runtimeOnly(project(":comment:adapter:persistence-schema"))
    implementation(project(":comment:adapter:persistence-jpa"))
    implementation("org.springframework.boot:spring-boot-starter-webmvc") // Spring Boot 4
    // implementation("org.springframework.boot:spring-boot-starter-web") // Spring Boot 3.x
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("com.tngtech.archunit:archunit-junit5:1.4.1")
}
```

## Plugin Placement

- Put Spring Boot executable plugin on `app`.
- Import the Spring Boot BOM from the root build before using versionless Spring, Jakarta, test, or annotation processor dependencies.
- Put `shared:web-support` on `spring-web` and `spring-context`, or the matching Boot web starter if the team intentionally accepts starter dependencies there.
- Put OpenFeign QueryDSL dependencies and annotation processor only in JPA adapter modules.
- Add `jakarta.persistence-api` and `jakarta.annotation-api` to the QueryDSL annotation processor path when JPA Q-class generation needs Jakarta types.
- Put jOOQ plugin and generated table dependencies only in jOOQ adapter modules.
- Put DB infrastructure bundles such as Flyway/p6spy helpers in `app` or selected persistence technology adapters, not domain `api/core` or the schema resource module. Architecture tests should protect this with internal project dependency checks and actual package/type usage rules, not a broad blacklist of external artifact coordinates.
- Put web starter and common response support in `app` or `shared:web-support`, not domain modules.
- Use `spring-boot-starter-webmvc` for Spring Boot 4 and `spring-boot-starter-web` for Spring Boot 3.x.

## Migration Resources

Reusable relational modules keep migrations in `persistence-schema`:

```text
board/adapter/persistence-schema/src/main/resources/db/migration/VyyyyMMddHHmm__board_create_posts.sql
comment/adapter/persistence-schema/src/main/resources/db/migration/VyyyyMMddHHmm__comment_create_comments.sql
```

App-only composition tables may use app migrations. Technology adapters consume schema resources; they do not own duplicate table DDL. Migration versions must be unique across the runtime classpath.
Use the actual creation date/time for `VyyyyMMddHHmm`; do not create new versions by incrementing the previous migration timestamp. If multiple migrations are created in the same minute, use the actual seconds in `VyyyyMMddHHmmss` or regenerate at the real later creation time, then verify no runtime classpath duplicate remains.
