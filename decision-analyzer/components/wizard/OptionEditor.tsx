"use client";

import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { calculateExpectedValue, formatEV, getEVColor } from "@/lib/calculations";
import type { Option, Scenario } from "@/lib/types";
import { ScenarioEditor } from "./ScenarioEditor";
import { ValidationWarning } from "./ValidationWarning";

interface OptionEditorProps {
  option: Option;
  optionNumber: number;
  canRemove: boolean;
  onOptionUpdate: (updates: Partial<Option>) => void;
  onScenarioUpdate: (scenarioId: string, updates: Partial<Scenario>) => void;
  onAddScenario: () => void;
  onRemoveScenario: (scenarioId: string) => void;
  onNormalize: () => void;
  onRemoveOption: () => void;
}

export function OptionEditor({
  option,
  optionNumber,
  canRemove,
  onOptionUpdate,
  onScenarioUpdate,
  onAddScenario,
  onRemoveScenario,
  onNormalize,
  onRemoveOption,
}: OptionEditorProps) {
  const ev = option.expectedValue ?? calculateExpectedValue(option.scenarios);

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">
              {optionNumber}
            </span>
            Option
          </CardTitle>
          <div className="flex items-center gap-2">
            <span
              className={`rounded-md bg-gray-50 px-2 py-1 text-sm font-bold ${getEVColor(ev)}`}
              title="Expected value"
            >
              EV {formatEV(ev)}
            </span>
            {canRemove && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-9 w-9 text-gray-400 hover:bg-red-50 hover:text-red-600"
                aria-label={`Remove ${option.name}`}
                onClick={onRemoveOption}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
        <div className="mt-2 space-y-2">
          <Input
            value={option.name}
            onChange={(e) => onOptionUpdate({ name: e.target.value })}
            placeholder="Option name"
            aria-label={`Option ${optionNumber} name`}
            className="min-h-11 text-sm font-medium"
          />
          <Textarea
            value={option.description}
            onChange={(e) => onOptionUpdate({ description: e.target.value })}
            placeholder="What does choosing this option involve?"
            rows={2}
            aria-label={`Option ${optionNumber} description`}
            className="min-h-11 resize-y text-sm"
          />
        </div>
      </CardHeader>
      <CardContent className="space-y-3 pt-0">
        <ValidationWarning scenarios={option.scenarios} onNormalize={onNormalize} />

        <Accordion type="multiple" className="rounded-md border border-gray-200">
          {option.scenarios.map((scenario, index) => (
            <ScenarioEditor
              key={scenario.id}
              scenario={scenario}
              canDelete={option.scenarios.length > 2}
              onUpdate={(updates) => onScenarioUpdate(scenario.id, updates)}
              onRemove={() => onRemoveScenario(scenario.id)}
            />
          ))}
        </Accordion>

        {option.scenarios.length < 8 && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="h-9 w-full border-dashed"
            onClick={onAddScenario}
          >
            <Plus className="mr-1 h-4 w-4" /> Add scenario
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
