# 분석(Analytics) 가이드

FLY Worship Camp 랜딩 페이지의 사용자 행동 추적 설정 정리.

- **GA4 측정 ID**: `G-17Z0NDZ34E`
- **Vercel Web Analytics**: `index.html` `<head>`에 `/_vercel/insights/script.js` 삽입됨 (정적 사이트라 수동 삽입 필요)
- 추적 코드 위치: `index.html` — `<head>`의 GA4 스니펫 + 하단 `<script>`의 `trackEvent()` 헬퍼 및 이벤트 호출

---

## 1. 직접 심은 커스텀 이벤트 (4종)

| 이벤트 이름 | 발생 시점 | 파라미터 | 볼 수 있는 것 |
|---|---|---|---|
| `cta_click` | CTA 버튼 클릭 | `cta_label` (버튼 글자)<br>`cta_location` (`nav` / `mobile_menu` / `announcements`) | 신청 유도 버튼 클릭 수, 어느 위치(데스크탑 nav / 모바일 메뉴 / 공지 영역)에서 더 많이 눌리나 |
| `faq_open` | FAQ 항목 펼침 | `faq_question` (질문 제목) | 어떤 질문을 가장 많이 궁금해하나 (질문별 순위) |
| `announcement_open` | 공지 항목 펼침 | `announcement_title` (공지 제목) | 어떤 공지를 가장 많이 열어보나 |
| `schedule_day_view` | Day 탭 전환 | `day` (1 / 2 / 3) | Day 01/02/03 중 어떤 일정에 관심이 많나 |

> **중요:** 위 파라미터(`cta_label`, `cta_location`, `faq_question`, `announcement_title`, `day`)는 GA4에 **맞춤 측정기준으로 등록해야** 보고서에서 표로 쪼개 볼 수 있다. 등록 전에는 이벤트 *횟수*만 보이고 "어떤 버튼/질문인지"는 안 보인다.
>
> 등록 위치: **관리 → 데이터 표시 → 맞춤 정의 → 맞춤 측정기준 만들기** → 범위 `이벤트`, 이벤트 매개변수에 위 이름 그대로 입력.

---

## 2. GA4 자동 수집 (코드 불필요)

| 이벤트 / 항목 | 지표 |
|---|---|
| `page_view` | 방문 수, 페이지뷰, 시간대별 추이 |
| `scroll` | 페이지 90%까지 스크롤한 비율 (콘텐츠를 끝까지 보나) |
| `session_start` / `first_visit` | 세션 수, 신규 vs 재방문 |
| `user_engagement` | 평균 참여 시간(체류시간) |
| 트래픽 소스(자동) | 유입 경로 — 카톡/인스타/직접입력 등 |
| 기기·지역(자동) | 모바일 vs PC 비율, 접속 지역 |

---

## 3. 권장 활용 순서

1. **실시간 보고서** — 이벤트가 잘 들어오는지 즉시 확인 (반영까지 수십 초~1분)
2. **참여도 → 이벤트** — `cta_click` 등 4종이 쌓이는지 확인
3. 위 **파라미터를 맞춤 측정기준으로 등록**
4. 며칠 데이터가 쌓인 뒤 **탐색(Explore)** 에서 분석:
   - FAQ 질문별 펼침 순위 (`faq_open` × `faq_question`)
   - CTA 위치별 클릭 (`cta_click` × `cta_location`)
   - Day별 관심도 (`schedule_day_view` × `day`)
5. (권장) **관리 → 이벤트**에서 `cta_click`을 **'주요 이벤트'로 표시** → 신청 전환 지표로 추적

### 만들 수 있는 파생 지표 예시
- **CTA 클릭률** = `cta_click` ÷ `page_view`
- **콘텐츠 완독률** = `scroll`(90%) ÷ `session_start`

---

## 4. 알려진 한계 / TODO

- 현재 CTA·메뉴 링크는 모두 페이지 내 앵커(`#cta`, `#announcements`) 스크롤이라, **"신청 완료"라는 최종 전환은 측정 불가**.
- 추후 구글폼/신청 페이지 같은 **외부 신청 링크**가 생기면 그 클릭에 별도 이벤트(예: `apply_click`)를 추가해야 전환 퍼널이 완성된다.

---

## 5. 새 이벤트 추가 방법 (개발 메모)

`index.html` 하단 `<script>`에 `trackEvent(name, params)` 헬퍼가 있다. 새 동작을 추적하려면 해당 요소의 클릭/이벤트 핸들러 안에서 호출:

```js
trackEvent('이벤트이름', { 파라미터키: '값' });
```

- 이벤트 이름·파라미터 키는 **영문 snake_case 권장** (GA4 호환성).
- 새 파라미터는 GA4에서 맞춤 측정기준으로 등록해야 보고서에 노출됨.
