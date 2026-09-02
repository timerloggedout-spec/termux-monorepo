import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-sm px-2 py-0.5 font-mono text-[0.6875rem] font-medium uppercase tracking-wider",
  {
    variants: {
      tone: {
        live: "bg-ok/15 text-ok",
        green: "bg-ok/15 text-ok",
        hold: "bg-warn/15 text-warn",
        fail: "bg-fail/15 text-fail",
        dirty: "bg-fail/15 text-fail",
        extract: "bg-accent/12 text-accent",
        parked: "bg-subtle text-muted",
        skip: "bg-subtle text-muted",
        candidate: "bg-ok/15 text-ok",
        staging: "bg-accent/12 text-accent",
        superseded: "bg-subtle text-muted",
      },
    },
    defaultVariants: { tone: "hold" },
  },
);

export function Badge({
  className,
  tone,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return <span className={cn(badgeVariants({ tone, className }))} {...props} />;
}
