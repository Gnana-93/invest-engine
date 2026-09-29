import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-gradient-to-b from-indigo-50 via-white to-white"
      />
      <div className="relative mx-auto max-w-5xl px-4 py-16 text-center sm:py-24">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-5xl">
          Make Better Decisions with Scenario Analysis
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-base text-gray-600 sm:text-lg">
          Stop ruminating. Start calculating. Analyze your biggest life
          decisions with confidence using expected value and probabilistic
          thinking.
        </p>
        <div className="mt-8 flex justify-center">
          <Button
            asChild
            size="lg"
            className="h-12 bg-indigo-600 px-6 text-base hover:bg-indigo-700"
          >
            <Link href="/analyze">
              Analyze Your Decision
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
