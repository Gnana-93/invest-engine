"use client";

import { Slider } from "@/components/ui/slider";
import { getValueLabel } from "@/lib/calculations";

interface ValueSliderProps {
  value: number;
  onChange: (value: number) => void;
}

export function ValueSlider({ value, onChange }: ValueSliderProps) {
  const colorClass =
    value > 0 ? "text-green-600" : value < 0 ? "text-red-600" : "text-gray-600";

  return (
    <div className="py-2">
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs font-medium text-gray-500">
          Value (how good/bad)
        </span>
        <span className={`text-sm font-bold ${colorClass}`}>
          {value > 0 ? `+${value}` : value} · {getValueLabel(value)}
        </span>
      </div>
      <Slider
        value={[value]}
        onValueChange={(vals) => onChange(vals[0])}
        min={-100}
        max={100}
        step={1}
        aria-label="Scenario value"
        className="[&_[data-slot=slider-thumb]]:h-5 [&_[data-slot=slider-thumb]]:w-5"
      />
    </div>
  );
}
