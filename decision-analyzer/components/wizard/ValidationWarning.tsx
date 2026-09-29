"use client";

import { Button } from "@/components/ui/button";
import { validateProbabilities } from "@/lib/calculations";
import type { Scenario } from "@/lib/types";

interface ValidationWarningProps {
  scenarios: Scenario[];
  onNormalize: () => void;
}

export function ValidationWarning({
  scenarios,
  onNormalize,
}: ValidationWarningProps) {
  const { isValid, sum, difference } = validateProbabilities(scenarios);

  if (isValid) {
    return (
      <div className="flex items-center gap-2 rounded-md bg-green-50 px-3 py-2 text-sm text-green-700">
        <span aria-hidden>✓</span>
        Probabilities sum to 100%
      </div>
    );
  }

  const near = difference <= 1;

  return (
    <div
      className={`flex flex-wrap items-center justify-between gap-2 rounded-md px-3 py-2 text-sm ${
        near
          ? "bg-yellow-50 text-yellow-800"
          : "bg-red-50 text-red-700"
      }`}
      role="status"
    >
      <span>
        Probabilities sum to <strong>{sum}%</strong> — should be 100% (off by{" "}
        {difference}%)
      </span>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className={`h-8 ${
          near
            ? "border-yellow-400 text-yellow-800 hover:bg-yellow-100"
            : "border-red-300 text-red-700 hover:bg-red-100"
        }`}
        onClick={onNormalize}
      >
        Normalize to 100%
      </Button>
    </div>
  );
}
