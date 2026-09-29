"use client";

import { Slider } from "@/components/ui/slider";
import { getProbabilityLabel } from "@/lib/calculations";

interface ProbabilitySliderProps {
  value: number;
  onChange: (value: number) => void;
}

export function ProbabilitySlider({ value, onChange }: ProbabilitySliderProps) {
  return (
    <div className="py-2">
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs font-medium text-gray-500">Probability</span>
        <span className="text-sm font-bold text-indigo-600">
          {value}% · {getProbabilityLabel(value)}
        </span>
      </div>
      <Slider
        value={[value]}
        onValueChange={(vals) => onChange(vals[0])}
        min={0}
        max={100}
        step={1}
        aria-label="Scenario probability"
        className="[&_[data-slot=slider-thumb]]:h-5 [&_[data-slot=slider-thumb]]:w-5 [&_[data-slot=slider-thumb]]:border-indigo-600 [&_[data-slot=slider-thumb]]:bg-indigo-600"
      />
    </div>
  );
}
