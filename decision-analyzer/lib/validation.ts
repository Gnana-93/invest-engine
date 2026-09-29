import { z } from "zod";
import type { DecisionTemplate, ValidationIssue } from "./types";
import { validateProbabilities } from "./calculations";

export const scenarioSchema = z.object({
  description: z
    .string()
    .trim()
    .min(10, "Scenario description needs at least 10 characters"),
  probability: z
    .number()
    .min(0, "Probability can't be below 0%")
    .max(100, "Probability can't exceed 100%"),
  value: z
    .number()
    .min(-100, "Value can't be below -100")
    .max(100, "Value can't exceed +100"),
  explanation: z.string().optional(),
});

export const optionSchema = z.object({
  name: z.string().trim().min(3, "Option name needs at least 3 characters"),
  description: z
    .string()
    .trim()
    .min(10, "Option description needs at least 10 characters"),
  scenarios: z
    .array(scenarioSchema)
    .min(2, "Each option needs at least 2 scenarios")
    .max(8, "An option can have at most 8 scenarios"),
});

export const decisionSchema = z.object({
  title: z.string().trim().min(10, "Decision title needs at least 10 characters"),
  description: z
    .string()
    .trim()
    .min(20, "Decision description needs at least 20 characters"),
  options: z
    .array(optionSchema)
    .min(2, "You need at least 2 options to compare")
    .max(5, "You can compare at most 5 options"),
});

export type DecisionValidation = z.infer<typeof decisionSchema>;

/**
 * Full decision validation: zod field rules + cross-field rules
 * (probability sums per option). Returns flat issue list for the UI.
 */
export function validateDecision(decision: DecisionTemplate): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  const base = decisionSchema.safeParse({
    title: decision.title,
    description: decision.description,
    options: decision.options.map((o) => ({
      name: o.name,
      description: o.description,
      scenarios: o.scenarios.map((s) => ({
        description: s.description,
        probability: s.probability,
        value: s.value,
        explanation: s.explanation,
      })),
    })),
  });

  if (!base.success) {
    for (const issue of base.error.issues) {
      issues.push({
        field: issue.path.join("."),
        message: issue.message,
        severity: "error",
      });
    }
  }

  // Cross-field rule: each option's probabilities should sum to 100 (±0.1)
  decision.options.forEach((opt) => {
    const { isValid, sum, difference } = validateProbabilities(opt.scenarios);
    if (!isValid) {
      issues.push({
        optionId: opt.id,
        field: `probabilities.${opt.id}`,
        message:
          sum === 0
            ? `"${opt.name}": probabilities are all 0 — set them to add up to 100%`
            : `"${opt.name}": probabilities add up to ${sum}% (should be 100%, off by ${difference}%)`,
        severity: difference <= 1 ? "warning" : "error",
      });
    }
  });

  return issues;
}

export function hasErrors(issues: ValidationIssue[]): boolean {
  return issues.some((i) => i.severity === "error");
}
