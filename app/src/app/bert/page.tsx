export default function BertPage() {
  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            Fine-Tuned BERT
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            End-to-end fine-tuning of a BERT model (bert-base-uncased) on the ticket
            classification task. The model learns task-specific representations rather
            than relying on generic embeddings.
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="px-12 pb-8">
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "F1 (macro)", value: "91.2%" },
            { label: "Inference latency", value: "~20ms" },
            { label: "Training time", value: "~17 min" },
            { label: "Parameters", value: "110M" },
          ].map((s) => (
            <div key={s.label} className="rounded-lg border p-4" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
              <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>{s.value}</p>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Comparison with Embeddings+XGBoost */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            BERT vs. Embeddings + XGBoost
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            BERT edges out embeddings+XGBoost by 2.1 points (91.2% vs 89.1%). The gains come primarily
            from rare categories and tickets near category boundaries, where task-specific fine-tuning helps.
          </p>
          <div className="overflow-hidden rounded-lg border" style={{ borderColor: "var(--border)" }}>
            <table className="w-full text-sm">
              <thead>
                <tr style={{ backgroundColor: "var(--background-secondary)" }}>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Dimension</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Embeddings + XGBoost</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Fine-Tuned BERT</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Winner</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { dim: "F1 (macro)", emb: "89.1%", bert: "91.2%", winner: "BERT (+2.1pt)" },
                  { dim: "Worst class F1", emb: "73-80%", bert: "83.9% (api_usage)", winner: "BERT" },
                  { dim: "Best class F1", emb: "~95%", bert: "98.8% (newer_products)", winner: "BERT" },
                  { dim: "Latency", emb: "~1ms", bert: "~20ms", winner: "Emb+XGB" },
                  { dim: "Can use metadata", emb: "Yes (natively)", bert: "No (text only)", winner: "Emb+XGB" },
                  { dim: "Training time", emb: "~23s", bert: "~17 min", winner: "Emb+XGB" },
                  { dim: "GPU required", emb: "For embedding only", bert: "Yes (train + infer)", winner: "Emb+XGB" },
                  { dim: "Interpretability", emb: "Feature importance", bert: "Black box", winner: "Emb+XGB" },
                ].map((row, i) => (
                  <tr key={row.dim} style={{ borderTop: "1px solid var(--border)", backgroundColor: i % 2 === 0 ? "var(--background-card)" : "var(--background-secondary)" }}>
                    <td className="px-5 py-2.5 text-xs font-medium" style={{ color: "var(--foreground)" }}>{row.dim}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>{row.emb}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>{row.bert}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--accent)" }}>{row.winner}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Training Details */}
      <section className="px-12 pb-8">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border p-5" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
            <h3 className="text-sm font-medium mb-3" style={{ color: "var(--foreground)" }}>Training Configuration</h3>
            <div className="space-y-2 text-xs" style={{ color: "var(--foreground-muted)" }}>
              <div className="flex justify-between"><span>Base model</span><span style={{ color: "var(--foreground-secondary)" }}>bert-base-uncased</span></div>
              <div className="flex justify-between"><span>Learning rate</span><span style={{ color: "var(--foreground-secondary)" }}>2e-5</span></div>
              <div className="flex justify-between"><span>Batch size</span><span style={{ color: "var(--foreground-secondary)" }}>32</span></div>
              <div className="flex justify-between"><span>Epochs</span><span style={{ color: "var(--foreground-secondary)" }}>3</span></div>
              <div className="flex justify-between"><span>Max sequence length</span><span style={{ color: "var(--foreground-secondary)" }}>128 tokens</span></div>
              <div className="flex justify-between"><span>Warmup steps</span><span style={{ color: "var(--foreground-secondary)" }}>500</span></div>
              <div className="flex justify-between"><span>Weight decay</span><span style={{ color: "var(--foreground-secondary)" }}>0.01</span></div>
            </div>
          </div>
          <div className="rounded-lg border p-5" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
            <h3 className="text-sm font-medium mb-3" style={{ color: "var(--foreground)" }}>Where BERT Gains Matter</h3>
            <div className="space-y-3">
              {[
                { label: "Category boundary cases", detail: "BERT handles tickets near category boundaries better because fine-tuning learns subtle contextual distinctions (e.g., API Usage vs. API Errors)" },
                { label: "Rare categories", detail: "Security (1.5% of data) benefits most from transfer learning — BERT's pre-training helps where XGBoost starves" },
                { label: "Semantic paraphrasing", detail: "'My login isn't working' vs 'I can't access my account' — fine-tuned attention heads learn these equivalences" },
              ].map((item) => (
                <div key={item.label}>
                  <p className="text-xs font-medium" style={{ color: "var(--foreground)" }}>{item.label}</p>
                  <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>{item.detail}</p>
                </div>
              ))}
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
            <li>BERT edges out embeddings+XGBoost by 2.1 points (91.2% vs 89.1%). The gains are real but narrow — mostly on rare classes and category boundary cases.</li>
            <li>The tradeoff: ~17 min training time, GPU dependency, no metadata integration, and no interpretability. In many production settings, that&apos;s not worth 2 points.</li>
            <li>BERT&apos;s real advantage emerges at lower data volumes (1K-5K tickets), where transfer learning compensates for limited training data.</li>
            <li>At ~9.5K tickets, the fine-tuned LLM (96.1% F1) crushes BERT by 4.9 points — making the BERT tradeoffs even harder to justify.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
