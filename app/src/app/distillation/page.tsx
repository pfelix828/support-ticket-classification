export default function DistillationPage() {
  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            Distillation: o1 → GPT-4o-mini
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            The OpenAI-specific method. Use a frontier reasoning model (o1) to generate
            high-quality labeled data with chain-of-thought rationale, then distill
            that knowledge into a fast, efficient production model (GPT-4o-mini).
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="px-12 pb-8">
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "F1 (macro)", value: "96%+" },
            { label: "Inference latency", value: "~200ms" },
            { label: "Internal cost", value: "No API cost" },
            { label: "vs. fine-tuned BERT", value: "+4pt" },
          ].map((s) => (
            <div key={s.label} className="rounded-lg border p-4" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
              <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>{s.value}</p>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Why distillation, not just fine-tuning */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Why Distillation, Not Just Fine-Tuning
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            Standard fine-tuning trains on human-labeled data: ticket text → category label.
            Distillation trains on a frontier model&apos;s outputs — including its reasoning.
            The difference matters.
          </p>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-xs font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--foreground-muted)" }}>
                Standard Fine-Tuning
              </h3>
              <div className="space-y-2">
                {[
                  { input: '"I was charged $200 and my API key stopped working"', output: 'billing', style: "basic" },
                ].map((ex) => (
                  <div key={ex.input} className="p-3 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                    <p className="text-xs font-mono" style={{ color: "var(--foreground-secondary)" }}>{ex.input}</p>
                    <p className="text-xs mt-2" style={{ color: "var(--foreground-muted)" }}>→ <span style={{ color: "var(--accent)" }}>billing</span></p>
                    <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>The model learns a mapping. No context about <em>why</em>.</p>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-xs font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--foreground-muted)" }}>
                o1-Distilled Fine-Tuning
              </h3>
              <div className="p-3 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                <p className="text-xs font-mono" style={{ color: "var(--foreground-secondary)" }}>&quot;I was charged $200 and my API key stopped working&quot;</p>
                <div className="mt-2 p-2 rounded" style={{ backgroundColor: "var(--background-tertiary)" }}>
                  <p className="text-xs" style={{ color: "var(--foreground-secondary)" }}>
                    <strong>o1 reasoning:</strong> The user has two issues. The $200 charge
                    is the primary complaint — it&apos;s mentioned first and is the financial impact.
                    The API key issue is likely a downstream effect of an account-level action
                    (suspension, key rotation) triggered by the billing dispute. Route to billing;
                    the API key will resolve when the billing issue does.
                  </p>
                </div>
                <p className="text-xs mt-2" style={{ color: "var(--foreground-muted)" }}>→ <span style={{ color: "var(--accent)" }}>billing</span> (confidence: 0.87)</p>
                <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>The student learns the <em>logic</em>, not just the label.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Pipeline */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-4" style={{ color: "var(--foreground-secondary)" }}>
            The Distillation Pipeline
          </h2>
          <div className="space-y-4">
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>1</div>
              <div className="flex-1 p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>
                  Collect unlabeled tickets
                </h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  Pull 50K-100K representative tickets from the support queue.
                  No manual labeling needed — o1 will handle classification.
                </p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>2</div>
              <div className="flex-1 p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>
                  Run o1 batch classification with Stored Completions
                </h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  o1 classifies each ticket with chain-of-thought reasoning. Use the Batch API for cost efficiency.
                  Stored Completions automatically capture the outputs for the fine-tuning step.
                </p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>3</div>
              <div className="flex-1 p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>
                  Quality check a sample
                </h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  Human-review 500-1000 of o1&apos;s classifications. This validates the teacher&apos;s accuracy
                  and catches systematic errors before they propagate to the student.
                </p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>4</div>
              <div className="flex-1 p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>
                  Fine-tune GPT-4o-mini via Model Distillation
                </h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  Use OpenAI&apos;s Model Distillation workflow to train 4o-mini on o1&apos;s stored completions.
                  The student learns both the classifications and the reasoning patterns.
                  Enable Structured Outputs to enforce strict JSON schema compliance.
                </p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>5</div>
              <div className="flex-1 p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>
                  Deploy with confidence thresholds
                </h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  The distilled 4o-mini handles production traffic. Low-confidence tickets
                  escalate to human agents. Their corrections feed the next distillation cycle.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why this beats everything else */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Why This Beats Every Other Method (Internally)
          </h2>
          <div className="overflow-hidden rounded-lg border" style={{ borderColor: "var(--border)" }}>
            <table className="w-full text-sm">
              <thead>
                <tr style={{ backgroundColor: "var(--background-secondary)" }}>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Dimension</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>TF-IDF + XGBoost</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Fine-Tuned BERT</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Fine-Tuned LLM</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--accent)" }}>o1 → 4o-mini</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { dim: "F1 (macro)", xgb: "88%", bert: "92%", ft: "95%", distill: "96%+" },
                  { dim: "Ambiguous tickets", xgb: "62%", bert: "76%", ft: "84%", distill: "90%+" },
                  { dim: "New product types", xgb: "Poor", bert: "Poor", ft: "Moderate", distill: "Strong" },
                  { dim: "Context window", xgb: "N/A", bert: "512 tokens", ft: "128K", distill: "128K" },
                  { dim: "Inference latency", xgb: "< 5ms", bert: "~20ms", ft: "~200ms", distill: "~200ms" },
                  { dim: "Marginal cost", xgb: "~$0 (CPU)", bert: "GPU time", ft: "GPU time", distill: "GPU time" },
                  { dim: "Requires labeled data", xgb: "Yes (lots)", bert: "Yes (lots)", ft: "Yes", distill: "No" },
                  { dim: "Handles reasoning", xgb: "No", bert: "No", ft: "Partially", distill: "Yes (from o1)" },
                ].map((row, i) => (
                  <tr key={row.dim} style={{ borderTop: "1px solid var(--border)", backgroundColor: i % 2 === 0 ? "var(--background-card)" : "var(--background-secondary)" }}>
                    <td className="px-5 py-2.5 text-xs font-medium" style={{ color: "var(--foreground)" }}>{row.dim}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-muted)" }}>{row.xgb}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-muted)" }}>{row.bert}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>{row.ft}</td>
                    <td className="px-5 py-2.5 text-xs font-medium" style={{ color: "var(--accent)" }}>{row.distill}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs mt-3" style={{ color: "var(--foreground-muted)" }}>
            The key row: &ldquo;Requires labeled data.&rdquo; Distillation sidesteps the labeling bottleneck entirely —
            o1 generates the labels. Every other supervised method needs humans to label thousands of tickets first.
          </p>
        </div>
      </section>

      {/* The reasoning transfer advantage */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Reasoning Transfer: Why New Products Don&apos;t Break It
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            OpenAI launches new products regularly — Sora, Codex, Atlas all arrived recently.
            Each launch creates ticket types the classifier has never seen. Here&apos;s how each method handles it:
          </p>
          <div className="grid grid-cols-2 gap-3">
            {[
              {
                method: "TF-IDF / BERT",
                response: "Fails. No training data for the new category. Tickets get misclassified until you label hundreds of examples and retrain.",
                icon: "var(--error)",
              },
              {
                method: "Fine-tuned LLM",
                response: "Partially handles it. The LLM's general knowledge helps, but it wasn't fine-tuned on these ticket types. Accuracy drops for new categories.",
                icon: "var(--warning)",
              },
              {
                method: "o1 (teacher)",
                response: "Reasons from first principles. 'This ticket mentions Codex, which is a coding agent product. The user is reporting incorrect code changes — this is a product issue, not an API error.' No retraining needed.",
                icon: "var(--success)",
              },
              {
                method: "Distilled 4o-mini",
                response: "Handles it if o1 re-labels a batch including the new ticket type. One distillation cycle (hours, not weeks) and the student is updated.",
                icon: "var(--success)",
              },
            ].map((m) => (
              <div key={m.method} className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: m.icon }}>{m.method}</h3>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>{m.response}</p>
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
            <li>Distillation eliminates the labeling bottleneck. o1 generates labels with reasoning — no human annotation required for the initial training set.</li>
            <li>The student model (4o-mini) learns <em>why</em> tickets belong to categories, not just <em>that</em> they do. This makes it robust to new ticket types.</li>
            <li>At OpenAI, this is the clear winner: highest accuracy, zero marginal cost, and the fastest path from zero to production.</li>
            <li>At any other company, the economics are different — o1 inference costs money, and fine-tuned BERT or embeddings+XGBoost may be the pragmatic choice. The method depends on the infrastructure.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
