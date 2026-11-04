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
const escapeHtml = (s) => String(s ?? "")
  .replace(/&/g, "&amp;").replace(/</g, "&lt;")
  .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const state = { data: null, cardIndex: 0, flipped: false,
                scheduler: "fsrs", srState: {}, reader: null,
                playing: false, timer: null,
                activeCourse: null, bundles: [] };

// Per-course persistence keys (iteration 3, #4416): the active
// course namespaces its SR state + check-ins; the pre-0.4.0
// global keys are adopted once by the first bundled course.
function srKey() {
  return courseStorageKey("studysprint-sr", state.activeCourse);
}
function checkinKey() {
  return courseStorageKey("ss.checkins", state.activeCourse);
}

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

/* ---------------- memory methods (iteration 2, #4415) */
// Ports of the core's study_memory scorers, rule-for-rule, over
// the build-time bundle in state.memory (palace + Feynman
// evidence assembled by web/build_data.py from the real core).
// The claims ceilings travel with the methods, as in the core.
const LEITNER_INTERVALS = { 1: 1, 2: 2, 3: 4, 4: 7, 5: 14 };
function leitnerReview(st, grade, now) {
  const box = st && st.box ? st.box : 1;
  let newBox, plain;
  if (grade === 1) {
    newBox = Math.min(5, box + 1);
    plain = newBox === 5 && box === 5 ?
      "You knew this one in the top box — it stays in box 5 " +
      "and comes back in 14 days." :
      `You knew this one — it moves up to box ${newBox} and ` +
      `comes back in ${LEITNER_INTERVALS[newBox]} days.`;
  } else {
    newBox = 1;
    plain = "Missed — no problem, it goes back to box 1 and " +
      "comes back tomorrow. That's how the boxes work.";
  }
  return { box: newBox,
           due: new Date(now.getTime() +
             LEITNER_INTERVALS[newBox] * 864e5).toISOString(),
           interval_days: LEITNER_INTERVALS[newBox],
           plain_language: plain };
}
function walkScore(placed, recalled) {
  // Mirror of study_memory.walk_review: ORDERED recall.
  let inPosition = 0;
  for (let i = 0; i < placed.length; i++) {
    if (i < recalled.length && recalled[i] === placed[i]) inPosition++;
  }
  const placedSet = new Set(placed);
  const recalledPlaced = recalled.filter((r) => placedSet.has(r)).length;
  const missed = placed.filter((p) => !recalled.includes(p));
  return { placed: placed.length, correct_in_position: inPosition,
           recalled_out_of_order: Math.max(0, recalledPlaced - inPosition),
           missed,
           ordered_recall: placed.length ?
             Math.round(inPosition / placed.length * 1000) / 1000 : null };
}
const FEYNMAN_STOP = new Set(["the", "a", "an", "of", "to", "in",
  "is", "are", "and", "or", "it", "its", "that", "this", "by",
  "for", "on", "as", "be", "with", "from"]);
function memoryTokens(text) {
  const out = new Set();
  for (const t of String(text).toLowerCase().match(/[a-z0-9']+/g) || []) {
    if (!FEYNMAN_STOP.has(t) && t.length > 2) out.add(t);
  }
  return out;
}
function explainBack(topic, explanation, evidenceTexts) {
  // Mirror of study_memory.explain_back: key-term coverage
  // against VERIFIED evidence only; none -> abstain.
  const texts = (evidenceTexts || []).filter((t) => t && t.trim());
  if (!texts.length) {
    return { verdict: "abstain", coverage: null, missing_terms: [],
             reason: "no verified evidence for this topic; " +
                     "nothing to grade against" };
  }
  const keyTerms = new Set();
  for (const t of texts) for (const tok of memoryTokens(t)) keyTerms.add(tok);
  const used = memoryTokens(explanation);
  const covered = [...keyTerms].filter((t) => used.has(t));
  const coverage = keyTerms.size ?
    Math.round(covered.length / keyTerms.size * 1000) / 1000 : 0;
  const missing = [...keyTerms].filter((t) => !used.has(t)).sort();
  if (coverage < 0.5) {
    return { verdict: "escalate", coverage, missing_terms: missing,
             guidance: "re-read the verified source, then explain " +
                       "again covering the missing terms" };
  }
  return { verdict: "graded", coverage, missing_terms: missing,
           guidance: "solid coverage of the verified evidence" };
}
function coreRetrievability(stability, elapsedDays) {
  // study_memory.fsrs_retrievability: R = (1 + (19/81) * t/S) ** -0.5
  if (stability === null || stability === undefined || stability <= 0) {
    return 0;
  }
  return Math.pow(1 + (19 / 81) * (elapsedDays / stability), -0.5);
}
function interleaveOrder(items) {
  // Mirror of study_memory.interleave_sessions' rotation:
  // round-robin across topics, never the same topic twice in a
  // row when avoidable; deterministic, receipt-reproducible.
  const queues = {};
  for (const it of items) {
    (queues[it.topic] = queues[it.topic] || []).push(it);
  }
  const topics = Object.keys(queues).sort();
  const out = [];
  let last = null;
  while (topics.some((t) => queues[t].length)) {
    let chosen = null;
    for (const t of topics) {
      if (!queues[t].length) continue;
      if (chosen === null) { chosen = t; continue; }
      const tScore = [t === last ? 1 : 0, -queues[t].length];
      const cScore = [chosen === last ? 1 : 0, -queues[chosen].length];
      if (tScore[0] < cScore[0] ||
          (tScore[0] === cScore[0] && tScore[1] < cScore[1])) {
        chosen = t;
      }
    }
    out.push(queues[chosen].shift());
    last = chosen;
  }
  return out;
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
function stateSuffix(scheduler) {
  return scheduler === "sm2" ? ":sm2" :
    scheduler === "leitner" ? ":leitner" : "";
}
function dueQueue(cards, srState, scheduler, now) {
  const suffix = stateSuffix(scheduler);
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
  const suffix = stateSuffix(scheduler);
  let best = null;
  for (const card of cards) {
    const st = srState[card.card_id + suffix];
    if (st && st.due && (!best || st.due < best)) best = st.due;
  }
  return best;
}

function buildPlanPort(doc, minutesPerDay) {
  // Mirror of core build_study_plan (study_tools): each topic
  // gets a learn block (minutesPerDay, default 45) + a retrieve
  // block (max(15, minutesPerDay // 3)). Battery-pinned to the
  // core in tests/test_iteration3_courses.py.
  const mpd = minutesPerDay || 45;
  const weeks = (doc.weeks || []).map((w) => {
    const sessions = [];
    (w.topics || []).forEach((topic) => {
      sessions.push({ topic: topic, kind: "learn", minutes: mpd });
      sessions.push({ topic: topic, kind: "retrieve",
                      minutes: Math.max(15, Math.floor(mpd / 3)) });
    });
    return { week: w.week, due: w.due, sessions: sessions };
  });
  return { course: doc.course, weeks: weeks,
           total_sessions: weeks.reduce(
             (n, w) => n + w.sessions.length, 0) };
}

function examCountdownPort(doc, todayIso) {
  // Mirror of core exam_countdown (study_courses): unset without
  // an exam_date (no invented deadline); milestones at 14/7/3/0
  // days with the core's labels; pace = total sessions over the
  // days remaining. Battery-pinned in the iteration-3 tests.
  const plan = buildPlanPort(doc);
  const base = { course: doc.course,
                 exam_date: doc.exam_date || null,
                 total_sessions: plan.total_sessions };
  if (!doc.exam_date) {
    return { ...base, days_remaining: null, weeks_remaining: null,
             urgency: "unset", milestones: [], pace: null };
  }
  const exam = new Date(doc.exam_date + "T00:00:00Z");
  const today = new Date(todayIso + "T00:00:00Z");
  const days = Math.round((exam - today) / 86400000);
  const urgency = days < 0 ? "past" : days === 0 ? "today" :
    days <= 7 ? "near" : "ahead";
  const milestones = [[14, "final review begins"],
                      [7, "mock exam week"],
                      [3, "light review only"],
                      [0, "EXAM"]].map(([offset, label]) => {
    const when = new Date(exam - offset * 86400000);
    return { label: `${doc.course}: ${label}`,
             date: when.toISOString().slice(0, 10),
             days_before_exam: offset,
             reached: when <= today };
  });
  const pace = days > 0 ?
    { sessions_remaining: plan.total_sessions,
      days_remaining: days,
      sessions_per_day: Math.round(
        plan.total_sessions / days * 100) / 100 } : null;
  return { ...base, days_remaining: days,
           weeks_remaining: Math.round(days / 7 * 10) / 10,
           urgency: urgency, milestones: milestones, pace: pace };
}

function courseStorageKey(base, course) {
  // Per-course persistence (iteration 3): SR state and check-ins
  // live under the course's own key -- one course's progress is
  // never another's. Isolation-pinned in the iteration-3 tests.
  return base + "::" + (course || "");
}

function bundleFromSyllabusPort(doc) {
  // A user course created on the surface from its syllabus doc:
  // plan + countdown from the ports above, reader sections as
  // honest per-topic stubs (the build_data rule: a stub naming
  // the topic, never another topic's content), SR empty until
  // cards are ingested, calendar/memory unbound until a bundle
  // build -- each absence is the view's own honest empty state.
  const sections = [];
  (doc.weeks || []).forEach((w) => (w.topics || []).forEach(
    (topic) => sections.push({
      title: topic, chapter: `Week ${w.week}`,
      text: `Week ${w.week} covers ${topic}. The full reading ` +
        `for this topic arrives with the course text at ` +
        `ingest; the plan, checks and reviews for it are live ` +
        `now.`,
      words: 0 })));
  return { course: doc.course, syllabus: doc,
           plan: buildPlanPort(doc), today: null,
           trust_receipt: null,
           sr: { cards: [], ux_state: null },
           reader: { sections: sections },
           calendar_geo: null, calendar_error: null,
           memory: null, custom: true };
}

/* ---------------- hardening ports (iteration 4, #4417)
   Browser ports of study_hardening.py, battery-pinned to the
   core in tests/test_iteration4_hardening_terms.py. The claims
   ceilings are the core's, verbatim. Hardening is OPT-IN ONLY:
   without the opt-in the plan port returns the core's refusal
   shape and no drill exists. */
const HARDENING_CEILING =
  "performance under stress/anxiety — not recall gains";
const RECALL_CEILING =
  "context effects are modest (encoding specificity, meta " +
  "d~0.28): varied-context practice + mental reinstatement, " +
  "not single-room matching";
const DEFAULT_CONTEXTS = [
  { place: "library desk", time_of_day: "morning",
    materials: "paper + pen" },
  { place: "kitchen table", time_of_day: "evening",
    materials: "laptop" },
  { place: "campus bench", time_of_day: "afternoon",
    materials: "phone cards" },
  { place: "quiet room", time_of_day: "morning",
    materials: "printed notes" },
];
const PRESSURE_MENU = [
  "visible countdown",
  "ambient exam-hall sounds",
  "strict per-question pacing",
  "one mid-drill interruption card",
  "unfamiliar room (or a picture of one)",
];
const SIT_PHASES = [
  { phase: 1, name: "conceptualization", timed: false,
    pressure: [],
    brief: "Learn the drill format. No clock, no pressure — " +
           "just see how it works." },
  { phase: 2, name: "rehearsal", timed: true, pressure: [],
    brief: "Timed, calm. Practice the skills: pacing, " +
           "breathing, moving on from a hard question." },
  { phase: 3, name: "application", timed: true,
    pressure: "graduated",
    brief: "Timed with exam-like pressure elements, added " +
           "one at a time. The drill is practice — nothing " +
           "here can hurt your grade." },
];
function variedContextPlanPort(sessions, contexts) {
  const ctxs = (contexts || DEFAULT_CONTEXTS).slice();
  if (sessions <= 0 || !ctxs.length) return { assignments: [] };
  const stride = ctxs.length > 2 ? 2 : 1;
  const assignments = [];
  let lastPlace = null, idx = 0;
  for (let i = 0; i < sessions; i++) {
    let ctx = ctxs[idx % ctxs.length];
    if (ctx.place === lastPlace && ctxs.length > 1) {
      idx += 1; ctx = ctxs[idx % ctxs.length];
    }
    assignments.push({ session: i + 1, ...ctx });
    lastPlace = ctx.place; idx += stride;
  }
  return { assignments, claims_ceiling: RECALL_CEILING };
}
function reinstatementScriptPort(examRoom, course) {
  return { course, exam_room: examRoom, steps: [
    `Close your eyes. Picture ${examRoom} — the door, the ` +
    "clock, where you will sit.",
    "Hear the room: paper, chairs, the invigilator's voice.",
    `Now picture the first ${course} question arriving, and ` +
    "yourself starting calmly — you have practiced in many " +
    "rooms, and this one is just another.",
    "Open your eyes. Begin with the question you know best.",
  ], claims_ceiling: RECALL_CEILING };
}
function sha256Hex(ascii) {
  // Compact SHA-256 (FIPS 180-4) — needed so the pressure
  // selection port is bit-identical to the core's seeded pick.
  const K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b,
    0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01,
    0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7,
    0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152,
    0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
    0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819,
    0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08,
    0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f,
    0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];
  const H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
             0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
  const bytes = [];
  for (let i = 0; i < ascii.length; i++) {
    const c = ascii.charCodeAt(i);
    if (c < 0x80) bytes.push(c);
    else if (c < 0x800) {
      bytes.push(0xc0 | (c >> 6), 0x80 | (c & 0x3f));
    } else {
      bytes.push(0xe0 | (c >> 12), 0x80 | ((c >> 6) & 0x3f),
                 0x80 | (c & 0x3f));
    }
  }
  const bitLen = bytes.length * 8;
  bytes.push(0x80);
  while (bytes.length % 64 !== 56) bytes.push(0);
  for (let i = 7; i >= 0; i--)
    bytes.push(Math.floor(bitLen / Math.pow(2, i * 8)) % 256);
  const rr = (v, n) => (v >>> n) | (v << (32 - n));
  for (let off = 0; off < bytes.length; off += 64) {
    const w = new Array(64);
    for (let t = 0; t < 16; t++)
      w[t] = (bytes[off + t * 4] << 24) | (bytes[off + t * 4 + 1] << 16) |
             (bytes[off + t * 4 + 2] << 8) | bytes[off + t * 4 + 3];
    for (let t = 16; t < 64; t++) {
      const s0 = rr(w[t - 15], 7) ^ rr(w[t - 15], 18) ^ (w[t - 15] >>> 3);
      const s1 = rr(w[t - 2], 17) ^ rr(w[t - 2], 19) ^ (w[t - 2] >>> 10);
      w[t] = (w[t - 16] + s0 + w[t - 7] + s1) | 0;
    }
    let [a, b, c, d, e, f, g, h] = H;
    for (let t = 0; t < 64; t++) {
      const S1 = rr(e, 6) ^ rr(e, 11) ^ rr(e, 25);
      const ch = (e & f) ^ (~e & g);
      const t1 = (h + S1 + ch + K[t] + w[t]) | 0;
      const S0 = rr(a, 2) ^ rr(a, 13) ^ rr(a, 22);
      const mj = (a & b) ^ (a & c) ^ (b & c);
      const t2 = (S0 + mj) | 0;
      h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b;
      b = a; a = (t1 + t2) | 0;
    }
    H[0] = (H[0] + a) | 0; H[1] = (H[1] + b) | 0;
    H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0;
    H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0;
    H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
  }
  return H.map((x) => (x >>> 0).toString(16).padStart(8, "0"))
          .join("");
}
function pressureForPort(drillId, count) {
  const seed = parseInt(sha256Hex(String(drillId)).slice(0, 8), 16);
  const picks = [], seen = new Set();
  let i = 0;
  while (picks.length < Math.min(count, PRESSURE_MENU.length)) {
    const pick = PRESSURE_MENU[(seed + i * 3) % PRESSURE_MENU.length];
    if (!seen.has(pick)) { picks.push(pick); seen.add(pick); }
    i += 1;
  }
  return picks;
}
function planHardeningDrillPort(drillId, phase, optIn) {
  const base = { schema: "studysprint-hardening-receipt/v1",
                 kind: "hardening-plan", drill_id: drillId,
                 opt_in: !!optIn,
                 claims_ceiling: HARDENING_CEILING };
  if (!optIn)
    return { ...base, status: "refused",
             reason: "hardening is opt-in only; this drill " +
                     "was not created" };
  if (![1, 2, 3].includes(phase))
    throw new Error(`SIT phase must be 1, 2, or 3, got ${phase}`);
  const spec = JSON.parse(JSON.stringify(SIT_PHASES[phase - 1]));
  if (spec.pressure === "graduated")
    spec.pressure = pressureForPort(drillId, phase - 1);
  return { ...base, status: "planned", ...spec,
           no_guilt: "pressure carries no penalties; a miss " +
                     "is 'not yet', never a failure" };
}
function drillResultClosePort() {
  return "Drill done. The 'not yet' pile is a study list, " +
         "not a verdict — it gets smaller every round.";
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
  $("#surface-version").textContent =
    state.data.surface_version || "0.1.0";
  initCourses();
}

function renderAll() {
  renderToday(); renderPlan(); renderReader(); showCard();
  renderCalendar(); renderRoutes(); renderMemory();
  renderBookReceipt(); renderAnnotations(); renderHardening();
  const ux = state.data.sr && state.data.sr.ux_state;
  if (ux && ux.generation && ux.generation !== FSRS_GENERATION) {
    $("#sr-receipt").textContent =
      `Scheduler generation mismatch: this app schedules with ` +
      `${FSRS_GENERATION} but the course data was exported as ` +
      `${ux.generation}. Intervals may differ from the core ` +
      `until the bundle is rebuilt.`;
  }
}

function allBundles() {
  // The course set (iteration 3): the bundled courses from the
  // state build + the student's own courses, rebuilt from their
  // stored syllabus docs by the ports on every load.
  const bundled = state.data.courses && state.data.courses.length ?
    state.data.courses : [state.data];
  const customDocs = JSON.parse(
    localStorage.getItem("ss.custom_courses") || "[]");
  return bundled.concat(customDocs.map(bundleFromSyllabusPort));
}

function activateCourse(name, first) {
  // Rebind the surface to one course of the set: the views keep
  // reading state.data.*, which now points at the active bundle;
  // SR state + check-ins load from the course's own keys (the
  // pre-0.4.0 global keys are adopted once, by the first bundled
  // course only -- no other course inherits that progress).
  if (!first && state.activeCourse &&
      state.activeCourse !== name) {
    localStorage.setItem(srKey(), JSON.stringify(state.srState));
  }
  const bundle = state.bundles.find((b) => b.course === name) ||
    state.bundles[0];
  state.activeCourse = bundle.course;
  ["course", "plan", "today", "sr", "reader", "calendar_geo",
   "calendar_error", "memory", "trust_receipt"].forEach((k) => {
    state.data[k] = bundle[k];
  });
  const key = srKey();
  let saved = localStorage.getItem(key);
  if (!saved && bundle === state.bundles[0]) {
    saved = localStorage.getItem("studysprint-sr");
    if (saved) localStorage.setItem(key, saved);
  }
  state.srState = saved ? JSON.parse(saved) : {};
  state.cardIndex = 0;
  localStorage.setItem("ss.active_course", bundle.course);
  $("#course-name").textContent = bundle.course;
  const sel = $("#course-switch");
  if (sel) sel.value = bundle.course;
  const cd = countdownFor(bundle);
  $("#course-countdown").textContent = cd;
  const ics = (state.data.ics_by_course || {})[bundle.course];
  const link = $("#course-ics");
  if (link) {
    if (ics) {
      link.href = URL.createObjectURL(new Blob([ics],
        { type: "text/calendar" }));
      link.classList.remove("hidden");
    } else {
      link.classList.add("hidden");
    }
  }
  renderAll();
}

function countdownFor(bundle) {
  const intake = state.data.courses_intake;
  let cd = null;
  if (intake && !bundle.custom) {
    const row = (intake.courses || []).find(
      (c) => c.course === bundle.course);
    cd = row && row.countdown;
  } else if (bundle.syllabus) {
    cd = examCountdownPort(bundle.syllabus,
      new Date().toISOString().slice(0, 10));
  }
  if (!cd || cd.urgency === "unset") {
    return "exam date unset";
  }
  return `exam ${cd.exam_date} — ${cd.days_remaining} day(s) ` +
    `(${cd.urgency})`;
}

function initCourses() {
  state.bundles = allBundles();
  const sel = $("#course-switch");
  if (sel) {
    sel.innerHTML = state.bundles.map((b) =>
      `<option value="${b.course}">${b.course}</option>`).join("");
    sel.addEventListener("change", () =>
      activateCourse(sel.value, false));
  }
  const savedName = localStorage.getItem("ss.active_course");
  activateCourse(savedName || state.bundles[0].course, true);
  const addBtn = $("#new-course-add");
  if (addBtn) {
    addBtn.addEventListener("click", () => {
      const status = $("#new-course-status");
      let doc = null;
      try {
        doc = JSON.parse($("#new-course-json").value);
      } catch (e) {
        status.textContent = "That is not valid JSON — a course " +
          "is created from its syllabus document.";
        return;
      }
      if (!doc.course || !Array.isArray(doc.weeks) ||
          !doc.weeks.some((w) => (w.topics || []).length)) {
        status.textContent = "A syllabus document needs a " +
          "course name and weeks with topics.";
        return;
      }
      const docs = JSON.parse(
        localStorage.getItem("ss.custom_courses") || "[]");
      docs.push(doc);
      localStorage.setItem("ss.custom_courses",
                           JSON.stringify(docs));
      state.bundles = allBundles();
      if (sel) {
        sel.innerHTML = state.bundles.map((b) =>
          `<option value="${b.course}">${b.course}</option>`).join("");
      }
      activateCourse(doc.course, false);
      status.textContent = `Course created: ${doc.course} — ` +
        "its plan and countdown follow the same core rules " +
        "as the bundled courses, and its progress is stored " +
        "under its own keys. Its .ics export arrives with its " +
        "first bundle build.";
    });
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
    localStorage.getItem(checkinKey()) || "{}");
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
        localStorage.getItem(checkinKey()) || "{}");
      const day = all[todayKey] || {};
      day[b.dataset.i] = b.dataset.checkin;
      all[todayKey] = day;
      localStorage.setItem(checkinKey(), JSON.stringify(all));
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
  renderInterleaved();
}

function renderInterleaved() {
  // Interleaving in the plan view (iteration 2): today's sessions
  // and the due SR cards mixed round-robin across topics — the
  // core's rotation (study_memory.interleave_sessions), so no two
  // consecutive items share a topic when avoidable.
  const el = $("#plan-interleaved");
  if (!el) return;
  const plan = state.data.plan || {};
  const total = plan.total_sessions ||
    (plan.weeks || []).reduce((n, w) => n + (w.sessions || []).length, 0);
  const sessions = todaySessions(plan,
    computeDayIndex(state.data.plan_start, total, new Date()));
  const items = sessions.map((s) => ({
    kind: "session", topic: s.topic,
    label: `${s.kind}: ${s.topic} (${s.minutes} min)` }));
  for (const card of dueQueue(state.data.sr.cards, state.srState,
                               "fsrs", new Date())) {
    items.push({ kind: "card",
                 topic: (card.tags || [])[0] ||
                   (card.source || {}).topic || "sr-cards",
                 label: `review card: ${card.front}` });
  }
  if (!items.length) {
    el.innerHTML = "<p>Nothing to interleave yet today.</p>";
    return;
  }
  const ordered = interleaveOrder(items);
  el.innerHTML = "<h3>Interleaved session — today, mixed by " +
    "topic</h3><ol>" + ordered.map((it) =>
      `<li>[${it.kind}] ${it.label} <em>(${it.topic})</em></li>`).join("") +
    "</ol><p>Rotation is deterministic (the core's rule): work " +
    "the list top to bottom.</p>";
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
    el.textContent = state.data.calendar_error ?
      `The core calendar intake refused this course's calendar: ${state.data.calendar_error}. The course itself is unaffected.` :
      "No calendar loaded for this course yet.";
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

/* ---------------- memory view (iteration 2, #4415) */
function renderMemory() {
  const mem = state.data.memory;
  const palaceEl = $("#palace-body");
  if (!mem || !mem.palace) {
    palaceEl.textContent = "No memory palace in this bundle yet.";
  } else {
    const p = mem.palace;
    palaceEl.innerHTML =
      `<p>Your route (${p.source === "temple-route" ?
        "your campus walk, from the Routes view" :
        "the default route"}), one placed item per stop:</p><ol>` +
      p.placements.map((pl) =>
        `<li>${pl.locus} — <strong>${pl.item}</strong> ` +
        `<em>(${pl.chapter})</em></li>`).join("") + "</ol>" +
      `<p>Claims ceiling: ${p.claims_ceiling}. Evidence: ` +
      `${p.evidence}</p>`;
  }
  const sel = $("#feynman-topic");
  if (sel && mem) {
    sel.innerHTML = (mem.feynman_topics || []).map((t, i) =>
      `<option value="${i}">${t.chapter} — ${t.topic}</option>`).join("");
  }
  renderRetrievability();
}

function renderRetrievability() {
  // The core's rule: fire at R <= 0.9 over the student's own
  // reviewed FSRS cards (stability + last review from the
  // persisted SR state). Unreviewed cards are not threshold
  // cases — the list says so instead of inventing reminders.
  const el = $("#retrievability-body");
  if (!el) return;
  const now = new Date();
  const fired = [];
  let above = 0;
  for (const card of state.data.sr.cards) {
    const st = state.srState[card.card_id];
    if (!st || st.stability === null || st.stability === undefined ||
        !st.last_review) continue;
    const elapsed = Math.max(0,
      (now - new Date(st.last_review)) / 864e5);
    const r = coreRetrievability(st.stability, elapsed);
    if (r <= 0.9) fired.push({ card, r });
    else above++;
  }
  if (!fired.length) {
    el.innerHTML = "<p>No card has fallen to the retrievability " +
      "threshold (R ≤ 0.9) yet" +
      (above ? ` — ${above} reviewed card(s) still above it.` : ".") +
      " Reminders appear here as your reviewed cards fade.</p>";
    return;
  }
  el.innerHTML = fired.map(({ card, r }) =>
    `<div class="session"><span>When this reminder fires, I will ` +
    `picture the answer to: <strong>${card.front}</strong> — ` +
    `then grade myself honestly. (R = ${r.toFixed(3)})</span>` +
    `<span class="row">` +
    [1, 2, 3, 4].map((g) =>
      `<button data-rgrade="${card.card_id}:${g}">${g}</button>`).join("") +
    "</span></div>").join("");
}

function gradeFromReminder(cardId, gradeValue) {
  const card = state.data.sr.cards.find((c) => c.card_id === cardId);
  if (!card) return;
  const next = fsrsReview(state.srState[cardId] || null,
                          gradeValue, new Date());
  state.srState[cardId] = next;
  localStorage.setItem(srKey(),
                       JSON.stringify(state.srState));
  $("#retrievability-status").textContent =
    `Receipt: scheduler=fsrs generation=${FSRS_GENERATION} ` +
    `grade=${gradeValue} via retrievability-notification — ` +
    `next due ${next.due.slice(0, 10)}.`;
  renderRetrievability();
  showCard();
}

/* ---------------- reader (RSVP) */
function allReaderSections() {
  // Course sections + the §1b demonstration book's sections
  // (iteration 4): one picker, the book flagged as book.
  const course = (state.data.reader.sections || []).map(
    (s) => ({ ...s, book: false }));
  const book = ((state.data.book || {}).sections || []).map(
    (s) => ({ ...s, book: true }));
  return course.concat(book);
}
function renderReader(sectionIndex) {
  const sections = allReaderSections();
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
      `${s.book ? "Book — " : ""}${s.chapter} — ${s.title}</option>`).join("");
  }
  $("#reader-section").textContent =
    `${sections[i].chapter} — ${sections[i].title} ` +
    `(section ${i + 1} of ${sections.length})`;
  $("#reader-word").textContent = "Press Start";
  renderReaderText(sections[i]);
}
function renderReaderText(section) {
  // The book section renders its full text with the core's
  // emphasized terms as tap targets (iteration 4, §1b): tap a
  // term -> its glossary definition + index pages + sections
  // expand inline, from the core's tap payload. Course sections
  // stay RSVP-only, as before.
  const el = $("#reader-text");
  const panel = $("#term-panel");
  if (!el) return;
  if (!section.book) {
    el.innerHTML = ""; el.classList.add("hidden");
    if (panel) { panel.innerHTML = ""; panel.classList.add("hidden"); }
    return;
  }
  el.classList.remove("hidden");
  el.innerHTML = (section.segments || []).map((seg) => seg.term
    ? `<button type="button" class="term" data-term="` +
      `${escapeHtml(seg.term.toLowerCase())}">` +
      `${escapeHtml(seg.text)}</button>`
    : escapeHtml(seg.text)).join("");
}
function renderTermPanel(termKey) {
  const panel = $("#term-panel");
  const tap = ((state.data.book || {}).taps || {})[termKey];
  if (!panel || !tap) return;
  panel.classList.remove("hidden");
  panel.innerHTML =
    `<strong>${escapeHtml(tap.term)}</strong> — ` +
    `${escapeHtml(tap.definition)}<br>` +
    `Index pages: ${tap.index_pages.length ? tap.index_pages.join(", ") : "—"} · ` +
    `Appears in: ${tap.sections.map(escapeHtml).join(", ")} ` +
    `(${escapeHtml(tap.chapter)})<br>` +
    `From the book's own Glossary + Index, mined at ingest ` +
    `by the core term bank.`;
  if (panel.scrollIntoView) panel.scrollIntoView();
}
function renderAnnotations() {
  const el = $("#annotations");
  if (!el) return;
  const book = state.data.book || {};
  const anns = book.annotations || [];
  el.innerHTML = `<h3>Annotations (hypothes.is leg)</h3>` +
    (anns.length ? anns.map((a) => {
      const sel = a.target.selector || {};
      return `<div class="annotation"><blockquote>` +
        `${escapeHtml(sel.exact || "")}</blockquote>` +
        `<p>${escapeHtml(a.body[0].value)}</p>` +
        `<p class="meta">Tags: ${(a.tags || []).map(escapeHtml).join(", ")} · ` +
        `model: W3C Web Annotation</p></div>`;
    }).join("") : "<p>No annotations of record.</p>") +
    `<p class="meta">${escapeHtml(book.annotations_note || "")}</p>`;
}
function hardeningOptIn() {
  return localStorage.getItem("ss.hardening.optin") === "1";
}
function renderHardening() {
  const el = $("#hardening-body");
  if (!el) return;
  const optIn = hardeningOptIn();
  const course = state.data.course || "your course";
  const contexts = variedContextPlanPort(6);
  const script = reinstatementScriptPort("the exam room", course);
  el.innerHTML =
    `<p>Adaptive hardening is <strong>opt-in only</strong> — ` +
    `it is ${optIn ? "ON" : "OFF"} on this device. ` +
    `Claims ceiling: ${escapeHtml(HARDENING_CEILING)}. ` +
    `No-guilt binds: pressure never carries penalties; there ` +
    `are no score or penalty fields here.</p>` +
    `<div class="row"><button id="hardening-toggle">` +
    `${optIn ? "Turn hardening off" : "Opt in to hardening"}` +
    `</button></div>` +
    `<h3>Varied-context practice</h3>` +
    `<p class="meta">Ceiling: ${escapeHtml(RECALL_CEILING)}.</p>` +
    `<ul>${contexts.assignments.map((a) =>
      `<li>Session ${a.session}: ${escapeHtml(a.place)} · ` +
      `${escapeHtml(a.time_of_day)} · ${escapeHtml(a.materials)}</li>`).join("")}</ul>` +
    `<h3>Mental reinstatement (exam day)</h3>` +
    `<ol>${script.steps.map((s) => `<li>${escapeHtml(s)}</li>`).join("")}</ol>` +
    `<h3>Plan a drill</h3>` +
    (optIn
      ? `<label>Drill id <input id="hardening-drill-id" value="drill-1"></label> ` +
        `<label>Phase <select id="hardening-phase">` +
        `<option value="1">1 — conceptualization</option>` +
        `<option value="2">2 — rehearsal</option>` +
        `<option value="3">3 — application</option></select></label> ` +
        `<button id="hardening-plan">Plan drill</button>` +
        `<div id="hardening-plan-out" aria-live="polite"></div>`
      : `<p>Opt in above to plan a drill. Without the opt-in, ` +
        `no drill exists — that refusal is the core's own ` +
        `receipt shape.</p>`);
  const toggle = $("#hardening-toggle");
  if (toggle) toggle.addEventListener("click", () => {
    localStorage.setItem("ss.hardening.optin", optIn ? "0" : "1");
    renderHardening();
  });
  const planBtn = $("#hardening-plan");
  if (planBtn) planBtn.addEventListener("click", () => {
    const id = $("#hardening-drill-id").value || "drill-1";
    const phase = Number($("#hardening-phase").value || 1);
    const plan = planHardeningDrillPort(id, phase, true);
    $("#hardening-plan-out").innerHTML =
      `<p><strong>Phase ${plan.phase} — ${escapeHtml(plan.name)}</strong> ` +
      `(${plan.timed ? "timed" : "untimed"})</p>` +
      `<p>${escapeHtml(plan.brief)}</p>` +
      (plan.pressure && plan.pressure.length
        ? `<p>Pressure elements (seeded by the drill id, ` +
          `receipt-reproducible): ${plan.pressure.map(escapeHtml).join(" · ")}</p>`
        : "") +
      `<p class="meta">${escapeHtml(plan.no_guilt)} · ceiling: ` +
      `${escapeHtml(plan.claims_ceiling)}</p>` +
      `<label>Answered <input id="hardening-answered" type="number" value="0" min="0"></label> ` +
      `<label>Not yet <input id="hardening-notyet" type="number" value="0" min="0"></label> ` +
      `<button id="hardening-record">Record result</button>` +
      `<p id="hardening-result" aria-live="polite"></p>`;
    $("#hardening-record").addEventListener("click", () => {
      // The core's result receipt carries answered + not-yet
      // counts and the supportive close — and no score,
      // deduction, or penalty field, by construction.
      $("#hardening-result").textContent = drillResultClosePort();
    });
  });
}
function renderBookReceipt() {
  const el = $("#book-receipt");
  if (!el) return;
  const book = state.data.book || {};
  const c = book.counts || {};
  el.innerHTML = `<h3>Textbook ingest — the demonstration book</h3>` +
    `<p>${escapeHtml(book.source || "")}</p>` +
    `<p>Ingest receipt (core term bank): <strong>${c.terms}` +
    `</strong> terms mined · <strong>${c.with_definitions}` +
    `</strong> with definitions · <strong>${c.with_index_refs}` +
    `</strong> with index refs. Read it in the Reader — tap a ` +
    `highlighted term for its expansion.</p>`;
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
  document.querySelectorAll("[data-leitner]").forEach((b) => {
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
  localStorage.setItem(srKey(),
                       JSON.stringify(state.srState));
  $("#sr-receipt").textContent = receipt;
  state.cardIndex = 0;  // the graded card left the due queue
  showCard();
}

function gradeLeitner(knewIt) {
  // Leitner rotation in SR (iteration 2): the core's box rules —
  // knew it -> up a box, missed -> back to box 1; every receipt
  // explains the move in plain language (study_memory).
  if (!state.data || !state.flipped) return;
  const card = currentCard();
  if (!card) return;
  const now = new Date();
  const prev = state.srState[card.card_id + ":leitner"] || null;
  const next = leitnerReview(prev, knewIt ? 1 : 0, now);
  state.srState[card.card_id + ":leitner"] =
    { box: next.box, due: next.due };
  localStorage.setItem(srKey(),
                       JSON.stringify(state.srState));
  $("#sr-receipt").textContent =
    `Receipt: scheduler=leitner grade=${knewIt ? 1 : 0} — ` +
    `${next.plain_language} (box ${next.box}, ` +
    `next due ${next.due.slice(0, 10)})`;
  state.cardIndex = 0;
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
$("#reader-text").addEventListener("click", (e) => {
  const btn = e.target.closest(".term");
  if (btn) renderTermPanel(btn.dataset.term);
});
$("#sr-flip").addEventListener("click", () => {
  $("#sr-back").textContent = currentCard().back;
  $("#sr-back").classList.remove("hidden");
  state.flipped = true;
  document.querySelectorAll("[data-grade]").forEach((b) => {
    b.disabled = false;
  });
  document.querySelectorAll("[data-leitner]").forEach((b) => {
    b.disabled = false;
  });
});
document.querySelectorAll("[data-grade]").forEach((b) =>
  b.addEventListener("click", () => grade(Number(b.dataset.grade))));
document.querySelectorAll("[data-leitner]").forEach((b) =>
  b.addEventListener("click", () =>
    gradeLeitner(Number(b.dataset.leitner) === 1)));
// Today actions (#4228), delegated so re-renders keep them live.
document.addEventListener("click", (e) => {
  if (!state.data) return;
  const todayKey = new Date().toISOString().slice(0, 10);
  const all = JSON.parse(localStorage.getItem(checkinKey()) || "{}");
  const day = all[todayKey] || {};
  if (e.target.id === "action-start") {
    day.started = "yes";
    all[todayKey] = day;
    localStorage.setItem(checkinKey(), JSON.stringify(all));
    $("#checkin-status").textContent =
      "Started — block 1 is underway. No timer, no pressure.";
  } else if (e.target.id === "action-missed") {
    day[0] = "missed";
    all[todayKey] = day;
    localStorage.setItem(checkinKey(), JSON.stringify(all));
    renderToday();
    $("#checkin-status").textContent =
      "Checked in: missed (session 1) — recorded. " +
      "Shifted to tomorrow, without guilt.";
  }
});
$("#sr-scheduler").addEventListener("change", (e) => {
  state.scheduler = e.target.value;
  // Leitner grades in boxes, not 1–4: swap the grade rows.
  const leitner = state.scheduler === "leitner";
  $("#sr-grades-row").classList.toggle("hidden", leitner);
  $("#sr-leitner-row").classList.toggle("hidden", !leitner);
  state.cardIndex = 0;
  showCard();
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

// ------------------------------------------------------------ memory
// Palace walk: the route is shown one locus at a time and the
// student types what they placed there; scoring is the core's
// walk_review (ordered recall, misses named).
state.walk = null;
$("#walk-start").addEventListener("click", () => {
  const mem = state.data && state.data.memory;
  if (!mem || !mem.palace || !mem.palace.placements.length) return;
  state.walk = { index: 0, recalled: [] };
  $("#walk-receipt").textContent = "";
  renderWalkStep();
});
function renderWalkStep() {
  const placements = state.data.memory.palace.placements;
  const w = state.walk;
  const area = $("#walk-area");
  if (w.index >= placements.length) {
    const placed = placements.map((p) => p.item);
    const s = walkScore(placed, w.recalled);
    $("#walk-receipt").textContent =
      `Walk receipt: placed ${s.placed} · correct in position ` +
      `${s.correct_in_position} · recalled out of order ` +
      `${s.recalled_out_of_order} · ordered recall ` +
      `${s.ordered_recall} · missed: ` +
      `${s.missed.length ? s.missed.join(", ") : "none"}. ` +
      `Ceiling: ${state.data.memory.palace.claims_ceiling}.`;
    area.innerHTML = "";
    state.walk = null;
    return;
  }
  const p = placements[w.index];
  area.innerHTML =
    `<p>Stop ${w.index + 1} of ${placements.length}: ` +
    `<strong>${p.locus}</strong> — what did you place here?</p>` +
    `<input id="walk-input" type="text" autocomplete="off">` +
    `<button id="walk-next">Next stop</button>`;
  $("#walk-next").addEventListener("click", () => {
    state.walk.recalled.push($("#walk-input").value.trim());
    state.walk.index++;
    renderWalkStep();
  });
}
$("#feynman-grade").addEventListener("click", () => {
  const mem = state.data && state.data.memory;
  if (!mem) return;
  const topic = (mem.feynman_topics || [])[
    Number($("#feynman-topic").value || 0)];
  if (!topic) return;
  const r = explainBack(topic.topic, $("#feynman-text").value,
                        [topic.evidence]);
  $("#feynman-result").textContent = r.verdict === "abstain" ?
    `Verdict: abstain — ${r.reason}.` :
    `Verdict: ${r.verdict} · coverage ${r.coverage} of the ` +
    `verified evidence's key terms` +
    (r.missing_terms.length ?
      ` · missing: ${r.missing_terms.slice(0, 12).join(", ")}` +
      (r.missing_terms.length > 12 ? " …" : "") : "") +
    ` · ${r.guidance}. (Key-term coverage against the verified ` +
    `text — not semantic grading.)`;
});
// Retrievability one-tap grades (delegated: rows re-render).
document.addEventListener("click", (e) => {
  const rg = e.target.dataset && e.target.dataset.rgrade;
  if (rg) {
    const [cardId, g] = rg.split(":");
    gradeFromReminder(cardId, Number(g));
  }
});

load();
