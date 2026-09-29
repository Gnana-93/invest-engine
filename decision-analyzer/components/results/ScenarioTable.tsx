"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  formatEV,
  formatScenarioEV,
  validateProbabilities,
} from "@/lib/calculations";
import type { Option } from "@/lib/types";

export function ScenarioTable({ option }: { option: Option }) {
  const { sum } = validateProbabilities(option.scenarios);
  const ev = option.expectedValue ?? 0;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">{option.name}</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-xs uppercase tracking-wide text-gray-400">
                <th className="py-2 pr-2 font-medium">Scenario</th>
                <th className="py-2 pr-2 text-right font-medium">Prob.</th>
                <th className="py-2 pr-2 text-right font-medium">Value</th>
                <th className="py-2 text-right font-medium">Contribution</th>
              </tr>
            </thead>
            <tbody>
              {option.scenarios.map((s) => (
                <tr key={s.id} className="border-b border-gray-100">
                  <td className="py-2 pr-2 text-gray-700">{s.description}</td>
                  <td className="py-2 pr-2 text-right tabular-nums text-gray-600">
                    {s.probability}%
                  </td>
                  <td
                    className={`py-2 pr-2 text-right tabular-nums ${
                      s.value >= 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {s.value > 0 ? `+${s.value}` : s.value}
                  </td>
                  <td className="py-2 text-right font-semibold tabular-nums">
                    {formatScenarioEV(s)}
                  </td>
                </tr>
              ))}
              <tr className="font-bold">
                <td className="py-2 pr-2">TOTAL</td>
                <td className="py-2 pr-2 text-right tabular-nums">
                  {sum}%
                </td>
                <td />
                <td className={`py-2 text-right tabular-nums ${ev >= 0 ? "text-green-600" : "text-red-600"}`}>
                  {formatEV(ev)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
