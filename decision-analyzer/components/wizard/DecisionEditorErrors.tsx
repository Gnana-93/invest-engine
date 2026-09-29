"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import type { ValidationIssue } from "@/lib/types";

export function DecisionEditorErrors({
  issues,
}: {
  issues: ValidationIssue[];
}) {
  if (issues.length === 0) return null;

  const errors = issues.filter((i) => i.severity === "error");
  const warnings = issues.filter((i) => i.severity === "warning");

  return (
    <div className="mt-4 space-y-2">
      {errors.length > 0 && (
        <Alert variant="destructive">
          <AlertTitle>
            {errors.length} thing{errors.length > 1 ? "s" : ""} to fix
          </AlertTitle>
          <AlertDescription>
            <ul className="mt-1 list-inside list-disc space-y-0.5 text-sm">
              {errors.slice(0, 5).map((issue, i) => (
                <li key={i}>{issue.message}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}
      {warnings.length > 0 && errors.length === 0 && (
        <p className="text-xs text-yellow-700">
          Tip: {warnings[0].message} — probabilities don&apos;t have to be
          perfect to calculate, but 100% is ideal.
        </p>
      )}
    </div>
  );
}
