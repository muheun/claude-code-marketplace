# Architecture Test Examples

## Contents

- [Baseline Gradle Checks](#baseline-gradle-checks)
- [Baseline API/Core/Adapter Boundary Checks](#baseline-apicoreadapter-boundary-checks)
- [Conditional Static Enforcement Checks](#conditional-static-enforcement-checks)
- [Avoid Required Checks That](#avoid-required-checks-that)

Use these as compact starting points. Adapt package names and module names to the project.

Architecture tests should guard stable architecture, not every design preference. Start and usually stop with baseline modularization checks: selected modules exist and dependency direction is correct. Add broad source/bytecode checks for technology bans, controller placement, adapter self-registration, and build/persistence policies only when the project already treats that static enforcement as stable policy, the current task touches the boundary, or the user asks to enforce it.

Do not add architecture tests for service method prefixes, Store method prefixes, exact interface names, command names, helper names, or file layout. Those are guide/review concerns unless the project explicitly makes them enforced policy.

## Baseline Gradle Checks

Use Gradle/build-file checks only for stable internal project boundaries: selected modules exist, `core` depends on its own `api`, `api` does not depend on its own `core`, and every selected technology adapter depends inward only on its own `api` and/or `core` contracts as its role requires. Persistence, outbound messaging, and cache port implementations normally depend on `core`; a reusable inbound messaging adapter may depend on `api`. No technology adapter depends on `app`, web-support, or another bounded context. `persistence-schema` stays resource-only by default, and `app` composes the selected domain modules, persistence, messaging, and cache adapters, and schema resources. Domain `api/core` remains free of technology adapters, app, web-support, and other bounded contexts. The compact example below only checks selected module inclusion; add build dependency checks when the build file is the smallest reliable enforcement point for dependency direction.

Keep custom parsers modest. If parsing Gradle accurately becomes larger than the boundary being protected, reduce the check to selected module inclusion and rely on Gradle compilation plus review for the rest.

Do not build broad external Maven-coordinate blacklists for DB, web, Kafka, or cache-client libraries. External artifacts change by Spring Boot version, starter choice, plugin convention, and vendor; if a project opts into technology bans, verify actual package/type usage with a narrow source or bytecode check.

```java
@Test
void selectedDomainModulesAreIncluded() throws Exception {
    var settings = Files.readString(Path.of("..", "settings.gradle.kts"));

    assertThat(settings).contains(
            "\"leave:api\"",
            "\"leave:core\"",
            "\"leave:adapter:persistence-schema\"",
            "\"leave:adapter:persistence-jooq\"",
            "\"leave:adapter:messaging-kafka\"",
            "\"member:api\"",
            "\"member:core\"",
            "\"member:adapter:persistence-schema\"",
            "\"member:adapter:persistence-jpa\"",
            "\"member:adapter:cache-redis\"",
            "\"app\"");
}
```

Keep the settings lookup robust: locate the project root by walking up parent directories until the settings file is found, or inject the path with a system property, instead of relying on the test working directory. Exclude commented-out `include` lines before matching so a disabled module cannot satisfy the check.

The example names messaging and cache modules because this sample project selected them. Omit unselected adapters from the expected module list; neither Kafka nor a cache adapter is universally required.

## Baseline API/Core/Adapter Boundary Checks

The examples show one bounded context (`leave`); repeat or parameterize per bounded context. The shown dependency rule checks only `leave` adapters, so the sample project must add the same rule for `member` to cover its selected cache adapter. Precondition for the package-existence assertion: the architecture test module must have every asserted module on its classpath, otherwise the check fails even when the module exists. Assert only adapter packages selected by that bounded context; the sample `leave` context selected persistence and Kafka, while an unselected messaging or cache package must not be required.

```java
@Test
void expectedModulePackagesExist() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    assertPackageExists(classes, ".leave.api.");
    assertPackageExists(classes, ".leave.core.");
    assertPackageExists(classes, ".leave.adapter.persistence.");
    assertPackageExists(classes, ".leave.adapter.messaging.");
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
}

@Test
void selectedTechnologyAdaptersDoNotDependOnAppWebSupportOrOtherContexts() {
    var classes = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("com.example");

    noClasses()
            .that().resideInAnyPackage("..leave.adapter..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..app..",
                    "..websupport..",
                    "..web.support..",
                    "..member..")
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
- Domain `api/core` source or bytecode does not use Kafka APIs such as `org.apache.kafka` or `org.springframework.kafka` when the project has stabilized that messaging boundary.
- Domain `api/core` source or bytecode does not use cache APIs or clients such as Spring Cache, Spring Data Redis, Lettuce, or Caffeine when the project has stabilized that cache boundary.
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
- Require service method prefixes such as `remove` instead of `delete`, Store method prefixes, exact suffixes, or other naming rules as always-on required checks; enforce them during implementation and review unless naming enforcement is an explicit project policy. Suffix checks promoted through the Conditional Static Enforcement Checks section above, such as `*Service`/`*ServiceImpl` or technology-explicit `*StoreAdapter`, are exempt.
- Maintain an exhaustive list of forbidden external Maven coordinates for web, DB, JDBC drivers, QueryDSL, jOOQ, Flyway, Kafka, cache clients, or Spring starters.
- Promote every code review note into a global architecture test. First decide whether the rule is baseline modularization, opt-in project policy, or review-only guidance.
- Assert exact Store write command record names, parameter order/count/names, or method signatures instead of testing service and adapter behavior.
- Enforce cleanup preferences with reflection/source-scan tests, such as "every Store write method must take exactly one command record" or "every command must use this exact suffix."
- Inspect AOP proxy internals when the contract is only that transaction/cache ownership stays outside `core`.
