# 학생 Streamlit 앱 갤러리 — GitHub 전용 버전

학생들이 제작한 Streamlit 앱을 제출하고 카드형 갤러리로 공유하는 프로젝트입니다.

이 버전은 **Supabase, Firebase, 별도 데이터베이스를 사용하지 않습니다.**

- 제출 저장: GitHub Issue Form
- 공개 승인: GitHub `published` 라벨
- 갤러리 데이터: `data/projects.json`
- 데이터 생성: GitHub Actions
- 좋아요: GitHub 이슈의 👍 및 ❤️ 반응
- 피드백: GitHub 이슈 댓글
- 갤러리 실행: Streamlit Community Cloud

## 1. 작동 방식

```text
학생이 GitHub 제출 양식 작성
        ↓
submission 이슈 생성
        ↓
관리자가 published 라벨 추가
        ↓
GitHub Actions가 이슈를 읽어 projects.json 생성
        ↓
자동 커밋 → Streamlit 갤러리 자동 갱신
```

별도 API 키나 데이터베이스 비밀번호는 필요하지 않습니다. GitHub Actions는 저장소에 기본 제공되는 `GITHUB_TOKEN`을 사용합니다.

## 2. 프로젝트 구조

```text
student-streamlit-gallery/
├── app.py
├── storage.py
├── gallery_config.json
├── requirements.txt
├── data/
│   ├── projects.json
│   └── sample_projects.json
├── scripts/
│   └── build_projects.py
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── app-submission.yml
│   │   └── config.yml
│   └── workflows/
│       └── sync-gallery.yml
└── .streamlit/
    └── config.toml
```

## 3. GitHub 저장소 만들기

1. GitHub에서 새 저장소를 만듭니다.
2. 학생들이 이슈를 제출할 수 있도록 **Public 저장소** 사용을 권장합니다.
3. 이 프로젝트 파일 전체를 저장소에 업로드합니다.
4. `gallery_config.json`의 저장소 주소를 실제 값으로 변경합니다.

```json
"github_repository": "YOUR-GITHUB-ID/YOUR-REPOSITORY"
```

예시:

```json
"github_repository": "greatsong/snu-streamlit-gallery"
```

## 4. GitHub Actions 쓰기 권한 허용

GitHub 저장소에서 다음 메뉴로 이동합니다.

```text
Settings
→ Actions
→ General
→ Workflow permissions
→ Read and write permissions
→ Save
```

이 권한은 GitHub Actions가 갱신된 `data/projects.json`을 저장소에 자동 커밋하기 위해 필요합니다.

## 5. 최초 설정 작업 실행

저장소의 **Actions** 탭에서 다음 작업을 한 번 수동 실행합니다.

```text
Sync gallery data
→ Run workflow
```

이 작업은 다음 라벨을 자동 생성합니다.

- `submission`: 학생이 제출한 작품
- `published`: 갤러리에 공개할 작품

처음 실행하면 `data/projects.json`의 예시 작품이 제거될 수 있습니다. 아직 승인된 이슈가 없으면 빈 배열 `[]`이 정상입니다.

## 6. 학생 제출 방법

Streamlit 갤러리의 **작품 제출** 탭에서 `GitHub 제출 양식 열기`를 누릅니다.

또는 다음 주소로 직접 접속합니다.

```text
https://github.com/YOUR-GITHUB-ID/YOUR-REPOSITORY/issues/new?template=app-submission.yml
```

학생은 다음 내용을 입력합니다.

- 산출물 구분
- 닉네임
- Streamlit 앱 URL
- 한 줄 소개
- 프로젝트 주제
- 사용한 데이터
- 데이터 출처 링크
- 프로젝트 소개
- 대표 이미지 URL(선택)

학생이 제출하려면 GitHub 계정 로그인이 필요합니다.

## 7. 작품 승인과 게시 취소

### 승인

1. GitHub 저장소의 **Issues**로 이동합니다.
2. 제출된 이슈를 확인합니다.
3. 오른쪽 Labels에서 `published`를 추가합니다.
4. GitHub Actions가 자동 실행됩니다.
5. `data/projects.json`이 갱신되고 Streamlit 앱에 반영됩니다.

### 게시 취소

이슈에서 `published` 라벨을 제거하면 갤러리에서 제외됩니다.

### 내용 수정

학생 또는 관리자가 이슈 본문을 수정하면 GitHub Actions가 다시 실행되어 갤러리 정보가 갱신됩니다.

## 8. 좋아요와 피드백

작품 카드의 `♥ 숫자 · 💬 숫자` 버튼을 누르면 해당 GitHub 이슈로 이동합니다.

- 좋아요: 이슈에 👍 또는 ❤️ 반응
- 피드백: 이슈 댓글 작성

댓글 작성이나 반응 추가 후 갤러리 집계가 갱신되는 시점은 다음과 같습니다.

- 이슈 댓글 작성·수정·삭제: 즉시 동기화 작업 실행
- 이슈 내용·라벨 변경: 즉시 동기화 작업 실행
- 이슈 반응 수: 매시간 자동 재집계

GitHub Actions의 예약 실행은 정각이 아니라 매시간 17분에 설정되어 있습니다.

## 9. Streamlit Community Cloud 배포

1. `https://share.streamlit.io`에 로그인합니다.
2. **Create app**을 선택합니다.
3. GitHub 저장소와 `main` 브랜치를 선택합니다.
4. Main file path에 다음을 입력합니다.

```text
app.py
```

5. Deploy를 누릅니다.

이 버전은 Streamlit Secrets 입력이 필요하지 않습니다.

## 10. 수업명과 분류 수정

수업명, 제목, 설명은 `gallery_config.json`에서 수정합니다.

```json
{
  "institution": "서울대학교 환경설계학과",
  "title": "학생 Streamlit 앱 갤러리",
  "subtitle": "학생들이 직접 만든 데이터 앱을 공유합니다."
}
```

작품 분류를 수정할 때는 다음 두 파일을 함께 변경해야 합니다.

1. `gallery_config.json`의 `categories`
2. `.github/ISSUE_TEMPLATE/app-submission.yml`의 dropdown options

두 파일의 분류 이름이 정확히 일치해야 자동 변환됩니다.

## 11. 운영상 유의사항

### 장점

- Supabase 등 외부 서비스 불필요
- 비용 없이 운영 가능
- 제출과 수정 이력이 GitHub에 남음
- 승인 과정이 투명함
- 별도 관리자 비밀번호 불필요
- 스팸이나 부적절한 제출은 이슈에서 바로 관리 가능

### 제한

- 학생에게 GitHub 계정이 필요함
- 좋아요와 댓글도 GitHub 로그인이 필요함
- 매우 많은 학생과 실시간 상호작용이 필요한 서비스에는 데이터베이스 방식이 더 적합함
- 저장소가 Public이면 제출 내용과 댓글도 공개됨

## 12. 로컬 실행

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS 또는 Linux:

```bash
source .venv/bin/activate
```

설치 및 실행:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 13. 문제 해결

### 제출 버튼이 잘못된 저장소로 이동함

`gallery_config.json`의 `github_repository` 값을 확인합니다.

### published 라벨을 붙였는데 작품이 보이지 않음

1. Actions 탭에서 `Sync gallery data` 실행 결과를 확인합니다.
2. Workflow permissions가 `Read and write permissions`인지 확인합니다.
3. 앱 URL이 `https://`로 시작하는지 확인합니다.
4. 이슈 양식의 항목 제목을 임의로 바꾸지 않았는지 확인합니다.

### GitHub Actions는 성공했지만 Streamlit에 바로 반영되지 않음

GitHub에서 `data/projects.json`이 변경되었는지 확인한 뒤 Streamlit 앱을 새로고침합니다. 필요하면 Streamlit Community Cloud에서 앱을 Reboot합니다.

### 예시 작품을 유지하고 싶음

`data/projects.json`의 예시 데이터는 첫 동기화 때 승인된 GitHub 이슈 목록으로 대체됩니다. 예시를 실제 작품으로 유지하려면 동일한 내용의 제출 이슈를 만들고 `published` 라벨을 붙이세요.
