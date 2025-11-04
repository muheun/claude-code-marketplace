# Android 디자인 핵심 원칙 (Android Design Principles)

## 철학 (Philosophy)

Material Design 3 (Material You)는 사용자 개인화와 표현을 중심으로 한 디자인 시스템입니다.

## Material Design 3 핵심 원칙

### 1. Expressive (표현력)
**정의**: 사용자 개성을 반영한 동적 색상 시스템

**적용 방법**:
- Dynamic Color: 배경화면에서 색상 추출
- 개인화된 테마
- 대담한 색상 사용

```kotlin
// Material Theme with Dynamic Color
MaterialTheme(
    colorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        dynamicColorScheme(LocalContext.current)
    } else {
        lightColorScheme()
    }
) { }
```

### 2. Adaptive (적응형)
**정의**: 다양한 디바이스와 화면 크기에 최적화

**적용 방법**:
- 반응형 레이아웃
- 다양한 폼 팩터 지원 (폰, 태블릿, 폴더블)
- Adaptive Navigation

### 3. Cohesive (일관성)
**정의**: 통합되고 일관된 사용자 경험

**적용 방법**:
- Material Components 사용
- 일관된 인터랙션 패턴
- 표준 애니메이션

## Flexible 확장 원칙

### 4. 간결함 (Simplicity)
- 불필요한 요소 제거
- 핵심 기능 집중

### 5. 접근성 (Accessibility)
- 터치 타겟 최소 48x48dp
- 대비 WCAG AA 준수
- TalkBack 지원

## Jetpack Compose 권장

- Declarative UI
- Material 3 Components
- State Hoisting
- Theming

## 참고 자료
- [Material Design 3](https://m3.material.io/)
- [Jetpack Compose](https://developer.android.com/jetpack/compose)
