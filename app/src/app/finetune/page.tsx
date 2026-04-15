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

      {/* Real results banner */}
      <section className="px-12 pb-4">
        <div className="rounded-lg border p-4" style={{ backgroundColor: "var(--success-muted)", borderColor: "var(--success)" }}>
          <p className="text-sm leading-relaxed" style={{ color: "var(--foreground-secondary)" }}>
            These are real measured results from GPT-4o-mini fine-tuned on 9,557 tickets and evaluated on 2,390 held-out test tickets. Only 2 unknowns in the entire test set. Lowest per-class F1 is 92.5% (account_management).
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="px-12 pb-8">
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "F1 (macro) at 9.5K tickets", value: "96.1%" },
            { label: "Inference latency", value: "~200ms" },
            { label: "Training cost", value: "~$50" },
            { label: "vs. embeddings+XGBoost (89.1%)", value: "+6.9pt" },
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
              { volume: "500", f1: "62%", note: "Projected. Worse than few-shot — not enough data to fine-tune effectively." },
              { volume: "1,000", f1: "73%", note: "Projected. Catching up to few-shot. Fine-tuning starts to learn category boundaries." },
              { volume: "5,000", f1: "86%", note: "Projected crossover. Overtakes embeddings+XGBoost (89.1%) at this scale." },
              { volume: "9,557", f1: "96.1%", note: "Measured. Trained here. Crushes all baselines — +7pt over embeddings+XGBoost." },
              { volume: "50,000", f1: "—", note: "Not tested. Diminishing returns expected given 96.1% already achieved at ~9.5K." },
              { volume: "100,000", f1: "—", note: "Not tested. Near-ceiling performance already reached with far less data." },
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
                  { approach: "GPT-4o zero-shot", f1: "77.7%", latency: "~800ms", why: "Powerful but not tuned for this task" },
                  { approach: "GPT-4o few-shot", f1: "pending", latency: "~1200ms", why: "Examples help, but long context is expensive" },
                  { approach: "GPT-4o-mini fine-tuned", f1: "96.1%", latency: "~200ms", why: "Smaller, faster, better — because it's specialized" },
                  { approach: "GPT-4o fine-tuned", f1: "—", latency: "~500ms", why: "Not tested — marginal gain unlikely to justify 2.5x latency" },
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
            <li>At 96.1% F1, fine-tuned GPT-4o-mini is the clear production winner — +7 points over embeddings+XGBoost (89.1%), with the lowest per-class F1 still at 92.5%.</li>
            <li>The crossover happens at ~5K tickets. Below that, embeddings+XGBoost or few-shot is better. We trained at ~9.5K and it&apos;s clearly dominant.</li>
            <li>At OpenAI specifically, the cost argument disappears. Internal LLM inference at near-zero cost makes this the default choice.</li>
            <li>Only 2 unknowns out of 2,390 test tickets — the model almost never refuses to classify.</li>
            <li>But: drift detection and retraining are real operational costs. The model needs ongoing maintenance as products and categories evolve.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
