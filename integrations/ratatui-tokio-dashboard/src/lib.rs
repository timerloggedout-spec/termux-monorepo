pub mod metrics;

use std::collections::VecDeque;
use std::time::Instant;

pub const HISTORY_LEN: usize = 48;
pub const STREAM_COUNT: usize = 6;

#[derive(Debug, Clone, PartialEq)]
pub struct ProcessInfo {
    pub pid: u32,
    pub command: String,
    pub rss_kb: u64,
}

#[derive(Debug, Clone, PartialEq)]
pub struct SystemSnapshot {
    pub cpu_percent: u8,
    pub memory_percent: u8,
    pub memory_used_kb: u64,
    pub memory_total_kb: u64,
    pub load_1m: f64,
    pub processes: Vec<ProcessInfo>,
    pub cpu_cores: usize,
}

#[derive(Debug, Clone, PartialEq)]
pub struct StreamUpdate {
    pub stream: usize,
    pub latency_ms: u64,
    pub throughput: u64,
    pub active: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum InputAction {
    Quit,
    Up,
    Down,
    Refresh,
}

#[derive(Debug, Clone, PartialEq)]
pub enum AppEvent {
    Metrics(SystemSnapshot),
    Stream(StreamUpdate),
    Input(InputAction),
    Resize,
}

#[derive(Debug)]
pub struct DashboardState {
    pub cpu_percent: u8,
    pub memory_percent: u8,
    pub memory_used_kb: u64,
    pub memory_total_kb: u64,
    pub load_1m: f64,
    pub cpu_cores: usize,
    pub processes: Vec<ProcessInfo>,
    pub cpu_history: VecDeque<u64>,
    pub throughput_history: VecDeque<u64>,
    pub streams: Vec<StreamUpdate>,
    pub selected_stream: usize,
    pub dirty: bool,
    pub redraws: u64,
    pub skipped_draws: u64,
    pub last_update: Instant,
    stream_batch_mask: u8,
}

impl DashboardState {
    pub fn new() -> Self {
        let streams = (0..STREAM_COUNT)
            .map(|stream| StreamUpdate {
                stream,
                latency_ms: 0,
                throughput: 0,
                active: false,
            })
            .collect();

        Self {
            cpu_percent: 0,
            memory_percent: 0,
            memory_used_kb: 0,
            memory_total_kb: 0,
            load_1m: 0.0,
            cpu_cores: 1,
            processes: Vec::new(),
            cpu_history: VecDeque::with_capacity(HISTORY_LEN),
            throughput_history: VecDeque::with_capacity(HISTORY_LEN),
            streams,
            selected_stream: 0,
            dirty: true,
            redraws: 0,
            skipped_draws: 0,
            last_update: Instant::now(),
            stream_batch_mask: 0,
        }
    }

    pub fn apply(&mut self, event: AppEvent) -> bool {
        let changed = match event {
            AppEvent::Metrics(snapshot) => {
                let changed = self.cpu_percent != snapshot.cpu_percent
                    || self.memory_percent != snapshot.memory_percent
                    || self.memory_used_kb != snapshot.memory_used_kb
                    || self.memory_total_kb != snapshot.memory_total_kb
                    || (self.load_1m - snapshot.load_1m).abs() > f64::EPSILON
                    || self.processes != snapshot.processes
                    || self.cpu_cores != snapshot.cpu_cores;

                self.cpu_percent = snapshot.cpu_percent;
                self.memory_percent = snapshot.memory_percent;
                self.memory_used_kb = snapshot.memory_used_kb;
                self.memory_total_kb = snapshot.memory_total_kb;
                self.load_1m = snapshot.load_1m;
                self.processes = snapshot.processes;
                self.cpu_cores = snapshot.cpu_cores;
                push_history(&mut self.cpu_history, self.cpu_percent as u64);
                changed
            }
            AppEvent::Stream(update) => {
                if let Some(current) = self.streams.get_mut(update.stream) {
                    let changed = *current != update;
                    *current = update;
                    self.stream_batch_mask |= 1u8 << update.stream;
                    let all_streams = (1u8 << STREAM_COUNT) - 1;
                    if self.stream_batch_mask == all_streams {
                        let throughput = self.streams.iter().map(|s| s.throughput).sum();
                        push_history(&mut self.throughput_history, throughput);
                        self.stream_batch_mask = 0;
                    }
                    changed
                } else {
                    false
                }
            }
            AppEvent::Input(action) => match action {
                InputAction::Quit => false,
                InputAction::Up => {
                    let next = self.selected_stream.saturating_sub(1);
                    let changed = next != self.selected_stream;
                    self.selected_stream = next;
                    changed
                }
                InputAction::Down => {
                    let next = (self.selected_stream + 1).min(self.streams.len().saturating_sub(1));
                    let changed = next != self.selected_stream;
                    self.selected_stream = next;
                    changed
                }
                InputAction::Refresh => true,
            },
            AppEvent::Resize => true,
        };

        if changed {
            self.dirty = true;
            self.last_update = Instant::now();
        } else {
            self.skipped_draws = self.skipped_draws.saturating_add(1);
        }
        changed
    }

    pub fn selected(&self) -> Option<&StreamUpdate> {
        self.streams.get(self.selected_stream)
    }
}

impl Default for DashboardState {
    fn default() -> Self {
        Self::new()
    }
}

fn push_history(history: &mut VecDeque<u64>, value: u64) {
    if history.len() == HISTORY_LEN {
        history.pop_front();
    }
    history.push_back(value);
}

#[cfg(test)]
mod tests {
    use super::*;

    fn snapshot(cpu: u8) -> SystemSnapshot {
        SystemSnapshot {
            cpu_percent: cpu,
            memory_percent: 40,
            memory_used_kb: 100,
            memory_total_kb: 250,
            load_1m: 0.5,
            processes: vec![],
            cpu_cores: 4,
        }
    }

    #[test]
    fn identical_metrics_do_not_mark_dashboard_dirty_twice() {
        let mut app = DashboardState::new();
        assert!(app.apply(AppEvent::Metrics(snapshot(20))));
        app.dirty = false;
        assert!(!app.apply(AppEvent::Metrics(snapshot(20))));
        assert!(!app.dirty);
    }

    #[test]
    fn stream_selection_is_bounded() {
        let mut app = DashboardState::new();
        for _ in 0..100 {
            app.apply(AppEvent::Input(InputAction::Down));
        }
        assert_eq!(app.selected_stream, STREAM_COUNT - 1);
        for _ in 0..100 {
            app.apply(AppEvent::Input(InputAction::Up));
        }
        assert_eq!(app.selected_stream, 0);
    }

    #[test]
    fn throughput_history_accepts_out_of_order_streams() {
        let mut app = DashboardState::new();

        for stream in [3, 0, 5, 2, 4, 1] {
            assert!(app.apply(AppEvent::Stream(StreamUpdate {
                stream,
                latency_ms: 10,
                throughput: (stream as u64) + 1,
                active: true,
            })));
        }

        assert_eq!(app.throughput_history.len(), 1);
        assert_eq!(
            app.throughput_history.back().copied(),
            Some((1..=STREAM_COUNT as u64).sum())
        );
    }

    #[test]
    fn throughput_history_is_bounded() {
        let mut app = DashboardState::new();

        for batch in 0..(HISTORY_LEN + 10) {
            for stream in 0..STREAM_COUNT {
                app.apply(AppEvent::Stream(StreamUpdate {
                    stream,
                    latency_ms: batch as u64,
                    throughput: batch as u64 + stream as u64,
                    active: true,
                }));
            }
        }

        assert_eq!(app.throughput_history.len(), HISTORY_LEN);
    }

    #[test]
    fn history_is_bounded() {
        let mut app = DashboardState::new();
        for cpu in 0..(HISTORY_LEN + 10) {
            app.apply(AppEvent::Metrics(snapshot(cpu as u8)));
        }
        assert_eq!(app.cpu_history.len(), HISTORY_LEN);
    }
}
