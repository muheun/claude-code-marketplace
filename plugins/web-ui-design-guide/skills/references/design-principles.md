# 디자인 핵심 원칙 (Core Design Principles)

## 철학 (Philosophy)
모던하고 전문적인 UI는 **간결함(minimalism)**과 **일관성(consistency)**에서 나온다.

## 5가지 핵심 원칙

### 1. 깔끔하고 미니멀 (Clean and Minimal)
- **여백 우선**: 충분한 화이트 스페이스로 시각적 숨통 확보
- **정보 밀도 절제**: 한 화면에 너무 많은 요소 배치 금지
- **시각적 노이즈 제거**: 불필요한 선, 그림자, 장식 요소 최소화

### 2. 중립적 색상 팔레트 (Neutral Color Palette)
- **기본 색상**: 회색(gray) 및 오프화이트(off-white) 계열
- **액센트 컬러**: **단 하나의 액센트 컬러**를 선택하여 절제되게 사용
- **금지**: 일반적인 보라/파란 그라디언트 (cliché gradients)

### 3. 일관된 간격 시스템 (Consistent Spacing)
- **8px 그리드 시스템** 준수: 8, 16, 24, 32, 48, 64px
- 모든 요소의 margin, padding, gap은 8의 배수 사용

### 4. 명확한 타이포그래피 계층 (Typography Hierarchy)
- **최소 본문 크기**: 16px (가독성 보장)
- **폰트 제한**: 최대 2개 폰트 패밀리
- **계층 구조 명확화**: Heading, Subheading, Body, Caption 구분

### 5. 절제된 시각 효과 (Subtle Visual Effects)
- **그림자**: 미묘하게(subtle), 과하지 않게
- **둥근 모서리**: 모든 요소를 둥글게 할 필요 없음, 선택적으로
- **상호작용 상태**: hover, active, disabled 상태를 명확히 표현

## 모바일 우선 사고 (Mobile-First Thinking)
- 작은 화면에서 먼저 디자인 → 큰 화면으로 확장
- 터치 타겟 크기 최소 44x44px
- 반응형 레이아웃 기본 전제
