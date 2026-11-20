/// Harmonizer – unified DeepSeek automation (Rust + Python bridge)
use std::process::{Command, Output};
use std::env;
use std::path::PathBuf;

fn home() -> PathBuf {
    env::var("HOME").map(PathBuf::from).unwrap_or_else(|_| PathBuf::from("."))
}

fn run_python(script: &str, args: &[&str]) -> Output {
    let mut cmd = Command::new("python3");
    cmd.arg(home().join("cli-synthegration").join(script));
    for a in args { cmd.arg(a); }
    cmd.output().expect("python failed")
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        print_usage();
        return;
    }

    match args[1].as_str() {
        "chat" => {
            Command::new("python3")
                .arg(home().join("deepcli-tui/tui.py"))
                .status().expect("tui failed");
        }
        "sessions" => {
            let search = if args.len() > 2 { &args[2] } else { "" };
            let out = run_python("conv_explorer.py", &["--list", search]);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        "export" => {
            let sid = args.get(2).expect("Usage: harmonizer export <session_id>");
            let out = run_python("live_export.py", &[sid]);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        "search" => {
            let term = args.get(2).expect("Usage: harmonizer search <term>");
            let out = run_python("live_message_search.py", &[term]);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        "sync" => {
            let out = run_python("sync/selective_sync.py", &[]);
            println!("{}", String::from_utf8_lossy(&out.stderr));
        }
        "refactor" => {
            let file = args.get(2).expect("Usage: harmonizer refactor <file>");
            Command::new("python3")
                .arg(home().join("termux-multi-agent/run.py"))
                .arg(file)
                .status().expect("refactor failed");
        }
        "cedar" => {
            Command::new("node")
                .arg(home().join("termux-multi-agent/cedar-mcp-server.js"))
                .status().expect("cedar failed");
        }
        "sprints" => {
            let out = run_python("sprints.py", &[]);
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        _ => print_usage(),
    }
}

fn print_usage() {
    println!("harmonizer – l33T DeepSeek automation");
    println!("  chat              – Launch TUI");
    println!("  sessions [query]  – List/search conversations");
    println!("  export <id>       – Export code blocks + thinking");
    println!("  search <term>     – Full‑text search across all sessions");
    println!("  sync              – Incremental sync (new/updated sessions)");
    println!("  refactor <file>   – Multi‑agent refactoring");
    println!("  cedar             – CEDARscript MCP server");
    println!("  sprints           – Show sprint board");
}
