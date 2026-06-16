# Build Setup Reference

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
    "board:adapter:persistence-jpa",
    "comment:api",
    "comment:core",
    "comment:adapter:persistence-jpa",
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

Persistence adapter modules:

```kotlin
plugins {
    `java-library`
}

dependencies {
    implementation(project(":board:core"))
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("com.querydsl:querydsl-jpa:5.1.0:jakarta")
    annotationProcessor("com.querydsl:querydsl-apt:5.1.0:jakarta")
    annotationProcessor("jakarta.persistence:jakarta.persistence-api")
    annotationProcessor("jakarta.annotation:jakarta.annotation-api")
}
```

The `app` module selects concrete adapters:

```kotlin
plugins {
    id("org.springframework.boot")
}

dependencies {
    implementation(project(":shared:web-support"))
    implementation(project(":board:api"))
    implementation(project(":board:core"))
    implementation(project(":board:adapter:persistence-jpa"))
    implementation(project(":comment:api"))
    implementation(project(":comment:core"))
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
- Put QueryDSL dependencies and annotation processor only in JPA adapter modules.
- Add `jakarta.persistence-api` and `jakarta.annotation-api` to the QueryDSL annotation processor path when JPA Q-class generation needs Jakarta types.
- Put jOOQ plugin and generated table dependencies only in jOOQ adapter modules.
- Put DB infrastructure bundles such as Flyway/p6spy helpers in `app` or selected persistence adapters, not domain `api/core`.
- Put web starter and common response support in `app` or `shared:web-support`, not domain modules.
- Use `spring-boot-starter-webmvc` for Spring Boot 4 and `spring-boot-starter-web` for Spring Boot 3.x.

## Migration Resources

Adapter-owned tables keep migrations in the adapter:

```text
board/adapter/persistence-jpa/src/main/resources/db/migration/VyyyyMMddHHmm__board_create_posts.sql
comment/adapter/persistence-jpa/src/main/resources/db/migration/VyyyyMMddHHmm__comment_create_comments.sql
```

App-only composition tables may use app migrations. Migration versions must be unique across the runtime classpath.
Use the actual creation date/time for `VyyyyMMddHHmm`; do not create new versions by incrementing the previous migration timestamp.
