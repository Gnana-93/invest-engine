"use client";

import { formatEV, getRiskProfile } from "@/lib/calculations";
import type { Option } from "@/lib/types";

export function ComparisonTable({ options }: { options: Option[] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
      <table className="w-full min-w-[560px] text-sm">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <th className="px-3 py-2.5 font-medium">Metric</th>
            {options.map((o) => (
              <th key={o.id} className="px-3 py-2.5 font-medium">
                {o.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <Row label="Expected Value" options={options} render={(o) => (
            <span className={`font-bold ${(o.expectedValue ?? 0) >= 0 ? "text-green-600" : "text-red-600"}`}>
              {formatEV(o.expectedValue ?? 0)}
            </span>
          )} />
          <Row label="Best case" options={options} render={(o) => `+${getRiskProfile(o).bestCase?.value ?? 0}`} />
          <Row label="Worst case" options={options} render={(o) => String(getRiskProfile(o).worstCase?.value ?? 0)} />
          <Row label="Range" options={options} render={(o) => String(getRiskProfile(o).range)} />
          <Row label="Volatility (std dev)" options={options} render={(o) => String(getRiskProfile(o).volatility)} />
          <Row label="Most likely outcome" options={options} render={(o) => (
            <span className="text-gray-600">{getRiskProfile(o).mostLikely?.description}</span>
          )} />
        </tbody>
      </table>
    </div>
  );
}

function Row({
  label,
  options,
  render,
}: {
  label: string;
  options: Option[];
  render: (o: Option) => React.ReactNode;
}) {
  return (
    <tr className="border-b border-gray-100 last:border-0">
      <td className="px-3 py-2.5 font-medium text-gray-500">{label}</td>
      {options.map((o) => (
        <td key={o.id} className="px-3 py-2.5 tabular-nums">
          {render(o)}
        </td>
      ))}
    </tr>
  );
}
