export default function FinetunePage() {
  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            Fine-Tuned LLM
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            The main event. Fine-tune a smaller LLM (e.g., GPT-4o-mini) specifically
            for ticket classification. At a company with internal LLM infrastructure,
            this changes the economics entirely.
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="px-12 pb-8">
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "F1 (macro) at 100K", value: "95%" },
            { label: "Inference latency", value: "~200ms" },
            { label: "Training cost", value: "~$50" },
            { label: "vs. best baseline", value: "+4pt" },
          ].map((s) => (
            <div key={s.label} className="rounded-lg border p-4" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
              <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>{s.value}</p>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Learning Curve Focus */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Data Efficiency: How Much Do You Need?
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            Fine-tuned LLMs are surprisingly data-efficient. The model already understands language —
            fine-tuning just teaches it your specific categories.
          </p>
          <div className="space-y-3">
            {[
              { volume: "500", f1: "62%", note: "Worse than few-shot (74%). Not enough data to fine-tune effectively." },
              { volume: "1,000", f1: "73%", note: "Catching up to few-shot. Fine-tuning starts to learn category boundaries." },
              { volume: "5,000", f1: "86%", note: "The crossover. Overtakes embeddings+XGBoost (85%) and BERT (83%)." },
              { volume: "10,000", f1: "91%", note: "Clear lead. 3 points over BERT, 6 over XGBoost." },
              { volume: "50,000", f1: "94%", note: "Diminishing returns starting, but still the best method." },
              { volume: "100,000", f1: "95%", note: "Peak performance. 3 points over BERT, 7 over baseline XGBoost." },
            ].map((row) => (
              <div key={row.volume} className="flex items-center gap-4 px-4 py-3 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                <span className="text-sm font-mono w-16 shrink-0 text-right" style={{ color: "var(--accent)" }}>{row.volume}</span>
                <div className="w-16 h-5 rounded-full overflow-hidden shrink-0" style={{ backgroundColor: "var(--background-tertiary)" }}>
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${parseFloat(row.f1)}%`,
                      backgroundColor: "var(--chart-1)",
                    }}
                  />
                </div>
                <span className="text-sm font-medium w-10 shrink-0" style={{ color: "var(--foreground)" }}>{row.f1}</span>
                <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>{row.note}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* The OpenAI Argument */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            The Internal LLM Advantage
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-xs font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--foreground-muted)" }}>
                External API (most companies)
              </h3>
              <div className="space-y-2 text-xs" style={{ color: "var(--foreground-secondary)" }}>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>Cost per ticket</span>
                  <span style={{ color: "var(--error)" }}>$0.001 - $0.005</span>
                </div>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>At 100K tickets/month</span>
                  <span style={{ color: "var(--error)" }}>$100 - $500/mo</span>
                </div>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>At 1M tickets/month</span>
                  <span style={{ color: "var(--error)" }}>$1K - $5K/mo</span>
                </div>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>Latency</span>
                  <span>200-500ms (network + inference)</span>
                </div>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>Data leaves your infra</span>
                  <span style={{ color: "var(--error)" }}>Yes</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-xs font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--foreground-muted)" }}>
                Internal infrastructure (OpenAI)
              </h3>
              <div className="space-y-2 text-xs" style={{ color: "var(--foreground-secondary)" }}>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>Cost per ticket</span>
                  <span style={{ color: "var(--success)" }}>No API billing</span>
                </div>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>At 100K tickets/month</span>
                  <span style={{ color: "var(--success)" }}>Internal GPU time only</span>
                </div>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>At 1M tickets/month</span>
                  <span style={{ color: "var(--success)" }}>Internal GPU time only</span>
                </div>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>Latency</span>
                  <span style={{ color: "var(--success)" }}>~50-100ms (no network hop)</span>
                </div>
                <div className="flex justify-between p-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                  <span>Data leaves your infra</span>
                  <span style={{ color: "var(--success)" }}>No</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Model Selection */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Model Selection: Smaller Is Often Better
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            For classification, a fine-tuned smaller model often outperforms a larger model with few-shot prompting.
          </p>
          <div className="overflow-hidden rounded-lg border" style={{ borderColor: "var(--border)" }}>
            <table className="w-full text-sm">
              <thead>
                <tr style={{ backgroundColor: "var(--background-secondary)" }}>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Approach</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>F1</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Latency</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Why</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { approach: "GPT-4o zero-shot", f1: "72%", latency: "~800ms", why: "Powerful but not tuned for this task" },
                  { approach: "GPT-4o few-shot", f1: "78%", latency: "~1200ms", why: "Examples help, but long context is expensive" },
                  { approach: "GPT-4o-mini fine-tuned", f1: "95%", latency: "~200ms", why: "Smaller, faster, better — because it's specialized" },
                  { approach: "GPT-4o fine-tuned", f1: "95.5%", latency: "~500ms", why: "Marginal gain doesn't justify 2.5x latency" },
                ].map((row, i) => (
                  <tr key={row.approach} style={{ borderTop: "1px solid var(--border)", backgroundColor: i % 2 === 0 ? "var(--background-card)" : "var(--background-secondary)" }}>
                    <td className="px-5 py-2.5 text-xs font-medium" style={{ color: "var(--foreground)" }}>{row.approach}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--accent)" }}>{row.f1}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>{row.latency}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-muted)" }}>{row.why}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Drift & Maintenance */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Drift Detection &amp; Maintenance
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            Support categories evolve. New products launch (Sora, Codex, Atlas all launched recently).
            A fine-tuned model needs a retraining strategy.
          </p>
          <div className="grid grid-cols-3 gap-3">
            {[
              { title: "Confidence monitoring", detail: "Track the distribution of prediction confidence scores. A shift toward lower confidence signals new ticket types the model hasn't seen." },
              { title: "Category emergence", detail: "Cluster low-confidence tickets with embeddings. If a cluster forms that doesn't map to existing categories, it's a new category candidate." },
              { title: "Retraining cadence", detail: "Monthly retraining with the latest labeled data. Use human-classified tickets from the past month as fresh training signal." },
            ].map((item) => (
              <div key={item.title} className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>{item.title}</h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>{item.detail}</p>
              </div>
            ))}
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
            <li>At 95% F1, fine-tuned GPT-4o-mini is the clear winner — 3 points over BERT, 7 over TF-IDF+XGBoost.</li>
            <li>The crossover happens at ~5K tickets. Below that, embeddings+XGBoost or few-shot is better.</li>
            <li>At OpenAI specifically, the cost argument disappears. Internal LLM inference at near-zero cost makes this the default choice.</li>
            <li>A fine-tuned smaller model (4o-mini) matches a fine-tuned larger model (4o) at 2.5x less latency. Size isn&apos;t everything for classification.</li>
            <li>But: drift detection and retraining are real operational costs. The model needs ongoing maintenance as products and categories evolve.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
