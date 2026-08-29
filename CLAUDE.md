# CLAUDE.md

> 이 파일은 Claude Code(claude.ai/code)가 이 저장소에서 작업할 때 참고하는 가이드다.

## 개요

종로구시각장애인취업역량강화센터 「재직자 AI 활용 직무향상과정(교사)」 김헌용 담당 4회기(2026-08-26~09-05)의 훈련생 배포용 강의 웹페이지. 훈련생 4명 전원이 전맹 센스리더 사용자이므로 슬라이드덱이 아니라 **원고 열람 페이지**다.

- 저장소: https://github.com/Engccer/jongno-ai-training-2608
- 배포 URL: https://engccer.github.io/jongno-ai-training-2608/
- 콘텐츠 정본: `G:\내 드라이브\KHY\Lectures\2608~2609 종로시각장애인복지관 재직자 AI 활용 직무향상과정(교사)\`의 `사전 준비 안내문.md`와 `5. 강의 원고\*.md`. 이 저장소는 그 내용을 옮긴 것이다. <!-- sanitize: allow 원고 정본 위치. 이 저장소의 존재 이유라 일반화 불가 -->

## 구조

- `build.py`: 드라이브의 마크다운을 읽어 `index.html`을 생성한다. 원고를 고치면 `python build.py` 후 commit·push. `SECTIONS`의 세 번째 값이 `False`인 회기는 본문 대신 「원고를 준비하고 있습니다.」만 실린다. 회기 원고가 확정되면 `True`로 바꾼다.
- `template.html`: 페이지 골격·CSS·JS. `{{BUTTONS}}`·`{{ARTICLES}}`를 build.py가 채운다.
- `index.html`: 생성물. 직접 편집하지 않는다.
- `sfx/open.mp3`·`close.mp3`: 열기·닫기 효과음(ElevenLabs sound-generation, 0.6초).

## 동작

첫 화면은 h1과 제목 버튼 5개뿐이다. 버튼을 누르면 목록이 숨고 해당 `<article>`이 열리며 포커스가 그 h2로 간다. 닫기 버튼(본문 위·아래)이나 Esc로 닫으면 눌렀던 버튼으로 포커스가 돌아온다. URL 해시(`#s1`~`#s5`)로 딥링크와 뒤로 가기를 지원한다.

## 접근성

글로벌 접근성 헌장(`~/.claude/ACCESSIBILITY.md`)을 따른다. landmark는 `<main>` 하나, ARIA 없음, 네이티브 `<button>`·heading 계층(h1 페이지 → h2 문서 제목 → h3 원고 `##`)만으로 탐색한다. 원고 heading은 build.py가 한 단계씩 내린다. <!-- sanitize: allow 준수 기준 문서 참조. 경로가 곧 기준의 이름 -->
