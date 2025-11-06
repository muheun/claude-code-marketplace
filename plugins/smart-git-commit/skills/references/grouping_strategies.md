# Commit Grouping Strategies

Advanced algorithms and patterns for intelligent commit grouping.

## Overview

When dealing with large changesets (10+ files), grouping related changes into separate commits improves:
- **Code review efficiency**: Reviewers can focus on one logical change at a time
- **Git history clarity**: Each commit represents a complete, cohesive change
- **Rollback precision**: Revert specific features without affecting others
- **CI/CD optimization**: Smaller commits reduce build/test time per change

---

## Grouping Algorithm

### Phase 1: Primary Grouping (Directory Structure)

**Priority: Highest**

Group files by their directory structure, as directories typically represent modules or features.

**Pattern:**
```
src/user/
  User.kt
  UserService.kt
  UserRepository.kt
→ Group: "User 모듈"

src/product/
  Product.kt
  ProductService.kt
→ Group: "Product 모듈"
```

**Implementation:**
1. Extract directory path from each file: `src/user/User.kt` → `src/user/`
2. Group files sharing the same directory
3. Create group name from directory: `src/user/` → "User 모듈"

---

### Phase 2: Secondary Grouping (File Naming Patterns)

**Priority: High**

When directory structure alone is insufficient, use file naming patterns.

**Patterns:**
```
User*.kt → "User" domain
Product*.kt → "Product" domain
*Test.kt, *_test.py, *.test.ts → "Tests"
*Controller.kt → "Controllers"
*Service.kt → "Services"
README.md, docs/*.md → "Documentation"
```

**Example:**
```
src/controllers/
  UserController.kt
  ProductController.kt
→ Split into:
  Group 1: UserController.kt (User domain)
  Group 2: ProductController.kt (Product domain)
```

---

### Phase 3: Tertiary Grouping (Change Types)

**Priority: Medium**

Group by the type of change when other methods don't provide clear separation.

**Categories:**

1. **Implementation** (`.kt`, `.py`, `.ts`, `.java`, `.go`)
   - Core business logic and features

2. **Tests** (`*Test.kt`, `*_test.py`, `*.test.ts`, `*.spec.js`)
   - Unit tests, integration tests

3. **Documentation** (`README.md`, `*.md` in `docs/`)
   - User-facing documentation

4. **Configuration** (`package.json`, `build.gradle`, `*.toml`, `*.yml`)
   - Build and deployment configuration

5. **Assets** (`*.png`, `*.svg`, `*.css`)
   - Static resources

**Example:**
```
Changeset:
  src/User.kt (implementation)
  src/UserService.kt (implementation)
  tests/UserTest.kt (test)
  README.md (docs)

→ Groups:
  Group 1: Implementation (User.kt, UserService.kt)
  Group 2: Tests (UserTest.kt)
  Group 3: Documentation (README.md)
```

---

### Phase 4: Semantic Analysis (Diff Content)

**Priority: Low (fallback)**

When structural grouping fails, analyze actual code changes to detect relationships.

**Detection patterns:**

1. **Import relationships:**
   ```kotlin
   // UserService.kt
   import com.example.UserRepository  // → Related to UserRepository.kt
   ```

2. **Class references:**
   ```kotlin
   // UserController.kt
   class UserController(private val userService: UserService)  // → Related to UserService.kt
   ```

3. **Shared functionality:**
   ```python
   # user_service.py
   def create_user(user_data: UserDTO)  # → Related to user_dto.py
   ```

**Implementation:**
- Extract import statements from diff
- Identify class/function references
- Group files with mutual references

---

## Project-Specific Patterns

### Monorepo Structure

**Pattern:**
```
packages/
  auth/
    src/
    tests/
  billing/
    src/
    tests/
```

**Grouping strategy:**
- Group by top-level package first (`auth/`, `billing/`)
- Then by type within package (`src/`, `tests/`)

**Example:**
```
Group 1: Auth 모듈 구현
  packages/auth/src/AuthService.kt
  packages/auth/src/TokenValidator.kt

Group 2: Auth 테스트
  packages/auth/tests/AuthTest.kt

Group 3: Billing 모듈 구현
  packages/billing/src/PaymentService.kt
```

---

### Feature-Based Structure

**Pattern:**
```
features/
  user-management/
    components/
    hooks/
    api/
  product-catalog/
    components/
    hooks/
```

**Grouping strategy:**
- Group by feature directory (`user-management/`, `product-catalog/`)
- Keep feature components together regardless of subdirectory

**Example:**
```
Group 1: User Management 기능
  features/user-management/components/UserList.tsx
  features/user-management/hooks/useUser.ts
  features/user-management/api/userApi.ts

Group 2: Product Catalog 기능
  features/product-catalog/components/ProductGrid.tsx
  features/product-catalog/hooks/useProduct.ts
```

---

### Layer-Based Architecture

**Pattern:**
```
src/
  controllers/
  services/
  repositories/
  models/
```

**Grouping strategy:**
- Group by domain across layers (User across all layers)
- NOT by layer (all controllers together)

**Example:**
```
✅ Good:
Group 1: User 모듈 (all layers)
  controllers/UserController.kt
  services/UserService.kt
  repositories/UserRepository.kt
  models/User.kt

❌ Bad:
Group 1: Controllers
  controllers/UserController.kt
  controllers/ProductController.kt
```

---

## Edge Cases and Fallback Strategies

### Case 1: Ambiguous Grouping

**Scenario:** Files could belong to multiple groups

```
Changeset:
  src/common/Validator.kt (shared utility)
  src/user/User.kt
  src/product/Product.kt
```

**Strategy:**
- Create separate group for shared utilities
- OR include in the group that uses it most

```
Option A:
  Group 1: 공통 유틸리티 (Validator.kt)
  Group 2: User 모듈 (User.kt)
  Group 3: Product 모듈 (Product.kt)

Option B (if Validator is primarily for User):
  Group 1: User 모듈 (User.kt, Validator.kt)
  Group 2: Product 모듈 (Product.kt)
```

---

### Case 2: Cross-Cutting Changes

**Scenario:** Single change affects multiple modules

```
Refactoring:
  src/user/UserService.kt (updated API)
  src/product/ProductService.kt (updated API)
  src/order/OrderService.kt (updated API)
```

**Strategy:**
- **Keep as single commit** (cross-cutting refactoring)
- Do NOT split (would break atomicity)

```
✅ Single commit:
♻️ refactor: Service 레이어 API 통일

- UserService API 업데이트
- ProductService API 업데이트
- OrderService API 업데이트
```

---

### Case 3: Dependent Groups

**Scenario:** Group B depends on Group A

```
Changeset:
  src/user/User.kt (new entity)
  src/order/Order.kt (references User.kt)
```

**Strategy:**
- Commit in dependency order (Group A → Group B)
- Ensure each commit is buildable

```
Commit 1:
✨ feat: User 엔티티 추가

Commit 2 (depends on Commit 1):
✨ feat: Order 엔티티 추가
- User 참조 관계 설정
```

---

### Case 4: Ungroupable Changes

**Scenario:** No clear grouping pattern

```
Changeset:
  fix typo in README.md
  update dependency version
  add new API endpoint
  refactor util function
```

**Strategy:**
- Fallback to **single commit**
- Inform user grouping is unclear

```
⚠️ Grouping unclear for this changeset.

Recommended: Create single commit with all changes.

Proceed with single commit? (yes/no)
```

---

## Grouping Quality Heuristics

### Good Grouping Indicators

✅ **Cohesion**: Files in group are closely related
✅ **Completeness**: Group represents a complete logical change
✅ **Independence**: Groups can be reviewed/tested separately
✅ **Size balance**: Groups have roughly similar size (not 1 file vs 20 files)

### Bad Grouping Indicators

❌ **Fragmentation**: Too many tiny groups (10 groups with 1 file each)
❌ **Mixed concerns**: Group contains unrelated changes
❌ **Breaking changes**: Group B fails without Group A
❌ **Size imbalance**: Group 1 has 1 file, Group 2 has 25 files

---

## Algorithm Decision Tree

```
Start: Analyze changeset
  │
  ├─ Files < 10? → Skip grouping, single commit
  │
  ├─ Clear directory structure?
  │   └─ Yes → Group by directory (Phase 1)
  │   └─ No → Continue
  │
  ├─ Clear naming patterns?
  │   └─ Yes → Group by naming (Phase 2)
  │   └─ No → Continue
  │
  ├─ Distinguishable change types?
  │   └─ Yes → Group by type (Phase 3)
  │   └─ No → Continue
  │
  ├─ Detectable semantic relationships?
  │   └─ Yes → Group by semantics (Phase 4)
  │   └─ No → Fallback to single commit
  │
End: Present grouping to user
```

---

## Implementation Notes

### User Interaction

Always present grouping as a **suggestion**, not a requirement:

```
Suggested grouping:
📦 Group 1: User 모듈 (5 files)
📦 Group 2: Product 모듈 (4 files)
📦 Group 3: 테스트 (3 files)

Options:
1. ✅ Accept grouping
2. ⚠️ Single commit instead
3. ✏️ Modify grouping
4. ❌ Cancel
```

### Fallback Safety

If any step fails or produces unclear results:
- Offer single commit option
- Never force grouping on ambiguous changes
- Respect user's decision to skip grouping

### Performance Considerations

- Limit analysis depth for very large changesets (>50 files)
- Use file paths and names first (fast)
- Use diff content analysis only when necessary (slow)
- Set maximum groups limit (e.g., 5-7 groups max)

---

## Examples

### Example 1: Backend API Development

**Changeset:**
```
src/api/UserController.kt (new)
src/api/ProductController.kt (new)
src/service/UserService.kt (new)
src/service/ProductService.kt (new)
src/repository/UserRepository.kt (new)
src/repository/ProductRepository.kt (new)
tests/UserApiTest.kt (new)
tests/ProductApiTest.kt (new)
```

**Grouping (Phase 2 - Naming Patterns):**
```
Group 1: User API 구현 (4 files)
  src/api/UserController.kt
  src/service/UserService.kt
  src/repository/UserRepository.kt
  tests/UserApiTest.kt

Group 2: Product API 구현 (4 files)
  src/api/ProductController.kt
  src/service/ProductService.kt
  src/repository/ProductRepository.kt
  tests/ProductApiTest.kt
```

---

### Example 2: Frontend Component Development

**Changeset:**
```
src/components/UserProfile.tsx (new)
src/components/UserList.tsx (new)
src/hooks/useUser.ts (new)
src/api/userApi.ts (new)
src/components/ProductCard.tsx (new)
src/hooks/useProduct.ts (new)
tests/UserProfile.test.tsx (new)
tests/ProductCard.test.tsx (new)
```

**Grouping (Phase 2 - Naming Patterns):**
```
Group 1: User 컴포넌트 구현 (4 files)
  src/components/UserProfile.tsx
  src/components/UserList.tsx
  src/hooks/useUser.ts
  src/api/userApi.ts
  tests/UserProfile.test.tsx

Group 2: Product 컴포넌트 구현 (2 files)
  src/components/ProductCard.tsx
  src/hooks/useProduct.ts
  tests/ProductCard.test.tsx
```

---

### Example 3: Mixed Changes (Fallback)

**Changeset:**
```
README.md (typo fix)
package.json (dependency update)
src/utils/helper.ts (new utility)
src/config.ts (environment update)
```

**Grouping: NOT POSSIBLE**
```
⚠️ Unable to identify clear grouping pattern.

Recommended: Single commit with all changes.

Proceed? (yes/no)
```

If user says yes:
```
🔧 chore: 프로젝트 설정 및 유틸리티 업데이트

- README 오타 수정
- 의존성 업데이트
- 헬퍼 유틸리티 추가
- 환경 설정 업데이트
```
