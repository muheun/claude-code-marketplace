# 컴포넌트 디자인 패턴 (Component Design Patterns)

각 컴포넌트의 올바른 디자인 방법과 모범 사례.

## 버튼 (Button)

### 기본 스타일
```
Padding: 12px (상하) × 24px (좌우)
Border-radius: 6px ~ 8px
Font: 16px, 500-600 weight
Transition: all 150ms ease
```

### 변형 (Variants)

**Primary (주요 액션)**:
```
배경: 액센트 컬러
텍스트: White
그림자: subtle (0 1px 3px rgba(0,0,0,0.1))
Hover: 배경색 5-10% 어둡게
Active: 배경색 15% 어둡게
```

**Secondary (보조 액션)**:
```
배경: Transparent
보더: 1px solid 액센트 컬러
텍스트: 액센트 컬러
Hover: 배경 액센트 컬러 10% 투명도
Active: 배경 액센트 컬러 20% 투명도
```

**Ghost (약한 액션)**:
```
배경: Transparent
텍스트: #666666
Hover: 배경 #F5F5F5
Active: 배경 #E0E0E0
```

**Disabled (비활성)**:
```
배경: #E0E0E0
텍스트: #CCCCCC
Cursor: not-allowed
포인터 이벤트 없음
```

### 금지 사항
❌ 그라디언트 배경
❌ 과도한 그림자 (드롭 섀도우 5px 이상)
❌ 불명확한 hover 상태
❌ 너무 작은 클릭 영역 (최소 44x44px)

---

## 카드 (Card)

### 기본 스타일
```
배경: #FFFFFF
Padding: 24px
Border-radius: 8px ~ 12px
```

### 변형 (Variants)

**보더 카드**:
```
보더: 1px solid #E0E0E0
그림자: 없음
```

**그림자 카드**:
```
보더: 없음
그림자: 0 1px 3px rgba(0,0,0,0.08)
Hover: 0 4px 12px rgba(0,0,0,0.12)
```

### 금지 사항
❌ 보더와 그림자 동시 사용
❌ 과도한 그림자 (blur 20px 이상)
❌ 카드 내부 과도한 색상
❌ 너무 작은 padding (16px 미만)

---

## 폼 (Form)

### 입력 필드 (Input)
```
Padding: 12px (상하) × 16px (좌우)
Border: 1px solid #E0E0E0
Border-radius: 6px
Font: 16px, 400 weight

Focus:
  보더: 2px solid 액센트 컬러
  Outline: 없음 (outline: none)
  그림자: 0 0 0 3px 액센트 컬러 20% 투명도

Error:
  보더: 1px solid #EF4444 (red)

Disabled:
  배경: #F5F5F5
  텍스트: #CCCCCC
```

### 라벨 (Label)
```
Font: 14px, 500 weight
색상: #333333
Label-Input 간격: 8px
```

### 에러 메시지
```
Font: 14px, 400 weight
색상: #EF4444 (red)
위치: input 하단 4px 간격
```

### 금지 사항
❌ placeholder만으로 라벨 대체
❌ 16px 미만 입력 텍스트 (모바일 줌 발생)
❌ 불명확한 focus 상태
❌ 에러 상태 시각적 피드백 없음

---

## 내비게이션 (Navigation)

### 헤더 (Header)
```
높이: 64px
배경: #FFFFFF
보더-bottom: 1px solid #E0E0E0
Padding: 0 24px

로고: 왼쪽 정렬
메뉴: 오른쪽 정렬 (데스크톱)
```

### 링크 (Nav Link)
```
Font: 16px, 500 weight
색상: #666666
Padding: 8px 16px

Hover:
  색상: 액센트 컬러

Active:
  색상: 액센트 컬러
  보더-bottom: 2px solid 액센트 컬러
```

---

## 모달/대화상자 (Modal/Dialog)

### 기본 스타일
```
배경: #FFFFFF
Max-width: 500px (작은 모달) ~ 800px (큰 모달)
Border-radius: 12px
Padding: 32px
그림자: 0 20px 40px rgba(0,0,0,0.15)

오버레이:
  배경: rgba(0,0,0,0.5)
```

### 구조
```
제목: 24px, 700 weight, #1A1A1A
내용: 16px, 400 weight, #666666
버튼 영역: 상단 24px 간격, 오른쪽 정렬
```

### 금지 사항
❌ 너무 큰 모달 (화면의 90% 이상)
❌ 닫기 버튼 없음
❌ 오버레이 클릭으로 닫기 불가

---

## 테이블 (Table)

### 기본 스타일
```
헤더:
  배경: #F5F5F5
  Font: 14px, 600 weight, #333333
  Padding: 12px 16px

행:
  보더-bottom: 1px solid #E0E0E0
  Padding: 12px 16px
  Hover: 배경 #FAFAFA

셀:
  Font: 14px, 400 weight, #666666
```

### 금지 사항
❌ 세로 보더 (시각적 노이즈)
❌ 번갈아가는 행 색상 (zebra striping, 현대적이지 않음)
❌ 너무 작은 padding

---

## 배지/태그 (Badge/Tag)

### 기본 스타일
```
Padding: 4px 12px
Border-radius: 12px (pill shape)
Font: 12px, 500 weight

Success: 배경 #D1FAE5, 텍스트 #065F46
Warning: 배경 #FEF3C7, 텍스트 #92400E
Error: 배경 #FEE2E2, 텍스트 #991B1B
Info: 배경 #DBEAFE, 텍스트 #1E40AF
Neutral: 배경 #F3F4F6, 텍스트 #374151
```

---

## 드롭다운 (Dropdown)

### 기본 스타일
```
트리거:
  Input과 동일한 스타일
  아이콘: 오른쪽 chevron-down

메뉴:
  배경: #FFFFFF
  보더: 1px solid #E0E0E0
  Border-radius: 6px
  그림자: 0 4px 12px rgba(0,0,0,0.1)
  Max-height: 300px (스크롤)

항목:
  Padding: 12px 16px
  Hover: 배경 #F5F5F5
  Active: 배경 액센트 컬러 10% 투명도
```

---

## 일반 원칙

1. **상호작용 상태 명확화**: hover, active, focus, disabled 모두 시각적으로 구분
2. **일관성 유지**: 같은 컴포넌트는 어디서나 동일한 스타일
3. **접근성**: 키보드 네비게이션, 스크린 리더 지원
4. **반응형**: 모바일에서도 터치하기 쉬운 크기 (최소 44x44px)
