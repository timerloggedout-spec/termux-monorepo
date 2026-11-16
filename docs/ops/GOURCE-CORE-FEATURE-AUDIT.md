# Core_fork-Gource Feature Audit (agentic / replay focus)

**Upstream**: acaudwell/Core  
**Fork**: timerloggedout-spec/Core_fork-Gource (2026-08-18, clean)  
**Priority**: Seekable activity history + event model for agentic refinements & replay evaluations.  
**Deprioritized**: OpenGL tree visualization, PPM video pipelines.

## High-value for monorepo

| Component | Files | Agentic value | Extract priority |
|-----------|-------|---------------|------------------|
| **SeekLog / StreamLog / BaseLog** | seeklog.h/.cpp | Percent/index seek, sequential + random access over timed logs, STDIN stream | **P0** — conceptual model already ported to Python (`ops_event_seeklog.py`) |
| **Custom log contract** | (Gource side; Core reads) | `ts\|actor\|op\|path\|colour` — universal ops IR | **P0** |
| **ConfFile / Settings** | conffile.*, settings.* | Typed CLI/config parsing, date-time parse | P2 — patterns only |
| **Timer** | timer.h/.cpp | GL + CPU timing probes | P3 (OTEL densify already covers) |
| **Logger** | logger.* | Basic logging | P3 |
| **Resource / Texture / PNG / PPM / TGA** | resource, texture, png_writer, ppm, tga | Asset lifetime + frame writers | P4 (Visualization Plane) |
| **Display / SDLApp / mouse / frustum / quadtree / VBO / shader*** | display, sdlapp, … | Rendering stack | P4 / parked |
| **Regex / UTF8 / FTGL / vectors / plane / bounds** | various | Utilities | P3 as needed |

## SeekLog surface (exact)

```cpp
class SeekLog : public BaseLog {
  void setPointer(std::streampos);
  std::streampos getPointer();
  void seekTo(float percent);
  bool getNextLine(std::string& line);
  bool getNextLineAt(std::string& line, float percent);
  float getPercent();
  bool isFinished();
};
```

Python port mirrors: `seek_to`, `seek_index`, `get_next`, `get_next_at`, `slice(start_pct, stop_pct)`, `to_gource_log`, `to_jsonl`.

## License note
Core / Gource are GPL-3. Any future native gitlink or derived C++ must stay GPL-compatible. Pure Python re-implementation of the *event model* is not a derivative work of the C++ sources.

## Recommendation
1. Ship Python SeekLog + OPS-EVENT schema first (this extract).
2. Keep Core_fork-Gource as OBSERVE reference; optional gitlink only if native performance or exact SeekLog behaviour is required later.
3. Full Gource binary (system/Docker) remains optional consumer of emitted custom logs — not a runtime dependency for agentic lanes.
