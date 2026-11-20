// Example Sentry bootstrap for Rust crates in this monorepo
// (harmonizer-prod_cli, synthegration-cli, workspace/maxc, appliedSxi/maxc)
//
// Cargo.toml:
//   [dependencies]
//   sentry = "0.49.0"

fn main() {
    let _guard = sentry::init((
        "https://8b6f33db85568dc94e5db28dfe5eee72@o4511844213522432.ingest.us.sentry.io/4511844272111616",
        sentry::ClientOptions {
            release: sentry::release_name!(),
            send_default_pii: true,
            ..Default::default()
        },
    ));

    // Sentry will capture this
    panic!("Everything is on fire!");
}
