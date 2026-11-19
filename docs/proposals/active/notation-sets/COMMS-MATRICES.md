# Comms Matrices — transport row: QUIC (worked example)

Competition entry (Linguist lane, owner ruling 2026-11-19).
Target of record: KodeKloud short "QUIC Protocol
Explained: Why HTTP/3 Runs Over UDP"
(youtube.com/shorts/NgWeyDIfbOw) — templated here into
fleet form. The Comms Matrices score comms patterns cell
by cell; this entry works the **transport row**.

## The row

| Cell | Multiplexing | HoL blocking | Handshake to first byte | Path change | Failure unit |
|---|---|---|---|---|---|
| **QUIC / HTTP/3** (worked example) | per-stream, native | confined to the affected stream | 1-RTT combined transport+TLS 1.3 (0-RTT resumption, replay caveat) | survives (connection ID, ¬ 4-tuple) | one stream |
| TCP + TLS | one ordered byte stream for everything | **global** — one loss stalls all | TCP handshake + TLS handshake stacked (2–3 RTT class) | connection dies, reconnect | the connection |
| repo-rendezvous (fleet incumbent) | per-artifact (issue/PR/comment) | none at transport; stalls = queue/claim latency instead | n/a — store-and-forward; latency = poll + dispatch cadence | survives trivially (async) | one artifact |

## Reading the row (Siglary)

- QUIC ⊃ TCP+TLS on the row's scored axes for HTTP-class
  traffic: streams are independent (∅ cross-stream HoL),
  handshake is fused (transport ∧ crypto in one pass),
  identity migrates with the connection.
- repo-rendezvous is **¬ a transport competitor**: it is
  the layer above. Its "latency" is cadence, its
  "blocking" is queue depth — different failure physics.
  QUIC under its legs would cut fetch latency; it does
  not change the rendezvous semantics (stamps, receipts,
  claims) the fleet runs on.
- ker of the comparison: UDP reachability (some networks
  block/throttle UDP — TCP fallback stays), 0-RTT replay
  surface, and CPU cost of userspace transport.

## Owner question: "QUIC or better established?"

Cell-by-cell, as of this entry:

- **Transport cell: QUIC stands.** No better-established
  successor exists for the general case — QUIC *is* the
  established successor (RFC 9000, 2021; HTTP/3 RFC 9114)
  to the TCP+TLS cell. Named adjacents, ¬ successors:
  WebTransport (an API *over* HTTP/3/QUIC), MASQUE
  (proxying *over* QUIC), MoQ (media over QUIC —
  emerging, ¬ established), SCTP (older, never
  web-established).
- **Rendezvous cell: no transport displaces it** — the
  better-established direction there is not a protocol
  swap but push-over-poll (webhooks/SSE where the
  platform offers them), already the fleet's direction
  of record where available.

## Sources

- Target: KodeKloud short (above), claims as templated:
  per-stream multiplexing · ∅ head-of-line blocking ·
  combined handshake 1-RTT.
- Standards: RFC 9000 (QUIC) · RFC 9001 (TLS) ·
  RFC 9002 (loss/congestion) · RFC 9114 (HTTP/3).
