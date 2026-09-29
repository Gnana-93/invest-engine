"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Footer } from "@/components/landing/Footer";
import { ComparisonTable } from "@/components/results/ComparisonTable";
import { EVComparison } from "@/components/results/EVComparison";
import { ExportButtons } from "@/components/results/ExportButtons";
import { InsightsPanel } from "@/components/results/InsightsPanel";
import { RiskAnalysis } from "@/components/results/RiskAnalysis";
import { ScenarioTable } from "@/components/results/ScenarioTable";
import { ProgressBar } from "@/components/wizard/ProgressBar";
import { useDecisionStore } from "@/lib/store";

export default function ResultsPage() {
  const decision = useDecisionStore((s) => s.currentDecision);
  const step = useDecisionStore((s) => s.currentStep);
  const setStep = useDecisionStore((s) => s.setStep);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-16 text-sm text-gray-400">
        Loading…
      </div>
    );
  }

  if (!decision || step < 2) {
    return (
      <div className="mx-auto flex min-h-dvh max-w-md flex-col items-center justify-center px-4 text-center">
        <p className="text-lg font-semibold text-gray-900">No results yet</p>
        <p className="mt-1 text-sm text-gray-600">
          Pick or build a decision first — results appear after you calculate.
        </p>
        <Button
          asChild
          className="mt-4 h-11 bg-indigo-600 hover:bg-indigo-700"
        >
          <Link href="/analyze">
            <ArrowLeft className="mr-1 h-4 w-4" /> Go to Analyzer
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <div className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 sm:px-6">
        <ProgressBar current={3} />

        <h1 className="mt-4 text-xl font-bold leading-snug text-gray-900 sm:text-2xl">
          {decision.title}
        </h1>
        <p className="mt-1 text-sm text-gray-600">{decision.description}</p>

        <div className="mt-6 space-y-6 pb-8">
          <EVComparison options={decision.options} />

          <Tabs defaultValue="breakdown">
            <TabsList className="flex w-full sm:w-auto">
              <TabsTrigger value="breakdown" className="flex-1 sm:flex-none">
                Breakdown
              </TabsTrigger>
              <TabsTrigger value="risk" className="flex-1 sm:flex-none">
                Risk
              </TabsTrigger>
              <TabsTrigger value="compare" className="flex-1 sm:flex-none">
                Compare
              </TabsTrigger>
            </TabsList>
            <TabsContent value="breakdown" className="mt-3 space-y-3">
              {decision.options.map((option) => (
                <ScenarioTable key={option.id} option={option} />
              ))}
            </TabsContent>
            <TabsContent value="risk" className="mt-3 space-y-3">
              {decision.options.map((option) => (
                <RiskAnalysis key={option.id} option={option} />
              ))}
            </TabsContent>
            <TabsContent value="compare" className="mt-3">
              <ComparisonTable options={decision.options} />
            </TabsContent>
          </Tabs>

          <InsightsPanel options={decision.options} />

          <section>
            <h2 className="mb-2 text-base font-bold text-gray-900">Export</h2>
            <ExportButtons
              title={decision.title}
              description={decision.description}
              options={decision.options}
            />
          </section>

          <div className="pb-4">
            <Button asChild variant="ghost" onClick={() => setStep(1)}>
              <Link href="/analyze">
                <ArrowLeft className="mr-1 h-4 w-4" /> Back to editor
              </Link>
            </Button>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
