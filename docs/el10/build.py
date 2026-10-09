#!/usr/bin/env python3
"""휴머노이드 로봇 백과사전 빌더.

content.json(본문) + images/*.svg(카툰 일러스트)를 읽어
모든 그림을 인라인한 단일 파일 index.html을 만든다.
사용법: python3 build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
D = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
E = html.escape

SECTIONS = [
    ("intro", "🤖", "로봇이 뭐예요?"),
    ("body", "🔧", "로봇 몸 탐험"),
    ("walk", "🚶", "걷는 비밀"),
    ("robots", "🃏", "로봇 도감"),
    ("history", "📜", "로봇 역사"),
    ("jobs", "🛠️", "로봇이 하는 일"),
    ("quiz", "❓", "로봇 퀴즈"),
    ("words", "📖", "낱말 사전"),
    ("future", "🌈", "미래와 약속"),
]
STAT_NAMES = [("walk", "걷기", "#06D6A0"), ("smart", "똑똑함", "#9B5DE5"),
              ("talk", "말하기", "#4CC9F0"), ("strong", "힘", "#FF6B6B")]
CARD_COLORS = ["#4CC9F0", "#FFD23F", "#FF6B6B", "#06D6A0", "#9B5DE5",
               "#FF9F1C", "#4CC9F0", "#FFD23F", "#FF6B6B", "#06D6A0"]


def svg(name, cls="art"):
    s = (ROOT / "images" / f"{name}.svg").read_text(encoding="utf-8")
    s = re.sub(r"<\?xml[^>]*\?>", "", s).strip()
    s = s.replace("<svg", f'<svg class="{cls}" role="img" aria-label="{E(name)} 그림"', 1)
    return s


def tip(i):
    tips = D["mascot"]["tips"]
    if i >= len(tips):
        return ""
    return f'''<div class="tip reveal"><div class="tip-bot" aria-hidden="true">{MINI_BOT}</div>
<p class="bubble"><b>{E(D["mascot"]["name"])}:</b> {E(tips[i])}</p></div>'''


MINI_BOT = '''<svg viewBox="0 0 100 100"><g stroke="#2B2D42" stroke-width="4" stroke-linejoin="round">
<line x1="50" y1="8" x2="50" y2="20"/><circle cx="50" cy="8" r="6" fill="#FF6B6B"/>
<rect x="18" y="20" width="64" height="50" rx="16" fill="#4CC9F0"/>
<path d="M62 24h14a6 6 0 0 1 6 6v30a10 10 0 0 1-10 10h-10z" fill="#2fa8cc" stroke="none"/>
<rect x="18" y="20" width="64" height="50" rx="16" fill="none"/>
<circle cx="38" cy="44" r="9" fill="#fff"/><circle cx="62" cy="44" r="9" fill="#fff"/>
<circle cx="39" cy="45" r="4.5" fill="#2B2D42" stroke="none"/><circle cx="63" cy="45" r="4.5" fill="#2B2D42" stroke="none"/>
<path d="M40 58q10 8 20 0" fill="none"/><rect x="30" y="72" width="40" height="22" rx="8" fill="#FFD23F"/>
</g><circle cx="41" cy="42" r="1.8" fill="#fff"/><circle cx="65" cy="42" r="1.8" fill="#fff"/></svg>'''


def speak_btn(sec):
    return f'<button class="speak" data-read="{sec}" aria-label="소리로 읽어 주기">🔊 읽어 주기</button>'


def head(sec_id, emoji, title, num):
    return f'''<div class="sec-head reveal"><span class="sec-num">{num}</span>
<h2><span class="emo" aria-hidden="true">{emoji}</span> {E(title)}</h2>{speak_btn(sec_id)}</div>'''


# ---------- sections ----------
def sec_intro():
    it = D["intro"]
    ps = "".join(f"<p>{E(p)}</p>" for p in it["paragraphs"])
    return f'''<section id="intro" class="band band-sky"><div class="wrap">
{head("intro", "🤖", it["heading"], 1)}
<div class="grid2">
<div class="card reveal readable">{ps}</div>
<div class="card card-yellow reveal readable"><div class="big-label">💡 휴머노이드란?</div>
<p class="huge">{E(it["humanoidMeaning"])}</p>
<div class="three"><div class="pill" style="--c:#4CC9F0">👀 느끼고</div><div class="pill" style="--c:#9B5DE5">🧠 생각하고</div><div class="pill" style="--c:#FF6B6B">💪 움직여요</div></div>
</div></div>{tip(0)}</div></section>'''


def sec_body():
    cards = "".join(f'''<button class="part reveal" style="--c:{E(a.get("color", "#4CC9F0"))}" data-i="{i}">
<span class="part-n">{i + 1}</span><span class="part-t"><b>{E(a["part"])}</b> <small>{E(a["real"])}</small></span>
<span class="part-d">{E(a["like"])}. {E(a["text"])}</span></button>''' for i, a in enumerate(D["anatomy"]))
    return f'''<section id="body" class="band band-mint"><div class="wrap">
{head("body", "🔧", "로봇 몸 탐험", 2)}
<p class="lead reveal">로봇 몸속에는 무엇이 들어 있을까요? 카드를 눌러 보세요!</p>
<div class="anat"><div class="anat-art card reveal wobble-in">{svg("anatomy")}</div>
<div class="parts readable">{cards}</div></div>{tip(1)}</div></section>'''


def sec_walk():
    w = D["howWalk"]
    steps = "".join(f'''<li class="step reveal" style="--d:{i * 120}ms"><span class="step-n">{i + 1}</span>{E(s)}</li>'''
                    for i, s in enumerate(w["steps"]))
    return f'''<section id="walk" class="band band-yellow"><div class="wrap">
{head("walk", "🚶", w["heading"], 3)}
<ol class="steps readable">{steps}</ol>
<div class="card card-coral tryit reveal readable"><div class="big-label">🧪 직접 해 봐요!</div><p class="huge">{E(w["tryIt"])}</p>
<button class="btn" id="timerBtn">⏱️ 10초 도전 시작</button><span id="timer" class="timer" aria-live="polite"></span></div>
{tip(2)}</div></section>'''


def sec_robots():
    cards = []
    for i, r in enumerate(D["robots"]):
        bars = "".join(f'''<div class="stat"><span>{lab}</span><div class="bar"><i style="--w:{r["stats"][k] * 20}%;--c:{c}"></i></div><em>{"★" * r["stats"][k]}</em></div>'''
                       for k, lab, c in STAT_NAMES)
        cards.append(f'''<div class="flip reveal" style="--c:{CARD_COLORS[i]};--d:{(i % 3) * 100}ms" tabindex="0" role="button" aria-label="{E(r["name"])} 카드 뒤집기">
<div class="flip-in">
<div class="face front"><div class="no">No.{i + 1:02d}</div><div class="robo-art">{svg(r["id"])}</div>
<h3>{E(r["name"])}</h3><div class="nick">“{E(r["nickname"])}”</div>
<div class="facts"><span>🏭 {E(r["maker"])}</span><span>🌏 {E(r["country"])}</span><span>📅 {E(r["year"])}년</span><span>📏 {E(r["height"])}</span></div>
<div class="stats">{bars}</div><div class="flip-hint">👆 눌러서 뒤집기</div></div>
<div class="face back readable"><h3>{E(r["name"])}</h3><div class="power">⚡ 특기: {E(r["power"])}</div>
<p>{E(r["text"])}</p><div class="wow"><b>😲 놀라운 사실!</b><br>{E(r["funFact"])}</div><div class="flip-hint">👆 다시 누르면 앞면</div></div>
</div></div>''')
    return f'''<section id="robots" class="band band-purple"><div class="wrap">
{head("robots", "🃏", "로봇 도감", 4)}
<p class="lead reveal light">세계의 유명한 휴머노이드 로봇 10명을 소개해요. 카드를 누르면 뒤집혀요!</p>
<div class="deck">{"".join(cards)}</div>{tip(3)}</div></section>'''


def sec_history():
    items = "".join(f'''<li class="tl reveal {"r" if i % 2 else "l"}"><div class="tl-year">{E(t["year"])}</div><div class="tl-card readable">{E(t["text"])}</div></li>'''
                    for i, t in enumerate(D["timeline"]))
    return f'''<section id="history" class="band band-cream"><div class="wrap">
{head("history", "📜", "로봇 역사 여행", 5)}
<p class="lead reveal">옛날부터 지금까지, 로봇은 이렇게 자라 왔어요.</p>
<ol class="timeline">{items}</ol></div></section>'''


def sec_jobs():
    cards = "".join(f'''<div class="job card reveal" style="--d:{i * 90}ms"><div class="job-art">{svg(j["id"])}</div>
<div class="job-txt readable"><h3>{E(j["title"])}</h3><p>{E(j["text"])}</p></div></div>''' for i, j in enumerate(D["jobs"]))
    return f'''<section id="jobs" class="band band-sky"><div class="wrap">
{head("jobs", "🛠️", "로봇이 하는 일", 6)}
<div class="jobs">{cards}</div>{tip(4)}</div></section>'''


def sec_quiz():
    qs = []
    for i, q in enumerate(D["quiz"]):
        opts = "".join(f'<button class="opt" data-q="{i}" data-o="{j}">{"ABCD"[j]}. {E(o)}</button>' for j, o in enumerate(q["options"]))
        qs.append(f'''<div class="q card reveal" data-answer="{q["answer"]}" data-explain="{E(q["explain"])}">
<div class="q-n">문제 {i + 1}</div><p class="q-t">{E(q["q"])}</p><div class="opts">{opts}</div><p class="q-f" aria-live="polite"></p></div>''')
    return f'''<section id="quiz" class="band band-coral"><div class="wrap">
{head("quiz", "❓", "로봇 박사 퀴즈", 7)}
<div class="score card reveal"><span>🏆 내 점수</span><b id="score">0</b><span>/ {len(D["quiz"])}</span>
<div id="badge" class="badge" hidden></div><button class="btn small" id="resetQuiz">🔄 다시 풀기</button></div>
<div class="quiz">{"".join(qs)}</div>{tip(5)}</div></section>'''


def sec_words():
    cards = "".join(f'''<div class="word card reveal" style="--c:{CARD_COLORS[i % 10]}"><div class="w">{E(g["word"])}</div><p>{E(g["meaning"])}</p></div>'''
                    for i, g in enumerate(D["glossary"]))
    return f'''<section id="words" class="band band-mint"><div class="wrap">
{head("words", "📖", "로봇 낱말 사전", 8)}
<div class="words readable">{cards}</div></div></section>'''


def sec_future():
    f = D["future"]
    ps = "".join(f"<p>{E(p)}</p>" for p in f["paragraphs"])
    pr = "".join(f'<li><label><input type="checkbox" data-p="{i}"><span>{E(p)}</span></label></li>' for i, p in enumerate(f["promises"]))
    return f'''<section id="future" class="band band-sunset"><div class="wrap">
{head("future", "🌈", f["heading"], 9)}
<div class="card hero-card reveal">{svg("future")}</div>
<div class="grid2"><div class="card reveal readable">{ps}</div>
<div class="card card-yellow reveal readable"><div class="big-label">🤝 로봇과 함께 지킬 약속</div><ul class="promises">{pr}</ul>
<p id="promiseDone" class="done" hidden>🎉 멋져요! 이제 여러분은 로봇의 좋은 친구예요!</p></div></div></div></section>'''


nav = "".join(f'<a href="#{i}"><span aria-hidden="true">{e}</span>{E(t)}</a>' for i, e, t in SECTIONS)
body = "".join(fn() for fn in [sec_intro, sec_body, sec_walk, sec_robots, sec_history, sec_jobs, sec_quiz, sec_words, sec_future])

CSS = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
JS = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")

page = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>휴머노이드 로봇 백과사전</title>
<meta name="description" content="{E(D["subtitle"])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
<canvas id="confetti" aria-hidden="true"></canvas>
<header class="hero">
<div class="gears" aria-hidden="true"><span>⚙️</span><span>⭐</span><span>⚙️</span><span>✨</span><span>🔩</span><span>⭐</span></div>
<div class="wrap hero-in">
<div class="hero-txt"><div class="kicker">초등학생을 위한 로봇 도감</div>
<h1>{"".join(f'<span style="--i:{i}">{E(ch) if ch != " " else "&nbsp;"}</span>' for i, ch in enumerate(D["title"]))}</h1>
<p class="sub">{E(D["subtitle"])}</p>
<div class="hello"><div class="tip-bot big" aria-hidden="true">{MINI_BOT}</div><p class="bubble">{E(D["mascot"]["greeting"])}</p></div>
<a class="btn big" href="#intro">🚀 탐험 시작!</a></div>
<div class="hero-art card wobble-in">{svg("hero")}</div></div>
<svg class="wave" viewBox="0 0 1440 80" preserveAspectRatio="none" aria-hidden="true"><path d="M0 40 Q 180 0 360 40 T 720 40 T 1080 40 T 1440 40 V80 H0Z" fill="#CFF3FF" stroke="#2B2D42" stroke-width="4"/></svg>
</header>
<nav class="nav" aria-label="목차"><div class="nav-in">{nav}</div></nav>
<main>{body}</main>
<footer class="foot"><div class="wrap"><p>🤖 {E(D["title"])}</p><p class="small">그림과 글은 초등학교 3학년 친구들이 읽기 쉽게 만들었어요. 로봇 정보는 공개된 자료를 바탕으로 했어요.</p></div></footer>
<button id="toTop" class="to-top" aria-label="맨 위로">⬆️</button>
<script>{JS}</script>
</body></html>'''

(ROOT / "index.html").write_text(page, encoding="utf-8")
print(f"index.html {len(page.encode('utf-8')) / 1024:.0f}KB")
