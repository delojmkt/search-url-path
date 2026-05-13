"""
주어진 URL의 하위 페이지를 찾아주는 스크립트.

사용 예:
    python test.py https://example.com/docs
    python test.py https://example.com/docs --depth 3 --max-pages 200
"""

import argparse
import json
import sys
import time
from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def normalize(url: str) -> str:
    url, _ = urldefrag(url)
    return url.rstrip("/")


def is_subpage(candidate: str, base: str) -> bool:
    """candidate가 base의 하위 경로인지 판단 (같은 호스트 + 경로 prefix)."""
    c = urlparse(candidate)
    b = urlparse(base)
    if c.scheme not in ("http", "https"):
        return False
    if c.netloc != b.netloc:
        return False
    base_path = b.path if b.path.endswith("/") else b.path + "/"
    cand_path = c.path if c.path.endswith("/") else c.path + "/"
    return cand_path.startswith(base_path)


def extract_links(html: str, current_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        links.append(urljoin(current_url, href))
    return links


def crawl(start_url: str, max_depth: int, max_pages: int, delay: float) -> list[str]:
    base = normalize(start_url)
    visited: set[str] = set()
    found: list[str] = []
    queue: deque[tuple[str, int]] = deque([(base, 0)])

    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    while queue and len(found) < max_pages:
        url, depth = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = session.get(url, timeout=10, allow_redirects=True)
        except requests.RequestException as e:
            print(f"[skip] {url} ({e})", file=sys.stderr)
            continue

        if resp.status_code != 200:
            print(f"[skip] {url} (status {resp.status_code})", file=sys.stderr)
            continue

        content_type = resp.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            continue

        found.append(url)
        print(f"[{depth}] {url}")

        if depth >= max_depth:
            continue

        for link in extract_links(resp.text, url):
            link = normalize(link)
            if link in visited:
                continue
            if is_subpage(link, base):
                queue.append((link, depth + 1))

        if delay > 0:
            time.sleep(delay)

    return found


def main() -> None:
    parser = argparse.ArgumentParser(description="주어진 URL의 하위 페이지 탐색")
    parser.add_argument("url", help="시작 URL")
    parser.add_argument("--depth", type=int, default=2, help="최대 탐색 깊이 (기본 2)")
    parser.add_argument("--max-pages", type=int, default=100, help="최대 페이지 수 (기본 100)")
    parser.add_argument("--delay", type=float, default=0.3, help="요청 간 지연(초) (기본 0.3)")
    parser.add_argument("--output", default="result.json", help="결과 JSON 파일 경로 (기본 result.json)")
    args = parser.parse_args()

    pages = crawl(args.url, args.depth, args.max_pages, args.delay)

    payload = {"url": args.url, "results": pages}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n총 {len(pages)}개의 하위 페이지를 찾았습니다. → {args.output}")


if __name__ == "__main__":
    main()
