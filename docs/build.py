#!/usr/bin/env python3
"""ARGOS premium build.

src/00-shell.html 의 <!--SECTIONS--> 자리에 src/0[1-7]-*.html 조각을 파일명 순서로 넣고,
푸터 출처(<!--SOURCES_*-->)를 data/*.json 정본에서 채워 index.html 을 만든다.

    python3 build.py          # data → 조각 인라인 JSON 동기화, index.html 생성, 점검 리포트
    python3 build.py --check  # 생성·동기화 없이 점검만 (정본과 사본 불일치, 문체, 스코프)

조각 안의 <script type="application/json" id="..."> 블록은 data/*.json 의 사본입니다.
사본은 손으로 고치지 않고, data 를 고친 뒤 빌드하면 INLINE 표대로 덮어씁니다.

_preview 로 시작하는 파일은 넣지 않는다.
셸과 조각의 "../assets/*.png" 참조(로고, 파비콘)는 data URI 로 인라인해 index.html 한 파일로 공유되게 한다.
"""
from __future__ import annotations

import base64
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DATA = ROOT / "data"
SHELL = SRC / "00-shell.html"
OUT = ROOT / "index.html"
EXPECTED = [f"0{i}" for i in range(1, 8)]
ASSET_REF = re.compile(r'"\.\./(assets/[^"]+\.png)"')
FORBIDDEN_LIBS = re.compile(r'<script[^>]+src=["\'][^"\']*(gsap|ScrollTrigger|three)[^"\']*["\']', re.I)


# (조각 파일, 블록 id, 정본을 만드는 함수, 직렬화 방식)
INLINE = [
    ("02-anatomy.html", "anatomy-data", lambda: load_json("content.json")["anatomy"], "pretty"),
    ("03-types.html", "types-data", lambda: load_json("content.json")["types"], "pretty"),
    ("06-history.html", "history-data", lambda: load_json("content.json")["history"], "pretty"),
    ("07-glossary.html", "glossary-data", lambda: load_json("content.json")["glossary"], "pretty"),
    ("07-glossary.html", "faq-data", lambda: load_json("content.json")["faq"], "pretty"),
    ("04-players.html", "players-data",
     lambda: {"west": load_json("videos_west.json"), "asia": load_json("videos_asia.json")}, "pretty"),
    ("05-reality.html", "reality-data", lambda: load_json("anthropic.json"), "compact"),
    ("05-reality.html", "korea-data", lambda: load_json("korea.json"), "compact"),
]
# 입니다체 문서에 섞이면 안 되는 종결. '~한다(괄호).' 와 '~하나?' 형태를 잡습니다.
TONE_BAD = re.compile(r"[^니습]다\([^)]*\)\.|[가-힣](?:나|인가)\?")


def dump_inline(obj, mode: str) -> str:
    if mode == "compact":
        out = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    else:
        out = json.dumps(obj, ensure_ascii=False, indent=2)
    return out.replace("</", "<\\/")


def inline_block(text: str, block_id: str):
    return re.search(r'(<script type="application/json" id="%s">)(.*?)(</script>)' % re.escape(block_id), text, re.S)


def sync_inline(write: bool) -> list[str]:
    """data/*.json 정본을 조각의 인라인 JSON 사본으로 내려보냅니다. write=False 면 불일치만 보고합니다."""
    problems: list[str] = []
    for fname, block_id, getter, mode in INLINE:
        f = SRC / fname
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        m = inline_block(text, block_id)
        if not m:
            problems.append(f"{fname}: 인라인 블록 #{block_id} 없음")
            continue
        try:
            canon = getter()
        except Exception as e:  # noqa: BLE001
            problems.append(f"{fname}#{block_id}: 정본을 읽지 못했습니다 ({e})")
            continue
        if json.loads(m.group(2)) == canon:
            continue
        if write:
            text = text[:m.start(2)] + dump_inline(canon, mode) + text[m.end(2):]
            f.write_text(text, encoding="utf-8")
            print(f"[sync] {fname}#{block_id} ← data")
        else:
            problems.append(f"{fname}#{block_id}: data 정본과 다릅니다 (python3 build.py 로 동기화)")
    return problems


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def load_json(name: str):
    p = DATA / name
    if not p.exists():
        print(f"[warn] data/{name} 없음. 해당 출처는 비워 둡니다.")
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def research_sources() -> str:
    a = load_json("anthropic.json")
    if not a:
        return "<ul></ul>"
    s = a.get("source", {})
    authors = ", ".join(s.get("authors", []))
    items = [
        f'<li><a href="{esc(s.get("url"))}" target="_blank" rel="noopener">{esc(s.get("title"))}</a>'
        f'<small>{esc(s.get("publisher"))} · {esc(authors)} · {esc(s.get("published"))}</small></li>'
    ]
    for key, label in (("pdf_main", "논문 PDF 본문"), ("pdf_appendix", "논문 PDF 부록")):
        if s.get(key):
            items.append(f'<li><a href="{esc(s[key])}" target="_blank" rel="noopener">{label}</a>'
                         f'<small>Anthropic · 확인일 {esc(s.get("retrieved"))}</small></li>')
    if s.get("data_release"):
        items.append(f'<li><a href="{esc(s["data_release"])}" target="_blank" rel="noopener">데이터 릴리스 (robot_exposure)</a>'
                     f'<small>Hugging Face · {esc(s.get("data_license"))}</small></li>')
    return "<ul>" + "".join(items) + "</ul>"


def channel_sources() -> str:
    """업체별 공식 채널 영상 1건씩. channel 이름이 업체명과 맞는 영상만 '공식'으로 본다."""
    seen, items = set(), []
    for fn in ("videos_west.json", "videos_asia.json"):
        d = load_json(fn)
        if not d:
            continue
        for c in d.get("companies", []):
            if c["id"] in seen:
                continue
            name = c.get("name", "")
            first_word = name.split()[0].lower() if name else ""
            official = [v for v in c.get("videos", [])
                        if first_word and first_word in v.get("channel", "").lower()]
            if not official:
                continue
            v = official[0]
            seen.add(c["id"])
            items.append(
                f'<li><a href="https://www.youtube.com/watch?v={esc(v["id"])}" target="_blank" rel="noopener">'
                f'{esc(v["channel"])}</a><small>{esc(c.get("name_ko"))} · YouTube 공식 영상 {esc(v.get("upload_date"))}</small></li>'
            )
    return "<ul>" + "".join(items) + "</ul>"


def source_note() -> str:
    c = load_json("content.json") or {}
    note = c.get("meta", {}).get("source_note_ko", "")
    note = note.replace("기준으로 한다.", "기준으로 합니다.").replace("뜻한다.", "뜻합니다.")
    return esc(note) + " 영상 썸네일은 각 업체가 YouTube에 올린 공식 영상에서 가져왔습니다."


def inline_assets(text: str) -> str:
    """src 기준 상대경로 "../assets/x.png" 를 data URI 로 바꿉니다. 같은 파일은 한 번만 읽습니다."""
    cache: dict[str, str] = {}

    def repl(m: re.Match) -> str:
        rel = m.group(1)
        if rel not in cache:
            f = ROOT / rel
            if not f.exists():
                print(f"[warn] {rel} 없음. 경로를 그대로 둡니다.")
                return m.group(0)
            cache[rel] = "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode()
        return f'"{cache[rel]}"'

    return ASSET_REF.sub(repl, text)


def check(fragments: list[Path]) -> list[str]:
    """조각 간 충돌 점검. 문제 목록을 돌려준다."""
    problems: list[str] = []
    ids: Counter = Counter()
    owner: dict[str, str] = {}
    for f in fragments:
        s = f.read_text(encoding="utf-8")
        m = re.match(r'\s*<section id="([^"]+)" class="sec[^"]*" data-nav="[^"]+"', s)
        if not m:
            problems.append(f"{f.name}: 첫 요소가 <section id class=sec data-nav> 규약과 다릅니다")
        for i in re.findall(r'\sid="([^"$\'+{]+)"', s):
            ids[i] += 1
            owner.setdefault(i, f.name)
        if FORBIDDEN_LIBS.search(s):
            problems.append(f"{f.name}: GSAP/Three 를 다시 로드합니다 (셸에서만 로드)")
        for hit in TONE_BAD.findall(s):
            problems.append(f"{f.name}: 문체 '~다/~나?' 종결 '{hit}'")
        sec = m.group(1) if m else None
        if sec:
            for style in re.findall(r"<style>(.*?)</style>", s, re.S):
                body = re.sub(r"/\*.*?\*/", "", style, flags=re.S)
                body = re.sub(r"@keyframes[^{]+\{(?:[^{}]*\{[^}]*\})*[^}]*\}", "", body)
                for sel in re.findall(r"(?:^|})\s*([^{}@]+)\{", body):
                    for part in sel.split(","):
                        p = part.strip()
                        if p and not p.startswith("#" + sec) and not re.match(r"^(from|to|\d+%)$", p):
                            problems.append(f"{f.name}: 스코프 밖 선택자 '{p[:60]}'")
    for i, n in ids.items():
        if n > 1:
            problems.append(f"중복 id '{i}' ({n}회, 처음 {owner[i]})")
    return problems


def main() -> int:
    only_check = "--check" in sys.argv
    if not SHELL.exists():
        print("[error] src/00-shell.html 이 없습니다")
        return 1
    fragments = sorted(p for p in SRC.glob("0[1-7]-*.html"))
    present = {p.name[:2] for p in fragments}
    for n in EXPECTED:
        if n not in present:
            print(f"[warn] 조각 {n}-*.html 없음. 건너뜁니다.")

    problems = sync_inline(write=not only_check) + check(fragments)
    for p in problems:
        print("[check]", p)
    if only_check:
        return 1 if problems else 0

    shell = SHELL.read_text(encoding="utf-8")
    if "<!--SECTIONS-->" not in shell:
        print("[error] 셸에 <!--SECTIONS--> 가 없습니다")
        return 1
    body = "\n".join(
        f"<!-- ===== {p.name} ===== -->\n" + p.read_text(encoding="utf-8").strip() + "\n"
        for p in fragments
    )
    out = (shell.replace("<!--SECTIONS-->", body)
                .replace("<!--SOURCES_RESEARCH-->", research_sources())
                .replace("<!--SOURCES_CHANNELS-->", channel_sources())
                .replace("<!--SOURCE_NOTE-->", source_note()))
    out = inline_assets(out)
    OUT.write_text(out, encoding="utf-8")
    print(f"[ok] {OUT.relative_to(ROOT.parent)}  {len(out.encode('utf-8')) / 1024:.0f}KB  "
          f"조각 {len(fragments)}개: {', '.join(p.name for p in fragments)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
