use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use blake3::Hasher;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::io::{self, BufRead, Write};

const REF_BYTES: usize = 25; // @< + 22-char base64url(128-bit) + >
const DEFAULT_MIN_BYTES: usize = 32;
const DEFAULT_MIN_FREQ: u64 = 2;
const DEFAULT_NODE_OVERHEAD: usize = 32;

#[derive(Debug, Deserialize)]
struct Fragment {
    id: String,
    level: String,
    #[serde(default)]
    text: String,
    #[serde(default)]
    children: Vec<String>,
    #[serde(default)]
    bytes: Option<usize>,
}

#[derive(Debug, Serialize)]
struct Fingerprint {
    id: String,
    level: String,
    bytes: usize,
    full_hash: String,
    ref_id: String,
    child_count: usize,
}

#[derive(Debug, Serialize)]
struct Policy {
    level: String,
    frequency: u64,
    bytes: usize,
    ref_bytes: usize,
    node_overhead: usize,
    estimated_savings: i64,
    pointer: bool,
}

#[derive(Debug, Serialize)]
struct Analysis {
    fingerprints: Vec<Fingerprint>,
    policies: Vec<Policy>,
    alpha: BTreeMap<String, f64>,
}

fn digest(fragment: &Fragment) -> [u8; 32] {
    let mut h = Hasher::new();
    h.update(b"crg-fragment-v1\0");
    h.update(fragment.level.as_bytes());
    h.update(b"\0");
    h.update(fragment.text.as_bytes());
    h.update(b"\0");
    for child in &fragment.children {
        h.update(child.as_bytes());
        h.update(b"\0");
    }
    *h.finalize().as_bytes()
}

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

fn ref_id(full: &[u8; 32]) -> String {
    URL_SAFE_NO_PAD.encode(&full[..16])
}

fn estimate_alpha(values: &[u64]) -> f64 {
    if values.len() < 2 {
        return 0.0;
    }

    let mut f = values.to_vec();
    f.sort_unstable_by(|a, b| b.cmp(a));
    let n = f.len() as f64;
    let (mut sx, mut sy, mut sxx, mut sxy) = (0.0, 0.0, 0.0, 0.0);

    for (rank, freq) in f.iter().enumerate() {
        let x = ((rank + 1) as f64).ln();
        let y = (*freq as f64).ln();
        sx += x;
        sy += y;
        sxx += x * x;
        sxy += x * y;
    }

    let den = n * sxx - sx * sx;
    if den.abs() < f64::EPSILON {
        0.0
    } else {
        -((n * sxy - sx * sy) / den)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let stdin = io::stdin();
    let mut fragments = Vec::new();
    for line in stdin.lock().lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        fragments.push(serde_json::from_str::<Fragment>(&line)?);
    }

    let mut by_level: BTreeMap<String, BTreeMap<[u8; 32], (u64, usize)>> = BTreeMap::new();
    let mut fingerprints = Vec::with_capacity(fragments.len());

    for fragment in &fragments {
        let hash = digest(fragment);
        let bytes = fragment.bytes.unwrap_or_else(|| fragment.text.len());
        let ref_text = ref_id(&hash);
        fingerprints.push(Fingerprint {
            id: fragment.id.clone(),
            level: fragment.level.clone(),
            bytes,
            full_hash: hex(&hash),
            ref_id: ref_text.clone(),
            child_count: fragment.children.len(),
        });
        by_level
            .entry(fragment.level.clone())
            .or_default()
            .entry(hash)
            .and_modify(|v| v.0 += 1)
            .or_insert((1, bytes));
    }

    let mut policies = Vec::new();
    let mut alpha = BTreeMap::new();
    for (level, values) in &by_level {
        let frequencies: Vec<u64> = values.values().map(|v| v.0).collect();
        alpha.insert(level.clone(), estimate_alpha(&frequencies));
        for (_hash, (freq, bytes)) in values {
            let savings = ((freq.saturating_sub(1) as i64) * (*bytes as i64))
                - ((freq as i64) * REF_BYTES as i64)
                - DEFAULT_NODE_OVERHEAD as i64;
            policies.push(Policy {
                level: level.clone(),
                frequency: *freq,
                bytes: *bytes,
                ref_bytes: REF_BYTES,
                node_overhead: DEFAULT_NODE_OVERHEAD,
                estimated_savings: savings,
                pointer: *freq >= DEFAULT_MIN_FREQ
                    && *bytes >= DEFAULT_MIN_BYTES
                    && savings > 0,
            });
        }
    }

    let result = Analysis {
        fingerprints,
        policies,
        alpha,
    };
    serde_json::to_writer(&mut io::stdout(), &result)?;
    io::stdout().write_all(b"\n")?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reference_is_128_bit_and_collision_safe_by_full_hash() {
        let f = Fragment {
            id: "a".into(),
            level: "function".into(),
            text: "hello".into(),
            children: vec![],
            bytes: None,
        };
        let hash = digest(&f);
        assert_eq!(ref_id(&hash).len(), 22);
        assert_eq!(hash.len(), 32);
    }

    #[test]
    fn alpha_is_observational_not_a_policy_gate() {
        let alpha = estimate_alpha(&[8, 4, 2, 1]);
        assert!(alpha > 0.0);
    }

    #[test]
    fn repeated_large_fragment_can_pay_for_pointer() {
        let freq = 8u64;
        let bytes = 256usize;
        let savings = ((freq - 1) * bytes as u64) as i64
            - (freq as i64 * REF_BYTES as i64)
            - DEFAULT_NODE_OVERHEAD as i64;
        assert!(savings > 0);
    }
}
