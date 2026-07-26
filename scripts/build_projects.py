from __future__ import annotations

import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "gallery_config.json"
OUTPUT_PATH = ROOT / "data" / "projects.json"
API_ROOT = "https://api.github.com"

FIELD_HEADINGS = {
    "산출물 구분": "category_label",
    "닉네임": "nickname",
    "앱 URL": "app_url",
    "한 줄 소개": "tagline",
    "프로젝트 주제": "topic",
    "사용한 데이터": "data_used",
    "데이터 출처 링크": "data_source_url",
    "프로젝트 소개": "description",
    "대표 이미지 URL": "thumbnail_url",
}


def request_json(url: str, token: str, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "student-streamlit-gallery-sync",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API error {exc.code}: {details}") from exc


def ensure_label(repository: str, token: str, name: str, color: str, description: str) -> None:
    encoded = urllib.parse.quote(name, safe="")
    url = f"{API_ROOT}/repos/{repository}/labels/{encoded}"
    try:
        request_json(url, token)
    except RuntimeError as exc:
        if "404" not in str(exc):
            raise
        request_json(
            f"{API_ROOT}/repos/{repository}/labels",
            token,
            method="POST",
            payload={"name": name, "color": color, "description": description},
        )


def parse_issue_form(body: str) -> dict[str, str]:
    values: dict[str, str] = {}
    pattern = re.compile(r"^###\s+(.+?)\s*$\n(.*?)(?=^###\s+|\Z)", re.MULTILINE | re.DOTALL)
    for heading, answer in pattern.findall(body or ""):
        key = FIELD_HEADINGS.get(heading.strip())
        if not key:
            continue
        cleaned = answer.strip()
        if cleaned in {"_No response_", "No response"}:
            cleaned = ""
        values[key] = cleaned
    return values


def valid_https(url: str) -> bool:
    return url.startswith("https://") and len(url) > 10


def fetch_comments(repository: str, issue_number: int, count: int, token: str) -> list[dict[str, Any]]:
    if count <= 0:
        return []
    page = max(1, math.ceil(count / 5))
    url = f"{API_ROOT}/repos/{repository}/issues/{issue_number}/comments?per_page=5&page={page}"
    rows = request_json(url, token) or []
    return [
        {
            "nickname": row.get("user", {}).get("login", "익명"),
            "content": row.get("body", ""),
            "created_at": row.get("created_at", ""),
            "url": row.get("html_url", ""),
        }
        for row in rows[-5:]
    ]


def fetch_published_issues(repository: str, token: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    page = 1
    while True:
        label = urllib.parse.quote("published")
        url = f"{API_ROOT}/repos/{repository}/issues?state=all&labels={label}&per_page=100&page={page}"
        rows = request_json(url, token) or []
        issues.extend(row for row in rows if "pull_request" not in row)
        if len(rows) < 100:
            break
        page += 1
    return issues


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not repository:
        print("GITHUB_REPOSITORY is required", file=sys.stderr)
        return 2

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    category_map = {item["label"]: item["key"] for item in config["categories"]}

    ensure_label(repository, token, "submission", "1D76DB", "학생 앱 제출")
    ensure_label(repository, token, "published", "0E8A16", "갤러리에 공개")

    projects: list[dict[str, Any]] = []
    for issue in fetch_published_issues(repository, token):
        values = parse_issue_form(issue.get("body", ""))
        app_url = values.get("app_url", "").strip()
        if not valid_https(app_url):
            print(f"Skip issue #{issue['number']}: invalid app URL")
            continue

        category_label = values.get("category_label", "")
        reactions = issue.get("reactions") or {}
        comment_count = int(issue.get("comments", 0))
        projects.append(
            {
                "id": str(issue["number"]),
                "issue_number": issue["number"],
                "issue_url": issue.get("html_url", ""),
                "category": category_map.get(category_label, category_label),
                "nickname": values.get("nickname", "익명")[:40],
                "app_url": app_url,
                "tagline": values.get("tagline", "")[:120],
                "topic": values.get("topic", issue.get("title", "제목 없는 프로젝트"))[:120],
                "data_used": values.get("data_used", "")[:1000],
                "data_source_url": values.get("data_source_url", "") if valid_https(values.get("data_source_url", "")) else "",
                "description": values.get("description", "")[:3000],
                "thumbnail_url": values.get("thumbnail_url", "") if valid_https(values.get("thumbnail_url", "")) else "",
                "created_at": issue.get("created_at", ""),
                "updated_at": issue.get("updated_at", ""),
                "like_count": int(reactions.get("+1", 0)) + int(reactions.get("heart", 0)),
                "feedback_count": comment_count,
                "feedback": fetch_comments(repository, int(issue["number"]), comment_count, token),
            }
        )

    projects.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(projects, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(projects)} projects to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
