"use strict";
/* StudySprint webApp surface (#4092).
 *
 * Renders the core state shapes from data/state.json (built by
 * build_data.py from the real core) and runs SR review in the
 * browser over the core's ts-fsrs UX-state export:
 *  - FSRS: the ts-fsrs formula set (FSRS-5 default weights) — the
 *    UX layer the core seeds for; receipts name the scheduler.
 *  - SM-2: the core's baseline algorithm, ported rule-for-rule.
 * Review state persists in localStorage on this device.
 */

const $ = (s) => document.querySelector(s);
const state = { data: null, cardIndex: 0, flipped: false,
                scheduler: "fsrs", srState: {}, reader: null,
                playing: false, timer: null };

/* ---------------- FSRS (ts-fsrs formulas, FSRS-5 default weights) */
const FSRS_W = [0.40255, 1.18385, 3.173, 15.69105, 7.1949, 0.5345,
  1.4604, 0.0046, 1.54575, 0.1192, 1.01925, 1.9395, 0.11, 0.29605,
  2.2698, 0.2315, 2.9898, 0.51655, 0.6621];
const FSRS_FACTOR = 19 / 81, FSRS_DECAY = -0.5, RETENTION = 0.9;

function fsrsInitDifficulty(g) {
  return Math.min(10, Math.max(1,
    FSRS_W[4] - Math.exp(FSRS_W[5] * (g - 1)) + 1));
}
function fsrsRetrievability(stability, elapsedDays) {
  if (!stability || stability <= 0) return 0;
  return Math.pow(1 + FSRS_FACTOR * (elapsedDays / stability),
                  FSRS_DECAY);
}
function fsrsInterval(stability) {
  const days = (stability / FSRS_FACTOR) *
    (Math.pow(RETENTION, 1 / FSRS_DECAY) - 1);
  return Math.max(1, Math.round(days));
}
function fsrsReview(st, grade, now) {
  const w = FSRS_W;
  if (!st || st.stability == null) {
    const s = w[grade - 1];
    return { stability: s, difficulty: fsrsInitDifficulty(grade),
             state: "Review", reps: 1, lapses: 0,
             due: new Date(now.getTime() + fsrsInterval(s) * 864e5)
                    .toISOString(),
             last_review: now.toISOString(),
             scheduled_days: fsrsInterval(s) };
  }
  const last = new Date(st.last_review || now);
  const elapsed = Math.max(0, (now - last) / 864e5);
  const R = fsrsRetrievability(st.stability, elapsed);
  const dPrime = st.difficulty +
    (-w[6] * (grade - 3)) * (10 - st.difficulty) / 9;
  const dTarget = fsrsInitDifficulty(4);
  let dNew = w[7] * dTarget + (1 - w[7]) * dPrime;
  dNew = Math.min(10, Math.max(1, dNew));
  let sNew;
  if (grade === 1) {
    sNew = w[11] * Math.pow(dNew, -w[12]) *
      (Math.pow(st.stability + 1, w[13]) - 1) *
      Math.exp(w[14] * (1 - R));
    st.lapses = (st.lapses || 0) + 1;
  } else {
    const hard = grade === 2 ? w[15] : 1;
    const easy = grade === 4 ? w[16] : 1;
    sNew = st.stability * (Math.exp(w[8]) * (11 - dNew) *
      Math.pow(st.stability, -w[9]) *
      (Math.exp(w[10] * (1 - R)) - 1) * hard * easy + 1);
  }
  const interval = fsrsInterval(sNew);
  return { stability: sNew, difficulty: dNew, state: "Review",
           reps: (st.reps || 0) + 1, lapses: st.lapses || 0,
           due: new Date(now.getTime() + interval * 864e5)
                  .toISOString(),
           last_review: now.toISOString(),
           scheduled_days: interval };
}

/* ---------------- SM-2 (the core baseline, rule-for-rule) */
function sm2Review(st, quality, now) {
  st = st || { repetitions: 0, easiness: 2.5, interval_days: 0 };
  let ef = st.easiness + (0.1 - (5 - quality) *
    (0.08 + (5 - quality) * 0.02));
  ef = Math.max(1.3, ef);
  let reps, interval;
  if (quality < 3) { reps = 0; interval = 1; }
  else {
    reps = st.repetitions + 1;
    interval = reps === 1 ? 1 : reps === 2 ? 6 :
      Math.round(st.interval_days * ef);
  }
  return { repetitions: reps, easiness: Math.round(ef * 1e4) / 1e4,
           interval_days: interval,
           due: new Date(now.getTime() + interval * 864e5)
                  .toISOString() };
}

/* ---------------- pure helpers (unit-tested) */
// #4214: the plan advances with the calendar. day_index counts
// whole days since the bundle's plan_start (stamped by
// build_data.py), clamped to the plan's length — the Today view
// is computed at open, never frozen at build time.
function computeDayIndex(planStartIso, totalSessions, now) {
  if (!planStartIso || !totalSessions) return 0;
  const start = new Date(planStartIso + "T00:00:00");
  const days = Math.floor((now - start) / 864e5);
  const maxDay = Math.ceil(totalSessions / 2) - 1;
  return Math.max(0, Math.min(days, maxDay));
}
// Mirror of the core's render_today_view grouping: flatten the
// plan's sessions in order, two per day.
function todaySessions(plan, dayIndex) {
  const all = [];
  for (const w of plan.weeks || []) {
    for (const s of w.sessions || []) all.push({ week: w.week, ...s });
  }
  return all.slice(dayIndex * 2, dayIndex * 2 + 2);
}
// #4218: the SR queue is DUE-AWARE. A card is due when it has no
// stored state for the active scheduler, or its stored due date
// has arrived. Queue order: earliest due first (new cards count
// as due now). Graded cards leave the queue until their due
// date — they never recycle inside a session.
function dueQueue(cards, srState, scheduler, now) {
  const suffix = scheduler === "sm2" ? ":sm2" : "";
  const due = [];
  for (const card of cards) {
    const st = srState[card.card_id + suffix];
    if (!st || !st.due || new Date(st.due) <= now) {
      due.push({ card, dueAt: st && st.due ? new Date(st.due) : now });
    }
  }
  due.sort((a, b) => a.dueAt - b.dueAt);
  return due.map((d) => d.card);
}
function nextDueDate(cards, srState, scheduler) {
  const suffix = scheduler === "sm2" ? ":sm2" : "";
  let best = null;
  for (const card of cards) {
    const st = srState[card.card_id + suffix];
    if (st && st.due && (!best || st.due < best)) best = st.due;
  }
  return best;
}

/* ---------------- loading + rendering */
async function load() {
  const resp = await fetch("data/state.json");
  state.data = await resp.json();
  const saved = localStorage.getItem("studysprint-sr");
  if (saved) state.srState = JSON.parse(saved);
  $("#course-name").textContent = state.data.course;
  $("#surface-version").textContent =
    state.data.surface_version || "0.1.0";
  renderToday(); renderPlan(); renderReader(); showCard();
}

function renderToday() {
  const plan = state.data.plan || {};
  const total = plan.total_sessions ||
    (plan.weeks || []).reduce((n, w) => n + (w.sessions || []).length, 0);
  const dayIndex = computeDayIndex(state.data.plan_start, total,
                                   new Date());
  const sessions = todaySessions(plan, dayIndex);
  // #4216: the bundled course is a sample until the student's own
  // syllabus is ingested — say so on the first screen, not in a
  // build script's README.
  const disclosure = $("#sample-disclosure");
  if (disclosure) {
    const isSample = /sample/i.test(state.data.course || "");
    disclosure.textContent = isSample ?
      "This is the bundled sample course. Make it yours: add " +
      "your own syllabus in the Ingest tab." : "";
    disclosure.classList.toggle("hidden", !isSample);
  }
  // #4215: check-ins PERSIST (localStorage, keyed by date +
  // session) and a missed session shifts — the no-guilt promise
  // in the core's hint text, honored by the surface.
  const todayKey = new Date().toISOString().slice(0, 10);
  const checkins = JSON.parse(
    localStorage.getItem("ss.checkins") || "{}");
  const mine = checkins[todayKey] || {};
  $("#today-summary").textContent = sessions.length ?
    `Today (day ${dayIndex + 1}): ${sessions.length} session(s). ` +
    `First up: ${sessions[0].kind} — ${sessions[0].topic} ` +
    `(${sessions[0].minutes} min)` :
    "Nothing scheduled today.";
  $("#today-sessions").innerHTML = sessions.map((s, i) => {
    const mark = mine[i];
    const shifted = mark === "missed" ?
      ` <em>(shifted to tomorrow — no guilt)</em>` : "";
    const done = mark ? ` — checked in: ${mark}` : "";
    return `<div class="session"><span>${s.kind}: ${s.topic} ` +
      `(${s.minutes} min)${done}${shifted}</span>` +
      `<span class="row">` +
      `<button data-checkin="done" data-i="${i}">Done</button>` +
      `<button data-checkin="partial" data-i="${i}">Partly</button>` +
      `<button data-checkin="missed" data-i="${i}">Missed</button>` +
      `</span></div>`;
  }).join("");
  document.querySelectorAll("[data-checkin]").forEach((b) =>
    b.addEventListener("click", () => {
      const all = JSON.parse(
        localStorage.getItem("ss.checkins") || "{}");
      const day = all[todayKey] || {};
      day[b.dataset.i] = b.dataset.checkin;
      all[todayKey] = day;
      localStorage.setItem("ss.checkins", JSON.stringify(all));
      $("#checkin-status").textContent =
        `Checked in: ${b.dataset.checkin} ` +
        `(session ${Number(b.dataset.i) + 1}) — recorded.` +
        (b.dataset.checkin === "missed" ?
          " Shifted to tomorrow, without guilt." : "");
      renderToday();
    }));
}

function renderPlan() {
  const plan = state.data.plan;
  $("#plan-body").innerHTML = (plan.weeks || []).map((w) =>
    `<h4>Week ${w.week} (due: ${w.due})</h4><ul>` +
    w.sessions.map((s) =>
      `<li>${s.kind}: ${s.topic} (${s.minutes} min)</li>`).join("") +
    "</ul>").join("");
  $("#receipt-body").textContent =
    JSON.stringify(state.data.trust_receipt, null, 2);
}

/* ---------------- reader (RSVP) */
function renderReader(sectionIndex) {
  const sections = state.data.reader.sections;
  if (!sections.length) return;
  // #4217: EVERY shipped section is reachable — a picker plus
  // prev/next, not just the first section forever.
  const i = Math.max(0, Math.min(sectionIndex || 0,
                                 sections.length - 1));
  state.reader = { section: sections[i], index: 0, sectionIndex: i };
  const picker = $("#reader-section-select");
  if (picker) {
    picker.innerHTML = sections.map((s, j) =>
      `<option value="${j}"${j === i ? " selected" : ""}>` +
      `${s.chapter} — ${s.title}</option>`).join("");
  }
  $("#reader-section").textContent =
    `${sections[i].chapter} — ${sections[i].title} ` +
    `(section ${i + 1} of ${sections.length})`;
  $("#reader-word").textContent = "Press Start";
}
function readerStep() {
  const r = state.reader;
  if (!r) return;
  if (r.index >= r.section.words.length) {
    $("#reader-word").textContent = "Section done. Nice reading.";
    stopPlay(); return;
  }
  $("#reader-word").textContent = r.section.words[r.index++];
}
function stopPlay() {
  state.playing = false;
  if (state.timer) { clearInterval(state.timer); state.timer = null; }
}

/* ---------------- SR review */
function currentCard() {
  const queue = dueQueue(state.data.sr.cards, state.srState,
                         state.scheduler, new Date());
  return queue.length ? queue[state.cardIndex % queue.length] : null;
}
function showCard() {
  const card = currentCard();
  const total = state.data.sr.cards.length;
  if (!card) {
    // nothing due: say when the next card arrives instead of
    // recycling a graded card inside the same session (#4218)
    const next = nextDueDate(state.data.sr.cards, state.srState,
                             state.scheduler);
    $("#sr-front").textContent = next ?
      `All caught up — next card due ${next.slice(0, 10)}.` :
      "No cards in this deck yet.";
    $("#sr-back").classList.add("hidden");
    return;
  }
  const queue = dueQueue(state.data.sr.cards, state.srState,
                         state.scheduler, new Date());
  state.flipped = false;
  $("#sr-front").textContent =
    `Card ${state.cardIndex % queue.length + 1} of ${queue.length} ` +
    `due (${total} in deck): ${card.front}`;
  $("#sr-back").classList.add("hidden");
}
function grade(gradeValue) {
  const card = currentCard();
  if (!card) return;  // nothing due — grading is a no-op (#4218)
  const now = new Date();
  const key = card.card_id;
  let receipt;
  if (state.scheduler === "fsrs") {
    const ux = (state.data.sr.ux_state.cards.find(
      (c) => c.card_id === key) || {}).ts_fsrs || {};
    const prev = state.srState[key] ||
      (ux.stability != null ? ux : null);
    const next = fsrsReview(prev, gradeValue, now);
    state.srState[key] = next;
    receipt = `Receipt: scheduler=fsrs grade=${gradeValue} ` +
      `next due ${next.due.slice(0, 10)} ` +
      `(in ${next.scheduled_days} day(s))`;
  } else {
    const quality = { 1: 1, 2: 3, 3: 4, 4: 5 }[gradeValue];
    const prev = state.srState[key + ":sm2"] || null;
    const next = sm2Review(prev, quality, now);
    state.srState[key + ":sm2"] = next;
    receipt = `Receipt: scheduler=sm2 grade=${gradeValue} ` +
      `next due ${next.due.slice(0, 10)} ` +
      `(in ${next.interval_days} day(s))`;
  }
  localStorage.setItem("studysprint-sr",
                       JSON.stringify(state.srState));
  $("#sr-receipt").textContent = receipt;
  state.cardIndex = 0;  // the graded card left the due queue
  showCard();
}

/* ---------------- wiring */
document.querySelectorAll(".tab").forEach((tab) =>
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) =>
      t.classList.toggle("active", t === tab));
    document.querySelectorAll(".view").forEach((v) =>
      v.classList.add("hidden"));
    $("#view-" + tab.dataset.view).classList.remove("hidden");
  }));
$("#sr-flip").addEventListener("click", () => {
  $("#sr-back").textContent = currentCard().back;
  $("#sr-back").classList.remove("hidden");
  state.flipped = true;
});
document.querySelectorAll("[data-grade]").forEach((b) =>
  b.addEventListener("click", () => grade(Number(b.dataset.grade))));
$("#sr-scheduler").addEventListener("change", (e) => {
  state.scheduler = e.target.value;
});
$("#reader-start").addEventListener("click", () => {
  if (state.reader) state.reader.index = 0;
  readerStep();
});
$("#reader-step").addEventListener("click", readerStep);
$("#reader-rewind").addEventListener("click", () => {
  if (state.reader)
    state.reader.index = Math.max(0, state.reader.index - 10);
  readerStep();
});
$("#reader-play").addEventListener("click", () => {
  if (state.playing) { stopPlay(); return; }
  state.playing = true;
  state.timer = setInterval(readerStep, 240);
});
$("#reader-section-select").addEventListener("change", (e) => {
  stopPlay();
  renderReader(Number(e.target.value));
});
$("#reader-prev").addEventListener("click", () => {
  if (state.reader) {
    stopPlay();
    renderReader(state.reader.sectionIndex - 1);
  }
});
$("#reader-next").addEventListener("click", () => {
  if (state.reader) {
    stopPlay();
    renderReader(state.reader.sectionIndex + 1);
  }
});
// ------------------------------------------------------------ ingest
// Build D leg 3: the web surface of the one core ingestion path.
// Text files parse in-browser with the same conservative line
// grammar as study_pipeline.parse_syllabus_text; placement is
// CONFIRM-GATED (records sit in ss.ingest.pending until the
// student confirms). Photographs are captured and recorded as
// awaiting core OCR — OCR runs in the core pipeline, not in the
// browser, and this surface says so rather than faking it.
const WEEKDAYS = { mon: "Mon", monday: "Mon", tue: "Tue", tues: "Tue",
  tuesday: "Tue", wed: "Wed", wednesday: "Wed", thu: "Thu",
  thur: "Thu", thurs: "Thu", thursday: "Thu", fri: "Fri",
  friday: "Fri", sat: "Sat", saturday: "Sat", sun: "Sun",
  sunday: "Sun" };

function parseSyllabus(text) {
  const classes = [], assessments = [];
  let course = null;
  const to24 = (h, m, ap) => {
    h = Number(h); m = Number(m);
    if (ap) { if (ap.toLowerCase() === "pm" && h !== 12) h += 12;
      if (ap.toLowerCase() === "am" && h === 12) h = 0; }
    return String(h).padStart(2, "0") + ":" + String(m).padStart(2, "0");
  };
  for (const raw of String(text || "").split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) continue;
    const cm = line.match(/\b([A-Z]{2,4})\s*(\d{2,4}[A-Z]?)\b/);
    if (cm) course = cm[1] + " " + cm[2];
    const days = (line.match(/[A-Za-z]+/g) || [])
      .map((t) => WEEKDAYS[t.toLowerCase()]).filter(Boolean);
    const tr = line.match(/(\d{1,2}):(\d{2})\s*([AaPp][Mm])?\s*[-–]\s*(\d{1,2}):(\d{2})\s*([AaPp][Mm])?/);
    if (days.length && tr) {
      classes.push({ course, days,
        start: to24(tr[1], tr[2], tr[3] || tr[6]),
        end: to24(tr[4], tr[5], tr[6] || tr[3]) });
      continue;
    }
    const km = line.match(/\b(quiz|midterm|final)\b/i);
    const dm = line.match(/\b(20\d{2})-(\d{2})-(\d{2})\b/);
    if (km && dm) {
      assessments.push({ course, kind: km[1].toLowerCase(),
        date: dm[0] });
    }
  }
  return { classes, assessments };
}

function renderIngestPreview(parsed, sourceName) {
  const el = $("#ingest-preview");
  el.textContent = "Parsed " + sourceName + ": " +
    parsed.classes.length + " class meeting(s), " +
    parsed.assessments.length + " assessment(s). " +
    "Not placed yet — review, then confirm placement.";
  $("#ingest-confirm").classList.remove("hidden");
}

$("#ingest-file").addEventListener("change", (e) => {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    const parsed = parseSyllabus(reader.result);
    localStorage.setItem("ss.ingest.pending",
      JSON.stringify({ source: file.name, parsed,
        captured_at: new Date().toISOString() }));
    renderIngestPreview(parsed, file.name);
  };
  reader.readAsText(file);
});

$("#ingest-camera").addEventListener("change", (e) => {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  const captures = JSON.parse(
    localStorage.getItem("ss.ingest.captures") || "[]");
  captures.push({ name: file.name, size: file.size,
    captured_at: new Date().toISOString(),
    status: "awaiting-core-ocr" });
  localStorage.setItem("ss.ingest.captures",
    JSON.stringify(captures));
  $("#ingest-status").textContent = "Photograph captured (" +
    file.name + "). OCR runs in the core pipeline — this capture " +
    "is recorded as awaiting-core-ocr, not parsed in the browser.";
});

$("#ingest-confirm").addEventListener("click", () => {
  const pending = localStorage.getItem("ss.ingest.pending");
  if (!pending) return;
  localStorage.setItem("ss.ingest.placed", pending);
  localStorage.removeItem("ss.ingest.pending");
  $("#ingest-confirm").classList.add("hidden");
  $("#ingest-status").textContent =
    "Placed. The confirmed records are stored locally " +
    "(ss.ingest.placed) for the calendar.";
});

load();
