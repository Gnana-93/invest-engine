import { Features } from "@/components/landing/Features";
import { Footer } from "@/components/landing/Footer";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { TemplatePreview } from "@/components/landing/TemplatePreview";

export default function LandingPage() {
  return (
    <div className="flex min-h-dvh flex-col">
      <main className="flex-1">
        <Hero />
        <HowItWorks />
        <TemplatePreview />
        <Features />
      </main>
      <Footer />
    </div>
  );
}
