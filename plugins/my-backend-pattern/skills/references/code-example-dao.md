# Code Example — DAO (PushLogDao)

실제 운영 중인 jOOQ DAO 표준 코드. 새 DAO 작성 시 이 구조를 그대로 따른다.

## 컨텍스트

- 프로젝트: slack-bot
- 도메인: Git push log 적재 + 조회
- 사용 도구: jOOQ (DSLContext) + Spring Repository

## 전체 코드

```java
package me.muheun.slackbot.dao;

import lombok.RequiredArgsConstructor;
import me.muheun.slackbot.domain.GitVo;
import me.muheun.slackbot.utils.DateUtils;
import org.jooq.Condition;
import org.jooq.DSLContext;
import org.jooq.Query;
import org.jooq.impl.DSL;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;

import static me.muheun.slackbot.domain.jooq.Tables.PUSH_LOG;

@Repository
@RequiredArgsConstructor
public class PushLogDao {

    private static final int BATCH_CHUNK_SIZE = 50;

    private final DSLContext dsl;

    public void insertBatch(List<GitVo.InsertVo> list) {
        for (int i = 0; i < list.size(); i += BATCH_CHUNK_SIZE) {
            List<GitVo.InsertVo> chunk = list.subList(i, Math.min(i + BATCH_CHUNK_SIZE, list.size()));
            dsl.batch(chunk.stream().map(vo ->
                    (Query) dsl.insertInto(PUSH_LOG)
                            .set(PUSH_LOG.ORGANIZATION, vo.organization())
                            .set(PUSH_LOG.PROJECT, vo.project())
                            .set(PUSH_LOG.BRANCH, vo.branch())
                            .set(PUSH_LOG.IS_TOP_BRANCH, vo.isTopBranch())
                            .set(PUSH_LOG.MESSAGE, vo.message())
                            .set(PUSH_LOG.COMMITED_AT, vo.commitedAt())
                            .set(PUSH_LOG.COMMIT_URL, vo.commitUrl())
                            .set(PUSH_LOG.COMMITTER, vo.committer())
                            .set(PUSH_LOG.EMAIL, vo.email())
                            .set(PUSH_LOG.CREATED_AT, DateUtils.nowKst())
            ).toArray(Query[]::new)).execute();
        }
    }

    public GitVo.SearchVo selectBy(GitVo.SearchVo paging) {
        Condition where = buildCondition(paging);

        int count = dsl.fetchCount(dsl.selectFrom(PUSH_LOG).where(where));

        if (count > 0) {
            paging.calcPaging(count);
            List<GitVo.ListVo> list = dsl.selectFrom(PUSH_LOG)
                    .where(where)
                    .orderBy(PUSH_LOG.COMMITED_AT.desc())
                    .offset(paging.offset())
                    .limit(paging.limit())
                    .fetchInto(GitVo.ListVo.class);
            paging.setBody(list);
        }
        return paging;
    }

    private Condition buildCondition(GitVo.SearchVo paging) {
        List<Condition> conditions = new ArrayList<>();

        if (paging.getProject() != null && !paging.getProject().isEmpty()) {
            String pattern = "%" + paging.getProject().toLowerCase() + "%";
            conditions.add(DSL.lower(PUSH_LOG.PROJECT).like(pattern)
                    .or(DSL.lower(PUSH_LOG.ORGANIZATION).like(pattern)));
        }
        if (paging.getBranch() != null && !paging.getBranch().isEmpty()) {
            String pattern = "%" + paging.getBranch().toLowerCase() + "%";
            conditions.add(DSL.lower(PUSH_LOG.BRANCH).like(pattern));
        }
        if (paging.getCommitter() != null && !paging.getCommitter().isEmpty()) {
            String pattern = "%" + paging.getCommitter().toLowerCase() + "%";
            conditions.add(DSL.lower(PUSH_LOG.COMMITTER).like(pattern)
                    .or(DSL.lower(PUSH_LOG.EMAIL).like(pattern)));
        }

        Condition where = DSL.trueCondition();
        for (Condition c : conditions) {
            where = where.and(c);
        }
        return where;
    }
}
```

## 학습 포인트

### 1. 클래스 구조
- `@Repository` + `@RequiredArgsConstructor`
- `DSLContext dsl` 필드 주입
- `BATCH_CHUNK_SIZE` 상수로 배치 크기 명시 (50)

### 2. 배치 입력 패턴 (`insertBatch`)
```java
for (int i = 0; i < list.size(); i += BATCH_CHUNK_SIZE) {
    List<...> chunk = list.subList(i, Math.min(i + BATCH_CHUNK_SIZE, list.size()));
    dsl.batch(chunk.stream().map(vo ->
            (Query) dsl.insertInto(TABLE)
                    .set(TABLE.COL, vo.field())
                    ...
    ).toArray(Query[]::new)).execute();
}
```

핵심:
- `subList` 로 청크 자름
- `dsl.batch(...)` 로 묶어서 실행
- `(Query)` cast 필요 (jOOQ generic 처리)
- `DateUtils.nowKst()` 같은 유틸로 timestamp

### 3. 페이징 조회 패턴 (`selectBy`)
```java
public GitVo.SearchVo selectBy(GitVo.SearchVo paging) {
    Condition where = buildCondition(paging);

    int count = dsl.fetchCount(dsl.selectFrom(TABLE).where(where));

    if (count > 0) {
        paging.calcPaging(count);
        List<...> list = dsl.selectFrom(TABLE)
                .where(where)
                .orderBy(TABLE.COL.desc())
                .offset(paging.offset())
                .limit(paging.limit())
                .fetchInto(...class);
        paging.setBody(list);
    }
    return paging;
}
```

핵심:
- 페이징 VO 자체를 입출력 (`SearchVo` 가 검색 조건 + 결과 다 가짐)
- `fetchCount` 먼저 → 0이면 쿼리 안 함 (성능)
- `calcPaging(count)` 으로 page/totalPage 계산
- `setBody(list)` 로 결과 채움

### 4. 동적 조건 빌더 (`buildCondition`)
```java
private Condition buildCondition(...paging) {
    List<Condition> conditions = new ArrayList<>();

    if (조건이 있으면) {
        conditions.add(조건);
    }

    Condition where = DSL.trueCondition();
    for (Condition c : conditions) {
        where = where.and(c);
    }
    return where;
}
```

핵심:
- private 메서드로 분리
- `DSL.trueCondition()` 으로 시작 → `.and()` 누적
- like 검색: `DSL.lower(컬럼).like("%" + value.toLowerCase() + "%")`
- OR 조건: `.or(다른 컬럼 검색)`

### 5. 명명 컨벤션
- 메서드: `insertBatch`, `selectBy` (jOOQ 스타일)
- private 헬퍼: `buildCondition` (동작 명사)
- 상수: `BATCH_CHUNK_SIZE` (UPPER_SNAKE_CASE)

## 새 DAO 작성 시 체크리스트

- [ ] `@Repository` + `@RequiredArgsConstructor`
- [ ] `DSLContext` 주입
- [ ] 배치 메서드 있으면 `BATCH_CHUNK_SIZE = 50` (또는 100)
- [ ] 동적 조건은 private `buildCondition` 분리
- [ ] like 검색 시 `DSL.lower()` + `%pattern%`
- [ ] 페이징 시 `fetchCount` 먼저
- [ ] 메서드명: `insertBatch`, `selectBy`, `updateBy`, `deleteBy`
- [ ] static import: `import static <패키지>.jooq.Tables.<TABLE>`
- [ ] timestamp는 `DateUtils.nowKst()` 같은 유틸 사용 (직접 `LocalDateTime.now()` 금지)

## 변형 예시

### 단건 조회 추가
```java
public PushLog selectById(Long id) {
    return dsl.selectFrom(PUSH_LOG)
            .where(PUSH_LOG.ID.eq(id))
            .fetchOneInto(PushLog.class);
}
```

### 카운트만
```java
public int countByCommitter(String committer) {
    return dsl.fetchCount(
            dsl.selectFrom(PUSH_LOG)
                    .where(PUSH_LOG.COMMITTER.eq(committer))
    );
}
```

### 존재 여부
```java
public boolean existsByEmail(String email) {
    return dsl.fetchExists(
            dsl.selectFrom(PUSH_LOG)
                    .where(PUSH_LOG.EMAIL.eq(email))
    );
}
```

### 수정
```java
public int updateById(Long id, String message) {
    return dsl.update(PUSH_LOG)
            .set(PUSH_LOG.MESSAGE, message)
            .where(PUSH_LOG.ID.eq(id))
            .execute();
}
```

### 삭제
```java
public int deleteById(Long id) {
    return dsl.deleteFrom(PUSH_LOG)
            .where(PUSH_LOG.ID.eq(id))
            .execute();
}
```
