# 색상 시스템 (Color System)

## 기본 색상 (Base Colors)

### 중립 팔레트 (Neutral Palette)
UI의 **80-90%**는 중립 색상으로 구성:

- **White/Off-White**: 배경, 카드, 입력 필드
  - `#FFFFFF` (pure white)
  - `#FAFAFA` (off-white, 눈의 피로 감소)
  - `#F5F5F5` (light gray background)

- **Grays**: 텍스트, 보더, 비활성 상태
  - `#F0F0F0` (light border)
  - `#E0E0E0` (divider)
  - `#CCCCCC` (disabled state)
  - `#999999` (secondary text)
  - `#666666` (body text)
  - `#333333` (heading text)

- **Black**: 강조 텍스트, 아이콘
  - `#1A1A1A` (near-black, pure black보다 부드러움)

## 액센트 컬러 (Accent Color)

**단 하나의 액센트 컬러** 선택:
- Primary actions (버튼, 링크)
- 중요한 정보 강조
- 활성 상태 표시

### 선택 가이드라인
- 브랜드 아이덴티티 반영
- 충분한 대비 (WCAG AA 이상)
- 과도한 사용 금지 (UI의 5-10%만)

### 예시 액센트 컬러
- **Green**: `#10B981` (성공, 성장, 신뢰)
- **Blue**: `#3B82F6` (신뢰, 전문성) - 단, 일반적이므로 차별화 고려
- **Orange**: `#F97316` (활력, 행동 유도)
- **Indigo**: `#6366F1` (혁신, 기술)

## 의미론적 색상 (Semantic Colors)

기능적 목적으로만 사용:
- **Success**: `#10B981` (green)
- **Warning**: `#F59E0B` (amber)
- **Error**: `#EF4444` (red)
- **Info**: `#3B82F6` (blue)

## 금지 사항 (Avoid)

❌ **무지개 그라디언트**: 여러 색상을 섞은 화려한 배경
❌ **일반적인 보라/파란 그라디언트**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
❌ **과도한 색상 사용**: 모든 요소가 다른 색상
❌ **낮은 대비**: 회색 배경에 밝은 회색 텍스트

## 올바른 사용 예시

✅ **버튼**:
```
Primary: 액센트 컬러 배경 + 화이트 텍스트
Secondary: 투명 배경 + 액센트 컬러 보더 + 액센트 컬러 텍스트
Ghost: 투명 배경 + 그레이 텍스트
```

✅ **카드**:
```
배경: #FFFFFF
보더: #E0E0E0 (1px solid)
그림자: 미묘한 회색 그림자
```

✅ **텍스트**:
```
Heading: #1A1A1A
Body: #666666
Secondary: #999999
Disabled: #CCCCCC
```
