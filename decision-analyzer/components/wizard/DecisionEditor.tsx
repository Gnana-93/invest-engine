"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo } from "react";
import { ArrowLeft, ArrowRight, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { hasErrors, validateDecision } from "@/lib/validation";
import { useDecisionStore } from "@/lib/store";
import { DecisionEditorErrors } from "./DecisionEditorErrors";
import { OptionEditor } from "./OptionEditor";
import { ProgressBar } from "./ProgressBar";

export function DecisionEditor() {
  const router = useRouter();
  const decision = useDecisionStore((s) => s.currentDecision);
  const updateDecisionInfo = useDecisionStore((s) => s.updateDecisionInfo);
  const updateOption = useDecisionStore((s) => s.updateOption);
  const updateScenario = useDecisionStore((s) => s.updateScenario);
  const addOption = useDecisionStore((s) => s.addOption);
  const removeOption = useDecisionStore((s) => s.removeOption);
  const addScenario = useDecisionStore((s) => s.addScenario);
  const removeScenario = useDecisionStore((s) => s.removeScenario);
  const normalizeProbabilities = useDecisionStore(
    (s) => s.normalizeProbabilities
  );
  const calculateExpectedValues = useDecisionStore(
    (s) => s.calculateExpectedValues
  );
  const setStep = useDecisionStore((s) => s.setStep);

  const issues = useMemo(
    () => (decision ? validateDecision(decision) : []),
    [decision]
  );
  const blocked = hasErrors(issues);

  if (!decision) return null;

  const goResults = () => {
    calculateExpectedValues();
    setStep(2);
    router.push("/results");
  };

  return (
    <div>
      <ProgressBar current={2} />

      <section className="mt-4">
        <label
          htmlFor="decision-title"
          className="mb-1 block text-xs font-medium text-gray-500"
        >
          Your decision
        </label>
        <Input
          id="decision-title"
          value={decision.title}
          onChange={(e) =>
            updateDecisionInfo(e.target.value, decision.description)
          }
          className="min-h-11 text-base font-semibold"
        />
        <Textarea
          aria-label="Decision description"
          value={decision.description}
          onChange={(e) => updateDecisionInfo(decision.title, e.target.value)}
          rows={2}
          className="mt-2 min-h-11 resize-y text-sm"
        />
      </section>

      <DecisionEditorErrors issues={issues} />

      <div className="mt-4 space-y-4">
        {decision.options.map((option, index) => (
          <OptionEditor
            key={option.id}
            option={option}
            optionNumber={index + 1}
            canRemove={decision.options.length > 2}
            onOptionUpdate={(updates) => updateOption(option.id, updates)}
            onScenarioUpdate={(scenarioId, updates) =>
              updateScenario(option.id, scenarioId, updates)
            }
            onAddScenario={() => addScenario(option.id)}
            onRemoveScenario={(scenarioId) =>
              removeScenario(option.id, scenarioId)
            }
            onNormalize={() => normalizeProbabilities(option.id)}
            onRemoveOption={() => removeOption(option.id)}
          />
        ))}
      </div>

      {decision.options.length < 5 && (
        <Button
          type="button"
          variant="outline"
          className="mt-4 h-11 w-full border-dashed"
          onClick={addOption}
        >
          <Plus className="mr-1 h-4 w-4" /> Add option
        </Button>
      )}

      <div className="sticky bottom-0 -mx-4 mt-6 flex items-center justify-between gap-3 border-t border-gray-200 bg-white/95 px-4 py-3 backdrop-blur sm:-mx-6 sm:px-6">
        <Button asChild variant="ghost" className="h-11">
          <Link href="/analyze" onClick={() => setStep(0)}>
            <ArrowLeft className="mr-1 h-4 w-4" /> Back
          </Link>
        </Button>
        <Button
          className="h-11 bg-indigo-600 px-6 hover:bg-indigo-700"
          disabled={blocked}
          onClick={goResults}
          title={
            blocked
              ? "Fix the highlighted errors to continue"
              : "Calculate expected values"
          }
        >
          Calculate Results <ArrowRight className="ml-1 h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
