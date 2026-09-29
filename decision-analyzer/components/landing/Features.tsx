const features = [
  "Probabilistic Analysis",
  "Expected Value Calculation",
  "Visual Comparisons",
  "Editable Templates",
  "Risk Analysis",
  "Export Results",
];

export function Features() {
  return (
    <section className="py-12 sm:py-16">
      <div className="mx-auto max-w-5xl px-4">
        <h2 className="text-center text-2xl font-bold text-gray-900 sm:text-3xl">
          Everything you need to decide
        </h2>
        <ul className="mx-auto mt-8 grid max-w-3xl gap-3 sm:grid-cols-2">
          {features.map((feature) => (
            <li
              key={feature}
              className="flex items-center gap-3 rounded-lg border border-gray-100 bg-white px-4 py-3 text-sm text-gray-700"
            >
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-green-100 text-sm font-bold text-green-600">
                ✓
              </span>
              {feature}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
