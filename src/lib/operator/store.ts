import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { CycleStep } from "./types";

const STEPS: CycleStep[] = [
  "recon",
  "ops",
  "review",
  "implement",
  "wait",
  "validate",
];

type OperatorStore = {
  step: CycleStep;
  notes: string;
  filter: string;
  setStep: (step: CycleStep) => void;
  advance: () => void;
  setNotes: (notes: string) => void;
  setFilter: (filter: string) => void;
};

export const useOperatorStore = create<OperatorStore>()(
  persist(
    (set, get) => ({
      step: "implement",
      notes: "",
      filter: "",
      setStep: (step) => set({ step }),
      advance: () => {
        const i = STEPS.indexOf(get().step);
        set({ step: STEPS[(i + 1) % STEPS.length] });
      },
      setNotes: (notes) => set({ notes }),
      setFilter: (filter) => set({ filter }),
    }),
    { name: "archwiz-operator-console" },
  ),
);

export { STEPS };
