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
    def repl(m):
        url = m.group(1)
        # 새 탭 안내를 aria-label로 준다. 낭독 전용 span으로 넣으면 화면에는 안 보여도
        # 선택·복사에는 딸려 가서, 통째로 복사해 에이전트에 붙여넣는 지시문이 깨진다.
        # 라벨이 URL 전문을 그대로 담으므로 눈에 보이는 텍스트를 가리지도 않는다.
        label = html.escape(f"{url}, 새 탭에서 열림", quote=True)
        return f'<a href="{url}" target="_blank" rel="noopener" aria-label="{label}">{url}</a>'
    return URL_RE.sub(repl, body)

def render(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^# .*\n", "", text, count=1)          # 문서 제목은 버튼·h2가 대신함
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
