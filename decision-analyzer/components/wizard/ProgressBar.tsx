"use client";

import { cn } from "@/lib/utils";

const steps = ["Template", "Edit", "Results"];

interface ProgressBarProps {
  current: number; // 1..3
}

export function ProgressBar({ current }: ProgressBarProps) {
  return (
    <div className="flex items-center gap-2" aria-label={`Step ${current} of 3`}>
      {steps.map((label, i) => {
        const stepNumber = i + 1;
        const isDone = stepNumber < current;
        const isCurrent = stepNumber === current;
        return (
          <div key={label} className="flex items-center gap-2">
            <div
              className={cn(
                "flex h-7 items-center gap-1.5 rounded-full px-2.5 text-xs font-semibold",
                isCurrent && "bg-indigo-600 text-white",
                isDone && "bg-indigo-100 text-indigo-700",
                !isCurrent && !isDone && "bg-gray-100 text-gray-400"
              )}
            >
              <span>{isDone ? "✓" : stepNumber}</span>
              <span className="hidden sm:inline">{label}</span>
            </div>
            {i < steps.length - 1 && (
              <div
                className={cn(
                  "h-px w-4 sm:w-8",
                  stepNumber < current ? "bg-indigo-300" : "bg-gray-200"
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
