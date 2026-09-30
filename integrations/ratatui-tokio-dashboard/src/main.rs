use crossterm::event::{self, Event, KeyCode};
use ratatui::prelude::*;
use ratatui::widgets::{Bar, BarChart, Block, Gauge, Paragraph, Row, Sparkline, Table};
use std::io;
use std::time::Duration;
use tokio::sync::mpsc;

use ratatui_tokio_dashboard::{
    AppEvent, DashboardState, InputAction, STREAM_COUNT, StreamUpdate, metrics::sample_system,
};

struct TerminalGuard;

impl Drop for TerminalGuard {
    fn drop(&mut self) {
        ratatui::restore();
    }
}

#[tokio::main(flavor = "multi_thread")]
async fn main() -> io::Result<()> {
    let mut terminal = ratatui::init();
    let _guard = TerminalGuard;
    run(&mut terminal).await
}

async fn run(terminal: &mut ratatui::DefaultTerminal) -> io::Result<()> {
    let (tx, mut rx) = mpsc::channel::<AppEvent>(128);
    let mut tasks = Vec::new();

    tasks.push(tokio::spawn(metrics_task(tx.clone())));
    tasks.push(tokio::spawn(stream_task(tx.clone())));
    tasks.push(tokio::task::spawn_blocking(move || input_task(tx)));

    let mut app = DashboardState::new();

    loop {
        if app.dirty {
            terminal.draw(|frame| render(frame, &app))?;
            app.dirty = false;
            app.redraws = app.redraws.saturating_add(1);
        }

        let Some(event) = rx.recv().await else {
            break;
        };

        let quit = matches!(event, AppEvent::Input(InputAction::Quit));
        app.apply(event);

        while let Ok(event) = rx.try_recv() {
            let quit_now = matches!(event, AppEvent::Input(InputAction::Quit));
            app.apply(event);
            if quit_now {
                break;
            }
        }

        if quit {
            break;
        }
    }

    for task in tasks {
        task.abort();
    }

    Ok(())
}

async fn metrics_task(tx: mpsc::Sender<AppEvent>) {
    let mut interval = tokio::time::interval(Duration::from_millis(750));
    let mut previous = None;

    loop {
        interval.tick().await;
        let snapshot = sample_system(&mut previous);
        if tx.send(AppEvent::Metrics(snapshot)).await.is_err() {
            break;
        }
    }
}

async fn stream_task(tx: mpsc::Sender<AppEvent>) {
    let mut interval = tokio::time::interval(Duration::from_millis(125));
    let mut tick = 0u64;

    loop {
        interval.tick().await;

        for stream in 0..STREAM_COUNT {
            let phase = tick.wrapping_add((stream as u64) * 17);
            let latency_ms = (phase.wrapping_mul(13) % 71).min(70);
            let throughput = 10 + (phase.wrapping_mul(29) % 91);
            let active = phase % 11 != 0;

            if tx
                .send(AppEvent::Stream(StreamUpdate {
                    stream,
                    latency_ms,
                    throughput,
                    active,
                }))
                .await
                .is_err()
            {
                return;
            }
        }

        tick = tick.wrapping_add(1);
    }
}

fn input_task(tx: mpsc::Sender<AppEvent>) {
    loop {
        match event::poll(Duration::from_millis(250)) {
            Ok(true) => match event::read() {
                Ok(Event::Key(key)) => {
                    let action = match key.code {
                        KeyCode::Char('q') | KeyCode::Esc => InputAction::Quit,
                        KeyCode::Up | KeyCode::Char('k') => InputAction::Up,
                        KeyCode::Down | KeyCode::Char('j') => InputAction::Down,
                        KeyCode::Char('r') => InputAction::Refresh,
                        _ => continue,
                    };

                    if tx.blocking_send(AppEvent::Input(action)).is_err() {
                        return;
                    }

                    if action == InputAction::Quit {
                        return;
                    }
                }
                Ok(Event::Resize(_, _)) => {
                    if tx.blocking_send(AppEvent::Resize).is_err() {
                        return;
                    }
                }
                Ok(_) => {}
                Err(_) => return,
            },
            Ok(false) => {}
            Err(_) => return,
        }
    }
}

fn render(frame: &mut Frame<'_>, app: &DashboardState) {
    let root = frame.area();

    if root.width < 80 || root.height < 24 {
        frame.render_widget(
            Paragraph::new("Terminal too small — resize to at least 80x24")
                .block(Block::bordered().title("RATATUI // TOKIO")),
            root,
        );
        return;
    }

    let vertical = Layout::vertical([
        Constraint::Length(2),
        Constraint::Percentage(58),
        Constraint::Percentage(40),
        Constraint::Length(1),
    ])
    .spacing(1)
    .split(root);

    let title = Paragraph::new(
        "RATATUI // TOKIO  •  TERMUX SYSTEM DASHBOARD  •  q:quit  ↑↓:stream  r:refresh",
    )
    .block(Block::bordered().title("ARCHW1Z TUI"))
    .style(Style::default().fg(Color::Cyan));
    frame.render_widget(title, vertical[0]);

    let main = Layout::horizontal([Constraint::Percentage(38), Constraint::Percentage(62)])
        .spacing(1)
        .split(vertical[1]);

    render_streams(frame, app, main[0]);
    render_charts(frame, app, main[1]);

    let lower = Layout::horizontal([Constraint::Percentage(50), Constraint::Percentage(50)])
        .spacing(1)
        .split(vertical[2]);

    render_processes(frame, app, lower[0]);
    render_runtime(frame, app, lower[1]);

    let footer = Paragraph::new(format!(
        " redraws={}  coalesced={}  cores={}  load={:.2}  mem={}%  last_update={}ms ago",
        app.redraws,
        app.skipped_draws,
        app.cpu_cores,
        app.load_1m,
        app.memory_percent,
        app.last_update.elapsed().as_millis()
    ));
    frame.render_widget(footer, vertical[3]);
}

fn render_streams(frame: &mut Frame<'_>, app: &DashboardState, area: Rect) {
    let rows = app.streams.iter().map(|stream| {
        let marker = if stream.active { "●" } else { "○" };
        let selected = if stream.stream == app.selected_stream {
            ">"
        } else {
            " "
        };

        Row::new(vec![
            format!("{selected}{marker} stream-{}", stream.stream + 1),
            format!("{:>4}ms", stream.latency_ms),
            format!("{:>4}/s", stream.throughput),
        ])
    });

    let table = Table::new(
        rows,
        [
            Constraint::Percentage(55),
            Constraint::Percentage(20),
            Constraint::Percentage(25),
        ],
    )
    .header(Row::new(vec!["ACTIVE STREAM", "LATENCY", "THROUGHPUT"]))
    .block(Block::bordered().title("TOKIO EVENT STREAMS"));

    frame.render_widget(table, area);
}

fn render_charts(frame: &mut Frame<'_>, app: &DashboardState, area: Rect) {
    let split = Layout::vertical([
        Constraint::Percentage(34),
        Constraint::Percentage(33),
        Constraint::Percentage(33),
    ])
    .spacing(1)
    .split(area);

    let cpu_data: Vec<u64> = app.cpu_history.iter().copied().collect();
    let throughput_data: Vec<u64> = app.throughput_history.iter().copied().collect();

    let cpu = Sparkline::default()
        .block(Block::bordered().title(format!("CPU {}%", app.cpu_percent)))
        .data(&cpu_data)
        .max(100)
        .style(Style::default().fg(Color::Green));
    frame.render_widget(cpu, split[0]);

    let throughput = Sparkline::default()
        .block(Block::bordered().title("THROUGHPUT (events/s)"))
        .data(&throughput_data)
        .max(800)
        .style(Style::default().fg(Color::Blue));
    frame.render_widget(throughput, split[1]);

    let bars = app
        .streams
        .iter()
        .map(|stream| Bar::with_label(format!("{}", stream.stream + 1), stream.latency_ms))
        .collect::<Vec<_>>();

    let latency = BarChart::new(bars)
        .block(Block::bordered().title("STREAM LATENCY"))
        .bar_width(3)
        .bar_gap(1)
        .max(75)
        .style(Style::default().fg(Color::Yellow));

    frame.render_widget(latency, split[2]);
}

fn render_processes(frame: &mut Frame<'_>, app: &DashboardState, area: Rect) {
    let rows = app.processes.iter().map(|process| {
        Row::new(vec![
            process.pid.to_string(),
            truncate(&process.command, 20),
            format!("{} MB", process.rss_kb / 1024),
        ])
    });

    let table = Table::new(
        rows,
        [
            Constraint::Length(8),
            Constraint::Percentage(62),
            Constraint::Percentage(28),
        ],
    )
    .header(Row::new(vec!["PID", "COMMAND", "RSS"]))
    .block(Block::bordered().title("ACTIVE BACKGROUND PROCESSES"));

    frame.render_widget(table, area);
}

fn render_runtime(frame: &mut Frame<'_>, app: &DashboardState, area: Rect) {
    let split =
        Layout::vertical([Constraint::Percentage(45), Constraint::Percentage(55)]).split(area);

    let gauges = Layout::horizontal([Constraint::Percentage(50), Constraint::Percentage(50)])
        .spacing(1)
        .split(split[0]);

    let cpu = Gauge::default()
        .block(Block::bordered().title("CPU %"))
        .gauge_style(Style::default().fg(Color::Green))
        .label(format!("{}%", app.cpu_percent))
        .ratio(f64::from(app.cpu_percent) / 100.0);
    frame.render_widget(cpu, gauges[0]);

    let memory = Gauge::default()
        .block(Block::bordered().title(format!(
            "MEMORY {} / {} MB",
            app.memory_used_kb / 1024,
            app.memory_total_kb / 1024
        )))
        .gauge_style(Style::default().fg(Color::Magenta))
        .label(format!("{}%", app.memory_percent))
        .ratio(f64::from(app.memory_percent) / 100.0);
    frame.render_widget(memory, gauges[1]);

    let selected = app
        .selected()
        .map(|stream| {
            format!(
                "stream-{}  active={}  latency={}ms  throughput={}/s",
                stream.stream + 1,
                stream.active,
                stream.latency_ms,
                stream.throughput
            )
        })
        .unwrap_or_else(|| "no stream selected".to_string());

    let text = vec![
        Line::from("RUNTIME"),
        Line::from(format!("Tokio workers: {}", app.cpu_cores)),
        Line::from(format!("Streams: {}", app.streams.len())),
        Line::from(format!("Selected: {selected}")),
        Line::from(""),
        Line::from("Dirty redraw policy: ON"),
        Line::from("Metric fallback: /proc + graceful zero"),
    ];

    frame.render_widget(
        Paragraph::new(text).block(Block::bordered().title("THREAD POOL / RUNTIME")),
        split[1],
    );
}

fn truncate(value: &str, max: usize) -> String {
    if value.chars().count() <= max {
        return value.to_string();
    }

    let mut result = value
        .chars()
        .take(max.saturating_sub(1))
        .collect::<String>();
    result.push('…');
    result
}
