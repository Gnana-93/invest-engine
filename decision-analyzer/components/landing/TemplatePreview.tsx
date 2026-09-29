import Link from "next/link";
import {
  ArrowRight,
  Briefcase,
  Heart,
  Home,
  Rocket,
  Sparkles,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { decisionTemplates } from "@/lib/templates";
import type { IconName } from "@/lib/types";

const icons: Record<IconName, React.ComponentType<{ className?: string }>> = {
  Heart,
  Briefcase,
  Home,
  Rocket,
  Sparkles,
};

export function TemplatePreview() {
  return (
    <section className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-5xl px-4">
        <h2 className="text-center text-2xl font-bold text-gray-900 sm:text-3xl">
          Start with a template
        </h2>
        <p className="mx-auto mt-2 max-w-xl text-center text-sm text-gray-600 sm:text-base">
          Pre-loaded with realistic scenarios — edit every number to match
          your situation.
        </p>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 sm:gap-6">
          {decisionTemplates.map((template) => {
            const Icon = icons[(template.icon as IconName) ?? "Sparkles"];
            return (
              <Card
                key={template.id}
                className="transition-all duration-200 hover:shadow-md"
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                      <Icon className="h-5 w-5" />
                    </div>
                    <CardTitle className="text-base leading-snug sm:text-lg">
                      {template.title}
                    </CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="line-clamp-2 text-sm text-gray-600">
                    {template.description}
                  </p>
                  <div className="mt-3 flex items-center justify-between">
                    <Badge variant="secondary">{template.category}</Badge>
                    <Button
                      asChild
                      variant="ghost"
                      className="h-9 text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700"
                    >
                      <Link href="/analyze">
                        Analyze This
                        <ArrowRight className="ml-1 h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}
