# Android 색상 시스템 (Android Color System)

## Material Theme 색상

Material Design 3는 **Dynamic Color**와 **Material Theme**를 사용합니다.

## 기본 원칙

1. **Dynamic Color**: Android 12+ 배경화면에서 색상 자동 추출
2. **Material Theme**: 체계적인 색상 역할 시스템
3. **다크 모드**: 모든 앱은 라이트/다크 모드 지원 필수

## Material Theme 색상 역할

### Primary Colors
```kotlin
// Primary - 주요 액션 및 강조
colorScheme.primary          // 주요 색상
colorScheme.onPrimary        // Primary 위의 텍스트/아이콘
colorScheme.primaryContainer // Primary 컨테이너
colorScheme.onPrimaryContainer
```

### Secondary Colors
```kotlin
// Secondary - 보조 액션
colorScheme.secondary
colorScheme.onSecondary
colorScheme.secondaryContainer
colorScheme.onSecondaryContainer
```

### Tertiary Colors
```kotlin
// Tertiary - 3차 강조색
colorScheme.tertiary
colorScheme.onTertiary
colorScheme.tertiaryContainer
colorScheme.onTertiaryContainer
```

### Surface Colors
```kotlin
// Surface - 배경 및 표면
colorScheme.surface          // 기본 배경
colorScheme.onSurface        // Surface 위의 텍스트
colorScheme.surfaceVariant   // 변형 표면 (카드 등)
colorScheme.onSurfaceVariant
```

### Error Colors
```kotlin
// Error - 에러 상태
colorScheme.error
colorScheme.onError
colorScheme.errorContainer
colorScheme.onErrorContainer
```

## Dynamic Color 사용

```kotlin
@Composable
fun MyApp() {
    val dynamicColor = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S
    val colorScheme = when {
        dynamicColor && isSystemInDarkTheme() ->
            dynamicDarkColorScheme(LocalContext.current)
        dynamicColor ->
            dynamicLightColorScheme(LocalContext.current)
        isSystemInDarkTheme() -> darkColorScheme()
        else -> lightColorScheme()
    }

    MaterialTheme(colorScheme = colorScheme) {
        // App content
    }
}
```

## 커스텀 색상 정의

```kotlin
private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF6750A4),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFEADDFF),
    onPrimaryContainer = Color(0xFF21005E),
    secondary = Color(0xFF625B71),
    // ...
)

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFD0BCFF),
    onPrimary = Color(0xFF381E72),
    primaryContainer = Color(0xFF4F378B),
    onPrimaryContainer = Color(0xFFEADDFF),
    // ...
)
```

## 색상 사용 가이드

### 텍스트
```kotlin
Text(
    text = "제목",
    color = MaterialTheme.colorScheme.onSurface  // 자동 다크 모드
)
```

### 배경
```kotlin
Surface(
    color = MaterialTheme.colorScheme.surface
) {
    // Content
}
```

### 버튼
```kotlin
Button(
    onClick = { },
    colors = ButtonDefaults.buttonColors(
        containerColor = MaterialTheme.colorScheme.primary,
        contentColor = MaterialTheme.colorScheme.onPrimary
    )
) {
    Text("확인")
}
```

## 금지 사항

❌ 고정된 색상: `Color.Black`, `Color.White` 직접 사용
❌ Hex 하드코딩: 다크 모드 미대응
❌ Material Theme 무시

## 참고 자료
- [Material Theme Builder](https://m3.material.io/theme-builder)
- [Dynamic Color](https://m3.material.io/styles/color/dynamic-color)
