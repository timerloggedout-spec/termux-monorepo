# Transport competition domain

Transport research spans physical transmission, link technologies, network routing, transport protocols and application communication. Maintain the layer relationships as a graph: technologies can cross layers and encapsulate one another.

## Target families

| Family | Example targets | Distinguishing constraints |
|---|---|---|
| Legacy document / analog | fax, modem families including 14.4 kbps | signal modulation, line quality, error correction, setup and interoperability |
| Physical media | copper, coaxial, fiber optics, free-space optics | distance, attenuation, interference, transceiver cost, energy and capacity |
| Access / link | Ethernet, Wi-Fi, cellular, satellite | contention, mobility, framing, link retransmission and medium access |
| Network | IPv4, IPv6, routing, tunnels | addressing, path selection, MTU, fragmentation and reachability |
| Transport | TCP, UDP, QUIC, Multipath QUIC | reliability, ordering, congestion control, multiplexing and loss recovery |
| Application transport | TLS, HTTP/2, HTTP/3, WebSocket, MASQUE, WebTransport | security setup, stream/session semantics, proxying and datagram support |

## QUIC reference card

- QUIC transport is standardized by RFC 9000.
- HTTP/3 maps HTTP semantics onto QUIC and is specified by RFC 9114.
- QUIC streams provide independent stream-level ordering while sharing a connection; this avoids TCP's transport-level head-of-line blocking between independent streams, while connection-level congestion and path failures still matter.
- QUIC integrates the TLS 1.3 handshake and supports 1-RTT connection establishment in the ordinary handshake flow; 0-RTT data has separate replay and safety considerations.
- MASQUE, WebTransport and Multipath QUIC are adjacent technologies or extensions with separate specifications and maturity states. Record exact draft/RFC revisions and implementation evidence per target.

## Benchmark protocol

Capture at minimum:
- RTT and bandwidth profiles, including constrained links;
- loss, reordering, jitter and path changes;
- cold connection, resumed connection and handshake counts;
- stream count, stream mix, head-of-line behavior and fairness;
- congestion-control algorithm and pacing;
- encryption and CPU overhead;
- bytes on wire, retransmission overhead and application goodput;
- energy and memory where measurable;
- proxy / tunnel behavior and network migration;
- correctness, security and interoperability results.

Run both controlled network emulation and real-network observations. Label them separately. Preserve hardware, OS, kernel, implementation revision, configuration and workload artifacts.

## Comparison rule

Fax, a 14.4 kbps modem, optical links, TCP and QUIC solve different parts of the transport problem. Compare technologies within meaningful layers and evaluate complete stacks separately. A faster physical medium does not prove a better transport protocol; a better protocol does not increase the capacity of a constrained physical channel.
