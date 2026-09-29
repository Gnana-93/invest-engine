import type { Option, Scenario } from "./types";

export function calculateExpectedValue(scenarios: Scenario[]): number {
  return scenarios.reduce((sum, scenario) => {
    return sum + (scenario.probability / 100) * scenario.value;
  }, 0);
}

export function probabilitySum(scenarios: Scenario[]): number {
  return scenarios.reduce((acc, s) => acc + s.probability, 0);
}

export function validateProbabilities(scenarios: Scenario[]): {
  isValid: boolean;
  sum: number;
  difference: number;
} {
  const sum = probabilitySum(scenarios);
  const difference = Math.abs(sum - 100);

  return {
    isValid: difference < 0.1,
    sum: Math.round(sum * 10) / 10,
    difference: Math.round(difference * 10) / 10,
  };
}

export function normalizeProbabilities(scenarios: Scenario[]): Scenario[] {
  const sum = probabilitySum(scenarios);
  if (sum === 0) return scenarios;

  return scenarios.map((s) => ({
    ...s,
    probability: Math.round((s.probability / sum) * 100 * 10) / 10,
  }));
}

export function getBestOption(options: Option[]): Option | null {
  if (options.length === 0) return null;

  return options.reduce((best, current) => {
    const bestEV = best.expectedValue ?? -Infinity;
    const currentEV = current.expectedValue ?? -Infinity;
    return currentEV > bestEV ? current : best;
  });
}

export function getWorstOption(options: Option[]): Option | null {
  if (options.length === 0) return null;

  return options.reduce((worst, current) => {
    const worstEV = worst.expectedValue ?? Infinity;
    const currentEV = current.expectedValue ?? Infinity;
    return currentEV < worstEV ? current : worst;
  });
}

export function getBestScenario(option: Option): Scenario | null {
  if (option.scenarios.length === 0) return null;
  return option.scenarios.reduce((best, current) =>
    current.value > best.value ? current : best
  );
}

export function getWorstScenario(option: Option): Scenario | null {
  if (option.scenarios.length === 0) return null;
  return option.scenarios.reduce((worst, current) =>
    current.value < worst.value ? current : worst
  );
}

export function getMostLikelyScenario(option: Option): Scenario | null {
  if (option.scenarios.length === 0) return null;
  return option.scenarios.reduce((mostLikely, current) =>
    current.probability > mostLikely.probability ? current : mostLikely
  );
}

/** Population standard deviation of scenario values, weighted by probability. */
export function getVolatility(option: Option): number {
  if (option.scenarios.length === 0) return 0;
  const ev = option.expectedValue ?? calculateExpectedValue(option.scenarios);
  const variance = option.scenarios.reduce(
    (acc, s) => acc + (s.probability / 100) * Math.pow(s.value - ev, 2),
    0
  );
  return Math.sqrt(variance);
}

export function formatEV(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}`;
}

export function formatScenarioEV(scenario: Scenario): string {
  const contribution = (scenario.probability / 100) * scenario.value;
  return formatEV(contribution);
}

export function getEVColor(value: number): string {
  if (value > 40) return "text-green-600";
  if (value > 0) return "text-green-500";
  if (value === 0) return "text-gray-600";
  if (value > -20) return "text-gray-600";
  if (value > -40) return "text-red-500";
  return "text-red-600";
}

export function getEVBg(value: number): string {
  if (value > 40) return "bg-green-600";
  if (value > 0) return "bg-green-500";
  if (value > -20) return "bg-gray-400";
  if (value > -40) return "bg-red-400";
  return "bg-red-600";
}

export function getValueLabel(value: number): string {
  if (value >= 80) return "Excellent";
  if (value >= 60) return "Very Good";
  if (value >= 40) return "Good";
  if (value >= 20) return "Okay";
  if (value >= 0) return "Neutral";
  if (value >= -20) return "Slightly Negative";
  if (value >= -40) return "Negative";
  if (value >= -60) return "Very Negative";
  return "Extremely Negative";
}

export function getProbabilityLabel(probability: number): string {
  if (probability >= 80) return "Very Likely";
  if (probability >= 60) return "Likely";
  if (probability >= 40) return "Possible";
  if (probability >= 20) return "Unlikely";
  return "Very Unlikely";
}

export interface RiskProfile {
  bestCase: Scenario | null;
  worstCase: Scenario | null;
  mostLikely: Scenario | null;
  upsidePotential: number; // best - EV
  downsideRisk: number; // EV - worst
  volatility: number;
  range: number; // best - worst
}

export function getRiskProfile(option: Option): RiskProfile {
  const bestCase = getBestScenario(option);
  const worstCase = getWorstScenario(option);
  const ev = option.expectedValue ?? calculateExpectedValue(option.scenarios);

  return {
    bestCase,
    worstCase,
    mostLikely: getMostLikelyScenario(option),
    upsidePotential: bestCase ? Math.round((bestCase.value - ev) * 10) / 10 : 0,
    downsideRisk: worstCase ? Math.round((ev - worstCase.value) * 10) / 10 : 0,
    volatility: Math.round(getVolatility(option) * 10) / 10,
    range:
      bestCase && worstCase
        ? Math.round((bestCase.value - worstCase.value) * 10) / 10
        : 0,
  };
}

/** Plain-text summary used by the Copy to Clipboard export. */
export function buildExportText(
  title: string,
  description: string,
  options: Option[]
): string {
  const lines: string[] = [];
  lines.push(`DECISION ANALYSIS`);
  lines.push(`=================`);
  lines.push(``);
  lines.push(title);
  lines.push(description);
  lines.push(``);

  const ranked = [...options].sort(
    (a, b) => (b.expectedValue ?? -Infinity) - (a.expectedValue ?? -Infinity)
  );

  lines.push(`RECOMMENDATION: ${ranked[0]?.name ?? "N/A"}`);
  lines.push(
    `Expected Value: ${formatEV(ranked[0]?.expectedValue ?? 0)} (on a -100 to +100 scale)`
  );
  lines.push(``);

  ranked.forEach((opt, i) => {
    const profile = getRiskProfile(opt);
    lines.push(`${i + 1}. ${opt.name} — EV ${formatEV(opt.expectedValue ?? 0)}`);
    lines.push(`   Best case: ${profile.bestCase?.description ?? "-"} (+${profile.bestCase?.value ?? 0})`);
    lines.push(`   Worst case: ${profile.worstCase?.description ?? "-"} (${profile.worstCase?.value ?? 0})`);
    lines.push(`   Most likely: ${profile.mostLikely?.description ?? "-"} (${profile.mostLikely?.probability ?? 0}%)`);
    lines.push(`   Upside: +${profile.upsidePotential} | Downside risk: ${profile.downsideRisk} | Volatility: ${profile.volatility}`);
    lines.push(`   Scenarios:`);
    opt.scenarios.forEach((sc) => {
      lines.push(
        `   - [${sc.probability}%] ${sc.description} → value ${sc.value}, contributes ${formatScenarioEV(sc)}`
      );
    });
    lines.push(``);
  });

  lines.push(`Generated by Scenario Decision Analyzer`);
  return lines.join("\n");
}
