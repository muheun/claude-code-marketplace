# SPI And Reuse Reference

SPI means Service Provider Interface: a contract that a host project implements to extend a reusable module without creating direct module dependencies.

## Core Rule

Reusable modules must not depend on host domains.

Example: `comment` must not depend on `board`, `product`, or `notice`. It should depend only on its own `api`, `core`, shared pure domain types, and its selected adapters.

## Target Integration Pattern

Put the SPI in the reusable module `api`:

```java
public interface CommentTargetPolicy {
    boolean isCommentable(CommentTarget target);

    default void ensureCommentable(CommentTarget target) {
        if (!isCommentable(target)) {
            throw new IllegalArgumentException("댓글을 작성할 수 없는 대상입니다.");
        }
    }
}
```

The host app implements it:

```java
class BoardPostCommentTargetPolicy implements CommentTargetPolicy {
    private final BoardPostService boardPostService;
    private final PostIdConverter postIdConverter;

    public boolean isCommentable(CommentTarget target) {
        if (!supports(target.type())) {
            return false;
        }

        return postIdConverter.tryFromExternal(target.id())
                .filter(boardPostService::exists)
                .isPresent();
    }
}
```

This implementation belongs in `app/.../support`, not in `comment` and not in `board:core`.

## What The Skill Should Generate

Generate the SPI shape and wiring point. Do not generate project-specific business policy unless the user asks.

Allowed:

- SPI interface in reusable module `api`
- default `ensure*` method that throws for command flows
- app-side implementation that calls host service `exists`
- app-side target converter/helper

Avoid:

- Hardcoding `BOARD_POST` as a universal policy
- Assuming every project needs closed/open target states
- Calling `get()` only to check existence
- Making reusable modules log, skip, or throw in a fixed way for all workflows
- Importing host domain classes in reusable modules

## Boolean Policy Methods

Prefer boolean `is*able` methods as the base SPI. Command flows may call `ensure*`; batch/import flows may call `is*able` and decide whether to log, skip, collect errors, or throw.
