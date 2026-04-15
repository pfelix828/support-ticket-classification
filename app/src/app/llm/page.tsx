export default function LlmPage() {
  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            LLM Zero-Shot &amp; Few-Shot
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            No training data required. Classify tickets using only a well-crafted
            prompt. Zero-shot uses just category descriptions; few-shot adds curated
            examples. The question: how close can prompt engineering get?
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="px-12 pb-8">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border p-5" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
            <h3 className="text-sm font-medium mb-3" style={{ color: "var(--foreground)" }}>Zero-Shot</h3>
            <p className="text-xs leading-relaxed mb-3" style={{ color: "var(--foreground-muted)" }}>
              Provide the 12 category names and descriptions, then ask the model to classify.
              No examples needed — the model relies on its pre-training understanding of support workflows.
            </p>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>77.7%</p>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>F1 (macro)</p>
              </div>
              <div>
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>~500ms</p>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>Latency</p>
              </div>
            </div>
          </div>
          <div className="rounded-lg border p-5" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
            <h3 className="text-sm font-medium mb-3" style={{ color: "var(--foreground)" }}>Few-Shot</h3>
            <p className="text-xs leading-relaxed mb-3" style={{ color: "var(--foreground-muted)" }}>
              Add 2-3 curated examples per category to the prompt. The model learns the classification
              boundaries from these demonstrations. Careful example selection matters more than quantity.
            </p>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-lg font-semibold" style={{ color: "var(--foreground-muted)" }}>~82-85%</p>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>F1 (macro) <span className="italic">(projected)</span></p>
              </div>
              <div>
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>~800ms</p>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>Latency</p>
              </div>
            </div>
            <p className="text-xs mt-2 italic" style={{ color: "var(--foreground-muted)" }}>
              Fresh batch evaluation in progress. Prior run had a mapping bug; projected range based on zero-shot baseline + typical few-shot lift.
            </p>
          </div>
        </div>
      </section>

      {/* Prompt Design */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Prompt Design Matters
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-xs font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--foreground-muted)" }}>What worked</h3>
              <ul className="space-y-2 text-xs" style={{ color: "var(--foreground-secondary)" }}>
                <li className="flex gap-2">
                  <span style={{ color: "var(--success)" }}>+</span>
                  Explicit category descriptions with boundary conditions (&ldquo;Account Access means login/auth issues, NOT account settings changes&rdquo;)
                </li>
                <li className="flex gap-2">
                  <span style={{ color: "var(--success)" }}>+</span>
                  Examples chosen at category boundaries — the hard cases, not the obvious ones
                </li>
                <li className="flex gap-2">
                  <span style={{ color: "var(--success)" }}>+</span>
                  Asking the model to output a confidence score alongside the classification
                </li>
                <li className="flex gap-2">
                  <span style={{ color: "var(--success)" }}>+</span>
                  Chain-of-thought: &ldquo;First identify the product, then the issue type&rdquo;
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--foreground-muted)" }}>What didn&apos;t</h3>
              <ul className="space-y-2 text-xs" style={{ color: "var(--foreground-secondary)" }}>
                <li className="flex gap-2">
                  <span style={{ color: "var(--error)" }}>-</span>
                  More than 3 examples per category (diminishing returns, higher latency)
                </li>
                <li className="flex gap-2">
                  <span style={{ color: "var(--error)" }}>-</span>
                  Asking the model to &ldquo;think step by step&rdquo; without structure (rambling, inconsistent)
                </li>
                <li className="flex gap-2">
                  <span style={{ color: "var(--error)" }}>-</span>
                  Including all 12 categories in examples (context window waste, confusion)
                </li>
                <li className="flex gap-2">
                  <span style={{ color: "var(--error)" }}>-</span>
                  Trying to handle multi-intent tickets in a single classification step
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Where LLM wins/loses */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            When Zero/Few-Shot Is the Right Choice
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--success)" }}>Use it when...</h3>
              <ul className="space-y-1.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>
                <li>You have &lt; 500 labeled tickets (can&apos;t train anything else)</li>
                <li>Categories change frequently (no retraining needed)</li>
                <li>You need a classifier today, not in a week</li>
                <li>You&apos;re bootstrapping labels for a supervised model later</li>
                <li>Multi-intent detection matters (LLMs can identify both categories)</li>
              </ul>
            </div>
            <div className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--error)" }}>Don&apos;t use it when...</h3>
              <ul className="space-y-1.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>
                <li>You have thousands of labeled tickets (supervised methods win)</li>
                <li>Latency matters (&gt;500ms per ticket at scale)</li>
                <li>Cost matters at volume ($0.002-0.005 per ticket adds up)</li>
                <li>You need guaranteed consistency (LLMs can be stochastic)</li>
                <li>Categories are well-defined and stable (overkill)</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Takeaways */}
      <section className="px-12 pb-16">
        <div className="rounded-lg p-6" style={{ backgroundColor: "var(--accent-muted)" }}>
          <h3 className="text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
            Key Takeaways
          </h3>
          <ul className="space-y-2 text-sm" style={{ color: "var(--foreground-secondary)" }}>
            <li>Zero-shot at 77.7% is strong for zero training data. Few-shot (evaluation in progress) should push into the low-to-mid 80s with proper example selection.</li>
            <li>At ~12K tickets, zero-shot (77.7%) underperforms the TF-IDF baselines (86-87%) — the value is at the low end of the data spectrum.</li>
            <li>The killer use case: bootstrapping. Use LLM classification to label your first 1K tickets, then train a supervised model on those labels.</li>
            <li>At OpenAI, the latency and cost concerns are reduced — but even then, a fine-tuned model will outperform prompt engineering.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
