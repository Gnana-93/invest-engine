"use client";

import {
  Briefcase,
  Heart,
  Home,
  Rocket,
  Sparkles,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { createCustomTemplate, decisionTemplates } from "@/lib/templates";
import { useDecisionStore } from "@/lib/store";
import type { DecisionTemplate, IconName } from "@/lib/types";

const icons: Record<IconName, React.ComponentType<{ className?: string }>> = {
  Heart,
  Briefcase,
  Home,
  Rocket,
  Sparkles,
};

export function TemplateSelector() {
  const setDecision = useDecisionStore((s) => s.setDecision);

  const pick = (template: DecisionTemplate) => {
    // Deep-clone so template edits never leak back into the source list
    setDecision(JSON.parse(JSON.stringify(template)));
  };

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900 sm:text-2xl">
          What decision are you facing?
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Pick a preloaded template and adjust it, or start from scratch.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {decisionTemplates.map((template) => {
          const Icon = icons[(template.icon as IconName) ?? "Sparkles"];
          return (
            <Card
              key={template.id}
              className="flex flex-col transition-all duration-200 hover:shadow-md"
            >
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                    <Icon className="h-5 w-5" />
                  </div>
                  <CardTitle className="text-base leading-snug">
                    {template.title}
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent className="flex flex-1 flex-col justify-between gap-3 pt-0">
                <p className="line-clamp-2 text-sm text-gray-600">
                  {template.description}
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{template.category}</Badge>
                    <span className="text-xs text-gray-400">
                      {template.options.length} options
                    </span>
                  </div>
                  <Button
                    size="sm"
                    className="h-9 bg-indigo-600 hover:bg-indigo-700"
                    onClick={() => pick(template)}
                  >
                    Use This Template
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}

        <Card className="flex flex-col border-dashed transition-all duration-200 hover:shadow-md sm:col-span-2">
          <CardContent className="flex flex-col items-center gap-3 py-6 text-center">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 text-gray-500">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">Create Custom</p>
              <p className="mt-0.5 text-sm text-gray-500">
                Start with 2 empty options and define your own scenarios.
              </p>
            </div>
            <Button
              variant="outline"
              className="h-10"
              onClick={() => pick(createCustomTemplate())}
            >
              Start Custom Decision
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
