# Android 디자인 안티패턴

## 색상 관련

### ❌ 다크 모드 미지원
```kotlin
// 나쁜 예
Text("제목", color = Color.Black)

// 좋은 예
Text("제목", color = MaterialTheme.colorScheme.onSurface)
```

### ❌ Material Theme 무시
```kotlin
// 나쁜 예
Button(
    colors = ButtonDefaults.buttonColors(
        containerColor = Color(0xFF6200EE)  // 하드코딩
    )
) { }

// 좋은 예
Button(onClick = { }) {  // Material Theme 자동 적용
    Text("확인")
}
```

## 간격 관련

### ❌ 임의의 dp 값
```kotlin
// 나쁜 예
Spacer(modifier = Modifier.height(13.dp))

// 좋은 예
Spacer(modifier = Modifier.height(16.dp))  // 4의 배수
```

### ❌ 48dp 미만 터치 타겟
```kotlin
// 나쁜 예
IconButton(
    onClick = { },
    modifier = Modifier.size(32.dp)  // 너무 작음
) { }

// 좋은 예
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp)
) { }
```

## 타이포그래피 관련

### ❌ 고정된 텍스트 크기
```kotlin
// 나쁜 예
Text(
    text = "제목",
    fontSize = 24.sp  // Material Type Scale 무시
)

// 좋은 예
Text(
    text = "제목",
    style = MaterialTheme.typography.headlineSmall
)
```

## 컴포넌트 관련

### ❌ 커스텀 컴포넌트 남용
```kotlin
// 나쁜 예
Box(
    modifier = Modifier
        .clickable { }
        .background(Color.Blue)
        .padding(16.dp)
) {
    Text("버튼", color = Color.White)
}

// 좋은 예
Button(onClick = { }) {
    Text("버튼")
}
```

### ❌ State Hoisting 무시
```kotlin
// 나쁜 예
@Composable
fun MyTextField() {
    var text by remember { mutableStateOf("") }  // 내부 상태
    TextField(value = text, onValueChange = { text = it })
}

// 좋은 예
@Composable
fun MyTextField(
    value: String,
    onValueChange: (String) -> Unit
) {
    TextField(value = value, onValueChange = onValueChange)
}
```

## 레이아웃 관련

### ❌ 중첩된 스크롤
```kotlin
// 나쁜 예
ScrollableColumn {
    LazyColumn { }  // 중첩 스크롤 금지
}

// 좋은 예
LazyColumn {
    // All items
}
```

## 참고 자료
- [Material Best Practices](https://m3.material.io/develop/android/jetpack-compose)
