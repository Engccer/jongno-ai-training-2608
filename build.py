"""드라이브의 마크다운 정본을 읽어 index.html을 생성한다. 원고를 고치면 다시 실행한다."""
import html, re
from pathlib import Path
import markdown

SRC = Path(r"G:\내 드라이브\KHY\Lectures\2608~2609 종로시각장애인복지관 재직자 AI 활용 직무향상과정(교사)")  # sanitize: allow 원고 정본 위치. 빌드 스크립트의 기능 자체라 일반화 불가
OUT = Path(__file__).with_name("index.html")

# (버튼 제목, 정본 파일, 게시 여부)
SECTIONS = [
    ("사전 준비 안내", SRC / "사전 준비 안내문.md", True),
    ("1회기: 작업 환경 셋업", SRC / "5. 강의 원고/강의 원고 1회기 작업 환경 셋업.md", True),
    ("2회기: 행정업무 자동화 기본", SRC / "5. 강의 원고/강의 원고 2회기 행정업무 자동화 기본.md", True),
    ("3회기: 행정업무 자동화 심화", SRC / "5. 강의 원고/강의 원고 3회기 행정업무 자동화 심화.md", False),
    ("4회기: 수업과 평가", SRC / "5. 강의 원고/강의 원고 4회기 수업과 평가.md", False),
]

# 본문에 그대로 적힌 URL을 새 탭 링크로 바꾼다. 정본 마크다운은 URL을 맨몸으로 두어야
# .md를 그대로 읽을 때 깔끔하므로, 링크화는 표시 단계인 여기서만 한다. 코드 블록 안의 URL도
# 대상이다(주소가 전부 복사용 코드 블록에 들어 있다). 링크 텍스트는 URL 그대로 두어
# 복사·붙여넣기를 깨지 않고, 새 탭에서 열린다는 사실은 낭독 전용 텍스트로 접근 가능한
# 이름에 덧붙인다(WCAG G201).
# 앞은 태그 끝(<code> 직후)이나 공백만 허용한다. 이러면 href="..." 안의 URL은 앞 문자가
# 따옴표라 걸리지 않아 이미 링크인 것을 두 번 감싸지 않는다.
URL_RE = re.compile(r"""(?:^|(?<=[>\s]))(https?://[^\s<>"']+?)(?=[.,)\]]*(?:\s|<|$))""", re.M)

def linkify(body: str) -> str:
    # 링크의 접근 가능한 이름에는 URL 말고 아무것도 넣지 않는다. 스크린 리더 가상 커서는
    # DOM 텍스트가 아니라 접근 가능한 이름을 복사하므로, 새 탭 안내를 sr-only span으로 넣든
    # aria-label로 넣든 복사본에 그대로 딸려 나와 붙여넣을 주소와 지시문을 깨뜨린다
    # (센스리더 실측 2026-08-30, 두 방식 모두 재현). 새 탭 안내는 페이지 머리말에 한 번만 둔다.
    return URL_RE.sub(
        lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener">{m.group(1)}</a>', body)


# 목록 항목 안에 들여쓴 ``` 펜스는 fenced_code가 처리하지 못하고 인라인 <code>로 흘러
# 지시문이 본문에 묻힌다(열 0의 펜스만 처리하는 전처리기다). 목록 안에서 <pre> 블록을 얻는
# 방법은 8칸 들여쓰기뿐이라, 정본의 펜스 표기는 그대로 두고 여기서 바꿔 넣는다.
INDENTED_FENCE = re.compile(r'^([ \t]+)```[^\n]*\n(.*?)^[ \t]*```[ \t]*$', re.M | re.S)

def unfence_in_lists(text: str) -> str:
    def repl(m):
        indent, inner = m.group(1), m.group(2)
        lines = [l[len(indent):] if l.startswith(indent) else l.lstrip()
                 for l in inner.rstrip('\n').split('\n')]
        return '\n' + '\n'.join(' ' * 8 + l if l.strip() else '' for l in lines) + '\n'
    return INDENTED_FENCE.sub(repl, text)

def render(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^# .*\n", "", text, count=1)          # 문서 제목은 버튼·h2가 대신함
    text = unfence_in_lists(text)
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    for lv in (5, 4, 3, 2):                                 # 페이지 h1 아래로 한 단계씩 내림
        body = body.replace(f"<h{lv}>", f"<h{lv+1}>").replace(f"</h{lv}>", f"</h{lv+1}>")
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    body = linkify(body)
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
