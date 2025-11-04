# Android 타이포그래피 (Android Typography)

## Material Type Scale

Material Design 3는 체계적인 **Type Scale** 시스템을 제공합니다.

## 시스템 폰트: Roboto

- 기본 폰트: **Roboto**
- Sans-serif 계열
- 다양한 Weight 지원

## Material 3 Type Scale

| 역할 | Compose | 기본 크기 | Weight | 용도 |
|------|---------|-----------|--------|------|
| **Display Large** | `displayLarge` | 57sp | Regular | 히어로 텍스트 |
| **Display Medium** | `displayMedium` | 45sp | Regular | 큰 제목 |
| **Display Small** | `displaySmall` | 36sp | Regular | 섹션 제목 |
| **Headline Large** | `headlineLarge` | 32sp | Regular | 페이지 제목 |
| **Headline Medium** | `headlineMedium` | 28sp | Regular | 서브 제목 |
| **Headline Small** | `headlineSmall` | 24sp | Regular | 작은 제목 |
| **Title Large** | `titleLarge` | 22sp | Regular | 리스트 제목 |
| **Title Medium** | `titleMedium` | 16sp | Medium | 카드 제목 |
| **Title Small** | `titleSmall` | 14sp | Medium | 작은 제목 |
| **Body Large** | `bodyLarge` | 16sp | Regular | 강조 본문 |
| **Body Medium** | `bodyMedium` | 14sp | Regular | **본문 기본** |
| **Body Small** | `bodySmall` | 12sp | Regular | 캡션 |
| **Label Large** | `labelLarge` | 14sp | Medium | 버튼, 탭 |
| **Label Medium** | `labelMedium` | 12sp | Medium | 칩, 배지 |
| **Label Small** | `labelSmall` | 11sp | Medium | 작은 라벨 |

## Compose 사용

```kotlin
Text(
    text = "제목",
    style = MaterialTheme.typography.headlineMedium
)

Text(
    text = "본문",
    style = MaterialTheme.typography.bodyMedium
)

Text(
    text = "라벨",
    style = MaterialTheme.typography.labelLarge
)
```

## 커스텀 타이포그래피

```kotlin
val Typography = Typography(
    displayLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 57.sp,
        lineHeight = 64.sp,
        letterSpacing = 0.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.25.sp
    ),
    // ...
)

MaterialTheme(typography = Typography) {
    // App content
}
```

## Font Weight

| Weight | 값 | Compose |
|--------|---|---------|
| Light | 300 | `FontWeight.Light` |
| Regular | 400 | `FontWeight.Normal` |
| Medium | 500 | `FontWeight.Medium` |
| Bold | 700 | `FontWeight.Bold` |

## 텍스트 색상

```kotlin
Text(
    text = "제목",
    color = MaterialTheme.colorScheme.onSurface
)

Text(
    text = "보조",
    color = MaterialTheme.colorScheme.onSurfaceVariant
)
```

## 금지 사항

❌ 고정 크기: `fontSize = 24.sp` 직접 사용
❌ Hardcoded 색상
❌ 11sp 미만 텍스트

## 참고 자료
- [Material Typography](https://m3.material.io/styles/typography)
