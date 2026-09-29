export interface Scenario {
  id: string;
  description: string;
  probability: number; // 0-100
  value: number; // -100 to +100
  explanation?: string;
}

export interface Option {
  id: string;
  name: string;
  description: string;
  scenarios: Scenario[];
  expectedValue?: number;
}

export interface DecisionTemplate {
  id: string;
  title: string;
  description: string;
  category: string;
  icon?: string;
  options: Option[];
}

export type IconName = "Heart" | "Briefcase" | "Home" | "Rocket" | "Sparkles";

export interface ValidationIssue {
  optionId?: string;
  field: string;
  message: string;
  severity: "error" | "warning";
}

export interface DecisionStore {
  currentDecision: DecisionTemplate | null;
  currentStep: number; // 1 = template chosen/edit, 2 = results ready
  confidence: number; // 0-100, user confidence in probabilities

  setDecision: (decision: DecisionTemplate) => void;
  updateDecisionInfo: (title: string, description: string) => void;
  updateOption: (optionId: string, updates: Partial<Option>) => void;
  updateScenario: (
    optionId: string,
    scenarioId: string,
    updates: Partial<Scenario>
  ) => void;
  addOption: () => void;
  removeOption: (optionId: string) => void;
  addScenario: (optionId: string) => void;
  removeScenario: (optionId: string, scenarioId: string) => void;
  normalizeProbabilities: (optionId: string) => void;
  calculateExpectedValues: () => void;
  setStep: (step: number) => void;
  setConfidence: (confidence: number) => void;
  reset: () => void;
}
