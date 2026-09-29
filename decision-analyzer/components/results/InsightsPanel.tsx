"use client";

import { useMemo } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  calculateExpectedValue,
  formatEV,
  getRiskProfile,
} from "@/lib/calculations";
import type { Option } from "@/lib/types";

interface Insight {
  text: string;
  tone: "pos" | "neg" | "neutral";
}

export function InsightsPanel({ options }: { options: Option[] }) {
  const insights = useMemo<Insight[]>(() => {
    if (options.length === 0) return [];

    const list: Insight[] = [];
    const ev = (o: Option) => o.expectedValue ?? calculateExpectedValue(o.scenarios);

    const ranked = [...options].sort((a, b) => ev(b) - ev(a));
    const best = ranked[0];
    const second = ranked[1];
    const worst = ranked[ranked.length - 1];
    const bestProfile = getRiskProfile(best);

    list.push({
      text: `"${best.name}" has the highest expected value (${formatEV(ev(best))}).`,
      tone: "pos",
    });

    if (second) {
      const gap = Math.round((ev(best) - ev(second)) * 10) / 10;
      if (gap < 2) {
        list.push({
          text: `The gap between "${best.name}" and "${second.name}" is only ${gap} points — effectively a tie. Consider risk and reversibility instead.`,
          tone: "neutral",
        });
      } else if (gap < 8) {
        list.push({
          text: `"${best.name}" leads "${second.name}" by ${gap} points — a meaningful but not decisive margin.`,
          tone: "neutral",
        });
      } else {
        list.push({
          text: `"${best.name}" leads "${second.name}" by ${gap} points — a decisive margin.`,
          tone: "pos",
        });
      }
    }

    if (bestProfile.upsidePotential >= bestProfile.downsideRisk) {
      list.push({
        text: `"${best.name}" has favorable asymmetry: upside (+${bestProfile.upsidePotential}) exceeds downside (−${bestProfile.downsideRisk}).`,
        tone: "pos",
      });
    } else {
      list.push({
        text: `"${best.name}" has unfavorable asymmetry: downside (−${bestProfile.downsideRisk}) exceeds upside (+${bestProfile.upsidePotential}). Make sure the worst case is survivable.`,
        tone: "neutral",
      });
    }

    if (ev(worst) < 0) {
      list.push({
        text: `"${worst.name}" has negative expected value (${formatEV(ev(worst))}) — you'd likely be better off avoiding it.`,
        tone: "neg",
      });
    }

    return list;
  }, [options]);

  const toneStyles = {
    pos: "border-green-200 bg-green-50",
    neg: "border-red-200 bg-red-50",
    neutral: "border-gray-200 bg-gray-50",
  } as const;

  return (
    <section className="space-y-2">
      <h2 className="text-base font-bold text-gray-900">Insights</h2>
      {insights.map((insight, i) => (
        <Alert key={i} className={toneStyles[insight.tone]}>
          <AlertDescription className="text-sm text-gray-700">
            {insight.text}
          </AlertDescription>
        </Alert>
      ))}
    </section>
  );
}
