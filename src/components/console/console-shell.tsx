import { useMemo, useState } from "react";
import {
  Activity,
  GitPullRequest,
  Layers,
  Radar,
  Shield,
  Users,
} from "lucide-react";
import { SNAPSHOT } from "@/lib/operator/snapshot";
import { STEPS, useOperatorStore } from "@/lib/operator/store";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { StatusDot } from "./status-dot";
import { cn } from "@/lib/utils";
import type { CycleStep, LaneStatus } from "@/lib/operator/types";

const NAV = [
  { id: "matrix", label: "Matrix", icon: Layers },
  { id: "prs", label: "PRs", icon: GitPullRequest },
  { id: "actions", label: "Actions", icon: Activity },
  { id: "ml", label: "ML", icon: Radar },
  { id: "swarm", label: "Swarm", icon: Users },
] as const;

type Tab = (typeof NAV)[number]["id"];

const STEP_COPY: Record<CycleStep, string> = {
  recon: "Inventory HEAD, issues, PRs, Actions, skills.",
  ops: "Classify dirty vs extract. Never wholesale.",
  review: "Dual-gate evidence only. Non-gate reviewers ack_pending.",
  implement: "Small SHA-bound slices on current master.",
  wait: "Let checks settle. Do not comment-loop.",
  validate: "repo_gate + termux_smoke, then ratchet.",
};

export function ConsoleShell() {
  const [tab, setTab] = useState<Tab>("matrix");
  const { step, notes, filter, setStep, advance, setNotes, setFilter } =
    useOperatorStore();
  const q = filter.trim().toLowerCase();

  const bands = useMemo(
    () =>
      SNAPSHOT.bands
        .map((band) => ({
          ...band,
          items: band.items.filter((item) =>
            !q
              ? true
              : `${item.title} ${item.action} ${item.refs.join(" ")}`
                  .toLowerCase()
                  .includes(q),
          ),
        }))
        .filter((band) => band.items.length > 0 || !q),
    [q],
  );

  const prs = useMemo(
    () =>
      SNAPSHOT.prs.filter((pr) =>
        !q ? true : `${pr.number} ${pr.title} ${pr.notes}`.toLowerCase().includes(q),
      ),
    [q],
  );

  const failCount = SNAPSHOT.actions.filter((a) => a.conclusion === "failure").length;
  const holdCount = SNAPSHOT.prs.filter((p) => p.lane === "candidate").length;

  return (
    <div className="min-h-dvh bg-bg text-fg">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(1200px_600px_at_80%_-10%,rgba(200,205,214,0.05),transparent_55%)]" />
      <header className="relative border-b border-border">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="min-w-0">
            <p className="font-mono text-[0.6875rem] uppercase tracking-[0.22em] text-muted">
              termux-monorepo · issue 175
            </p>
            <h1 className="mt-1 font-display text-3xl font-medium tracking-[-0.03em] text-fg sm:text-4xl">
              ArchW1z Operator
            </h1>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted">
              Priority matrix, PR lanes, Actions pulse, and SHA-bound ML lineage.
              Master stays functional. Dirty stacks are extracted, never swallowed.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="live">master {SNAPSHOT.master.short}</Badge>
            <Badge tone="live">SHE {SNAPSHOT.master.sheVersion}</Badge>
            <Badge tone={SNAPSHOT.master.publishOnMaster ? "live" : "hold"}>
              publish {SNAPSHOT.master.publishOnMaster ? "on" : "absent"}
            </Badge>
            <Badge tone={failCount ? "fail" : "live"}>
              {failCount ? `${failCount} action fail` : "gates live"}
            </Badge>
          </div>
        </div>
      </header>

      <div className="relative mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_280px]">
        <main className="min-w-0">
          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <nav className="flex gap-1 overflow-x-auto rounded-lg bg-surface p-1" aria-label="Console views">
              {NAV.map((item) => {
                const Icon = item.icon;
                const active = tab === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setTab(item.id)}
                    className={cn(
                      "inline-flex h-11 min-w-11 shrink-0 items-center gap-2 rounded-md px-3 text-sm font-medium transition-colors duration-[var(--motion-quick)]",
                      active ? "bg-subtle text-fg" : "text-muted hover:text-fg",
                    )}
                    aria-current={active ? "page" : undefined}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="hidden sm:inline">{item.label}</span>
                  </button>
                );
              })}
            </nav>
            <label className="block min-w-0 sm:w-64">
              <span className="sr-only">Filter matrix</span>
              <input
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Filter issues, PRs, refs"
                className="h-11 w-full rounded-md border border-border bg-surface px-3 text-sm text-fg placeholder:text-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </label>
          </div>

          {tab === "matrix" && (
            <section className="grid gap-4">
              {bands.map((band) => (
                <article
                  key={band.id}
                  className="rounded-lg border border-border bg-surface p-4 sm:p-5"
                >
                  <div className="flex items-baseline justify-between gap-3">
                    <h2 className="font-display text-xl tracking-[-0.02em]">
                      <span className="text-muted">{band.id}</span> {band.title}
                    </h2>
                    <span className="font-mono text-[0.6875rem] text-faint">
                      {band.items.length} live
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-muted">{band.blurb}</p>
                  <ul className="mt-4 grid gap-3">
                    {band.items.map((item) => (
                      <li
                        key={item.id}
                        className="rounded-md border border-border bg-subtle p-3 sm:p-4"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <StatusDot status={item.status} />
                          <h3 className="text-sm font-medium">{item.title}</h3>
                          <Badge tone={item.status as LaneStatus}>{item.status}</Badge>
                        </div>
                        <p className="mt-2 text-sm leading-relaxed text-muted">{item.action}</p>
                        <p className="mt-2 font-mono text-[0.6875rem] text-faint">
                          {item.refs.join(" · ")}
                        </p>
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </section>
          )}

          {tab === "prs" && (
            <section className="overflow-hidden rounded-lg border border-border bg-surface">
              <div className="border-b border-border px-4 py-3">
                <h2 className="font-display text-xl">PR lanes</h2>
                <p className="mt-1 text-sm text-muted">
                  {holdCount} merge candidates held. Staging stays off master.
                </p>
              </div>
              <ul className="divide-y divide-border">
                {prs.map((pr) => (
                  <li key={pr.number} className="px-4 py-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-sm text-muted">#{pr.number}</span>
                      <h3 className="text-sm font-medium">{pr.title}</h3>
                      <Badge tone={pr.lane}>{pr.lane}</Badge>
                      <Badge tone="hold">{pr.mergeable}</Badge>
                    </div>
                    <p className="mt-2 text-sm leading-relaxed text-muted">{pr.notes}</p>
                    <p className="mt-2 font-mono text-[0.6875rem] text-faint">
                      {pr.head} → {pr.base}
                      {pr.files ? ` · ${pr.files} files` : ""}
                    </p>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {tab === "actions" && (
            <section className="grid gap-3">
              {SNAPSHOT.actions.map((run) => (
                <article
                  key={run.name}
                  className="rounded-lg border border-border bg-surface p-4"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusDot
                      status={
                        run.conclusion === "success"
                          ? "live"
                          : run.conclusion === "failure"
                            ? "fail"
                            : "skip"
                      }
                    />
                    <h3 className="text-sm font-medium">{run.name}</h3>
                    <Badge
                      tone={
                        run.conclusion === "success"
                          ? "live"
                          : run.conclusion === "failure"
                            ? "fail"
                            : "skip"
                      }
                    >
                      {run.conclusion}
                    </Badge>
                    <span className="font-mono text-[0.6875rem] text-faint">{run.event}</span>
                  </div>
                  <p className="mt-2 text-sm text-muted">{run.note}</p>
                </article>
              ))}
            </section>
          )}

          {tab === "ml" && (
            <section className="grid gap-3 sm:grid-cols-2">
              {SNAPSHOT.ml.map((stage) => (
                <article
                  key={stage.id}
                  className="rounded-lg border border-border bg-surface p-4"
                >
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-medium">{stage.name}</h3>
                    <Badge tone={stage.state}>{stage.state}</Badge>
                  </div>
                  <dl className="mt-3 grid grid-cols-2 gap-2 font-mono text-[0.6875rem] text-muted">
                    <div>
                      <dt className="text-faint">SHA-bound</dt>
                      <dd>{stage.shaBound ? "yes" : "no"}</dd>
                    </div>
                    <div>
                      <dt className="text-faint">Live</dt>
                      <dd>{stage.live ? "on" : "observer"}</dd>
                    </div>
                  </dl>
                  <p className="mt-3 text-sm leading-relaxed text-muted">{stage.note}</p>
                </article>
              ))}
            </section>
          )}

          {tab === "swarm" && (
            <section className="grid gap-3">
              {SNAPSHOT.swarm.map((agent) => (
                <article
                  key={agent.name}
                  className="flex flex-col gap-2 rounded-lg border border-border bg-surface p-4 sm:flex-row sm:items-start sm:justify-between"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <StatusDot status={agent.status} />
                      <h3 className="text-sm font-medium">{agent.name}</h3>
                    </div>
                    <p className="mt-1 text-xs uppercase tracking-wider text-faint">
                      {agent.role}
                    </p>
                    <p className="mt-2 text-sm text-muted">{agent.note}</p>
                  </div>
                  <Badge tone={agent.status}>{agent.status}</Badge>
                </article>
              ))}
            </section>
          )}
        </main>

        <aside className="flex flex-col gap-4">
          <section className="rounded-lg border border-border bg-surface p-4">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-lg">Cycle</h2>
              <Button size="sm" variant="secondary" onClick={advance}>
                Advance
              </Button>
            </div>
            <ol className="mt-3 grid gap-1">
              {STEPS.map((id) => (
                <li key={id}>
                  <button
                    type="button"
                    onClick={() => setStep(id)}
                    className={cn(
                      "flex w-full items-start gap-3 rounded-md px-2 py-2 text-left transition-colors duration-[var(--motion-quick)]",
                      step === id ? "bg-subtle" : "hover:bg-subtle/60",
                    )}
                  >
                    <span
                      className={cn(
                        "mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full",
                        step === id ? "bg-accent" : "bg-faint",
                      )}
                    />
                    <span>
                      <span className="block text-sm font-medium capitalize">{id}</span>
                      <span className="block text-xs leading-relaxed text-muted">
                        {STEP_COPY[id]}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ol>
          </section>

          <section className="rounded-lg border border-border bg-surface p-4">
            <h2 className="flex items-center gap-2 font-display text-lg">
              <Shield className="h-4 w-4 text-muted" />
              Hard rules
            </h2>
            <ul className="mt-3 grid gap-2">
              {SNAPSHOT.hardRules.map((rule) => (
                <li key={rule} className="text-sm leading-relaxed text-muted">
                  {rule}
                </li>
              ))}
            </ul>
          </section>

          <section className="rounded-lg border border-border bg-surface p-4">
            <h2 className="font-display text-lg">Next</h2>
            <ol className="mt-3 grid list-decimal gap-2 pl-4">
              {SNAPSHOT.next.map((item) => (
                <li key={item} className="text-sm leading-relaxed text-muted">
                  {item}
                </li>
              ))}
            </ol>
          </section>

          <section className="rounded-lg border border-border bg-surface p-4">
            <h2 className="font-display text-lg">Operator log</h2>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Local notes stay on this device."
              rows={5}
              className="mt-3 w-full resize-y rounded-md border border-border bg-subtle p-3 text-sm text-fg placeholder:text-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            <p className="mt-2 font-mono text-[0.6875rem] text-faint">
              snapshot {SNAPSHOT.generatedAt}
            </p>
          </section>
        </aside>
      </div>
    </div>
  );
}
