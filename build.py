"""드라이브의 마크다운 정본을 읽어 index.html을 생성한다. 원고를 고치면 다시 실행한다."""
import html, re
from pathlib import Path
import markdown

SRC = Path(r"G:\내 드라이브\KHY\Lectures\2608~2609 종로시각장애인복지관 재직자 AI 활용 직무향상과정(교사)")
OUT = Path(__file__).with_name("index.html")

# (버튼 제목, 정본 파일, 게시 여부)
SECTIONS = [
    ("사전 준비 안내", SRC / "사전 준비 안내문.md", True),
    ("1회기: 작업 환경 셋업", SRC / "5. 강의 원고/강의 원고 1회기 작업 환경 셋업.md", True),
    ("2회기: 행정업무 자동화 기본", SRC / "5. 강의 원고/강의 원고 2회기 행정업무 자동화 기본.md", False),
    ("3회기: 행정업무 자동화 심화", SRC / "5. 강의 원고/강의 원고 3회기 행정업무 자동화 심화.md", False),
    ("4회기: 수업과 평가", SRC / "5. 강의 원고/강의 원고 4회기 수업과 평가.md", False),
]

def render(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^# .*\n", "", text, count=1)          # 문서 제목은 버튼·h2가 대신함
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    for lv in (5, 4, 3, 2):                                 # 페이지 h1 아래로 한 단계씩 내림
        body = body.replace(f"<h{lv}>", f"<h{lv+1}>").replace(f"</h{lv}>", f"</h{lv+1}>")
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return body

articles, buttons = [], []
for i, (title, path, live) in enumerate(SECTIONS, 1):
    sid = f"s{i}"
    buttons.append(f'<li><button type="button" data-open="{sid}">{html.escape(title)}</button></li>')
    inner = render(path) if live else "<p>원고를 준비하고 있습니다.</p>"
    articles.append(
        f'<article id="{sid}" hidden>\n'
        f'<button type="button" class="close" data-close>닫기</button>\n'
        f'<h2 tabindex="-1">{html.escape(title)}</h2>\n{inner}\n'
        f'<button type="button" class="close" data-close>닫기</button>\n</article>'
    )

template = Path(__file__).with_name("template.html").read_text(encoding="utf-8")
OUT.write_text(template.replace("{{BUTTONS}}", "\n".join(buttons)).replace("{{ARTICLES}}", "\n".join(articles)), encoding="utf-8")
print("wrote", OUT, OUT.stat().st_size, "bytes")
