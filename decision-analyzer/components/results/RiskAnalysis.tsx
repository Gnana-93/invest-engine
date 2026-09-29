"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatEV, getRiskProfile } from "@/lib/calculations";
import type { Option } from "@/lib/types";

export function RiskAnalysis({ option }: { option: Option }) {
  const p = getRiskProfile(option);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">{option.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 pt-0 text-sm">
        <div className="flex justify-between gap-3">
          <span className="shrink-0 text-gray-500">Best case</span>
          <span className="text-right text-green-700">
            {p.bestCase?.description}{" "}
            <strong>(+{p.bestCase?.value})</strong>
          </span>
        </div>
        <div className="flex justify-between gap-3">
          <span className="shrink-0 text-gray-500">Worst case</span>
          <span className="text-right text-red-700">
            {p.worstCase?.description}{" "}
            <strong>({p.worstCase?.value})</strong>
          </span>
        </div>
        <div className="flex justify-between gap-3">
          <span className="shrink-0 text-gray-500">Most likely</span>
          <span className="text-right text-gray-700">
            {p.mostLikely?.description}{" "}
            <strong>({p.mostLikely?.probability}%)</strong>
          </span>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
          <Stat label="Upside" value={`+${p.upsidePotential}`} tone="pos" />
          <Stat label="Downside" value={`−${p.downsideRisk}`} tone="neg" />
          <Stat label="Volatility" value={String(p.volatility)} tone="neutral" />
          <Stat label="Range" value={String(p.range)} tone="neutral" />
        </div>
      </CardContent>
    </Card>
  );
}

function Stat({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "pos" | "neg" | "neutral";
}) {
  const color =
    tone === "pos"
      ? "text-green-600"
      : tone === "neg"
        ? "text-red-600"
        : "text-gray-700";
  return (
    <div className="rounded-md bg-gray-50 px-3 py-2 text-center">
      <div className={`text-base font-bold tabular-nums ${color}`}>{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
