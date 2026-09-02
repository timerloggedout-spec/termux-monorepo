import { cn } from "@/lib/utils";
import type { LaneStatus } from "@/lib/operator/types";

const TONE: Record<string, string> = {
  live: "bg-ok",
  green: "bg-ok",
  hold: "bg-warn",
  fail: "bg-fail",
  dirty: "bg-fail",
  extract: "bg-accent",
  parked: "bg-faint",
  skip: "bg-faint",
};

export function StatusDot({ status }: { status: LaneStatus | string }) {
  return (
    <span
      className={cn("inline-block h-1.5 w-1.5 rounded-full", TONE[status] ?? "bg-muted")}
      aria-hidden
    />
  );
}
