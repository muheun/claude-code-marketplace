# 타이포그래피 시스템 (Typography System)

## 핵심 원칙

1. **가독성 우선**: 최소 16px 본문 크기
2. **명확한 계층**: Heading, Subheading, Body, Caption 구분
3. **폰트 제한**: 최대 2개 폰트 패밀리

## 폰트 선택 (Font Selection)

### 시스템 폰트 스택 (권장)
빠르고 안전한 선택:

```css
font-family:
  -apple-system, BlinkMacSystemFont,
  "Segoe UI", Roboto,
  "Helvetica Neue", Arial,
  sans-serif;
```

### 커스텀 폰트 (선택적)
최대 2개 폰트:
- **Heading 폰트**: 개성있는 serif 또는 geometric sans-serif
- **Body 폰트**: 가독성 높은 sans-serif

**추천 조합**:
- Inter (body) + Inter (heading with different weight)
- Roboto (body) + Poppins (heading)
- System font (body) + Playfair Display (heading)

❌ **금지**: 3개 이상 폰트 사용, 과도하게 장식적인 폰트

## 타입 스케일 (Type Scale)

8px 그리드에 맞춘 타입 스케일:

| 레벨 | 크기 (px) | Line Height | 용도 |
|------|-----------|-------------|------|
| **Display** | 48px | 1.2 | 히어로 섹션, 랜딩 페이지 제목 |
| **H1** | 32px | 1.3 | 페이지 메인 제목 |
| **H2** | 24px | 1.4 | 섹션 제목 |
| **H3** | 20px | 1.4 | 서브섹션 제목 |
| **Body Large** | 18px | 1.6 | 강조 본문, 인트로 |
| **Body** | 16px | 1.6 | 일반 본문 (최소 크기) |
| **Body Small** | 14px | 1.5 | 보조 정보, 메타 데이터 |
| **Caption** | 12px | 1.4 | 작은 라벨, 각주 (최소화) |

## 폰트 두께 (Font Weight)

3-4단계로 제한:

| Weight | 값 | 용도 |
|--------|---|------|
| **Regular** | 400 | 본문 텍스트 |
| **Medium** | 500 | 강조, 버튼 텍스트 |
| **Semibold** | 600 | 서브헤딩 |
| **Bold** | 700 | 헤딩, 중요 강조 |

❌ **금지**: 너무 얇은 폰트 (100-200), 너무 많은 weight 변화

## 텍스트 색상 (Text Color)

계층에 따라 투명도 조절:

```
Primary text (heading): #1A1A1A (near-black)
Secondary text (body): #666666 (medium gray)
Tertiary text (caption): #999999 (light gray)
Disabled text: #CCCCCC (very light gray)
```

## 라인 길이 (Line Length)

가독성을 위한 최적 길이:

```
최적: 60-80 characters per line
최대: 90 characters
모바일: 45-60 characters
```

구현:
```css
max-width: 65ch; /* characters 기준 */
max-width: 800px; /* pixel 기준 */
```

## 텍스트 정렬 (Text Alignment)

- **Left-align**: 본문 텍스트 기본 (한글, 영어)
- **Center**: 제목, 히어로 섹션 (선택적)
- **Right-align**: 숫자, 날짜 (테이블)
- ❌ **Justify**: 사용 금지 (웹에서 가독성 저하)

## 컴포넌트별 타이포그래피

### 버튼 (Button)
```
폰트 크기: 14px (작은 버튼) ~ 16px (중간) ~ 18px (큰 버튼)
폰트 두께: 500 (Medium) ~ 600 (Semibold)
Letter spacing: 0.02em (선택적)
```

### 폼 입력 (Form Input)
```
Label: 14px, 500 weight
Input text: 16px, 400 weight (모바일 줌 방지)
Placeholder: 16px, 400 weight, #999999
Error message: 14px, 400 weight, red
```

### 카드 (Card)
```
제목: 18-20px, 600 weight
설명: 14-16px, 400 weight
메타데이터: 12-14px, 400 weight, #999999
```

## 접근성 (Accessibility)

- **최소 대비비**: WCAG AA 기준 4.5:1 (본문), 3:1 (헤딩)
- **최소 크기**: 16px 본문 (모바일 줌 방지, 가독성)
- **확대 가능**: `rem` 단위 사용으로 브라우저 설정 반영

## 금지 사항 (Avoid)

❌ 16px 미만 본문 텍스트 (가독성 저하)
❌ 3개 이상 폰트 패밀리
❌ 과도한 대문자 사용 (ALL CAPS)
❌ 얇은 폰트 (100-200 weight) 작은 크기에 사용
❌ 낮은 대비 (회색 배경에 밝은 회색 텍스트)

## 올바른 사용 예시

✅ **페이지 제목**:
```
H1: 32px, 700 weight, #1A1A1A
서브헤딩: 18px, 400 weight, #666666
```

✅ **본문**:
```
Body: 16px, 400 weight, #666666, line-height 1.6
Max-width: 65ch
```

✅ **버튼**:
```
Text: 16px, 500 weight, uppercase (선택적)
Letter-spacing: 0.02em
```
