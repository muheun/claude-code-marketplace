# Android 간격 시스템 (Android Spacing System)

## 4dp 그리드 시스템

Android는 **4밀도 독립 픽셀(dp) 그리드**를 사용합니다.

## dp vs px

- **dp**: 밀도 독립 픽셀 (Density-independent Pixels)
- **1dp** = 160dpi 화면에서 1물리 픽셀
- 다양한 화면 밀도에서 일관된 크기

## 간격 스케일

| 값 (dp) | Compose | 사용 용도 |
|---------|---------|-----------|
| `4`     | `4.dp` | 최소 간격 |
| `8`     | `8.dp` | 작은 간격 |
| `12`    | `12.dp` | 컴팩트 padding |
| `16`    | `16.dp` | **기본 간격** (표준) |
| `24`    | `24.dp` | 중간 간격 |
| `32`    | `32.dp` | 큰 간격 |
| `48`    | `48.dp` | 터치 타겟 최소 크기 |
| `64`    | `64.dp` | 매우 큰 여백 |

## Compose Modifiers

### Padding
```kotlin
Box(
    modifier = Modifier
        .padding(16.dp)  // 모든 방향
        .padding(horizontal = 16.dp, vertical = 8.dp)
        .padding(start = 16.dp, end = 16.dp, top = 8.dp, bottom = 8.dp)
)
```

### Spacer
```kotlin
Column {
    Text("A")
    Spacer(modifier = Modifier.height(16.dp))
    Text("B")
}

Row {
    Text("A")
    Spacer(modifier = Modifier.width(16.dp))
    Text("B")
}
```

### Arrangement
```kotlin
Column(
    verticalArrangement = Arrangement.spacedBy(16.dp)
) {
    Text("A")
    Text("B")
    Text("C")
}
```

## 컴포넌트별 간격

### 버튼
```kotlin
Button(
    onClick = { },
    contentPadding = PaddingValues(horizontal = 24.dp, vertical = 12.dp)
) {
    Text("확인")
}
```

### 카드
```kotlin
Card(
    modifier = Modifier.padding(16.dp)  // 외부 간격
) {
    Column(
        modifier = Modifier.padding(16.dp)  // 내부 padding
    ) {
        Text("제목")
        Spacer(modifier = Modifier.height(8.dp))
        Text("내용")
    }
}
```

### 리스트
```kotlin
LazyColumn(
    verticalArrangement = Arrangement.spacedBy(8.dp),
    contentPadding = PaddingValues(16.dp)
) {
    items(items) { item ->
        Text(item.name)
    }
}
```

## 터치 타겟

최소 **48x48dp** 필수:

```kotlin
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp)  // 최소 터치 영역
) {
    Icon(Icons.Default.Add, contentDescription = null)
}
```

## 금지 사항

❌ 임의의 값: 13dp, 27dp (4의 배수 아님)
❌ px 단위 사용
❌ 48dp 미만 터치 타겟

## 참고 자료
- [Material Spacing](https://m3.material.io/foundations/layout/understanding-layout/spacing)
