export type Priority = "P0" | "P1" | "P2" | "P3";
export type LaneStatus =
  | "green"
  | "hold"
  | "dirty"
  | "extract"
  | "parked"
  | "live"
  | "fail"
  | "skip";

export type CycleStep =
  | "recon"
  | "ops"
  | "review"
  | "implement"
  | "wait"
  | "validate";

export type MatrixItem = {
  id: string;
  title: string;
  status: LaneStatus;
  action: string;
  refs: string[];
};

export type PriorityBand = {
  id: Priority;
  title: string;
  blurb: string;
  items: MatrixItem[];
};

export type PullLane = {
  number: number;
  title: string;
  head: string;
  base: string;
  files: number;
  mergeable: string;
  lane: "candidate" | "extract" | "dirty" | "staging" | "superseded";
  notes: string;
};

export type ActionPulse = {
  name: string;
  conclusion: "success" | "failure" | "skipped" | "cancelled";
  event: string;
  note: string;
};

export type MlStage = {
  id: string;
  name: string;
  state: LaneStatus;
  shaBound: boolean;
  live: boolean;
  note: string;
};

export type AgentSeat = {
  name: string;
  role: string;
  status: LaneStatus;
  note: string;
};

export type OperatorSnapshot = {
  generatedAt: string;
  agent: string;
  master: {
    sha: string;
    short: string;
    message: string;
    sheVersion: string;
    publishOnMaster: boolean;
  };
  counts: {
    openIssues: number;
    openPrs: number;
    workflowRunsSampled: number;
  };
  bands: PriorityBand[];
  prs: PullLane[];
  actions: ActionPulse[];
  ml: MlStage[];
  swarm: AgentSeat[];
  hardRules: string[];
  next: string[];
};
