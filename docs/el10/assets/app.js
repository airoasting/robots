(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // 스크롤 등장
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    $$(".reveal, .wobble-in").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal, .wobble-in").forEach(function (el) { el.classList.add("in"); });
  }

  // 내비 현재 위치
  var links = $$(".nav a");
  if ("IntersectionObserver" in window) {
    var so = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) {
          var on = a.getAttribute("href") === "#" + e.target.id;
          a.classList.toggle("on", on);
          if (on && a.scrollIntoView) a.parentNode.scrollTo({ left: a.offsetLeft - 40, behavior: "smooth" });
        });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    $$("main section").forEach(function (s) { so.observe(s); });
  }

  // 맨 위로
  var top = $("#toTop");
  window.addEventListener("scroll", function () { top.classList.toggle("show", window.scrollY > 600); }, { passive: true });
  top.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });

  // 로봇 몸 부품
  $$(".part").forEach(function (p) {
    p.addEventListener("click", function () {
      var was = p.classList.contains("on");
      $$(".part").forEach(function (x) { x.classList.remove("on"); });
      if (!was) p.classList.add("on");
    });
  });

  // 플립 카드
  $$(".flip").forEach(function (c) {
    var t = function () { var f = c.classList.toggle("flipped"); c.setAttribute("aria-pressed", f ? "true" : "false"); };
    c.addEventListener("click", t);
    c.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); t(); } });
  });

  // 10초 도전
  var tb = $("#timerBtn"), tv = $("#timer"), tid = null;
  if (tb) tb.addEventListener("click", function () {
    clearInterval(tid);
    var n = 10; tv.textContent = n;
    tid = setInterval(function () {
      n--;
      if (n > 0) { tv.textContent = n; return; }
      clearInterval(tid); tv.textContent = "🎉 성공!"; burst(window.innerWidth / 2, window.innerHeight / 2);
    }, 1000);
  });

  // 퀴즈
  var score = 0, answered = 0, total = $$(".q").length;
  var scoreEl = $("#score"), badge = $("#badge");
  function updateBadge() {
    scoreEl.textContent = score;
    if (answered < total) { badge.hidden = true; return; }
    badge.hidden = false;
    badge.textContent = score === total ? "🏅 로봇 박사 인증!" : score >= total - 2 ? "🥈 로봇 연구원!" : "🥉 로봇 견습생! 다시 도전해요";
    if (score === total) { for (var i = 0; i < 4; i++) setTimeout(function () { burst(Math.random() * window.innerWidth, window.innerHeight * 0.3); }, i * 250); }
  }
  $$(".opt").forEach(function (b) {
    b.addEventListener("click", function () {
      var q = b.closest(".q");
      if (q.dataset.done) return;
      q.dataset.done = "1"; answered++;
      var ans = +q.dataset.answer, pick = +b.dataset.o, opts = $$(".opt", q);
      opts.forEach(function (o) { o.disabled = true; });
      opts[ans].classList.add("ok");
      var fb = $(".q-f", q);
      if (pick === ans) {
        score++; q.classList.add("done-ok");
        fb.textContent = "⭕ 정답이에요! " + q.dataset.explain;
        var r = b.getBoundingClientRect(); burst(r.left + r.width / 2, r.top + r.height / 2);
      } else {
        b.classList.add("no"); q.classList.add("done-no");
        fb.textContent = "💪 아쉬워요! " + q.dataset.explain;
      }
      updateBadge();
    });
  });
  $("#resetQuiz").addEventListener("click", function () {
    score = 0; answered = 0;
    $$(".q").forEach(function (q) {
      delete q.dataset.done; q.classList.remove("done-ok", "done-no"); $(".q-f", q).textContent = "";
      $$(".opt", q).forEach(function (o) { o.disabled = false; o.classList.remove("ok", "no"); });
    });
    updateBadge();
  });

  // 약속 체크리스트 (브라우저에만 기억)
  var KEY = "robot-promises";
  var boxes = $$(".promises input"), saved = [];
  try { saved = JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { saved = []; }
  function checkDone(celebrate) {
    var all = boxes.every(function (b) { return b.checked; });
    $("#promiseDone").hidden = !all;
    if (all && celebrate) burst(window.innerWidth / 2, window.innerHeight * 0.4);
  }
  boxes.forEach(function (b, i) {
    b.checked = saved.indexOf(i) >= 0;
    b.addEventListener("change", function () {
      try { localStorage.setItem(KEY, JSON.stringify(boxes.map(function (x, j) { return x.checked ? j : -1; }).filter(function (j) { return j >= 0; }))); } catch (e) {}
      checkDone(true);
    });
  });
  checkDone(false);

  // 읽어 주기
  var synth = window.speechSynthesis, current = null;
  $$(".speak").forEach(function (btn) {
    if (!synth) { btn.hidden = true; return; }
    btn.addEventListener("click", function () {
      var sec = document.getElementById(btn.dataset.read);
      var on = btn.classList.contains("on");
      synth.cancel();
      $$(".speak").forEach(function (x) { x.classList.remove("on"); x.textContent = "🔊 읽어 주기"; });
      $$(".reading").forEach(function (x) { x.classList.remove("reading"); });
      if (on) return;
      var parts = $$(".readable", sec).filter(function (el) { return !el.closest(".back") || el.closest(".flipped"); });
      var text = $("h2", sec).textContent + ". " + parts.map(function (el) { return el.innerText; }).join(" ");
      var u = new SpeechSynthesisUtterance(text.replace(/[^\S\n]+/g, " "));
      u.lang = "ko-KR"; u.rate = 0.92; u.pitch = 1.15;
      var ko = synth.getVoices().filter(function (v) { return /ko/i.test(v.lang); })[0];
      if (ko) u.voice = ko;
      u.onend = u.onerror = function () { btn.classList.remove("on"); btn.textContent = "🔊 읽어 주기"; sec.classList.remove("reading"); };
      btn.classList.add("on"); btn.textContent = "⏹️ 그만 읽기"; sec.classList.add("reading");
      current = u; synth.speak(u);
    });
  });

  // 색종이
  var cv = $("#confetti"), ctx = cv.getContext("2d"), bits = [], raf = null;
  var COLORS = ["#4CC9F0", "#FFD23F", "#FF6B6B", "#06D6A0", "#9B5DE5", "#FF9F1C"];
  function size() { cv.width = window.innerWidth * (window.devicePixelRatio || 1); cv.height = window.innerHeight * (window.devicePixelRatio || 1); }
  size(); window.addEventListener("resize", size);
  function burst(x, y) {
    if (reduce) return;
    var dpr = window.devicePixelRatio || 1;
    for (var i = 0; i < 90; i++) {
      var a = Math.random() * Math.PI * 2, s = 4 + Math.random() * 9;
      bits.push({ x: x * dpr, y: y * dpr, vx: Math.cos(a) * s * dpr, vy: (Math.sin(a) * s - 6) * dpr, r: (5 + Math.random() * 6) * dpr,
        c: COLORS[i % COLORS.length], rot: Math.random() * 6, vr: Math.random() * 0.3 - 0.15, life: 90 + Math.random() * 40, shape: i % 3 });
    }
    if (!raf) raf = requestAnimationFrame(tick);
  }
  function tick() {
    ctx.clearRect(0, 0, cv.width, cv.height);
    var dpr = window.devicePixelRatio || 1;
    bits = bits.filter(function (b) { return b.life > 0 && b.y < cv.height + 40; });
    bits.forEach(function (b) {
      b.vy += 0.35 * dpr; b.vx *= 0.985; b.x += b.vx; b.y += b.vy; b.rot += b.vr; b.life--;
      ctx.save(); ctx.translate(b.x, b.y); ctx.rotate(b.rot); ctx.fillStyle = b.c;
      ctx.strokeStyle = "#2B2D42"; ctx.lineWidth = 1.5 * dpr; ctx.globalAlpha = Math.min(1, b.life / 30);
      ctx.beginPath();
      if (b.shape === 0) ctx.rect(-b.r / 2, -b.r / 3, b.r, b.r / 1.5);
      else if (b.shape === 1) ctx.arc(0, 0, b.r / 2, 0, Math.PI * 2);
      else { ctx.moveTo(0, -b.r / 1.6); ctx.lineTo(b.r / 1.8, b.r / 2); ctx.lineTo(-b.r / 1.8, b.r / 2); ctx.closePath(); }
      ctx.fill(); ctx.stroke(); ctx.restore();
    });
    raf = bits.length ? requestAnimationFrame(tick) : null;
    if (!raf) ctx.clearRect(0, 0, cv.width, cv.height);
  }
  window.addEventListener("load", function () { setTimeout(function () { burst(window.innerWidth * 0.7, window.innerHeight * 0.35); }, 600); });
})();
