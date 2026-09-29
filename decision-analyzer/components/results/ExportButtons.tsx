"use client";

import { useState } from "react";
import { Check, Copy, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { buildExportText } from "@/lib/calculations";
import { useDecisionStore } from "@/lib/store";
import type { Option } from "@/lib/types";

interface ExportButtonsProps {
  title: string;
  description: string;
  options: Option[];
}

export function ExportButtons({ title, description, options }: ExportButtonsProps) {
  const [copied, setCopied] = useState(false);
  const reset = useDecisionStore((s) => s.reset);
  const setStep = useDecisionStore((s) => s.setStep);

  const handleCopy = async () => {
    const text = buildExportText(title, description, options);
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // Fallback for browsers without clipboard permission
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
  }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleNew = () => {
    reset();
    setStep(0);
    window.location.href = "/";
  };

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        type="button"
        variant="outline"
        className="h-11"
        onClick={handleCopy}
      >
        {copied ? <Check className="mr-1 h-4 w-4" /> : <Copy className="mr-1 h-4 w-4" />}
        {copied ? "Copied!" : "Copy to Clipboard"}
      </Button>
      <Button
        type="button"
        variant="ghost"
        className="h-11 text-gray-600"
        onClick={handleNew}
      >
        <RotateCcw className="mr-1 h-4 w-4" /> Start New Analysis
      </Button>
    </div>
  );
}
