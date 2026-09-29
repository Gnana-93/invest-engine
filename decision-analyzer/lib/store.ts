import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { DecisionStore, DecisionTemplate, Option, Scenario } from "./types";

export const useDecisionStore = create<DecisionStore>()(
  persist(
    (set, get) => ({
      currentDecision: null,
      currentStep: 0,
      confidence: 70,

      setDecision: (decision) => {
        set({ currentDecision: decision, currentStep: 1 });
      },

      updateDecisionInfo: (title, description) => {
        const current = get().currentDecision;
        if (!current) return;

        set({
          currentDecision: {
            ...current,
            title,
            description,
          },
        });
      },

      updateOption: (optionId, updates) => {
        const current = get().currentDecision;
        if (!current) return;

        set({
          currentDecision: {
            ...current,
            options: current.options.map((opt) =>
              opt.id === optionId ? { ...opt, ...updates } : opt
            ),
          },
        });
      },

      updateScenario: (optionId, scenarioId, updates) => {
        const current = get().currentDecision;
        if (!current) return;

        set({
          currentDecision: {
            ...current,
            options: current.options.map((opt) =>
              opt.id === optionId
                ? {
                    ...opt,
                    scenarios: opt.scenarios.map((sc) =>
                      sc.id === scenarioId ? { ...sc, ...updates } : sc
                    ),
                  }
                : opt
            ),
          },
        });
      },

      addOption: () => {
        const current = get().currentDecision;
        if (!current || current.options.length >= 5) return;

        const newOption: Option = {
          id: `option-${Date.now()}`,
          name: `Option ${current.options.length + 1}`,
          description: "Describe this option...",
          scenarios: [
            {
              id: `scenario-${Date.now()}-1`,
              description: "Best case scenario",
              probability: 50,
              value: 70,
            },
            {
              id: `scenario-${Date.now()}-2`,
              description: "Worst case scenario",
              probability: 50,
              value: -30,
            },
          ],
        };

        set({
          currentDecision: {
            ...current,
            options: [...current.options, newOption],
          },
        });
      },

      removeOption: (optionId) => {
        const current = get().currentDecision;
        if (!current || current.options.length <= 2) return;

        set({
          currentDecision: {
            ...current,
            options: current.options.filter((opt) => opt.id !== optionId),
          },
        });
      },

      addScenario: (optionId) => {
        const current = get().currentDecision;
        if (!current) return;

        const option = current.options.find((opt) => opt.id === optionId);
        if (!option || option.scenarios.length >= 8) return;

        const newScenario: Scenario = {
          id: `scenario-${Date.now()}`,
          description: "New scenario",
          probability: 0,
          value: 0,
        };

        set({
          currentDecision: {
            ...current,
            options: current.options.map((opt) =>
              opt.id === optionId
                ? { ...opt, scenarios: [...opt.scenarios, newScenario] }
                : opt
            ),
          },
        });
      },

      removeScenario: (optionId, scenarioId) => {
        const current = get().currentDecision;
        if (!current) return;

        const option = current.options.find((opt) => opt.id === optionId);
        if (!option || option.scenarios.length <= 2) return;

        set({
          currentDecision: {
            ...current,
            options: current.options.map((opt) =>
              opt.id === optionId
                ? {
                    ...opt,
                    scenarios: opt.scenarios.filter((sc) => sc.id !== scenarioId),
                  }
                : opt
            ),
          },
        });
      },

      normalizeProbabilities: (optionId) => {
        const current = get().currentDecision;
        if (!current) return;

        const option = current.options.find((opt) => opt.id === optionId);
        if (!option) return;

        const sum = option.scenarios.reduce((acc, sc) => acc + sc.probability, 0);
        if (sum === 0) return;

        set({
          currentDecision: {
            ...current,
            options: current.options.map((opt) =>
              opt.id === optionId
                ? {
                    ...opt,
                    scenarios: opt.scenarios.map((sc) => ({
                      ...sc,
                      probability:
                        Math.round((sc.probability / sum) * 100 * 10) / 10,
                    })),
                  }
                : opt
            ),
          },
        });
      },

      calculateExpectedValues: () => {
        const current = get().currentDecision;
        if (!current) return;

        set({
          currentDecision: {
            ...current,
            options: current.options.map((opt) => ({
              ...opt,
              expectedValue: opt.scenarios.reduce(
                (sum, sc) => sum + (sc.probability / 100) * sc.value,
                0
              ),
            })),
          },
        });
      },

      setStep: (step) => set({ currentStep: step }),

      setConfidence: (confidence) => set({ confidence }),

      reset: () =>
        set({ currentDecision: null, currentStep: 0, confidence: 70 }),
    }),
    {
      name: "decision-storage",
    }
  )
);
