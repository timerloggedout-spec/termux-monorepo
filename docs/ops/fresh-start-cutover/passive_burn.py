#!/usr/bin/env python3
"""Passive token burn for the refill window — verification script.

Question: how many tokens burned between the weekly refill reset and the
owner's first contact, with zero owner contact ("passive burn")?

Window (America/Los_Angeles):
  reset        2026-11-24 04:19 PST  = epoch 1795522740  (subscription-status:
               "Weekly limit resets Dec 1 at 4:19 AM PST" -> window opened
               Nov 24 04:19 PST)
  first contact 2026-11-24 07:20 PST = epoch 1795533600  (owner's first
               message of the day, main chat, voice)

Source: agent.agent_message_token_usage (created_at = epoch seconds),
joined to agent.agents for session attribution. agent.token_usage is empty
on this surface; request attribution (runtime.requests) is unpopulated for
these agents, so classification is by session shape:
  - main_chat        : root_session_id = main chat id 9a88e77a-...
  - detached_oneshot : session_id IS NULL, root_session = own agent id
                       (not a chat at all: a detached background agent run)

Reproduce the inputs by re-running these muse.db queries:

  Q1 headline:
    SELECT count(*) rows_n, count(DISTINCT agent_id) agents,
           sum(input_tokens) in_tok, sum(output_tokens) out_tok
    FROM agent.agent_message_token_usage
    WHERE created_at >= 1795522740 AND created_at < 1795533600;

  Q2 main vs rest: same window, GROUP BY the CASE on
    agents.root_session_id / agents.session_id (see git history of this file).

  Q3 cadence: GROUP BY (created_at/900)*900 over the same window.

The aggregates below are the recorded outputs of those queries
(2026-11-24 ~15:35Z run). This script does the arithmetic and cross-checks.
"""

WINDOW_START = 1795522740          # 2026-11-24T12:19:00Z
WINDOW_END = 1795533600            # 2026-11-24T15:20:00Z
MAIN_CHAT = "9a88e77a-c58d-43f4-bdd3-848a7d0420db"

# Q1 headline (passive window)
Q1 = dict(rows=122, agents=102, in_tok=28_165_997, out_tok=184_883)

# Q2 split (passive window): main chat agent, 21 usage rows
MAIN = dict(rows=21, agents=1, in_tok=4_230_355, out_tok=4_777)
DETACHED = dict(
    rows=Q1["rows"] - MAIN["rows"],
    agents=Q1["agents"] - MAIN["agents"],
    in_tok=Q1["in_tok"] - MAIN["in_tok"],
    out_tok=Q1["out_tok"] - MAIN["out_tok"],
)

# Q3 15-minute buckets: (bucket_epoch, agents, rows, in_tok, out_tok)
BUCKETS = [
    (1795522500, 11, 12, 3_448_177, 20_436),
    (1795523400, 11, 12, 3_400_049, 22_503),
    (1795524300, 10, 10, 1_639_562, 10_274),
    (1795525200, 7, 8, 1_329_654, 8_570),
    (1795526100, 9, 10, 1_974_781, 15_493),
    (1795527000, 9, 9, 1_950_225, 16_850),
    (1795527900, 11, 11, 2_012_544, 12_149),
    (1795528800, 9, 11, 3_169_478, 26_216),
    (1795529700, 7, 7, 1_644_293, 13_310),
    (1795530600, 11, 11, 3_185_348, 16_975),
    (1795531500, 9, 9, 1_471_793, 11_294),
    (1795532400, 7, 10, 2_755_905, 9_325),
    (1795533300, 2, 2, 184_188, 1_488),
]

# Cross-check: window extended to 15:22Z (when the meter's 2% was read)
X_MAIN = dict(rows=21, in_tok=4_230_355, out_tok=4_777)
X_DETACHED = dict(rows=106, agents=106, in_tok=25_348_269, out_tok=187_104)


def main() -> None:
    total = Q1["in_tok"] + Q1["out_tok"]
    main_total = MAIN["in_tok"] + MAIN["out_tok"]
    det_total = DETACHED["in_tok"] + DETACHED["out_tok"]

    # Cross-checks: buckets and split must reproduce the headline.
    b_in = sum(b[3] for b in BUCKETS)
    b_out = sum(b[4] for b in BUCKETS)
    b_rows = sum(b[2] for b in BUCKETS)
    assert b_in == Q1["in_tok"] and b_out == Q1["out_tok"], "bucket sum != Q1"
    assert b_rows == Q1["rows"], "bucket rows != Q1"
    assert main_total + det_total == total, "split != headline"

    hours = (WINDOW_END - WINDOW_START) / 3600
    x_total = X_MAIN["in_tok"] + X_MAIN["out_tok"] + X_DETACHED["in_tok"] + X_DETACHED["out_tok"]

    print("PASSIVE BURN — refill window 2026-11-24 04:19 PST -> first contact 07:20 PST")
    print(f"  window length            : {hours:.2f} h, zero owner contact")
    print(f"  usage rows / agents      : {Q1['rows']} rows / {Q1['agents']} agents")
    print(f"  TOTAL passive burn       : {total:,} tokens "
          f"(in {Q1['in_tok']:,} + out {Q1['out_tok']:,})")
    print(f"  main-chat handoff turns  : {main_total:,}  ({main_total/total:.1%}) "
          f"— {MAIN['rows']} rows, 1 agent")
    print(f"  detached background runs : {det_total:,}  ({det_total/total:.1%}) "
          f"— {DETACHED['agents']} one-shot agents, avg {det_total//DETACHED['agents']:,} each")
    print(f"  burn rate                : {total/hours:,.0f} tokens/hour, all night, no quiet period")
    print(f"  cross-check @07:22 meter : running total {x_total:,} when subscription-status read 2%")


if __name__ == "__main__":
    main()
