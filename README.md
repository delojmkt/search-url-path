# search-url-path

주어진 URL의 하위 페이지를 BFS로 탐색해 JSON으로 저장하는 스크립트.

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

```bash
python test.py <URL> [옵션]
```

### 예시

```bash
# 기본 (depth=2, max-pages=100)
python test.py https://example.com/docs

# 깊이/개수 조정
python test.py https://example.com/docs --depth 3 --max-pages 200

# 출력 파일 변경
python test.py https://example.com/docs --output pages.json
```

### 옵션

| 옵션 | 기본값 | 설명 |
| --- | --- | --- |
| `--depth` | `2` | 최대 탐색 깊이 |
| `--max-pages` | `100` | 수집할 최대 페이지 수 |
| `--delay` | `0.3` | 요청 간 지연(초) |
| `--output` | `result.json` | 결과 JSON 파일 경로 |

## 동작 방식

- 시작 URL과 **같은 호스트**이면서, 시작 URL의 **경로를 prefix로 갖는** 링크만 하위 페이지로 인정합니다.
  예: `https://example.com/docs`로 시작하면 `https://example.com/docs/intro`는 포함, `https://example.com/blog`는 제외.
- `#fragment`는 정규화 단계에서 제거되어 같은 페이지로 취급됩니다.
- HTML이 아닌 응답(이미지·PDF 등)은 결과에서 제외됩니다.
- JavaScript로 렌더되는 SPA는 `requests` 기반이라 링크를 추출하지 못할 수 있습니다. 이 경우 헤드리스 브라우저(Playwright 등)가 필요합니다.

## 출력 형식

`result.json`:

```json
{
  "url": "https://example.com/docs",
  "results": [
    "https://example.com/docs",
    "https://example.com/docs/intro",
    "https://example.com/docs/guide"
  ]
}
```
