# Architecture Test Examples

Use these as compact starting points. Adapt package names and module names to the project.

Architecture tests should guard stable architecture, not every design preference. Start and usually stop with baseline modularization checks: selected modules exist and dependency direction is correct. Add broad source/bytecode checks for technology bans, controller placement, adapter self-registration, and build/persistence policies only when the project already treats that static enforcement as stable policy, the current task touches the boundary, or the user asks to enforce it.

Do not add architecture tests for service method prefixes, Store method prefixes, exact interface names, command names, helper names, or file layout. Those are guide/review concerns unless the project explicitly makes them enforced policy.

## Baseline Gradle Checks

Use Gradle/build-file checks only for stable internal project boundaries: selected modules exist, `core` depends on its own `api`, `api` does not depend on its own `core`, selected `adapter:persistence-*` modules depend on their own `core`, `app` composes selected domain modules, `api/core` do not depend on `app`, adapters, web-support, or other bounded contexts, and persistence adapters do not depend on `app`, web-support, or other bounded contexts. The compact example below only checks selected module inclusion; add build dependency checks when the build file is the smallest reliable enforcement point for dependency direction.

Keep custom parsers modest. If parsing Gradle accurately becomes larger than the boundary being protected, reduce the check to selected module inclusion and rely on Gradle compilation plus review for the rest.

Do not build broad external Maven-coordinate blacklists for DB/web libraries. External artifacts change by Spring Boot version, starter choice, plugin convention, and vendor; if a project opts into technology bans, verify actual package/type usage with a narrow source or bytecode check.

```java
@Test
void selectedDomainModulesAreIncluded() throws Exception {
    var settings = Files.readString(Path.of("..", "settings.gradle.kts"));

    assertThat(settings).contains(
            "\"leave:api\"",
            "\"leave:core\"",
            "\"leave:adapter:persistence-jooq\"",
            "\"member:api\"",
            "\"member:core\"",
            "\"member:adapter:persistence-jpa\"",
            "\"app\"");
}
```

## Baseline API/Core Boundary Checks

```java
@Test
void expectedModulePackagesExist() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    assertPackageExists(classes, ".leave.api.");
    assertPackageExists(classes, ".leave.core.");
    assertPackageExists(classes, ".leave.adapter.persistence.");
    assertPackageExists(classes, ".member.api.");
    assertPackageExists(classes, ".member.core.");
    assertPackageExists(classes, ".member.adapter.persistence.");
}

@Test
void apiModulesDoNotDependOnCoreAdaptersAppWebSupportOrOtherContexts() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage("..leave.api..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..leave.core..",
                    "..app..",
                    "..adapter..",
                    "..websupport..",
                    "..web.support..",
                    "..member..")
            .check(classes);

    noClasses()
            .that().resideInAnyPackage("..member.api..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..member.core..",
                    "..app..",
                    "..adapter..",
                    "..websupport..",
                    "..web.support..",
                    "..leave..")
            .check(classes);
}

@Test
void coreModulesDoNotDependOnAppAdaptersWebSupportOrOtherContexts() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage("..leave.core..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..app..",
                    "..adapter..",
                    "..websupport..",
                    "..web.support..",
                    "..member..")
            .check(classes);

    noClasses()
            .that().resideInAnyPackage("..member.core..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..app..",
                    "..adapter..",
                    "..websupport..",
                    "..web.support..",
                    "..leave..")
            .check(classes);
}

@Test
void selectedPersistenceAdaptersDoNotDependOnAppWebSupportOrOtherContexts() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage("..leave.adapter.persistence..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..app..",
                    "..websupport..",
                    "..web.support..",
                    "..member..")
            .check(classes);

    noClasses()
            .that().resideInAnyPackage("..member.adapter.persistence..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..app..",
                    "..websupport..",
                    "..web.support..",
                    "..leave..")
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

## Conditional Static Enforcement Checks

The guide can still make a design rule mandatory while keeping broad static enforcement proportional. Add these checks only when the rule is already a project standard, the current task touches that boundary, or the user asks to enforce it:

- Domain modules do not contain controllers or `adapter:web`.
- Domain `api/core` source or bytecode does not use JPA, Hibernate, QueryDSL, jOOQ, Flyway, Spring Web, Spring Data/JDBC/ORM/transaction, or SQL APIs.
- Persistence adapters do not self-register with `@Component`, `@Service`, `@Repository`, or component-scanned `@Configuration`.
- Service contracts use `*Service`; concrete core implementations, including decorators and variants, use `*ServiceImpl`.
- App web/controller code depends on `*:api` service contracts, not concrete `*ServiceImpl` classes.
- Store implementations use technology-explicit `*StoreAdapter` names.
- Standard JPA Stores do not use `JpaRepository`.
- jOOQ-backed Stores do not use JPA, Spring Data, `JpaRepository`, or `EntityManager` for reads/writes.
- jOOQ-backed adapters keep JPA entities and Hibernate `ddl-auto: validate` schema verification.
- jOOQ code generation runs after Flyway-migrated schema verification and before `compileJava`/`test`.
- Paging mutation stays in service code, not Store adapters.

## Avoid Required Checks That

- Assert exact source file existence or one-off file paths. If source URI checks are needed to distinguish modules, keep them at stable module-boundary segments and prefer package/module metadata when available.
- Require one exact class/interface name when several role-equivalent decompositions would be acceptable.
- Require service method prefixes such as `remove` instead of `delete`, Store method prefixes, exact suffixes, or other naming rules that should be enforced during implementation and review unless naming enforcement is an explicit project policy.
- Maintain an exhaustive list of forbidden external Maven coordinates for web, DB, JDBC drivers, QueryDSL, jOOQ, Flyway, or Spring starters.
- Promote every code review note into a global architecture test. First decide whether the rule is baseline modularization, opt-in project policy, or review-only guidance.
- Assert exact Store write command record names, parameter order/count/names, or method signatures instead of testing service and adapter behavior.
- Enforce cleanup preferences with reflection/source-scan tests, such as "every Store write method must take exactly one command record" or "every command must use this exact suffix."
- Inspect AOP proxy internals when the contract is only that transaction/cache ownership stays outside `core`.
