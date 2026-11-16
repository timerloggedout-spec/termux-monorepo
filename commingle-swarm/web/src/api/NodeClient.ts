const BASE = "http://localhost:8080";

export async function status() {
  const res = await fetch(`${BASE}/status`);
  return res.json();
}

export async function proposeTrade(payload: any) {
  const res = await fetch(`${BASE}/proposeTrade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function getPlans() {
  const res = await fetch(`${BASE}/plans`);
  return res.json();
}

export async function getVault(clientId?: string) {
  const url = clientId ? `${BASE}/vault/${clientId}` : `${BASE}/vault`;
  const res = await fetch(url);
  return res.json();
}
