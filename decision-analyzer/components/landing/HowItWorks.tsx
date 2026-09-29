const steps = [
  {
    number: "1",
    title: "Choose Your Decision",
    description: "Select from templates or create a custom one.",
  },
  {
    number: "2",
    title: "Analyze Scenarios",
    description:
      "Define outcomes with probabilities and how good/bad each would be.",
  },
  {
    number: "3",
    title: "Get Recommendation",
    description:
      "See data-driven insights and expected values for every option.",
  },
];

export function HowItWorks() {
  return (
    <section className="py-12 sm:py-16">
      <div className="mx-auto max-w-5xl px-4">
        <h2 className="text-center text-2xl font-bold text-gray-900 sm:text-3xl">
          How it works
        </h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-3 sm:gap-6">
          {steps.map((step) => (
            <div
              key={step.number}
              className="rounded-lg border border-gray-200 bg-white p-5 transition-all duration-200 hover:shadow-md sm:p-6"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-600 text-sm font-bold text-white">
                {step.number}
              </div>
              <h3 className="mt-4 text-base font-bold text-gray-900 sm:text-lg">
                {step.title}
              </h3>
              <p className="mt-2 text-sm text-gray-600">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
