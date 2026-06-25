# Architecture Test Examples

Use these as compact starting points. Adapt package names and module names to the project.

Architecture tests should guard stable architecture, not every design preference. Use these examples for dependency direction, forbidden frameworks, controller placement, adapter self-registration, and build/persistence contracts. See the final avoid list before adding new required checks.

## Gradle Dependency Checks

Use Gradle/build-file checks for stable internal project boundaries: selected modules exist, `api/core` do not depend on `app`, web-support, persistence adapters, or other bounded contexts, and test-support modules stay in the intended scope. Do not build broad external Maven-coordinate blacklists for DB/web libraries. External artifacts change by Spring Boot version, starter choice, plugin convention, and vendor; instead, verify forbidden technology by actual package/type usage in source or bytecode checks.

```java
@Test
void sharedModuleNamesAreStable() throws Exception {
    var settings = Files.readString(Path.of("..", "settings.gradle.kts"));

    assertThat(settings).contains("\"shared:domain\"", "\"shared:web-support\"");
    assertThat(settings).doesNotContain("\"shared:kernel\"");
}
```

## API And Core Boundary Checks

```java
@Test
void expectedModulePackagesExist() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    assertPackageExists(classes, ".board.api.");
    assertPackageExists(classes, ".board.core.");
    assertPackageExists(classes, ".board.adapter.persistence.");
    assertPackageExists(classes, ".comment.api.");
    assertPackageExists(classes, ".comment.core.");
    assertPackageExists(classes, ".comment.adapter.persistence.");
    assertPackageExists(classes, ".file.api.");
    assertPackageExists(classes, ".file.core.");
    assertPackageExists(classes, ".file.adapter.persistence.");
}

@Test
void apiModulesStayAsPublicContracts() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage("..board.api..", "..comment.api..", "..file.api..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "org.springframework..",
                    "..core..",
                    "..adapter..",
                    "..websupport..",
                    "..web.support..")
            .check(classes);
}

@Test
void apiAndCoreModulesDoNotDependOnAppOrAdapters() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage(
                    "..board.api..", "..board.core..",
                    "..comment.api..", "..comment.core..",
                    "..file.api..", "..file.core..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..app..",
                    "..adapter..")
            .check(classes);
}

@Test
void domainAndPersistenceModulesDoNotDependOnWebSupport() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage(
                    "..board.api..", "..board.core..", "..board.adapter.persistence..",
                    "..comment.api..", "..comment.core..", "..comment.adapter.persistence..",
                    "..file.api..", "..file.core..", "..file.adapter.persistence..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..websupport..",
                    "..web.support..")
            .check(classes);
}

@Test
void apiAndCoreModulesDoNotDependOnOtherBoundedContexts() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage("..board.api..", "..board.core..")
            .should().dependOnClassesThat().resideInAnyPackage("..comment..", "..file..")
            .check(classes);

    noClasses()
            .that().resideInAnyPackage("..comment.api..", "..comment.core..")
            .should().dependOnClassesThat().resideInAnyPackage("..board..", "..file..")
            .check(classes);

    noClasses()
            .that().resideInAnyPackage("..file.api..", "..file.core..")
            .should().dependOnClassesThat().resideInAnyPackage("..board..", "..comment..")
            .check(classes);
}

@Test
void apiAndCoreModulesDoNotDependOnPersistenceTechnology() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage(
                    "..board.api..", "..board.core..",
                    "..comment.api..", "..comment.core..",
                    "..file.api..", "..file.core..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "jakarta.persistence..",
                    "javax.persistence..",
                    "com.querydsl..",
                    "org.hibernate..",
                    "org.jooq..",
                    "org.flywaydb..",
                    "org.springframework.data..",
                    "org.springframework.jdbc..",
                    "org.springframework.orm..",
                    "org.springframework.transaction..",
                    "jakarta.transaction..",
                    "javax.transaction..",
                    "java.sql..",
                    "javax.sql..")
            .check(classes);
}

private static void assertPackageExists(JavaClasses classes, String packagePart) {
    var exists = classes.stream()
            .map(JavaClass::getPackageName)
            .map(packageName -> "." + packageName + ".")
            .anyMatch(packageName -> packageName.contains(packagePart));

    assertThat(exists)
            .as("Expected at least one class in package segment %s", packagePart)
            .isTrue();
}
```

## Web And Persistence Checks

```java
@Test
void domainModulesDoNotOwnHttpAdapters() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    var webAdapterPackages = classes.stream()
            .filter(javaClass -> javaClass.getPackageName().contains(".adapter.web"))
            .map(JavaClass::getName)
            .toList();

    assertThat(webAdapterPackages).isEmpty();

    var domainControllers = classes.stream()
            .filter(javaClass -> javaClass.isAnnotatedWith("org.springframework.web.bind.annotation.RestController")
                    || javaClass.isAnnotatedWith("org.springframework.stereotype.Controller"))
            .filter(ArchitectureTest::isFromDomainModuleSource)
            .map(JavaClass::getName)
            .toList();

    assertThat(domainControllers).isEmpty();
}

private static boolean isFromDomainModuleSource(JavaClass javaClass) {
    // Use source URI only as a fallback to distinguish stable Gradle module boundaries.
    // Prefer package or module metadata when the project exposes it.
    var sourceUri = javaClass.getSource()
            .map(source -> source.getUri().toString())
            .orElse("");
    return sourceUri.contains("/board/api/")
            || sourceUri.contains("/board/core/")
            || sourceUri.contains("/board/adapter/")
            || sourceUri.contains("/comment/api/")
            || sourceUri.contains("/comment/core/")
            || sourceUri.contains("/comment/adapter/")
            || sourceUri.contains("/file/api/")
            || sourceUri.contains("/file/core/")
            || sourceUri.contains("/file/adapter/");
}

@Test
void jpaAdaptersDoNotUseSpringDataRepositoryAsStoreImplementation() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage("..adapter.persistence..")
            .should().dependOnClassesThat()
            .haveFullyQualifiedName("org.springframework.data.jpa.repository.JpaRepository")
            .check(classes);
}

@Test
void persistenceAdaptersDoNotSelfRegisterWithComponentScanning() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    var componentRegisteredAdapters = classes.stream()
            .filter(javaClass -> javaClass.getPackageName().contains(".adapter.persistence"))
            .filter(javaClass -> javaClass.isAnnotatedWith("org.springframework.stereotype.Component")
                    || javaClass.isAnnotatedWith("org.springframework.stereotype.Service")
                    || javaClass.isAnnotatedWith("org.springframework.stereotype.Repository"))
            .map(JavaClass::getName)
            .toList();

    assertThat(componentRegisteredAdapters).isEmpty();

    var componentScannedConfigurations = classes.stream()
            .filter(javaClass -> javaClass.getPackageName().contains(".adapter.persistence"))
            .filter(javaClass -> javaClass.getSimpleName().endsWith("Configuration"))
            .filter(javaClass -> javaClass.isAnnotatedWith("org.springframework.context.annotation.Configuration"))
            .map(JavaClass::getName)
            .toList();

    assertThat(componentScannedConfigurations).isEmpty();
}
```

## Configuration Checks

```java
@Test
void scaffoldUsesFlywayAndValidateDdl() throws Exception {
    var applicationYaml = Files.readString(Path.of("src", "main", "resources", "application.yml"));

    assertThat(applicationYaml).contains("ddl-auto: validate");
    assertThat(applicationYaml).doesNotContain("ddl-auto: create", "ddl-auto: create-drop", "ddl-auto: update");
}
```

Required checks:

- Domain modules do not contain controllers or `adapter:web`.
- Architecture tests fail when expected `api/core/adapter.persistence` packages are absent.
- Domain `api/core` modules do not depend on app or adapter packages.
- Domain `api/core` modules do not depend on other bounded contexts.
- Domain `api/core` source or bytecode does not depend on JPA, Hibernate, QueryDSL, jOOQ, Flyway, Spring Web, Spring Data/JDBC/ORM/transaction, or SQL APIs.
- Persistence adapters do not depend on `shared:web-support`.
- Persistence adapters do not self-register with `@Component`, `@Service`, `@Repository`, or component-scanned `@Configuration`.
- Service contracts use `*Service`; concrete core implementations, including decorators and variants, use `*ServiceImpl`.
- App web/controller code depends on `*:api` service contracts, not concrete `*ServiceImpl` classes.
- Store implementations use technology-explicit `*StoreAdapter` names.
- Standard JPA Stores do not use `JpaRepository`.
- jOOQ-backed Stores do not use JPA, Spring Data, `JpaRepository`, or `EntityManager` for reads/writes.
- jOOQ-backed adapters keep JPA entities and Hibernate `ddl-auto: validate` schema verification.
- jOOQ code generation runs after Flyway-migrated schema verification and before `compileJava`/`test`.
- Paging mutation stays in service code, not Store adapters.

Avoid required checks that:

- Assert exact source file existence or one-off file paths. If source URI checks are needed to distinguish modules, keep them at stable module-boundary segments and prefer package/module metadata when available.
- Require one exact class/interface name when several role-equivalent decompositions would be acceptable.
- Maintain an exhaustive list of forbidden external Maven coordinates for web, DB, JDBC drivers, QueryDSL, jOOQ, Flyway, or Spring starters. If the stable boundary is "domain code must not use this technology," test package/type usage instead of dependency coordinate strings.
- Assert exact Store write command record names, parameter order/count/names, or method signatures instead of testing service and adapter behavior. Checks may still forbid app DTOs, read projections, adapter entities, JPA entities, jOOQ records, and Spring Data types at Store boundaries, but must not fail scalar parameter lists only because a command record would be cleaner.
- Enforce cleanup preferences with reflection/source-scan tests, such as "every Store write method must take exactly one command record" or "every command must use this exact suffix." Treat those as review/refactoring guidance unless the project has explicitly made them public contracts.
- Inspect AOP proxy internals when the contract is only that transaction/cache ownership stays outside `core`.
