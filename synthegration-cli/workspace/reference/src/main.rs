use std::process::Command;
use std::env;
use std::path::PathBuf;

const CONV_EXPLORER: &str = "conv_explorer.py";
const LIVE_EXPORT: &str = "live_export.py";
const LIVE_SEARCH: &str = "live_search.py";
const MULTI_AGENT: &str = "termux-multi-agent/run.py";
const CEDAR_MCP: &str = "termux-multi-agent/cedar-mcp-server.js";

fn home() -> PathBuf {
    env::var("HOME").map(PathBuf::from).unwrap_or_else(|_| PathBuf::from("."))
}

fn run_python(script: &str, args: &[&str]) -> std::process::Output {
    let mut cmd = Command::new("python3");
    cmd.arg(home().join("cli-synthegration").join(script));
    for a in args { cmd.arg(a); }
    cmd.output().expect("python failed")
}

fn run_node(script: &str, args: &[&str]) -> std::process::Output {
    let mut cmd = Command::new("node");
    cmd.arg(home().join(script));
    for a in args { cmd.arg(a); }
    cmd.output().expect("node failed")
}

fn main() {
    let args: Vec<String> = env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("chat") => {
            Command::new("python3")
                .arg(home().join("deepcli-tui/tui.py"))
                .status().ok();
        }
        Some("refactor") => {
            let target = args.get(2).expect("Usage: synthegration refactor <file>");
            Command::new("python3")
                .arg(home().join(MULTI_AGENT))
                .arg(target)
                .status().ok();
        }
        Some("sessions") => {
            let search = args.get(2);
            let mut argv = vec!["--list"];
            if let Some(s) = search { argv = vec!["search", s]; }
            let out = run_python(CONV_EXPLORER, &argv);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("live-export") => {
            let sid = args.get(2).expect("Usage: synthegration live-export <session_id> [--account <name>]");
            let mut py_args: Vec<String> = vec![sid.to_string()];
            if args.get(3).map(|s| s.as_str()) == Some("--account") {
                py_args.push("--account".into());
                py_args.push(args.get(4).expect("Missing account name").to_string());
            }
            let py_refs: Vec<&str> = py_args.iter().map(|s| s.as_str()).collect();
            let out = run_python(LIVE_EXPORT, &py_refs);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("export") => {
            let sid = args.get(2).expect("Usage: synthegration export <session_id>");
            let out = run_python(CONV_EXPLORER, &["--export", sid]);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("cedar") => {
            let sub = args.get(2).expect("Usage: synthegration cedar [serve|validate|eval]");
            match sub.as_str() {
                "serve" => {
                    let mut child = Command::new("node")
                        .arg(home().join(CEDAR_MCP))
                        .spawn().expect("cedar mcp failed");
                    child.wait().ok();
                }
                "validate" => {
                    let code = args.get(3).map(String::as_str).unwrap_or("");
                    let out = Command::new("python3")
                        .arg(home().join("cli-synthegration/cedar_bridge.py"))
                        .arg("validate").arg(code)
                        .output().expect("validate failed");
                    println!("{}", String::from_utf8_lossy(&out.stdout));
                }
                "eval" => {
                    let code = args.get(3).map(String::as_str).unwrap_or("");
                    let schema = args.get(4).map(String::as_str).unwrap_or("{}");
                    let input = args.get(5).map(String::as_str).unwrap_or("{}");
                    let out = Command::new("python3")
                        .arg(home().join("cli-synthegration/cedar_bridge.py"))
                        .arg("eval").arg(code).arg(schema).arg(input)
                        .output().expect("eval failed");
                    println!("{}", String::from_utf8_lossy(&out.stdout));
                }
                _ => println!("Usage: synthegration cedar [serve|validate|eval]"),
            }
        }
        Some("mcp") => {
            let out = run_node(CEDAR_MCP, &[]);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("offline-sessions") => {
            let dir = args.get(2).expect("Usage: synthegration offline-sessions <export_dir>");
            let out = run_python(CONV_EXPLORER, &["--offline", dir, "--list"]);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("offline-search") => {
            let dir = args.get(2).expect("Usage: synthegration offline-search <export_dir> <term>");
            let term = args.get(3).expect("Usage: synthegration offline-search <export_dir> <term>");
            let out = run_python(CONV_EXPLORER, &["--offline", dir, "search", term]);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("offline-export") => {
            let dir = args.get(2).expect("Usage: synthegration offline-export <export_dir> <session_id>");
            let sid = args.get(3).expect("Usage: synthegration offline-export <export_dir> <session_id>");
            let out = run_python(CONV_EXPLORER, &["--offline", dir, "--export", sid]);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("codex-index") => {
            let out = Command::new("python3")
                .arg(home().join("cli-synthegration/synthegration_index.py"))
                .output().expect("codex index failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }

        Some("codex-update") => {
            let out = run_python(LIVE_EXPORT, &[]); // trick to trigger index build
            println!("Codex updated from live exports.");
        }
        Some("live-search") => {
            let term = args.get(2).expect("Usage: synthegration live-search <term> [--language <lang>]");
            let mut py_args = vec![term.to_string()];
            if args.get(3).map(|s| s.as_str()) == Some("--language") {
                py_args.push("--language".into());
                py_args.push(args.get(4).expect("Missing language").to_string());
            }
            let py_refs: Vec<&str> = py_args.iter().map(|s| s.as_str()).collect();
            let out = run_python(LIVE_SEARCH, &py_refs);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("codex-search") => {
            let term = args.get(2).expect("Usage: synthegration codex-search <term>");
            let out = Command::new("python3")
                .args(["-c", &format!("import sys; sys.path.insert(0,'{}'); from synthegration_index import CodexIndex; idx = CodexIndex(); results = idx.search_by_taxonomy('{}'); [print(r['pointer'], r['hash'], r['code'][:80]) for r in results[:10]]", home().join("cli-synthegration").display(), term)])
                .output().expect("search failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("branches") => {
            let out = Command::new("python3")
                .arg(home().join("cli-synthegration/conv_branching.py"))
                .arg("list")
                .output().expect("branch list failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("branch-fork") => {
            let name = args.get(2).expect("Usage: synthegration branch-fork <name> [parent]");
            let parent = args.get(3);
            let mut cmd = Command::new("python3");
            cmd.arg(home().join("cli-synthegration/conv_branching.py"))
               .arg("fork").arg(name);
            if let Some(p) = parent { cmd.arg(p); }
            let out = cmd.output().expect("fork failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("branch-merge") => {
            let src = args.get(2).expect("Usage: synthegration branch-merge <source> <target>");
            let tgt = args.get(3).expect("Usage: synthegration branch-merge <source> <target>");
            let out = Command::new("python3")
                .args([&home().join("cli-synthegration/conv_branching.py").to_string_lossy().to_string(), "merge", src, tgt])
                .output().expect("merge failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("branch-link") => {
            let from = args.get(2).expect("Usage: synthegration branch-link <from> <to>");
            let to = args.get(3).expect("Usage: synthegration branch-link <from> <to>");
            let out = Command::new("python3")
                .args([&home().join("cli-synthegration/conv_branching.py").to_string_lossy().to_string(), "link", from, to])
                .output().expect("link failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("export-all") => {
            let out = Command::new("python3")
                .arg(home().join("cli-synthegration/batch_export_all.py"))
                .output().expect("export-all failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }

        Some("search") => {
            let term = args.get(2).expect("Usage: synthegration search <term>");
            let out = std::process::Command::new("python3")
                .arg("-c")
                .arg(format!(
                    "import sys; sys.path.insert(0,'{0}'); from synthegration_index import MessageIndex; mi=MessageIndex.load(); results=mi.search('{1}'); [print(f'{{r[0][:8]}}... | {{r[3][:60]}} | {{r[1]}}: {{r[2][:100]}}') for r in results[:15]]",
                    home().join("cli-synthegration").display(), term
                ))
                .output().expect("search failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }


        Some("categories") => {
            let cat = args.get(2).map(String::as_str);
            let mut cmd = std::process::Command::new("python3");
            cmd.arg(home().join("cli-synthegration/session_categories.py"));
            if let Some(c) = cat { cmd.arg(c); }
            let out = cmd.output().expect("categories failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }


        Some("elo-backfill") => {
            let out = std::process::Command::new("python3")
                .arg(home().join("cli-synthegration/backfill_elo.py"))
                .output().expect("elo backfill failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("elo-stats") => {
            let out = std::process::Command::new("python3")
                .arg("-c")
                .arg(format!(
                    "import sys; sys.path.insert(0,'{0}'); from success_metrics import RefactorELO; elo=RefactorELO(); print(f'Moving average: {{elo.moving_average(window=50):.2f}}'); print(f'Top patterns:'); [print(f'  {{h}}: {{r:.0f}}') for h,r in elo.top_patterns(5)]",
                    home().join("cli-synthegration").display()
                ))
                .output().expect("elo stats failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }


        Some("abc-test") => {
            let target = args.get(2).expect("Usage: synthegration abc-test <file> [strategies...]");
            let mut cmd = std::process::Command::new("python3");
            cmd.arg(home().join("termux-multi-agent/src/parallel_agents.py"))
               .arg("test").arg(target);
            for s in args.iter().skip(3) { cmd.arg(s); }
            let out = cmd.output().expect("abc-test failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("timeline") => {
            let days = args.get(2).map(String::as_str).unwrap_or("30");
            let out = std::process::Command::new("python3")
                .arg(home().join("termux-multi-agent/src/parallel_agents.py"))
                .arg("analyze").arg(days)
                .output().expect("timeline failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }


        Some("sprints") => {
            let filter = args.get(2).map(String::as_str);
            let mut cmd = std::process::Command::new("python3");
            cmd.arg(home().join("cli-synthegration/sprints.py"));
            if let Some(f) = filter { cmd.arg(f); }
            let out = cmd.output().expect("sprints failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }


        Some("tools") => {
            let out = std::process::Command::new("python3")
                .arg(home().join("termux-multi-agent/src/tool_registry.py"))
                .output().expect("tool registry failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }

        Some("forks") => {
            let filter = args.get(2).map(String::as_str);
            let gap = args.get(3).and_then(|g| g.parse::<i32>().ok());
            let mut cmd = std::process::Command::new("python3");
            cmd.arg(home().join("cli-synthegration/branch_manager.py"))
               .arg("forks");
            if let Some(f) = filter { cmd.arg("--session").arg(f); }
            if let Some(g) = gap { cmd.arg("--min-gap").arg(g.to_string()); }
            let out = cmd.output().expect("forks failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }

        Some("handoff") => {
            let mut cmd = std::process::Command::new("python3");
            cmd.arg(home().join("cli-synthegration/generate_handoff.py"));
            for a in args.iter().skip(2) { cmd.arg(a); }
            let out = cmd.output().expect("handoff failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }

        Some("message-map") => {
            let sid = args.get(2).map(String::as_str);
            let mut cmd = std::process::Command::new("python3");
            cmd.arg(home().join("cli-synthegration/branch_manager.py"))
               .arg("message-map");
            if let Some(s) = sid { cmd.arg(s); }
            let out = cmd.output().expect("message-map failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }

        Some("detect") => {
            let text = args.get(2).expect("Usage: synthegration detect 'pasted text'");
            let out = std::process::Command::new("python3")
                .arg(home().join("cli-synthegration/detect_paste.py"))
                .arg(text)
                .output().expect("detect failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }

        Some("loop") => {
            let mut cmd = std::process::Command::new("python3");
            cmd.arg(home().join("cli-synthegration/loop_optimizer.py"));
            for a in args.iter().skip(2) { cmd.arg(a); }
            let out = cmd.output().expect("loop failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("loop-prompt") => {
            let default_sid = "e102d768-8a47-4001-95cb-14fb6245c6fa".to_string();
            let sid = args.get(2).unwrap_or(&default_sid);
            let empty_pid = "".to_string();
            let pid = args.get(3).unwrap_or(&empty_pid);
            let out = std::process::Command::new("python3")
                .arg(home().join("cli-synthegration/generate_loop.py"))
                .arg(sid).arg(pid)
                .output().expect("loop-prompt failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }

        Some("loop") => {
            let mut cmd = std::process::Command::new("python3");
            cmd.arg(home().join("cli-synthegration/loop_optimizer.py"));
            for a in args.iter().skip(2) { cmd.arg(a); }
            let out = cmd.output().expect("loop failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        Some("loop-prompt") => {
            let default_sid = "e102d768-8a47-4001-95cb-14fb6245c6fa".to_string();
            let sid = args.get(2).unwrap_or(&default_sid);
            let empty_pid = "".to_string();
            let pid = args.get(3).unwrap_or(&empty_pid);
            let out = std::process::Command::new("python3")
                .arg(home().join("cli-synthegration/generate_loop.py"))
                .arg(sid).arg(pid)
                .output().expect("loop-prompt failed");
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }

        _ => {
            println!("synthegration-cli – unified DeepSeek automation utility");
            println!("Usage:");
            println!("  synthegration chat              – Launch TUI");
            println!("  synthegration sessions [query]  – List/search conversations");
            println!("  synthegration export <id>       – Export code blocks from session");
            println!("  synthegration refactor <file>   – Run multi‑agent refactoring");
            println!("  synthegration cedar [serve|validate|eval] – CEDARscript tools");
            println!("  synthegration mcp               – CEDAR MCP server");
            println!("  synthegration offline-sessions <dir>  – List local sessions");
            println!("  synthegration offline-search <dir> <term> – Search local");
            println!("  synthegration offline-export <dir> <id> – Export local");
            println!("  synthegration codex-index       – Build codex from offline");
            println!("  synthegration codex-search <t>  – Search codex");
            println!("  synthegration forks [session] [min-gap] – Cross‑session forks (new sessions)
  synthegration branches [sess]   – In‑session branches (message edits)");
            println!("  synthegration branch-fork <n> [parent] – Fork branch");
            println!("  synthegration branch-merge <src> <tgt> – Merge branches");
            println!("  synthegration branch-link <from> <to> – Link knowledge");
            println!("  synthegration categories [category]  – Auto‑categorized sessions
  synthegration search <term>      – Search inside all conversation messages
  synthegration export-all        – Export all sessions");
        }
    }
}
