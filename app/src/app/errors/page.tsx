export default function ErrorsPage() {
  const confusionPairs = [
    { actual: "Account Access", predicted: "Account Mgmt", rate: "12%", why: "Both involve accounts. 'I need to change my account settings' vs 'I can't access my account' — the boundary is subtle." },
    { actual: "API Errors", predicted: "API Usage", rate: "8%", why: "'How do I fix 429 errors?' is technically a question (usage) about an error. Intent is ambiguous." },
    { actual: "Billing", predicted: "Account Mgmt", rate: "6%", why: "'How do I update my payment method?' touches both billing and account management." },
    { actual: "ChatGPT Apps", predicted: "ChatGPT Product", rate: "11%", why: "'ChatGPT isn't working' — is it the app or the product? Without device context, both are plausible." },
    { actual: "Enterprise", predicted: "Account Mgmt", rate: "9%", why: "'How do I add users to my workspace?' — Enterprise workspace management vs general account management." },
    { actual: "GPTs", predicted: "API Errors", rate: "7%", why: "'My GPT action returns a 429 error' — is it a GPT problem or an API problem?" },
  ];

  const methodErrorProfiles = [
    {
      method: "TF-IDF + XGBoost",
      strength: "Clear keyword signals (e.g., 'refund' → Billing)",
      weakness: "Fails when the same words appear across categories ('account', 'access', 'settings')",
      ambiguous_f1: "62%",
    },
    {
      method: "Embeddings + XGBoost",
      strength: "Semantic similarity helps with paraphrasing. Metadata disambiguates.",
      weakness: "Still confused by tickets where text is ambiguous and metadata doesn't help",
      ambiguous_f1: "71%",
    },
    {
      method: "Fine-Tuned BERT",
      strength: "Learns subtle contextual cues from fine-tuning",
      weakness: "No metadata. Purely text-based, misses customer tier signals.",
      ambiguous_f1: "76%",
    },
    {
      method: "Fine-Tuned LLM",
      strength: "Best at disambiguating — can reason about intent, not just pattern match",
      weakness: "Occasional overconfidence on edge cases. Sometimes invents a rationale.",
      ambiguous_f1: "84%",
    },
  ];

  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            Error Analysis
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            Understanding what each method gets wrong is more valuable than knowing
            what it gets right. The errors reveal the real classification challenges
            in support ticket routing.
          </p>
        </div>
      </section>

      {/* Common Confusion Pairs */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-1" style={{ color: "var(--foreground-secondary)" }}>
            Most Common Confusion Pairs
          </h2>
          <p className="text-xs mb-4" style={{ color: "var(--foreground-muted)" }}>
            Categories that get confused with each other most often, across all methods.
          </p>
          <div className="space-y-3">
            {confusionPairs.map((pair) => (
              <div key={`${pair.actual}-${pair.predicted}`} className="flex gap-4 p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <div className="shrink-0 w-40">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="px-2 py-0.5 rounded" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>{pair.actual}</span>
                    <span style={{ color: "var(--foreground-muted)" }}>→</span>
                    <span className="px-2 py-0.5 rounded" style={{ backgroundColor: "rgba(196, 112, 90, 0.1)", color: "var(--error)" }}>{pair.predicted}</span>
                  </div>
                  <p className="text-xs mt-2 font-medium" style={{ color: "var(--error)" }}>
                    {pair.rate} misclassification rate
                  </p>
                </div>
                <p className="text-xs leading-relaxed flex-1" style={{ color: "var(--foreground-muted)" }}>
                  {pair.why}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Per-Method Error Profile */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-1" style={{ color: "var(--foreground-secondary)" }}>
            Error Profiles by Method
          </h2>
          <p className="text-xs mb-4" style={{ color: "var(--foreground-muted)" }}>
            How each method handles the 10% of ambiguous/multi-intent tickets.
          </p>
          <div className="grid grid-cols-2 gap-3">
            {methodErrorProfiles.map((m) => (
              <div key={m.method} className="rounded-lg border p-4" style={{ borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium" style={{ color: "var(--foreground)" }}>{m.method}</h3>
                  <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>
                    {m.ambiguous_f1} on ambiguous
                  </span>
                </div>
                <div className="space-y-2 text-xs">
                  <div>
                    <span style={{ color: "var(--success)" }}>Strength: </span>
                    <span style={{ color: "var(--foreground-muted)" }}>{m.strength}</span>
                  </div>
                  <div>
                    <span style={{ color: "var(--error)" }}>Weakness: </span>
                    <span style={{ color: "var(--foreground-muted)" }}>{m.weakness}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* The Long Tail */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            The Rare Category Problem
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            Security tickets make up only 1.5% of the dataset. Every method struggles here — but they struggle differently.
          </p>
          <div className="overflow-hidden rounded-lg border" style={{ borderColor: "var(--border)" }}>
            <table className="w-full text-sm">
              <thead>
                <tr style={{ backgroundColor: "var(--background-secondary)" }}>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Method</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Security F1</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Privacy F1</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Newer Products F1</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { method: "TF-IDF + XGBoost", security: "73%", privacy: "82%", newer: "84%" },
                  { method: "Embeddings + XGBoost", security: "80%", privacy: "86%", newer: "88%" },
                  { method: "Fine-Tuned BERT", security: "82%", privacy: "88%", newer: "89%" },
                  { method: "Fine-Tuned LLM", security: "89%", privacy: "93%", newer: "94%" },
                ].map((row, i) => (
                  <tr key={row.method} style={{ borderTop: "1px solid var(--border)", backgroundColor: i % 2 === 0 ? "var(--background-card)" : "var(--background-secondary)" }}>
                    <td className="px-5 py-2.5 text-xs font-medium" style={{ color: "var(--foreground)" }}>{row.method}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>{row.security}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>{row.privacy}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>{row.newer}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs mt-3" style={{ color: "var(--foreground-muted)" }}>
            The fine-tuned LLM&apos;s advantage is largest on rare categories (+16 points over XGBoost on Security).
            Transfer learning from pre-training compensates for limited training examples.
          </p>
        </div>
      </section>

      {/* Takeaways */}
      <section className="px-12 pb-16">
        <div className="rounded-lg p-6" style={{ backgroundColor: "var(--accent-muted)" }}>
          <h3 className="text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
            Key Takeaways
          </h3>
          <ul className="space-y-2 text-sm" style={{ color: "var(--foreground-secondary)" }}>
            <li>The hardest errors are semantic, not lexical. &ldquo;Account Access&rdquo; vs &ldquo;Account Management&rdquo; is a real ambiguity, not a model failure.</li>
            <li>Fine-tuned LLMs handle ambiguity best (84% on ambiguous tickets vs 62% for XGBoost) — they can reason about intent.</li>
            <li>Rare categories are where LLM fine-tuning shines most. The gap widens as class frequency drops.</li>
            <li>The production answer: don&apos;t try to eliminate all errors. Route low-confidence predictions to human agents and use their decisions as training data.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
