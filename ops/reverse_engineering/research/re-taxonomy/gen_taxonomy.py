#!/usr/bin/env python3
"""Generate ops/reverse_engineering/taxonomy.json (fleet RE taxonomy v1)."""
import json

AXES = {
    "target": ["native", "bytecode", "script", "firmware", "protocol",
               "hardware", "mobile", "web-client", "data-format"],
    "format": ["PE", "ELF", "Mach-O", "DEX", "JAR", "CLR", "raw-image",
               "filesystem-image", "APK", "JS-bundle", "WASM"],
    "architecture": ["x86", "x64", "ARM", "ARM64", "MIPS", "RISC-V", "other"],
    "method": ["static", "dynamic", "hybrid", "comparative", "emulated",
               "automated"],
    "objective": ["understanding", "interoperability", "malware-analysis",
                  "vulnerability-research", "patch-analysis", "cross-validation",
                  "ctf", "incident-support"],
    "tool_role": ["disassembler", "decompiler", "debugger", "instrumentation",
                  "extractor", "emulator", "workspace", "cross-validator",
                  "capture", "deobfuscator", "adapter-factory"],
    "environment": ["linux", "windows", "macos", "android", "ios", "embedded",
                    "ci-remote", "b160v-thin"],
    "evidence": ["observed", "inferred", "reproduced", "contradicted",
                 "unknown"],
}

def cat(id, name, parents, tags, desc=""):
    return {"id": id, "name": name, "kind": "category", "parents": parents,
            "tags": tags, "description": desc}

def tool(id, name, parents, roles, tags, desc=""):
    t = dict(tags); t["tool_role"] = roles
    return {"id": id, "name": name, "kind": "tool", "parents": parents,
            "tags": t, "description": desc}

NODES = [
    cat("reverse-engineering", "Reverse engineering", [], {},
        "The discipline root of this registry: understand how an artifact works, from the artifact. Polyhierarchy — a node has as many parents as are true; primary placement is recorded once, overlaps live in parents/tags, never in duplicated nodes."),
    # --- by target
    cat("target-native", "Native compiled software", ["reverse-engineering"],
        {"target": ["native"]}),
    cat("native-windows", "Windows PE / DLL / drivers", ["target-native"],
        {"target": ["native"], "format": ["PE"], "environment": ["windows"]}),
    cat("native-linux", "Linux / Unix ELF", ["target-native"],
        {"target": ["native"], "format": ["ELF"], "environment": ["linux"]}),
    cat("native-macos", "macOS / iOS Mach-O", ["target-native"],
        {"target": ["native"], "format": ["Mach-O"], "environment": ["macos", "ios"]}),
    cat("target-bytecode", "Managed code / VM bytecode", ["reverse-engineering"],
        {"target": ["bytecode"]}),
    cat("bytecode-jvm", "Java / JVM", ["target-bytecode"],
        {"target": ["bytecode"], "format": ["JAR"]}),
    cat("bytecode-android-dex", "Android DEX", ["target-bytecode", "mobile-android"],
        {"target": ["bytecode", "mobile"], "format": ["DEX", "APK"],
         "environment": ["android"]}),
    cat("bytecode-dotnet", ".NET / CLR", ["target-bytecode"],
        {"target": ["bytecode"], "format": ["CLR"]}),
    cat("target-scripts", "Scripts / packaged applications", ["reverse-engineering"],
        {"target": ["script"]},
        "JavaScript / PowerShell / shell / Python packages, obfuscated logic, embedded interpreters."),
    cat("target-firmware", "Firmware / embedded software", ["reverse-engineering"],
        {"target": ["firmware"], "environment": ["embedded"]}),
    cat("firmware-embedded-linux", "Embedded Linux firmware", ["target-firmware"],
        {"target": ["firmware"], "format": ["filesystem-image"],
         "environment": ["embedded", "linux"]}),
    cat("firmware-bare-metal", "Bare-metal / RTOS images", ["target-firmware"],
        {"target": ["firmware"], "format": ["raw-image"],
         "environment": ["embedded"]}),
    cat("target-protocols-formats", "Protocols / file formats", ["reverse-engineering"],
        {"target": ["protocol", "data-format"]},
        "Network messages + state machines, IPC/device interfaces, containers and proprietary formats."),
    cat("target-hardware", "Hardware-assisted targets", ["reverse-engineering"],
        {"target": ["hardware"]},
        "Debug interfaces, serial/peripheral buses, device behaviour and signal capture."),
    cat("target-mobile", "Mobile applications", ["reverse-engineering"],
        {"target": ["mobile"]}),
    cat("mobile-android", "Android applications (APK)", ["target-mobile"],
        {"target": ["mobile"], "format": ["APK"], "environment": ["android"]},
        "An APK is not homogeneous: manifest/resources, DEX bytecode and native .so libraries are three layers, analysed by different tools and correlated at runtime."),
    cat("mobile-ios", "iOS applications", ["target-mobile", "native-macos"],
        {"target": ["mobile"], "format": ["Mach-O"], "environment": ["ios"]}),
    cat("target-web-client", "Web clients / web applications", ["reverse-engineering"],
        {"target": ["web-client"], "format": ["JS-bundle", "WASM"]},
        "The Foundry's home ground: request->DOM attribution, bundle recovery, adapter synthesis. Full sub-registry: ops/web_adapter_foundry/taxonomy.json (web-reverse-engineering)."),
    cat("work-malware", "Malware analysis (work family)", ["reverse-engineering"],
        {"objective": ["malware-analysis", "incident-support"],
         "method": ["hybrid"]},
        "A work family, not a target: preserved sample, contained workspace, static hypotheses correlated with controlled runtime observation."),
    cat("work-ctf-reversing", "CTF reversing (work family)", ["reverse-engineering"],
        {"objective": ["ctf", "understanding"]}),
    # --- tools / platforms / fleet belts
    tool("ghidra", "Ghidra", ["target-native", "firmware-bare-metal"],
         ["disassembler", "decompiler"],
         {"method": ["static"], "environment": ["linux", "windows", "macos"]},
         "NSA framework: multi-architecture disassembly/decompilation, graphing, scripting."),
    tool("rizin-cutter", "Rizin / Cutter (radare2 family)", ["target-native"],
         ["disassembler"], {"method": ["static"]}),
    tool("gdb", "GDB (+ GEF)", ["native-linux", "firmware-embedded-linux"],
         ["debugger"], {"method": ["dynamic"], "environment": ["linux"]}),
    tool("platform-debuggers", "LLDB / WinDbg / x64dbg", ["native-macos", "native-windows"],
         ["debugger"], {"method": ["dynamic"]}),
    tool("frida", "Frida", ["bytecode-android-dex", "target-native", "mobile-android"],
         ["instrumentation"], {"method": ["dynamic", "hybrid"],
         "environment": ["android", "ios", "linux", "windows", "macos"]},
         "Runtime instrumentation bridge between static structure and observed behaviour."),
    tool("jadx", "JADX", ["bytecode-android-dex", "bytecode-jvm"],
         ["decompiler"], {"method": ["static"], "format": ["DEX", "APK", "JAR"]}),
    tool("apktool", "Apktool", ["mobile-android"],
         ["extractor"], {"method": ["static"], "format": ["APK"]},
         "APK resources/manifest decode. Fleet note: the apk-xref belt's stdlib AXML parser is the portable floor; apktool corroborates in CI."),
    tool("dex2jar-jd", "dex2jar / JD-GUI / Bytecode Viewer", ["bytecode-jvm", "bytecode-android-dex"],
         ["decompiler"], {"method": ["static"]}),
    tool("binwalk", "Binwalk", ["target-firmware"],
         ["extractor"], {"method": ["static"], "format": ["filesystem-image", "raw-image"]},
         "Identifies/extracts embedded objects; does not replace a decompiler."),
    tool("qemu", "QEMU", ["firmware-embedded-linux", "firmware-bare-metal"],
         ["emulator"], {"method": ["emulated", "dynamic"]}),
    tool("flare-vm", "FLARE-VM", ["work-malware"],
         ["workspace"], {"environment": ["windows"]},
         "Windows RE VM installer scripts — an environment, not a containment boundary; VM + snapshots + host-only networking required."),
    tool("kali-linux", "Kali Linux", ["reverse-engineering"],
         ["workspace"], {"environment": ["ci-remote"]},
         "Fleet-registered agentic RE environment (campaign doc, 2026-10-26): offload/container only, never on the B160V. A platform/workspace — not a discipline, methodology or credential."),
    tool("apk-xref", "apk_xref (fleet belt)", ["mobile-android", "bytecode-android-dex"],
         ["cross-validator", "extractor"],
         {"method": ["static", "comparative"], "format": ["APK"],
          "objective": ["cross-validation", "interoperability"],
          "environment": ["ci-remote", "linux", "b160v-thin"]},
         "ops/web_adapter_foundry/apk_xref.py (PR #2143): acquire/extract/classify/cross-validate a published APK against its repo, both directions; findings in the apk-xref/v1 template shape."),
    tool("web-adapter-foundry", "Web Adapter Foundry (waf)", ["target-web-client"],
         ["adapter-factory", "cross-validator"],
         {"method": ["static", "dynamic", "comparative"],
          "objective": ["interoperability", "cross-validation"],
          "environment": ["ci-remote", "b160v-thin"]},
         "ops/web_adapter_foundry/waf.py: registry/probe/promotion core; probing = finding the DOMs from the request."),
    tool("webcrack", "webcrack", ["target-scripts", "target-web-client"],
         ["deobfuscator"], {"method": ["static"], "format": ["JS-bundle"]}),
    tool("mitmproxy", "mitmproxy (family)", ["target-protocols-formats", "target-web-client"],
         ["capture"], {"method": ["dynamic"]},
         "Traffic capture; mitmproxy2swagger sits in the Foundry sub-registry (capture -> draft OpenAPI)."),
]

STAGES = ["acquire", "identify", "extract", "analyze-static",
          "observe-dynamic", "validate", "document"]

def chain(cat_id, rows):
    return {"category": cat_id,
            "stages": [{"stage": s, "tools": t, "output": o} for s, t, o in rows]}

TOOLCHAINS = [
    chain("mobile-android", [
        ("acquire", ["apk-xref"], "published artifact + provenance (source, version, build, sha256)"),
        ("extract", ["apktool", "apk-xref"], "manifest, permissions, resources, DEX + native split"),
        ("analyze-static", ["jadx", "ghidra"], "reconstructed logic per layer (DEX vs .so)"),
        ("observe-dynamic", ["frida"], "runtime calls correlated across managed/native layers"),
        ("validate", ["apk-xref"], "repo<->APK divergences both directions, apk-xref/v1 findings"),
        ("document", [], "architecture notes + validated findings")]),
    chain("native-linux", [
        ("identify", [], "format/architecture confirmation (ELF)"),
        ("analyze-static", ["ghidra", "rizin-cutter"], "functions, strings, xrefs, control flow"),
        ("observe-dynamic", ["gdb", "frida"], "breakpoint/trace validation of selected paths"),
        ("document", [], "annotated functions + behaviour notes")]),
    chain("native-windows", [
        ("analyze-static", ["ghidra"], "reconstructed PE/DLL logic"),
        ("observe-dynamic", ["platform-debuggers", "frida"], "observed execution"),
        ("document", [], "documented behaviour (FLARE-VM as workspace when malware-adjacent)")]),
    chain("firmware-embedded-linux", [
        ("extract", ["binwalk"], "component inventory: filesystems, scripts, configs, binaries"),
        ("analyze-static", ["ghidra"], "selected service binaries analysed"),
        ("observe-dynamic", ["qemu", "gdb"], "emulated execution where the environment reproduces"),
        ("document", [], "component map + verified behaviour")]),
    chain("firmware-bare-metal", [
        ("identify", ["ghidra"], "processor + memory layout established before code claims"),
        ("observe-dynamic", ["qemu"], "hardware debugging or emulation evidence"),
        ("document", [], "code/data map + execution evidence")]),
    chain("work-malware", [
        ("acquire", [], "preserved sample, hash recorded, contained workspace (FLARE-VM)"),
        ("analyze-static", ["ghidra"], "static triage -> focused code hypotheses"),
        ("observe-dynamic", ["platform-debuggers", "frida"], "controlled runtime observation"),
        ("document", [], "behaviour report / incident-support findings")]),
    chain("target-web-client", [
        ("analyze-static", ["web-adapter-foundry", "webcrack"], "request inventory -> DOM attribution -> DOM data sources"),
        ("observe-dynamic", ["mitmproxy"], "captured traffic / replay"),
        ("validate", ["web-adapter-foundry"], "promotion pipeline: discovered -> captured -> modeled -> reproduced -> verified"),
        ("document", [], "adapter registry entry in the Foundry sub-registry")]),
    chain("target-protocols-formats", [
        ("extract", ["mitmproxy"], "captured messages / state machine samples"),
        ("analyze-static", ["web-adapter-foundry"], "format model + field selection"),
        ("validate", [], "differential probes against live/recorded traffic"),
        ("document", [], "interoperability notes / draft contract")]),
]

OVERLAP = {  # work family x method: central | supporting | peripheral
    "native-linux":        {"static": "central", "debugging": "central", "instrumentation": "supporting", "extraction": "supporting", "emulation": "supporting"},
    "mobile-android":      {"static": "central", "debugging": "supporting", "instrumentation": "central", "extraction": "central", "emulation": "supporting"},
    "firmware-embedded-linux": {"static": "central", "debugging": "supporting", "instrumentation": "supporting", "extraction": "central", "emulation": "central"},
    "work-malware":        {"static": "central", "debugging": "central", "instrumentation": "central", "extraction": "supporting", "emulation": "supporting"},
    "target-protocols-formats": {"static": "supporting", "debugging": "peripheral", "instrumentation": "central", "extraction": "supporting", "emulation": "peripheral"},
    "work-ctf-reversing":  {"static": "central", "debugging": "central", "instrumentation": "supporting", "extraction": "supporting", "emulation": "peripheral"},
}
OVERLAP_METHODS = ["static", "debugging", "instrumentation", "extraction", "emulation"]

doc = {
    "schema": "re-taxonomy/v1",
    "name": "reverse-engineering",
    "umbrella": {
        "name": "cybersecurity / information security (polyhierarchy)",
        "note": "This registry is the RE family of the wider field taxonomy. Entity types stay distinct up there too: Kali is a platform, OWASP a foundation/ecosystem, pentest an activity, CISSP a credential, CompTIA a provider, OverTheWire a lab, CTF a format. Conduct axes (hats), function axes (red/blue/purple teams) and visibility axes (black/gray/white-box) belong to that umbrella, not to this registry — here they appear only as method/objective tags when they describe RE work.",
        "external_axes": {
            "hats": ["white (authorized)", "black (unauthorized/malicious)", "gray (authorization unclear) — record actual permission, not the label"],
            "teams": ["red (offense)", "blue (defense)", "purple (offense+defense feedback)"],
            "visibility": ["black-box", "gray-box", "white-box"]},
        "sibling_registries": [
            "ops/web_adapter_foundry/taxonomy.json (web-reverse-engineering sub-registry)",
            "docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md (Kali registered environment)"]},
    "placement_rules": [
        "One node, placed once, by primary kind; overlap is expressed as extra parents + tags, never duplicate nodes.",
        "Kinds stay distinct: category != tool != platform != credential != format. A workspace (Kali, FLARE-VM) is not a discipline.",
        "Every claim carries the Foundry evidence vocabulary: observed | inferred | reproduced | contradicted | unknown.",
        "Toolchains are handoffs between stages, not shopping lists: a chain names the stage's tool(s) and the output that passes on."],
    "axes": AXES,
    "workflow_stages": STAGES,
    "nodes": NODES,
    "toolchains": TOOLCHAINS,
    "overlap_matrix": {"methods": OVERLAP_METHODS, "values": ["central", "supporting", "peripheral"],
                       "rows": OVERLAP},
    "example_record": {
        "name": "Android native-library analysis",
        "parents": ["mobile-android", "target-native"],
        "tags": {"target": ["native"], "format": ["ELF"], "architecture": ["ARM64"],
                 "method": ["hybrid"], "objective": ["understanding"]},
        "toolchain": {"package-inspection": "apktool", "managed-code-context": "jadx",
                      "native-code-analysis": "ghidra", "runtime-instrumentation": "frida",
                      "cross-validation": "apk-xref"},
        "outputs": ["annotated-functions", "managed-native-call-map",
                    "runtime-observations", "unresolved-hypotheses"]},
    "source_example": "Adapted from a collaborator's Perplexity taxonomy export (owner-supplied 2026-10-28): cybersecurity polyhierarchy + RE category/toolchain map. Fleet version: machine-readable, validated, fleet assets placed; improvement research filed separately.",
}
print(json.dumps(doc, indent=1, sort_keys=True))
