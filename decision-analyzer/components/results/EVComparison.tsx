"use client";

import {
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getEVBg, getEVColor, formatEV, getBestOption } from "@/lib/calculations";
import type { Option } from "@/lib/types";

interface EVComparisonProps {
  options: Option[];
}

export function EVComparison({ options }: EVComparisonProps) {
  const best = getBestOption(options);

  const data = options.map((opt) => ({
    name: opt.name.length > 18 ? `${opt.name.slice(0, 17)}…` : opt.name,
    fullName: opt.name,
    ev: Math.round((opt.expectedValue ?? 0) * 10) / 10,
  }));

  return (
    <section>
      {best && (
        <div className="mb-4 rounded-lg border-2 border-indigo-200 bg-indigo-50 p-4 text-center">
          <p className="text-sm text-indigo-900">
            Based on expected value analysis,{" "}
            <strong className="text-base">{best.name}</strong> is the best
            choice with an EV of{" "}
            <strong className={getEVColor(best.expectedValue ?? 0)}>
              {formatEV(best.expectedValue ?? 0)}
            </strong>
          </p>
        </div>
      )}

      <div className="rounded-lg border border-gray-200 bg-white p-3 sm:p-4">
        <h3 className="mb-2 text-sm font-semibold text-gray-700">
          Expected Value Comparison
        </h3>
        <div className="h-64 w-full sm:h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ top: 24, right: 8, bottom: 0, left: -16 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, fill: "#6B7280" }}
                interval={0}
                tickLine={false}
              />
              <YAxis
                domain={[-100, 100]}
                tick={{ fontSize: 11, fill: "#9CA3AF" }}
                tickLine={false}
              />
              <Tooltip
                formatter={(value) => [formatEV(Number(value)), "Expected Value"]}
                labelFormatter={(_, payload) =>
                  payload?.[0]?.payload?.fullName ?? ""
                }
                contentStyle={{
                  fontSize: 12,
                  borderRadius: 8,
                  border: "1px solid #E5E7EB",
                }}
              />
              <ReferenceLine y={0} stroke="#9CA3AF" />
              <Bar dataKey="ev" radius={[4, 4, 0, 0]} maxBarSize={72}>
                {data.map((entry, i) => (
                  <Cell key={i} fill={entry.ev >= 0 ? "#10B981" : "#EF4444"} />
                ))}
                <LabelList
                  dataKey="ev"
                  position="top"
                  formatter={(value) => formatEV(Number(value))}
                  style={{ fontSize: 11, fontWeight: 700, fill: "#374151" }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-2 text-center text-xs text-gray-400">
          Green = positive expected value · Red = negative · Scale −100 to +100
        </p>
      </div>
    </section>
  );
}
