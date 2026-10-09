# 로봇 백과사전

휴머노이드 로봇 백과사전을 두 독자층으로 나눠 둔 폴더입니다.

| 폴더 | 독자 | 분류 | 열기 |
|---|---|---|---|
| [`docs/`](docs/) | 경영 리더 (ARGOS, 메인) | Prototype, 목표 9.5점 | `docs/index.html` |
| [`docs/el10/`](docs/el10/) | 초등학교 3학년 (10살, 만 8~9세) | Prototype, 7점 실험 | `docs/el10/index.html` |

- `docs/`는 GitHub Pages에서 그대로 배포할 수 있는 구조입니다. `docs/index.html` 한 파일에 모든 것이 인라인됩니다. 수정과 빌드는 [`docs/README.md`](docs/README.md), 시각 규약은 [`docs/DESIGN.md`](docs/DESIGN.md)를 따릅니다.
- `docs/el10/`은 `python3 docs/el10/build.py`로 다시 빌드합니다. GitHub Pages에서는 `/el10/` 경로로 함께 배포됩니다. 현재 `docs/el10/index.html`은 마지막 빌드 이후 고친 원고(`content.json`, `assets/style.css`)를 아직 반영하지 않은 상태입니다.
- 로컬 확인: 이 폴더에서 `python3 -m http.server 8765 --bind 127.0.0.1`을 실행하고 `http://127.0.0.1:8765/docs/` 또는 `/docs/el10/`을 엽니다.
