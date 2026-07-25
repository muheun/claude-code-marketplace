# Messaging (Kafka)

## Contents

- [Default Stack and Cost Policy](#default-stack-and-cost-policy)
- [Module Placement](#module-placement)
- [Contract Ownership](#contract-ownership)
- [Transaction and Delivery](#transaction-and-delivery)
- [Consumer Rules](#consumer-rules)
- [Serialization and Topic Contracts](#serialization-and-topic-contracts)
- [Managed and Commercial Services](#managed-and-commercial-services)
- [Testing](#testing)
- [Common Mistakes](#common-mistakes)

## Default Stack and Cost Policy

- Default broker: Apache Kafka (open source, self-hostable). Dev runs the official `apache/kafka` image in KRaft mode via Docker Compose. Use the Strimzi operator as the default only when the project operates Kafka on Kubernetes and has no established deployment mechanism; otherwise follow the project's established mechanism.
- Do not select a paid or managed service (Confluent Cloud, Amazon MSK, Azure Event Hubs, and similar) by default. Choose one only when the project already runs it or the user explicitly opts in; then apply the Managed and Commercial Services section.
- Use `<version>` placeholders or the project version catalog for Spring Kafka and broker image versions; resolve actual versions from the project build, never by copying a pinned number from documentation.

## Module Placement

| Artifact | Module |
|---|---|
| Domain event meaning and framework-neutral event-recording, outbox storage, and outbound message ports | `<domain>:api` / `<domain>:core` |
| Outbox row/table and event-recording/outbox store implementations | the domain's persistence adapter / schema module |
| Kafka producer/client and outbound message port implementation | `<domain>:adapter:messaging-kafka` |
| Relay scheduling, topic configuration, adapter composition, and a host-specific subscription's `@KafkaListener` + wire DTO (single-host default) | `app` |
| A reusable subscription's `@KafkaListener`, wire DTO/deserializer, and consumer configuration (only once a second host consumes it) | an inbound `<domain>:adapter:messaging-kafka` selected by `app` |

- `adapter:messaging-kafka` is a sibling of `adapter:persistence-*`, with role-sensitive inward dependencies: an outbound adapter may implement its bounded context's `core` ports, while a reusable inbound adapter may call that bounded context's framework-neutral `api`. Neither role depends on `app`, web-support, or another bounded context; the adapter never self-registers via component scan and is selected by app `@Import`. A context needing both roles may keep them in one `messaging-kafka` module (depending on both `api` and `core`) or split outbound and inbound modules; either layout keeps the per-role dependency limits above.
- No `org.apache.kafka` or `org.springframework.kafka` type appears in any `api` or `core` module. This is the messaging analogue of the Store write-input rule.
- Both inbound ownership modes keep `api/core` Kafka-free; a reusable inbound adapter calls only the consuming context's framework-neutral service API and never depends on `app`.
- Keep event recording distinct from transport publishing. A persistence adapter records the event in the outbox; an app-owned relay later passes a framework-neutral outbound envelope to the Kafka adapter.

## Contract Ownership

- The domain event record lives in the producing context's `core` and carries semantic data only: public identifiers (UUIDv7 or ULID per the identifier strategy in `persistence.md`), amounts, timestamps. Never DB PKs, translated text, or channel templates (see `i18n.md` for non-HTTP rendering).
- The topic schema is the cross-context contract, not a shared Java class. Each consuming context owns its wire DTO in its selected inbound boundary: `app` for a host-specific subscription, or the inbound messaging adapter for a reusable subscription. Never share the producer's event class across contexts.
- Every outbound envelope carries `eventId`, `aggregateId`, aggregate sequence/version, event type, occurrence time, payload schema version, and payload. Assign the stable `eventId` exactly once when the event/outbox row is created, persist it, and reuse it unchanged for every relay attempt, redelivery, or manual replay.

## Transaction and Delivery

- Default: transactional outbox. Persist the business state change and its complete outbox envelope atomically in one local database transaction. A rollback leaves neither change committed.
- The app-owned relay may run with competing workers, but claiming is a recoverable lease rather than a terminal state. Store claim owner and lease expiry (or an equivalent recoverable claim), reclaim expired work after a crash, and keep the same `eventId` on every attempt.
- Preserve per-aggregate ordering at the outbox boundary. A worker may claim only the row with the lowest unpublished aggregate sequence, and the claim operation must prevent another worker from concurrently claiming a later sequence for that aggregate. Other aggregates may publish in parallel.
- Send the claimed envelope through the framework-neutral outbound message port and mark the row published only after broker acknowledgment. A crash after broker acknowledgment but before the published mark causes a duplicate by design, so the contract is at-least-once rather than exactly-once.
- Use `aggregateId` as the Kafka key so records submitted in order for one aggregate stay in one partition. The key preserves submitted partition order; it cannot repair relay reordering, which is why next-sequence-only claiming is required before send.
- Direct publish (no outbox) is allowed only when losing the event on a crash between commit and send is explicitly acceptable (fire-and-forget signals with no downstream obligation). Record that acceptance in the design note.
- Kafka transactions do not span an external RDBMS; do not present them as an outbox alternative.

## Consumer Rules

- For a host-specific subscription, the `@KafkaListener` and its wire DTO/deserializer may be app-owned, exactly like a controller and request DTO. The listener calls the consuming context's framework-neutral service API with a service command; it contains no business logic.
- When the same subscription must be reused by more than one host application, move its `@KafkaListener`, wire DTO/deserializer, and consumer configuration together into an inbound `<domain>:adapter:messaging-kafka`. The adapter calls the same framework-neutral service API, does not depend on `app`, and is selected by each app; the app still supplies host-specific broker and topic settings. Until a second host exists, keep the subscription in `app`.
- Delivery is at-least-once. Scope processed-event idempotency to the logical consumer or subscription, not globally to `eventId`. Use either one marker table per logical consumer or a unique constraint on `(consumer/subscription identity, eventId)`; the identity is stable and shared by every replica of that logical consumer. Insert the scoped marker and apply the business mutation in one local transaction. A duplicate for the same logical consumer skips the already-applied mutation; a failed mutation rolls back the marker as well. Two independent subscriptions receiving the same event use distinct scopes and each apply their own mutation.
- Complete or acknowledge the Kafka offset only after that local transaction commits. If the process crashes after commit but before offset completion, Kafka redelivers and the processed-event uniqueness check makes the retry harmless.
- Kafka offsets are cumulative per partition. While poison transfer or transient processing remains unresolved, enforce a partition barrier such as pause/seek, blocking retry, stopping and seeking the remaining batch records, or an equivalent mechanism that prevents later records from advancing the committed offset past the failed position. Leaving only the failed record unacknowledged is not sufficient. Release the barrier only after the failed record succeeds or its durable terminal transfer succeeds.
- Route poison input separately before service invocation. Deserialization failures, unsupported payload schema versions, and envelope or wire validation failures go directly to a quarantine/dead-letter path with diagnostics; they do not enter business processing retries and never call the service. Complete the poison source offset only after successful durable transfer to that path. If the transfer fails, keep the source offset incomplete and the partition barrier in place so the record can be redelivered and the transfer retried without invoking the service.
- Treat transient processing failures after service invocation as retryable. Use bounded attempts with backoff; keep the partition barrier in place while an attempt or its local transaction has failed. After exhaustion, durably transfer the original envelope to the dead-letter path before completing the source offset, preserve its `eventId` for controlled replay, and release the barrier only after that transfer succeeds.

## Serialization and Topic Contracts

- Default payload format: plain JSON with a versioned topic name (`<context>.<event>.v1`) and the payload schema version in the envelope. Breaking changes create `v2`, never mutate `v1` in place.
- A schema registry is opt-in, not default. If the project wants one, prefer Apicurio Registry (open source); Confluent Schema Registry is under the Confluent Community License, not an OSI license — treat it as a commercial-adjacent choice and record the decision.

## Managed and Commercial Services

Apply when the project has explicitly opted into a paid or managed broker:

- Keep every port and adapter on the open Kafka protocol. Provider-specific features (IAM auth adapters, proprietary connectors, ksqlDB) stay in `app` configuration or a dedicated adapter, never in domain contracts, so the code remains portable to self-hosted Kafka.
- Auth, TLS, and endpoint configuration go through app configuration and the secret store, not code.
- State the cost consequence in the change description and get the user's confirmation before adding the dependency; do not upgrade a project onto a paid tier silently.
- Tests still run against the open-source image via Testcontainers; provider-specific behavior is verified in a staging environment, not unit tests.

## Testing

- Sender adapter and listener integration tests use Testcontainers with the official Apache Kafka image — never an embedded broker substitute, same principle as the no-H2 rule in `testing-checklist.md`.
- Core service tests use a hand-written capturing fake for the publisher port (state matters: exactly-one-event assertions).
- Persistence integration tests prove state/outbox atomicity, stable `eventId` reuse, expired-claim recovery, and next-sequence-only claims with competing relay workers.
- Listener tests verify forwarding (valid payload → one service call; poison payload → dead-letter, no call) with a Mockito service mock and Awaitility for async assertions.
- Architecture baseline extends the existing dependency-direction rule: no Kafka packages in `api`/`core`; an outbound messaging adapter may depend on its own `core`, a reusable inbound messaging adapter may depend on its own framework-neutral `api`, and neither depends on `app`, web-support, or another bounded context.
- Consumer integration tests cover both ownership modes and prove scoped duplicate handling, rollback of both the processed-event marker and business mutation, post-commit offset completion, bounded transient retries, and partition barriers for poison or terminal transfer failure. Give two independent subscriptions the same `eventId` and prove both process it while replicas of either subscription share one stable idempotency scope.
- In a single-partition test, place failed record `n` immediately before valid record `n+1`; `n+1` must not advance the committed partition offset past `n` until `n` succeeds or its durable terminal transfer succeeds.

## Common Mistakes

- `KafkaTemplate` or `@KafkaListener` inside a `core` service.
- Publishing inside the transaction (rollback ghost-publishes) or in `afterCommit` (crash loses the event) when the event carries a downstream obligation.
- Generating a new `eventId` on retry, using a non-recoverable claimed state, or allowing competing workers to claim later aggregate sequences.
- Assuming a Kafka key repairs messages that the relay submitted out of order.
- Recording processed-event uniqueness outside the business transaction or acknowledging the offset before commit.
- Treating global `eventId` uniqueness as consumer idempotency, so one independent subscription suppresses another.
- Completing a poison record's source offset before its quarantine/dead-letter transfer succeeds, or assuming one unacknowledged record prevents later same-partition records from advancing the cumulative offset.
- Moving a reusable `@KafkaListener` into an adapter while leaving its wire DTO/deserializer or consumer configuration in `app`, or making that adapter depend on app types.
- Sending poison input through the same retry path as transient processing failures.
- Sharing one event class across producing and consuming contexts.
- Selecting a managed broker in the design without a project opt-in on record.
- Selecting Strimzi by default when Kafka is not operated on Kubernetes or the project already has a deployment mechanism.
- Pinning broker or Spring Kafka versions copied from examples instead of resolving them from the project build.
