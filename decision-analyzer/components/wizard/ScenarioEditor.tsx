"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { formatScenarioEV } from "@/lib/calculations";
import type { Scenario } from "@/lib/types";
import { ProbabilitySlider } from "./ProbabilitySlider";
import { ValueSlider } from "./ValueSlider";

interface ScenarioEditorProps {
  scenario: Scenario;
  canDelete: boolean;
  onUpdate: (updates: Partial<Scenario>) => void;
  onRemove: () => void;
}

export function ScenarioEditor({
  scenario,
  canDelete,
  onUpdate,
  onRemove,
}: ScenarioEditorProps) {
  return (
    <AccordionItem value={scenario.id} className="border-gray-200">
      <AccordionTrigger className="py-3 text-left hover:no-underline">
        <span className="flex w-full items-center justify-between gap-3 pr-2">
          <span className="line-clamp-1 flex-1 text-sm font-medium text-gray-800">
            {scenario.description || "Untitled scenario"}
          </span>
          <span className="flex shrink-0 items-center gap-2 text-xs">
            <span className="rounded bg-indigo-50 px-2 py-0.5 font-semibold text-indigo-700">
              {scenario.probability}%
            </span>
            <span
              className={`rounded px-2 py-0.5 font-semibold ${
                scenario.value >= 0
                  ? "bg-green-50 text-green-700"
                  : "bg-red-50 text-red-700"
              }`}
            >
              {scenario.value > 0 ? `+${scenario.value}` : scenario.value}
            </span>
            <span className="hidden text-gray-400 sm:inline">
              EV {formatScenarioEV(scenario)}
            </span>
          </span>
        </span>
      </AccordionTrigger>
      <AccordionContent className="pb-4">
        <div className="space-y-3">
          <div>
            <label
              htmlFor={`scenario-desc-${scenario.id}`}
              className="mb-1 block text-xs font-medium text-gray-500"
            >
              What happens
            </label>
            <Textarea
              id={`scenario-desc-${scenario.id}`}
              value={scenario.description}
              onChange={(e) => onUpdate({ description: e.target.value })}
              rows={2}
              className="min-h-11 resize-y text-sm"
              placeholder="Describe this outcome"
            />
          </div>

          <ProbabilitySlider
            value={scenario.probability}
            onChange={(probability) => onUpdate({ probability })}
          />
          <ValueSlider
            value={scenario.value}
            onChange={(value) => onUpdate({ value })}
          />

          <div>
            <label
              htmlFor={`scenario-exp-${scenario.id}`}
              className="mb-1 block text-xs font-medium text-gray-500"
            >
              Why these numbers? (optional)
            </label>
            <Textarea
              id={`scenario-exp-${scenario.id}`}
              value={scenario.explanation ?? ""}
              onChange={(e) => onUpdate({ explanation: e.target.value })}
              rows={2}
              className="min-h-11 resize-y text-sm"
              placeholder="Your reasoning, so future-you remembers"
            />
          </div>

          {canDelete && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-9 text-red-600 hover:bg-red-50 hover:text-red-700"
              onClick={onRemove}
            >
              Delete scenario
            </Button>
          )}
        </div>
      </AccordionContent>
    </AccordionItem>
  );
}
