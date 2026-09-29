"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Footer } from "@/components/landing/Footer";
import { DecisionEditor } from "@/components/wizard/DecisionEditor";
import { TemplateSelector } from "@/components/wizard/TemplateSelector";
import { useDecisionStore } from "@/lib/store";

export default function AnalyzePage() {
  const decision = useDecisionStore((s) => s.currentDecision);
  const step = useDecisionStore((s) => s.currentStep);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return <div className="min-h-dvh" />;
  }

  const showEditor = decision !== null && step >= 1;

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="border-b border-gray-100">
        <div className="mx-auto flex w-full max-w-3xl items-center justify-between px-4 py-3 sm:px-6">
          <Link
            href="/"
            className="text-sm font-bold text-gray-900 hover:text-indigo-600"
          >
            ← Scenario Decision Analyzer
          </Link>
          <span className="text-xs text-gray-400">Autosaves as you edit</span>
        </div>
      </header>

      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-5 sm:px-6 sm:py-8">
        {showEditor ? <DecisionEditor /> : <TemplateSelector />}
      </main>

      <Footer />
    </div>
  );
}
