use serde::{Deserialize, Serialize};
use std::{
    io::{self, Read},
    time::Duration,
};
use swarms_rs::{
    llm::provider::openai::OpenAI,
    structs::{agent::Agent, sequential_workflow::SequentialWorkflow},
};
use url::Url;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Config {
    task: String,
    model: String,
    number_agents: u8,
    max_loops: u8,
    execute: bool,
    max_tokens: Option<u64>,
    timeout_seconds: Option<u64>,
}

#[derive(Serialize)]
#[serde(tag = "status", rename_all = "lowercase")]
enum ResultDocument {
    Complete {
        backend: &'static str,
        output: serde_json::Value,
        passes: Vec<serde_json::Value>,
    },
    Error {
        error: String,
    },
}

fn validate_base(value: &str) -> Result<String, &'static str> {
    if value.chars().any(char::is_whitespace) || value.contains('\\') {
        return Err("invalid LLM API base URL");
    }
    let authority = value
        .split_once("://")
        .map(|(_, rest)| rest.split('/').next().unwrap_or_default());
    if authority.is_some_and(|authority| authority.contains('@')) {
        return Err("LLM API base URL must not contain userinfo");
    }
    let mut parsed = Url::parse(value).map_err(|_| "invalid LLM API base URL")?;
    if parsed.scheme() != "http" && parsed.scheme() != "https" {
        return Err("LLM API base URL must use HTTP or HTTPS");
    }
    if !parsed.username().is_empty()
        || parsed.password().is_some()
        || parsed.query().is_some()
        || parsed.fragment().is_some()
    {
        return Err("LLM API base URL must not contain userinfo, query, or fragment");
    }
    if parsed.host_str().is_none() {
        return Err("LLM API base URL must have a host");
    }
    if parsed.port() == Some(0) {
        return Err("LLM API base URL port must be positive");
    }
    if parsed.scheme() == "http" {
        let loopback = match parsed.host() {
            Some(url::Host::Domain(host)) => host.eq_ignore_ascii_case("localhost"),
            Some(url::Host::Ipv4(ip)) => ip.is_loopback(),
            Some(url::Host::Ipv6(ip)) => ip.is_loopback(),
            None => false,
        };
        if !loopback {
            return Err("cleartext HTTP is allowed only for loopback");
        }
    }
    let path = parsed.path().trim_end_matches('/').to_owned();
    parsed.set_path(if path.is_empty() { "/" } else { &path });
    Ok(parsed.to_string().trim_end_matches('/').to_owned())
}

fn validate_config(config: &Config) -> Result<(u64, u64), &'static str> {
    if config.task.trim().is_empty() {
        return Err("task must not be empty");
    }
    if config.model.trim().is_empty() {
        return Err("model must not be empty");
    }
    if !(1..=2).contains(&config.number_agents) {
        return Err("number_agents must be between 1 and 2");
    }
    if !(1..=3).contains(&config.max_loops) {
        return Err("max_loops must be between 1 and 3");
    }
    if !config.execute {
        return Err("execute must be true");
    }
    let tokens = config.max_tokens.unwrap_or(8192);
    if tokens == 0 {
        return Err("max_tokens must be positive");
    }
    let timeout = config.timeout_seconds.unwrap_or(120);
    if timeout == 0 {
        return Err("timeout_seconds must be positive");
    }
    Ok((tokens, timeout))
}

fn make_agent(client: &OpenAI, name: &str, max_tokens: u64) -> Box<dyn Agent> {
    Box::new(
        client
            .agent_builder()
            .agent_name(name)
            .system_prompt(format!(
                "You are the {name}. Complete only the provided task."
            ))
            .max_loops(1)
            .retry_attempts(1)
            .max_tokens(max_tokens)
            .disable_task_complete_tool()
            .verbose(false)
            .pretty_print_on(false)
            .build(),
    )
}

async fn run(
    config: Config,
    base: String,
    max_tokens: u64,
) -> Result<ResultDocument, &'static str> {
    let key = std::env::var("LLM_API_HUB_KEY").unwrap_or_else(|_| "local".to_owned());
    let client = OpenAI::from_url(base, key).set_model(config.model.clone());
    let mut task = config.task;
    let mut passes = Vec::with_capacity(config.max_loops as usize);
    for pass in 1..=config.max_loops {
        let output = if config.number_agents == 1 {
            let agent = make_agent(&client, "swarms-rs-worker", max_tokens);
            let value = agent
                .run(task.clone())
                .await
                .map_err(|_| "agent execution failed")?;
            serde_json::Value::String(value)
        } else {
            let agents = vec![
                make_agent(&client, "researcher", max_tokens),
                make_agent(&client, "reviewer", max_tokens),
            ];
            let workflow = SequentialWorkflow::builder()
                .name("termux-swarms-rs-worker")
                .metadata_output_dir(format!("./metadata/pass-{pass}"))
                .agents(agents)
                .build();
            let conversation = workflow
                .run(task.clone())
                .await
                .map_err(|_| "workflow execution failed")?;
            serde_json::to_value(conversation).map_err(|_| "conversation serialization failed")?
        };
        task = match &output {
            serde_json::Value::String(text) => text.clone(),
            other => {
                serde_json::to_string(other).map_err(|_| "conversation serialization failed")?
            }
        };
        passes.push(output);
    }
    let output = passes.last().cloned().ok_or("no pass completed")?;
    Ok(ResultDocument::Complete {
        backend: "swarms-rs",
        output,
        passes,
    })
}

fn write_result(result: &ResultDocument) -> io::Result<()> {
    std::fs::write("./result.json", serde_json::to_vec(result)?)
}

#[tokio::main]
async fn main() {
    let result = match execute().await {
        Ok(result) => result,
        Err(message) => ResultDocument::Error {
            error: message.to_owned(),
        },
    };
    if write_result(&result).is_err() {
        eprintln!("worker could not write result.json");
        std::process::exit(2);
    }
    if matches!(result, ResultDocument::Error { .. }) {
        std::process::exit(2);
    }
}

async fn execute() -> Result<ResultDocument, &'static str> {
    let mut input = String::new();
    io::stdin()
        .read_to_string(&mut input)
        .map_err(|_| "could not read configuration")?;
    let config: Config = serde_json::from_str(&input).map_err(|_| "invalid JSON configuration")?;
    let (max_tokens, timeout) = validate_config(&config)?;
    let configured_base =
        std::env::var("LLM_API_HUB_BASE").unwrap_or_else(|_| "http://127.0.0.1:8787/v1".to_owned());
    let base = validate_base(&configured_base)?;
    tokio::time::timeout(Duration::from_secs(timeout), run(config, base, max_tokens))
        .await
        .map_err(|_| "workflow timed out")?
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn accepts_secure_and_loopback_bases_and_normalizes_slash() {
        assert_eq!(
            validate_base("http://127.0.0.1:8787/v1///").unwrap(),
            "http://127.0.0.1:8787/v1"
        );
        assert_eq!(
            validate_base("https://api.example/v1/").unwrap(),
            "https://api.example/v1"
        );
        assert_eq!(
            validate_base("http://[::1]:8787/v1").unwrap(),
            "http://[::1]:8787/v1"
        );
    }
    #[test]
    fn rejects_unsafe_bases() {
        for bad in [
            "http://example.com/v1",
            "ftp://localhost/a",
            "https://u:p@example.com/v1",
            "https://example.com/v1?x=y",
            "https://example.com/#x",
            "https://@example.com/v1",
            "https://example.com:0/v1",
            "https://example.com/a b",
            "https://example.com\\evil/v1",
        ] {
            assert!(validate_base(bad).is_err(), "accepted {bad}");
        }
    }
    #[test]
    fn bounds_config_before_network() {
        let cfg: Config = serde_json::from_str(
            r#"{"task":"x","model":"m","number_agents":2,"max_loops":3,"execute":true}"#,
        )
        .unwrap();
        assert_eq!(validate_config(&cfg).unwrap(), (8192, 120));
        let mut bad: Config = serde_json::from_str(
            r#"{"task":"x","model":"m","number_agents":3,"max_loops":1,"execute":true}"#,
        )
        .unwrap();
        assert!(validate_config(&bad).is_err());
        bad.number_agents = 1;
        bad.execute = false;
        assert!(validate_config(&bad).is_err());
    }
    #[test]
    fn rejects_unknown_configuration_keys() {
        assert!(serde_json::from_str::<Config>(r#"{"task":"x","model":"m","number_agents":1,"max_loops":1,"execute":true,"surprise":1}"#).is_err());
    }
}
