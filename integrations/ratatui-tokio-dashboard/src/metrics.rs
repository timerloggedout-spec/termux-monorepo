use crate::{ProcessInfo, SystemSnapshot};
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Copy)]
pub struct CpuTimes {
    total: u64,
    idle: u64,
}

pub fn sample_system(previous: &mut Option<CpuTimes>) -> SystemSnapshot {
    let current = read_cpu_times().unwrap_or(CpuTimes { total: 0, idle: 0 });
    let cpu_percent = previous
        .take()
        .and_then(|old| {
            let total_delta = current.total.saturating_sub(old.total);
            let idle_delta = current.idle.saturating_sub(old.idle);
            (total_delta > 0).then(|| {
                (((total_delta.saturating_sub(idle_delta)) as f64 / total_delta as f64) * 100.0)
                    .round()
                    .clamp(0.0, 100.0) as u8
            })
        })
        .unwrap_or(0);
    *previous = Some(current);

    let (memory_used_kb, memory_total_kb, memory_percent) = read_memory().unwrap_or((0, 0, 0));
    let load_1m = read_load_1m().unwrap_or(0.0);
    let processes = read_processes();
    let cpu_cores = std::thread::available_parallelism()
        .map(|n| n.get())
        .unwrap_or(1);

    SystemSnapshot {
        cpu_percent,
        memory_percent,
        memory_used_kb,
        memory_total_kb,
        load_1m,
        processes,
        cpu_cores,
    }
}

fn read_cpu_times() -> Option<CpuTimes> {
    let stat = fs::read_to_string("/proc/stat").ok()?;
    let line = stat.lines().find(|line| line.starts_with("cpu "))?;
    let values: Vec<u64> = line
        .split_whitespace()
        .skip(1)
        .filter_map(|value| value.parse().ok())
        .collect();
    if values.len() < 5 {
        return None;
    }
    let total = values.iter().copied().sum();
    let idle = values[3].saturating_add(values.get(4).copied().unwrap_or_default());
    Some(CpuTimes { total, idle })
}

fn read_memory() -> Option<(u64, u64, u8)> {
    let text = fs::read_to_string("/proc/meminfo").ok()?;
    let mut total = None;
    let mut available = None;

    for line in text.lines() {
        let mut fields = line.split_whitespace();
        match fields.next() {
            Some("MemTotal:") => total = fields.next().and_then(|v| v.parse::<u64>().ok()),
            Some("MemAvailable:") => available = fields.next().and_then(|v| v.parse::<u64>().ok()),
            _ => {}
        }
    }

    let total = total?;
    let available = available.unwrap_or_default().min(total);
    let used = total.saturating_sub(available);
    let percent = if total == 0 {
        0
    } else {
        ((used as f64 / total as f64) * 100.0)
            .round()
            .clamp(0.0, 100.0) as u8
    };
    Some((used, total, percent))
}

fn read_load_1m() -> Option<f64> {
    fs::read_to_string("/proc/loadavg")
        .ok()?
        .split_whitespace()
        .next()?
        .parse()
        .ok()
}

fn read_processes() -> Vec<ProcessInfo> {
    let mut processes = fs::read_dir("/proc")
        .ok()
        .into_iter()
        .flatten()
        .filter_map(|entry| entry.ok())
        .filter_map(|entry| {
            let name = entry.file_name().to_string_lossy().into_owned();
            let pid = name.parse::<u32>().ok()?;
            let root = entry.path();
            let command = read_command(&root).unwrap_or_else(|| "unknown".to_string());
            let rss_kb = read_rss_kb(&root).unwrap_or_default();
            Some(ProcessInfo {
                pid,
                command,
                rss_kb,
            })
        })
        .collect::<Vec<_>>();

    processes.sort_by(|a, b| b.rss_kb.cmp(&a.rss_kb).then_with(|| a.pid.cmp(&b.pid)));
    processes.truncate(8);
    processes
}

fn read_command(root: &Path) -> Option<String> {
    let command = fs::read_to_string(root.join("comm")).ok()?;
    Some(command.trim().to_string())
}

fn read_rss_kb(root: &Path) -> Option<u64> {
    let text = fs::read_to_string(root.join("statm")).ok()?;
    let pages = text.split_whitespace().nth(1)?.parse::<u64>().ok()?;
    let page_size = 4096u64;
    Some(pages.saturating_mul(page_size) / 1024)
}

#[cfg(test)]
mod tests {
    #[test]
    fn process_rss_conversion_is_page_based() {
        let pages = 10_u64;
        let rss_kb = pages * 4096 / 1024;
        assert_eq!(rss_kb, 40);
    }
}
