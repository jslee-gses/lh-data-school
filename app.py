from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import streamlit as st

from storage import GalleryStorage, StorageError

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "gallery_config.json"


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def is_valid_https_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
        return parsed.scheme == "https" and bool(parsed.netloc)
    except ValueError:
        return False


def safe_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except ValueError:
        return ""


def relative_date(iso_text: str | None) -> str:
    if not iso_text:
        return ""
    try:
        created = datetime.fromisoformat(iso_text.replace("Z", "+00:00"))
        return created.astimezone().strftime("%Y.%m.%d")
    except (ValueError, TypeError):
        return str(iso_text)[:10]


def category_label(categories: list[dict[str, str]], key: str) -> str:
    return next((item["label"] for item in categories if item["key"] == key), key)


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def repository_urls(config: dict[str, Any]) -> dict[str, str]:
    repository = str(config.get("github_repository", "YOUR-ID/YOUR-REPOSITORY")).strip("/")
    root = f"https://github.com/{repository}"
    return {
        "root": root,
        "submit": f"{root}/issues/new?template=app-submission.yml",
        "pending": f"{root}/issues?q=is%3Aissue+label%3Asubmission+-label%3Apublished",
        "published": f"{root}/issues?q=is%3Aissue+label%3Apublished",
        "actions": f"{root}/actions/workflows/sync-gallery.yml",
    }


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 4rem;}
        [data-testid="stHeader"] {background: rgba(255,255,255,0.75); backdrop-filter: blur(10px);}
        .gallery-hero {padding: 2.4rem 2.5rem; border-radius: 24px; background: linear-gradient(135deg,#eef2ff 0%,#f8fafc 48%,#ecfeff 100%); border:1px solid rgba(99,102,241,.13); margin-bottom:1.25rem;}
        .gallery-eyebrow {font-size:.78rem; font-weight:800; letter-spacing:.12em; color:#4f46e5;}
        .gallery-title {font-size:clamp(2rem,5vw,3.45rem); line-height:1.08; font-weight:900; color:#111827; margin:.35rem 0 .7rem;}
        .gallery-subtitle {font-size:1.05rem; color:#4b5563; max-width:760px; margin:0;}
        .project-meta {font-size:.78rem; color:#6b7280; margin-bottom:.2rem;}
        .project-title {font-size:1.15rem; font-weight:800; color:#111827; line-height:1.35; margin-bottom:.35rem;}
        .project-tagline {font-size:.94rem; color:#4b5563; line-height:1.55; min-height:3rem;}
        .pill {display:inline-block; padding:.25rem .62rem; border-radius:999px; background:#eef2ff; color:#4338ca; font-size:.72rem; font-weight:700; margin-right:.35rem;}
        .thumbnail-placeholder {height:138px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:3rem; background:linear-gradient(135deg,#f3f4f6,#eef2ff); margin-bottom:.85rem;}
        .empty-state {text-align:center; padding:4rem 1rem; border:1px dashed #cbd5e1; border-radius:20px; background:#f8fafc;}
        .footer {text-align:center; color:#94a3b8; font-size:.8rem; padding-top:2.5rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(config: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <section class="gallery-hero">
          <div class="gallery-eyebrow">{esc(config['institution'])} · STUDENT APP GALLERY</div>
          <div class="gallery-title">{esc(config['title'])}</div>
          <p class="gallery-subtitle">{esc(config['subtitle'])}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.caption("● GitHub Issues 제출 · GitHub Actions 자동 동기화 · 별도 데이터베이스 없음")


def render_guide() -> None:
    with st.expander("❓ 처음이신가요? — 30초 사용법"):
        st.markdown(
            """
            1. **둘러보기** — 작품 카드의 **앱 열기**를 누르면 학생 앱이 실행됩니다.  
            2. **골라보기** — 작품 유형과 검색어로 원하는 프로젝트만 볼 수 있습니다.  
            3. **응원하기** — GitHub 이슈에서 👍 또는 ❤️ 반응과 댓글을 남깁니다.  
            4. **제출하기** — **작품 제출** 탭의 버튼을 눌러 GitHub 제출 양식을 작성합니다.
            """
        )


def render_project_card(project: dict[str, Any], categories: list[dict[str, str]]) -> None:
    with st.container(border=True):
        thumbnail_url = str(project.get("thumbnail_url", ""))
        if thumbnail_url and is_valid_https_url(thumbnail_url):
            st.image(thumbnail_url, use_container_width=True)
        else:
            st.markdown('<div class="thumbnail-placeholder">🚀</div>', unsafe_allow_html=True)

        st.markdown(
            f'<span class="pill">{esc(category_label(categories, project.get("category", "")))}</span>'
            f'<span class="pill">{esc(project.get("nickname", "익명"))}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="project-title">{esc(project.get("topic", "제목 없는 프로젝트"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="project-tagline">{esc(project.get("tagline", ""))}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="project-meta">{esc(safe_domain(project.get("app_url", "")))} · {esc(relative_date(project.get("created_at")))}</div>',
            unsafe_allow_html=True,
        )

        app_url = str(project.get("app_url", ""))
        issue_url = str(project.get("issue_url", ""))
        if issue_url and is_valid_https_url(issue_url):
            left, right = st.columns([1.35, 1])
            with left:
                st.link_button("앱 열기 ↗", app_url, use_container_width=True)
            with right:
                likes = int(project.get("like_count", 0))
                comments = int(project.get("feedback_count", 0))
                st.link_button(f"♥ {likes} · 💬 {comments}", issue_url, use_container_width=True)
        else:
            st.link_button("앱 열기 ↗", app_url, use_container_width=True)

        with st.expander(f"프로젝트 자세히 · 피드백 {int(project.get('feedback_count', 0))}개"):
            st.markdown(f"**사용한 데이터**  \n{esc(project.get('data_used', '-'))}")
            st.markdown(f"**프로젝트 소개**  \n{esc(project.get('description', '-'))}")
            source_url = str(project.get("data_source_url", ""))
            if source_url and is_valid_https_url(source_url):
                st.link_button("데이터 출처 보기 ↗", source_url)

            feedback_items = project.get("feedback", []) or []
            if feedback_items:
                st.divider()
                for item in feedback_items[-5:]:
                    st.markdown(f"**{esc(item.get('nickname', '익명'))}** · {esc(relative_date(item.get('created_at')))}")
                    st.write(str(item.get("content", "")))
            else:
                st.caption("아직 GitHub 댓글 피드백이 없습니다.")

            if issue_url and is_valid_https_url(issue_url):
                st.link_button("GitHub에서 응원·피드백 남기기 ↗", issue_url, use_container_width=True)


def render_gallery(config: dict[str, Any], storage: GalleryStorage) -> None:
    categories = config["categories"]
    try:
        projects = storage.get_projects()
    except StorageError as exc:
        st.error(str(exc))
        return

    total_likes = sum(int(item.get("like_count", 0)) for item in projects)
    total_feedback = sum(int(item.get("feedback_count", 0)) for item in projects)
    metrics = st.columns(3)
    metrics[0].metric("공개 작품", len(projects))
    metrics[1].metric("받은 좋아요", total_likes)
    metrics[2].metric("남겨진 피드백", total_feedback)

    filter_col, search_col, sort_col = st.columns([1.6, 1.2, 1])
    options = ["전체"] + [item["label"] for item in categories]
    selected_label = filter_col.selectbox("작품 유형", options, label_visibility="collapsed")
    query = search_col.text_input("검색", placeholder="주제·닉네임·데이터 검색", label_visibility="collapsed")
    sort_by = sort_col.selectbox("정렬", ["최신순", "좋아요순", "피드백순"], label_visibility="collapsed")

    selected_key = next((item["key"] for item in categories if item["label"] == selected_label), None)
    normalized_query = query.strip().lower()
    filtered: list[dict[str, Any]] = []
    for project in projects:
        if selected_key and project.get("category") != selected_key:
            continue
        haystack = " ".join(str(project.get(field, "")) for field in ["nickname", "topic", "tagline", "data_used", "description"]).lower()
        if normalized_query and normalized_query not in haystack:
            continue
        filtered.append(project)

    if sort_by == "좋아요순":
        filtered.sort(key=lambda item: (item.get("like_count", 0), item.get("created_at", "")), reverse=True)
    elif sort_by == "피드백순":
        filtered.sort(key=lambda item: (item.get("feedback_count", 0), item.get("created_at", "")), reverse=True)
    else:
        filtered.sort(key=lambda item: item.get("created_at", ""), reverse=True)

    st.subheader(f"작품 둘러보기 · {len(filtered)}개")
    if not filtered:
        st.markdown('<div class="empty-state"><h3>조건에 맞는 작품이 없습니다.</h3><p>검색어를 바꾸거나 첫 작품을 제출해 보세요.</p></div>', unsafe_allow_html=True)
        return

    columns = st.columns(3)
    for index, project in enumerate(filtered):
        with columns[index % 3]:
            render_project_card(project, categories)


def render_submission(config: dict[str, Any], urls: dict[str, str]) -> None:
    st.subheader("내 작품 제출하기")
    st.write("GitHub Issue Form이 제출 양식과 저장소 역할을 합니다. 별도 API 키나 데이터베이스 계정은 필요하지 않습니다.")
    st.info("제출하려면 GitHub 계정 로그인이 필요합니다. 제출 내용은 관리자가 `published` 라벨을 붙인 뒤 갤러리에 공개됩니다.", icon="ℹ️")
    st.link_button("GitHub 제출 양식 열기 ↗", urls["submit"], type="primary", use_container_width=True)
    st.markdown(
        """
        **제출 절차**
        1. 산출물 구분, 닉네임, 앱 URL과 프로젝트 설명을 입력합니다.
        2. 제출하면 저장소에 `submission` 이슈가 생성됩니다.
        3. 관리자가 내용을 확인하고 `published` 라벨을 추가합니다.
        4. GitHub Actions가 `data/projects.json`을 갱신하고 갤러리가 자동 업데이트됩니다.
        """
    )


def render_admin(urls: dict[str, str]) -> None:
    st.subheader("관리자 승인")
    st.write("관리자 화면을 별도로 만들지 않고 GitHub의 이슈와 라벨을 사용합니다.")
    col1, col2 = st.columns(2)
    col1.link_button("승인 대기 제출 보기 ↗", urls["pending"], use_container_width=True)
    col2.link_button("공개된 작품 보기 ↗", urls["published"], use_container_width=True)
    st.markdown(
        """
        **승인:** 제출 이슈를 열고 `published` 라벨을 추가합니다.  
        **게시 취소:** `published` 라벨을 제거합니다.  
        **내용 수정:** 학생이 이슈 본문을 수정하거나 관리자가 수정한 뒤 동기화 작업을 실행합니다.  
        **응원·피드백:** 이슈의 👍·❤️ 반응과 댓글이 갤러리에 집계됩니다.
        """
    )
    st.link_button("동기화 작업 확인 ↗", urls["actions"], use_container_width=True)


def main() -> None:
    config = load_config()
    urls = repository_urls(config)
    st.set_page_config(page_title=config["title"], page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")
    inject_css()
    storage = GalleryStorage(BASE_DIR)
    render_hero(config)
    render_guide()

    gallery_tab, submit_tab, admin_tab = st.tabs(["🖼️ 갤러리", "🚀 작품 제출", "🔐 관리 안내"])
    with gallery_tab:
        render_gallery(config, storage)
    with submit_tab:
        render_submission(config, urls)
    with admin_tab:
        render_admin(urls)

    st.markdown(f'<div class="footer">{esc(config["footer"])}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
