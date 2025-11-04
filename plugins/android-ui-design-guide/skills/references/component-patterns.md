# Android 컴포넌트 패턴 (Jetpack Compose)

## 버튼 (Button)

### Filled Button (Primary)
```kotlin
Button(onClick = { }) {
    Text("확인")
}
```

### Outlined Button (Secondary)
```kotlin
OutlinedButton(onClick = { }) {
    Text("취소")
}
```

### Text Button (Tertiary)
```kotlin
TextButton(onClick = { }) {
    Text("건너뛰기")
}
```

### Filled Tonal Button
```kotlin
FilledTonalButton(onClick = { }) {
    Text("적용")
}
```

## 카드 (Card)

```kotlin
Card(
    modifier = Modifier
        .fillMaxWidth()
        .padding(16.dp)
) {
    Column(
        modifier = Modifier.padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(
            text = "제목",
            style = MaterialTheme.typography.titleLarge
        )
        Text(
            text = "내용",
            style = MaterialTheme.typography.bodyMedium
        )
    }
}
```

## 리스트 (LazyColumn)

```kotlin
LazyColumn(
    verticalArrangement = Arrangement.spacedBy(8.dp),
    contentPadding = PaddingValues(16.dp)
) {
    items(items) { item ->
        ListItem(
            headlineContent = { Text(item.title) },
            supportingContent = { Text(item.subtitle) },
            leadingContent = {
                Icon(Icons.Default.Star, contentDescription = null)
            }
        )
    }
}
```

## 입력 필드 (TextField)

### Filled TextField
```kotlin
var text by remember { mutableStateOf("") }

TextField(
    value = text,
    onValueChange = { text = it },
    label = { Text("이메일") },
    modifier = Modifier.fillMaxWidth()
)
```

### Outlined TextField
```kotlin
OutlinedTextField(
    value = text,
    onValueChange = { text = it },
    label = { Text("이름") },
    modifier = Modifier.fillMaxWidth()
)
```

## Navigation

### Top App Bar
```kotlin
Scaffold(
    topBar = {
        TopAppBar(
            title = { Text("제목") },
            navigationIcon = {
                IconButton(onClick = { }) {
                    Icon(Icons.Default.ArrowBack, null)
                }
            }
        )
    }
) { padding ->
    // Content
}
```

### Bottom Navigation Bar
```kotlin
NavigationBar {
    NavigationBarItem(
        selected = selectedItem == 0,
        onClick = { selectedItem = 0 },
        icon = { Icon(Icons.Default.Home, null) },
        label = { Text("홈") }
    )
    NavigationBarItem(
        selected = selectedItem == 1,
        onClick = { selectedItem = 1 },
        icon = { Icon(Icons.Default.Search, null) },
        label = { Text("검색") }
    )
}
```

## 다이얼로그 (AlertDialog)

```kotlin
AlertDialog(
    onDismissRequest = { showDialog = false },
    title = { Text("제목") },
    text = { Text("내용") },
    confirmButton = {
        TextButton(onClick = { showDialog = false }) {
            Text("확인")
        }
    },
    dismissButton = {
        TextButton(onClick = { showDialog = false }) {
            Text("취소")
        }
    }
)
```

## 참고 자료
- [Material Components](https://m3.material.io/components)
- [Compose Layouts](https://developer.android.com/jetpack/compose/layouts)
