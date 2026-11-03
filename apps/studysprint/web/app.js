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

/* ---------------- FSRS (pinned generation: FSRS-6) */
// An in-browser port of the core's PINNED generation (RFP-D1-8
// #4231): FSRS-6, mirroring the py-fsrs Scheduler the core
// constructs in apps/studysprint/study_sr.py with FSRS_PARAMETERS
// pinned, desired retention 0.9 and fuzzing off. The seed export
// stamps its generation; load() warns in the SR view if it ever
// differs from FSRS_GENERATION here, so drift between the surface
// and the core is visible instead of silent. Learning steps (1m,
// 10m) and relearning steps (10m) are the library defaults the core
// uses; interval rounding follows Python's round() (banker's), as
// in the library.
const FSRS_GENERATION = "FSRS-6";
const STATE_SCHEMA_VERSION = "studysprint-state/1";
const FSRS_W = [0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194,
  0.001, 1.8722, 0.1666, 0.796, 1.4835, 0.0614, 0.2629, 1.6483, 0.6014,
  1.8729, 0.5425, 0.0912, 0.0658, 0.1542];
const FSRS_RETENTION = 0.9;
const FSRS_DECAY = -FSRS_W[20];
const FSRS_FACTOR = Math.pow(0.9, 1 / FSRS_DECAY) - 1;
const LEARNING_STEPS_MIN = [1, 10];
const RELEARNING_STEPS_MIN = [10];
const clampD = (d) => Math.min(10, Math.max(1, d));
const clampS = (v) => Math.max(0.001, v);
function pyRound(x) {
  const f = Math.floor(x), d = x - f;
  return d > 0.5 ? f + 1 : d < 0.5 ? f : (f % 2 === 0 ? f : f + 1);
}
function fsrsInitD(grade, clamp = true) {
  const d = FSRS_W[4] - Math.exp(FSRS_W[5] * (grade - 1)) + 1;
  return clamp ? clampD(d) : d;
}
function fsrsRetrievability(stability, elapsedDays) {
  return Math.pow(1 + FSRS_FACTOR * elapsedDays / stability, FSRS_DECAY);
}
function fsrsIntervalDays(stability) {
  const days = pyRound((stability / FSRS_FACTOR) *
    (Math.pow(FSRS_RETENTION, 1 / FSRS_DECAY) - 1));
  return Math.min(36500, Math.max(1, days));
}
function fsrsNextD(difficulty, grade) {
  const arg1 = fsrsInitD(4, false);
  const delta = -FSRS_W[6] * (grade - 3);
  const arg2 = difficulty + (10 - difficulty) * delta / 9;
  return clampD(FSRS_W[7] * arg1 + (1 - FSRS_W[7]) * arg2);
}
function fsrsShortTerm(stability, grade) {
  let inc = Math.exp(FSRS_W[17] * (grade - 3 + FSRS_W[18])) *
    Math.pow(stability, -FSRS_W[19]);
  if (grade >= 2) inc = Math.max(inc, 1);
  return clampS(stability * inc);
}
function fsrsNextS(difficulty, stability, retrievability, grade) {
  let next;
  if (grade === 1) {
    const longTerm = FSRS_W[11] * Math.pow(difficulty, -FSRS_W[12]) *
      (Math.pow(stability + 1, FSRS_W[13]) - 1) *
      Math.exp((1 - retrievability) * FSRS_W[14]);
    const shortTerm = stability / Math.exp(FSRS_W[17] * FSRS_W[18]);
    next = Math.min(longTerm, shortTerm);
  } else {
    const hardPenalty = grade === 2 ? FSRS_W[15] : 1;
    const easyBonus = grade === 4 ? FSRS_W[16] : 1;
    next = stability * (1 + Math.exp(FSRS_W[8]) * (11 - difficulty) *
      Math.pow(stability, -FSRS_W[9]) *
      (Math.exp((1 - retrievability) * FSRS_W[10]) - 1) *
      hardPenalty * easyBonus);
  }
  return clampS(next);
}

function fsrsReview(prev, grade, nowMs) {
  // Mirrors py-fsrs Scheduler.review_card over the UX state shape.
  const s = prev ? { ...prev } : { due: "", stability: null,
    difficulty: null, elapsed_days: 0, scheduled_days: 0, reps: 0,
    lapses: 0, state: "New", last_review: null, step: 0 };
  let cardState = s.state === "New" ? "Learning" : s.state;
  let step = s.state === "New" ? 0 : s.step;
  const daysSince = s.last_review ?
    Math.floor((nowMs - Date.parse(s.last_review)) / 86400000) : null;
  const steps = cardState === "Relearning" ? RELEARNING_STEPS_MIN :
    LEARNING_STEPS_MIN;
  let dueMs;
  if (cardState === "Learning" || cardState === "Relearning") {
    if (s.stability === null || s.difficulty === null) {
      s.stability = clampS(FSRS_W[grade - 1]);
      s.difficulty = fsrsInitD(grade);
    } else if (daysSince !== null && daysSince < 1) {
      s.stability = fsrsShortTerm(s.stability, grade);
      s.difficulty = fsrsNextD(s.difficulty, grade);
    } else {
      const r = fsrsRetrievability(s.stability, daysSince || 0);
      s.stability = fsrsNextS(s.difficulty, s.stability, r, grade);
      s.difficulty = fsrsNextD(s.difficulty, grade);
    }
    if (steps.length === 0 || (step >= steps.length && grade >= 2)) {
      cardState = "Review"; step = null;
      dueMs = nowMs + fsrsIntervalDays(s.stability) * 86400000;
    } else if (grade === 1) {
      step = 0;
      dueMs = nowMs + steps[0] * 60000;
    } else if (grade === 2) {
      if (step === 0 && steps.length === 1) {
        dueMs = nowMs + steps[0] * 1.5 * 60000;
      } else if (step === 0 && steps.length >= 2) {
        dueMs = nowMs + (steps[0] + steps[1]) / 2 * 60000;
      } else {
        dueMs = nowMs + steps[step] * 60000;
      }
    } else if (grade === 3) {
      if (step + 1 === steps.length) {
        cardState = "Review"; step = null;
        dueMs = nowMs + fsrsIntervalDays(s.stability) * 86400000;
      } else {
        step += 1;
        dueMs = nowMs + steps[step] * 60000;
      }
    } else {
      cardState = "Review"; step = null;
      dueMs = nowMs + fsrsIntervalDays(s.stability) * 86400000;
    }
  } else {
    if (daysSince !== null && daysSince < 1) {
      s.stability = fsrsShortTerm(s.stability, grade);
    } else {
      const r = fsrsRetrievability(s.stability, daysSince || 0);
      s.stability = fsrsNextS(s.difficulty, s.stability, r, grade);
    }
    s.difficulty = fsrsNextD(s.difficulty, grade);
    if (grade === 1) {
      s.lapses += 1;
      if (RELEARNING_STEPS_MIN.length === 0) {
        dueMs = nowMs + fsrsIntervalDays(s.stability) * 86400000;
      } else {
        cardState = "Relearning"; step = 0;
        dueMs = nowMs + RELEARNING_STEPS_MIN[0] * 60000;
      }
    } else {
      dueMs = nowMs + fsrsIntervalDays(s.stability) * 86400000;
    }
  }
  s.elapsed_days = daysSince || 0;
  s.scheduled_days = (dueMs - nowMs) / 86400000;
  s.reps += 1;
  s.state = cardState;
  s.step = cardState === "Review" ? null : step;
  s.due = new Date(dueMs).toISOString();
  s.last_review = new Date(nowMs).toISOString();
  return s;
}

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
  // Failure state (#4237): a failed or unparsable state.json used
  // to leave every view empty under a permanent "Loading your
  // course..." -- now the failure is named, explained, retryable.
  try {
    const resp = await fetch("data/state.json");
    if (!resp.ok) {
      throw new Error(`data/state.json answered HTTP ${resp.status}`);
    }
    state.data = await resp.json();
    // Schema discipline (#4470): state written under a
    // different schema_version is refused loudly -- it lands
    // in the named failure state below, never rendered
    // best-effort. An absent version is a pre-discipline
    // bundle and is accepted as legacy: the bundle ships
    // with this reader, so absence means "older", not
    // "foreign".
    const foundSchema = state.data.schema_version;
    if (foundSchema && foundSchema !== STATE_SCHEMA_VERSION) {
      throw new Error(
        `course data schema ${foundSchema} -- this app reads ` +
        `${STATE_SCHEMA_VERSION}. Rebuild or update the app; ` +
        `nothing was rendered from mismatched data`);
    }
  } catch (err) {
    $("#course-name").textContent = "Couldn't load your course data";
    $("#app").insertAdjacentHTML("afterbegin",
      `<section id="load-error"><h3>Something went wrong loading ` +
      `your course</h3><p>${err.message} -- the app data ` +
      `(data/state.json) didn't arrive or didn't parse. Nothing ` +
      `is lost: your saved progress lives in this browser, not ` +
      `in that file.</p>` +
      `<button id="load-retry" class="primary">Retry</button></section>`);
    $("#load-retry").addEventListener("click", () => location.reload());
    return;
  }
  const saved = localStorage.getItem("studysprint-sr");
  if (saved) state.srState = JSON.parse(saved);
  $("#course-name").textContent = state.data.course;
  $("#surface-version").textContent =
    state.data.surface_version || "0.1.0";
  renderToday(); renderPlan(); renderReader(); showCard();
  renderCalendar(); renderRoutes();
  const ux = state.data.sr && state.data.sr.ux_state;
  if (ux && ux.generation && ux.generation !== FSRS_GENERATION) {
    $("#sr-receipt").textContent =
      `Scheduler generation mismatch: this app schedules with ` +
      `${FSRS_GENERATION} but the course data was exported as ` +
      `${ux.generation}. Intervals may differ from the core ` +
      `until the bundle is rebuilt.`;
  }
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
  // The core's designed Today actions ship in state.today.actions
  // and render here (#4228): the primary start, and the subtle
  // no-guilt "I missed this" whose shift the check-ins apply.
  const todayActions = ((state.data.today || {}).actions || [])
    .map((a) => a.style === "primary"
      ? `<button id="action-start" class="primary">${a.label}</button>`
      : `<button id="action-missed">${a.label}</button>`).join("");
  $("#today-sessions").innerHTML =
    (todayActions ? `<div class="row">${todayActions}</div>` : "") +
    sessions.map((s, i) => {
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

/* ---------------- calendar + routes (iteration 1, #4414) */
// The state carries the core assembler's output verbatim
// (study_geo.surface_calendar_geo via build_data.py): classes,
// briefings (ramps + shift notices), the frequency plan,
// quiet-hours probes, locations, routes, the temple route.
// Build-time state, like the rest of the bundle — the surfaces
// that compute live (TUI) say so in their parity statements.
const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
function renderCalendar() {
  const cg = state.data.calendar_geo;
  const el = $("#calendar-body");
  if (!cg) {
    el.textContent = "No calendar loaded for this course yet.";
    return;
  }
  const classes = (cg.classes || []).map((c) =>
    `<li>${c.course}: ${(c.days || []).map((d) => DAY_NAMES[d]).join("/")} ` +
    `${c.start}–${c.end} · ${c.location}</li>`).join("");
  const briefings = (cg.briefings || []).map((b) =>
    `<li>${b.date} ${b.time} · ${b.kind} — ${b.course} · ${b.location} · ` +
    `${b.days_away}d away · ramp ${b.ramp.tier} ×${b.ramp.multiplier}` +
    (b.briefing ? `<br>⚠ ${b.briefing}` : "") + "</li>").join("");
  const freq = Object.entries(cg.frequency_plan || {}).map(([course, f]) =>
    `<li>${course}: ${f.per_day}/day (base ${f.base_per_day} × ` +
    `${f.multiplier}, ${f.tier}` +
    (f.driven_by ? `; driven by ${f.driven_by}` : "") + ")</li>").join("");
  const q = cg.quiet_hours;
  const quiet = q ? (q.batched || []).map((n) =>
      `<li>in-class note ${n.at.slice(11, 16)} → held by ${n.held_by}, ` +
      `released ${n.release_at.slice(11, 16)}</li>`).join("") +
    (q.delivered || []).map((n) =>
      `<li>outside note ${n.at.slice(11, 16)} → delivered</li>`).join("")
    : "<li>no class block in the next 7 days to probe</li>";
  el.innerHTML =
    `<h3>Classes</h3><ul>${classes}</ul>` +
    `<h3>Assessments (nearest first)</h3><ul>${briefings}</ul>` +
    `<h3>Today's question frequency</h3><ul>${freq}</ul>` +
    `<h3>Quiet hours (probed against the class blocks)</h3><ul>${quiet}</ul>` +
    `<p>Ceiling: ${cg.claims_ceiling}</p>`;
}
function renderRoutes() {
  const cg = state.data.calendar_geo;
  const el = $("#routes-body");
  if (!cg) {
    el.textContent = "No calendar loaded — routes need the " +
      "calendar's locations first (see the Calendar view).";
    return;
  }
  const locs = (cg.locations || []).map((r) =>
    `<li>${r.location} — ${(r.used_by || []).join(", ")}</li>`).join("");
  const routes = (cg.routes || []).length ? (cg.routes || []).map((r) =>
    `<li>${r.assessment_kind} (${r.course}) → ${r.destination}: ` +
    `${r.travel_minutes} min walk + ${r.buffer_minutes} buffer · ` +
    `leave by ${r.depart_by.slice(0, 10)} ${r.depart_by.slice(11, 16)} ` +
    `(${r.source})</li>`).join("")
    : "<li>no routes — the calendar carries no coordinates, so " +
      "nothing is drawn or faked</li>";
  const temple = cg.temple_route;
  const templeHtml = temple ?
    `<h3>Temple route (loci over your walk)</h3><ol>` +
    temple.placements.map((p) =>
      `<li>${p.locus} — ${p.item}</li>`).join("") + "</ol>" +
    `<h3>Audio cues</h3><ol>` +
    (cg.audio_cues || []).map((c) => `<li>${c.cue}</li>`).join("") +
    "</ol>"
    : "<p>no waypoints on this calendar</p>";
  el.innerHTML =
    `<h3>Locations</h3><ul>${locs}</ul>` +
    `<h3>Routes from ${cg.origin || "—"}</h3><ul>${routes}</ul>` +
    templeHtml;
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
  // Grading stays locked until the answer is visible (#4234): a
  // grade records recall of an answer the learner has seen.
  document.querySelectorAll("[data-grade]").forEach((b) => {
    b.disabled = true;
  });
  $("#sr-front").textContent =
    `Card ${state.cardIndex % queue.length + 1} of ${queue.length} ` +
    `due (${total} in deck): ${card.front}`;
  $("#sr-back").classList.add("hidden");
}
function grade(gradeValue) {
  // Belt and braces with the disabled buttons (#4234 + #4237):
  // never grade pre-flip, never grade without loaded data.
  if (!state.data || !state.flipped) return;
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
    receipt = `Receipt: scheduler=fsrs generation=${FSRS_GENERATION} grade=${gradeValue} ` +
      `next due ${next.due.slice(0, 10)} ` +
      `(in ${next.scheduled_days} day(s))`;
  } else {
    // SM-2 qualities: the map preserves the core's pass boundary
    // (quality < 3 resets repetitions) --Again 1, Hard 2 (still a
    // reset: it does NOT pass), Good 3 (the bare pass), Easy 5.
    const quality = { 1: 1, 2: 2, 3: 3, 4: 5 }[gradeValue];
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
  document.querySelectorAll("[data-grade]").forEach((b) => {
    b.disabled = false;
  });
});
document.querySelectorAll("[data-grade]").forEach((b) =>
  b.addEventListener("click", () => grade(Number(b.dataset.grade))));
// Today actions (#4228), delegated so re-renders keep them live.
document.addEventListener("click", (e) => {
  if (!state.data) return;
  const todayKey = new Date().toISOString().slice(0, 10);
  const all = JSON.parse(localStorage.getItem("ss.checkins") || "{}");
  const day = all[todayKey] || {};
  if (e.target.id === "action-start") {
    day.started = "yes";
    all[todayKey] = day;
    localStorage.setItem("ss.checkins", JSON.stringify(all));
    $("#checkin-status").textContent =
      "Started — block 1 is underway. No timer, no pressure.";
  } else if (e.target.id === "action-missed") {
    day[0] = "missed";
    all[todayKey] = day;
    localStorage.setItem("ss.checkins", JSON.stringify(all));
    renderToday();
    $("#checkin-status").textContent =
      "Checked in: missed (session 1) — recorded. " +
      "Shifted to tomorrow, without guilt.";
  }
});
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
