export default function ArchitecturePage() {
  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            Production Architecture
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            The real production recommendation isn&apos;t a single model — it&apos;s a cascade.
            Fast, cheap models handle the confident cases. The LLM handles the hard ones.
          </p>
        </div>
      </section>

      {/* The Cascade */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-4" style={{ color: "var(--foreground-secondary)" }}>
            The Cascade System
          </h2>
          <div className="space-y-4">
            {/* Step 1 */}
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>1</div>
              <div className="flex-1 p-4 rounded-lg border" style={{ borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium" style={{ color: "var(--foreground)" }}>XGBoost + Embeddings (Fast Classifier)</h3>
                  <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: "var(--background-secondary)", color: "var(--foreground-muted)" }}>~50ms</span>
                </div>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  Every ticket hits this first. Pre-computed embeddings + metadata features.
                  If confidence &gt; 0.85, route immediately. Handles ~75% of all tickets.
                </p>
                <div className="flex gap-4 mt-3">
                  <div className="text-xs"><span style={{ color: "var(--success)" }}>75%</span> of tickets routed here</div>
                  <div className="text-xs"><span style={{ color: "var(--accent)" }}>93%</span> accuracy on routed tickets</div>
                  <div className="text-xs"><span style={{ color: "var(--foreground-muted)" }}>~50ms</span> latency</div>
                </div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex gap-4 items-center">
              <div className="w-8 flex justify-center"><div className="w-0.5 h-6" style={{ backgroundColor: "var(--border)" }} /></div>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                Confidence &lt; 0.85 → escalate to LLM
              </p>
            </div>

            {/* Step 2 */}
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>2</div>
              <div className="flex-1 p-4 rounded-lg border" style={{ borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium" style={{ color: "var(--foreground)" }}>Fine-Tuned LLM (Deep Classifier)</h3>
                  <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: "var(--background-secondary)", color: "var(--foreground-muted)" }}>~200ms</span>
                </div>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  Handles the ambiguous 25%: multi-intent tickets, rare categories, semantic edge cases.
                  Can also detect if the ticket contains multiple issues and flag for split routing.
                </p>
                <div className="flex gap-4 mt-3">
                  <div className="text-xs"><span style={{ color: "var(--success)" }}>20%</span> of tickets routed here</div>
                  <div className="text-xs"><span style={{ color: "var(--accent)" }}>91%</span> accuracy on routed tickets</div>
                  <div className="text-xs"><span style={{ color: "var(--foreground-muted)" }}>~200ms</span> latency</div>
                </div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex gap-4 items-center">
              <div className="w-8 flex justify-center"><div className="w-0.5 h-6" style={{ backgroundColor: "var(--border)" }} /></div>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                LLM confidence &lt; 0.70 → escalate to human
              </p>
            </div>

            {/* Step 3 */}
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "rgba(196, 112, 90, 0.1)", color: "var(--error)" }}>3</div>
              <div className="flex-1 p-4 rounded-lg border" style={{ borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium" style={{ color: "var(--foreground)" }}>Human Agent (Manual Routing)</h3>
                  <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: "var(--background-secondary)", color: "var(--foreground-muted)" }}>minutes</span>
                </div>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  The truly hard cases. These are often genuinely ambiguous tickets that need a human
                  judgment call. Crucially, the human&apos;s classification feeds back into the training set.
                </p>
                <div className="flex gap-4 mt-3">
                  <div className="text-xs"><span style={{ color: "var(--error)" }}>5%</span> of tickets routed here</div>
                  <div className="text-xs"><span style={{ color: "var(--success)" }}>100%</span> accuracy (by definition)</div>
                  <div className="text-xs"><span style={{ color: "var(--foreground-muted)" }}>Training data!</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* System Performance */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            System-Level Performance
          </h2>
          <div className="grid grid-cols-4 gap-3">
            {[
              { label: "Overall accuracy", value: "96%", detail: "Weighted across all three tiers" },
              { label: "Avg latency", value: "~90ms", detail: "75% at 50ms, 20% at 200ms, 5% manual" },
              { label: "Auto-routed", value: "95%", detail: "Only 5% need human intervention" },
              { label: "Cost at scale", value: "No API cost", detail: "Internal GPU + XGBoost on CPU" },
            ].map((s) => (
              <div key={s.label} className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>{s.value}</p>
                <p className="text-xs font-medium mt-1" style={{ color: "var(--foreground)" }}>{s.label}</p>
                <p className="text-xs mt-0.5" style={{ color: "var(--foreground-muted)" }}>{s.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Cascade > Single Model */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Why a Cascade Beats a Single Model
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-xs font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--foreground-muted)" }}>Single Fine-Tuned LLM</h3>
              <div className="space-y-2 text-xs" style={{ color: "var(--foreground-secondary)" }}>
                <p>95% F1, ~200ms latency, every ticket hits the LLM</p>
                <p>At 1M tickets/month: 1M LLM inference calls</p>
                <p>At 10M tickets/month: 10M LLM inference calls</p>
                <p style={{ color: "var(--foreground-muted)" }}>Even at OpenAI, GPU time isn&apos;t infinite — there&apos;s opportunity cost</p>
              </div>
            </div>
            <div>
              <h3 className="text-xs font-medium mb-2 uppercase tracking-wide" style={{ color: "var(--foreground-muted)" }}>Cascade (XGBoost → LLM → Human)</h3>
              <div className="space-y-2 text-xs" style={{ color: "var(--foreground-secondary)" }}>
                <p>96% effective accuracy, ~90ms avg latency</p>
                <p>At 1M tickets/month: 250K LLM calls (75% handled by XGBoost)</p>
                <p>At 10M tickets/month: 2.5M LLM calls (75% savings)</p>
                <p style={{ color: "var(--success)" }}>Better accuracy AND lower resource usage</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Scaling: What Changes at 1M+ */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            What Changes at 1M+ Tickets
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            At high volume, the accuracy gap between methods narrows — but the cost and latency gap widens.
            The architecture evolves to handle this.
          </p>
          <div className="overflow-hidden rounded-lg border" style={{ borderColor: "var(--border)" }}>
            <table className="w-full text-sm">
              <thead>
                <tr style={{ backgroundColor: "var(--background-secondary)" }}>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Volume</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>LLM Accuracy</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>XGBoost Accuracy</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Gap</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>LLM Cost (external)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { vol: "100K/mo", llm: "95%", xgb: "91%", gap: "4pt", cost: "$100/mo" },
                  { vol: "1M/mo", llm: "95.5%", xgb: "92.5%", gap: "3pt", cost: "$1K/mo" },
                  { vol: "10M/mo", llm: "96%", xgb: "93%", gap: "3pt", cost: "$10K/mo" },
                  { vol: "100M/mo", llm: "96%", xgb: "93.5%", gap: "2.5pt", cost: "$100K/mo" },
                ].map((row, i) => (
                  <tr key={row.vol} style={{ borderTop: "1px solid var(--border)", backgroundColor: i % 2 === 0 ? "var(--background-card)" : "var(--background-secondary)" }}>
                    <td className="px-5 py-2.5 text-xs font-medium" style={{ color: "var(--foreground)" }}>{row.vol}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--accent)" }}>{row.llm}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>{row.xgb}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-muted)" }}>{row.gap}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--error)" }}>{row.cost}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs mt-3" style={{ color: "var(--foreground-muted)" }}>
            The accuracy gap shrinks because at high volume, even classical methods have seen enough examples of every edge case.
            The cost gap grows linearly. Even at OpenAI, GPU-seconds have opportunity cost.
          </p>
        </div>
      </section>

      {/* Distillation */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Distillation: The High-Volume Endgame
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            At 1M+ tickets, you have a third option that combines the best of both worlds:
            train a fast, cheap model on the LLM&apos;s predictions.
          </p>
          <div className="space-y-4">
            {/* Step by step */}
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>1</div>
              <div className="flex-1 p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>Fine-tune the LLM on your labeled data</h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  This is your &ldquo;teacher&rdquo; model. It achieves 95-96% accuracy and understands ambiguous tickets.
                </p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>2</div>
              <div className="flex-1 p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>Run the LLM on 1M+ unlabeled tickets</h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  Generate &ldquo;soft labels&rdquo; — not just the predicted category, but the full probability distribution across all 12 classes.
                  The LLM&apos;s uncertainty is signal.
                </p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>3</div>
              <div className="flex-1 p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>Train a &ldquo;student&rdquo; model on the LLM&apos;s outputs</h3>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                  An embeddings + XGBoost model (or a tiny BERT) trained on the LLM&apos;s soft labels.
                  It learns the LLM&apos;s decision boundaries — including how it handles ambiguity — at a fraction of the cost.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-5 grid grid-cols-3 gap-3">
            <div className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
              <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>93-94%</p>
              <p className="text-xs font-medium mt-1" style={{ color: "var(--foreground)" }}>Distilled model accuracy</p>
              <p className="text-xs mt-0.5" style={{ color: "var(--foreground-muted)" }}>~1-2pt below the teacher LLM</p>
            </div>
            <div className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
              <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>&lt; 5ms</p>
              <p className="text-xs font-medium mt-1" style={{ color: "var(--foreground)" }}>Inference latency</p>
              <p className="text-xs mt-0.5" style={{ color: "var(--foreground-muted)" }}>40x faster than the LLM</p>
            </div>
            <div className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
              <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>No API cost</p>
              <p className="text-xs font-medium mt-1" style={{ color: "var(--foreground)" }}>Per-ticket cost</p>
              <p className="text-xs mt-0.5" style={{ color: "var(--foreground-muted)" }}>Internal GPU time; opportunity cost exists</p>
            </div>
          </div>

          <div className="mt-4 p-4 rounded-lg" style={{ backgroundColor: "var(--accent-muted)" }}>
            <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-secondary)" }}>
              <strong style={{ color: "var(--foreground)" }}>The full evolution:</strong> Start with LLM few-shot (day 1, no data).
              Fine-tune the LLM as labeled data accumulates (month 2). Deploy the cascade (month 3).
              Once you have 1M+ LLM-classified tickets, distill into a fast model and use the LLM only for
              the ambiguous tail and drift detection. The LLM becomes the teacher, not the workhorse.
            </p>
          </div>
        </div>
      </section>

      {/* At OpenAI: The Optimal Architecture */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)", border: "2px solid var(--accent)" }}>
          <h2 className="text-sm font-medium mb-1" style={{ color: "var(--accent)" }}>
            At OpenAI: The Optimal Architecture
          </h2>
          <p className="text-xs mb-5 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            With internal access to frontier models and zero inference cost, the architecture
            shifts from &ldquo;which model is cheapest&rdquo; to &ldquo;which model produces the best training signal.&rdquo;
            The answer is a hierarchical distillation pipeline.
          </p>

          {/* The pipeline */}
          <div className="space-y-4">
            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>1</div>
              <div className="flex-1 p-4 rounded-lg border" style={{ borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium" style={{ color: "var(--foreground)" }}>The Oracle: o1 as Teacher</h3>
                  <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: "var(--background-secondary)", color: "var(--foreground-muted)" }}>offline, batch</span>
                </div>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  Use o1 to generate a high-quality training set. Because o1 uses chain-of-thought reasoning,
                  it doesn&apos;t just output a label — it outputs <em>why</em> the ticket belongs to that category.
                  This reasoning is the key: the student model learns the logic, not just the mapping.
                </p>
                <div className="mt-3 p-3 rounded font-mono text-xs" style={{ backgroundColor: "var(--background-secondary)", color: "var(--foreground-secondary)" }}>
                  <p style={{ color: "var(--foreground-muted)" }}>// o1 output for an ambiguous ticket:</p>
                  <p>&quot;The user mentions both a charge and an API key issue.</p>
                  <p>The primary complaint is the unauthorized charge ($200),</p>
                  <p>which is a billing issue. The API key problem is secondary</p>
                  <p>and likely a symptom of account-level action taken due to</p>
                  <p>the billing dispute.&quot;</p>
                  <p style={{ color: "var(--accent)" }}>→ category: billing (confidence: 0.87)</p>
                </div>
              </div>
            </div>

            <div className="flex gap-4 items-center">
              <div className="w-8 flex justify-center"><div className="w-0.5 h-6" style={{ backgroundColor: "var(--border)" }} /></div>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                Stored Completions capture o1&apos;s reasoning → feed into fine-tuning job
              </p>
            </div>

            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "var(--accent-muted)", color: "var(--accent)" }}>2</div>
              <div className="flex-1 p-4 rounded-lg border" style={{ borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium" style={{ color: "var(--foreground)" }}>The Student: Fine-Tuned GPT-4o-mini</h3>
                  <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: "var(--background-secondary)", color: "var(--foreground-muted)" }}>real-time, production</span>
                </div>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  Use OpenAI&apos;s Model Distillation workflow to train GPT-4o-mini on o1&apos;s outputs.
                  The mini model is significantly faster, already outperforms original GPT-4 on many benchmarks,
                  and is 16x more compute-efficient. With Structured Outputs, it returns strict JSON
                  matching your ticket schema — no parsing errors, no format drift.
                </p>
                <div className="flex gap-4 mt-3">
                  <div className="text-xs"><span style={{ color: "var(--accent)" }}>~200ms</span> latency</div>
                  <div className="text-xs"><span style={{ color: "var(--accent)" }}>128K</span> context window</div>
                  <div className="text-xs"><span style={{ color: "var(--success)" }}>No API cost</span></div>
                </div>
              </div>
            </div>

            <div className="flex gap-4 items-center">
              <div className="w-8 flex justify-center"><div className="w-0.5 h-6" style={{ backgroundColor: "var(--border)" }} /></div>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                Confidence &lt; 0.70 → escalate to human (same cascade pattern)
              </p>
            </div>

            <div className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold" style={{ backgroundColor: "rgba(196, 112, 90, 0.1)", color: "var(--error)" }}>3</div>
              <div className="flex-1 p-4 rounded-lg border" style={{ borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium" style={{ color: "var(--foreground)" }}>Human Agents + Feedback Loop</h3>
                  <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: "var(--background-secondary)", color: "var(--foreground-muted)" }}>continuous improvement</span>
                </div>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  Low-confidence tickets reach human agents. Their classifications feed back into the next
                  o1 labeling batch. The system improves continuously — and when new products launch
                  (the next Sora, the next Codex), o1 can reason about new ticket types without retraining.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why this beats BERT */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Why o1 → 4o-mini Beats Fine-Tuned BERT Internally
          </h2>
          <div className="grid grid-cols-3 gap-3">
            {[
              {
                title: "Context window",
                detail: "BERT truncates at 512 tokens. Real support tickets with email chains, error logs, or conversation history get cut off. GPT-4o-mini handles 128K tokens — nothing gets lost.",
              },
              {
                title: "Reasoning transfer",
                detail: "BERT learns that Text A = Label B. A distilled 4o-mini learns why Text A = Label B. When a new product launches and unfamiliar tickets arrive, the reasoning generalizes — pattern matching doesn't.",
              },
              {
                title: "Structured outputs",
                detail: "4o-mini with Structured Outputs returns strict JSON matching your ticket schema. No logit post-processing, no format drift, no parsing failures. BERT requires a separate output layer and schema enforcement.",
              },
            ].map((item) => (
              <div key={item.title} className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>{item.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>{item.detail}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 rounded-lg" style={{ backgroundColor: "var(--accent-muted)" }}>
            <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-secondary)" }}>
              <strong style={{ color: "var(--foreground)" }}>Important context:</strong> At any other company,
              fine-tuned BERT is a strong production choice — fast, well-understood, and no API dependency.
              The o1 → 4o-mini pipeline only dominates when you have zero-cost access to frontier reasoning models.
              That&apos;s an advantage specific to OpenAI.
            </p>
          </div>
        </div>
      </section>

      {/* Cold Start Timeline */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            The 90-Day Rollout
          </h2>
          <div className="space-y-3">
            {[
              { week: "Day 1", action: "Deploy o1 zero-shot classifier", result: "Immediate routing at ~75% accuracy. No labeled data needed.", color: "var(--chart-6)" },
              { week: "Week 1", action: "o1 labels 10K historical tickets with reasoning", result: "High-quality training set with chain-of-thought rationale.", color: "var(--chart-5)" },
              { week: "Week 2", action: "Distill into fine-tuned GPT-4o-mini", result: "Production classifier at ~93% accuracy, ~200ms latency.", color: "var(--chart-2)" },
              { week: "Month 2", action: "Deploy cascade with confidence thresholds", result: "Low-confidence tickets → human review. Humans generate training signal.", color: "var(--chart-4)" },
              { week: "Month 3", action: "Re-distill with human feedback + o1 re-labeling", result: "~95%+ accuracy. System is self-improving.", color: "var(--chart-1)" },
              { week: "Ongoing", action: "Monitor drift, handle new product launches", result: "o1 can reason about new ticket types without retraining the student.", color: "var(--chart-1)" },
            ].map((step) => (
              <div key={step.week} className="flex items-start gap-4 p-3 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <span className="text-xs font-medium w-16 shrink-0 pt-0.5" style={{ color: step.color }}>{step.week}</span>
                <div className="flex-1">
                  <p className="text-xs font-medium" style={{ color: "var(--foreground)" }}>{step.action}</p>
                  <p className="text-xs mt-0.5" style={{ color: "var(--foreground-muted)" }}>{step.result}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feedback Loop */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            The Feedback Loop
          </h2>
          <p className="text-xs mb-4 leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
            The cascade creates a self-improving system. Human-classified tickets from Step 3 become training data for both models.
          </p>
          <div className="grid grid-cols-3 gap-3">
            {[
              { title: "Human labels flow back", detail: "The 5% of tickets that reach human agents are the hardest cases — exactly the training data the models need most." },
              { title: "Confidence thresholds adapt", detail: "As models improve, the confidence threshold can increase, sending more tickets to auto-routing and fewer to humans." },
              { title: "New categories emerge", detail: "When agents consistently create tickets in a new category, it's automatically added to the next retraining cycle." },
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
            <li>The cascade (XGBoost → LLM → Human) achieves 96% effective accuracy — better than any single model — with 75% less LLM inference.</li>
            <li>At 1M+ tickets, distillation is the endgame: train a fast model on the LLM&apos;s outputs to get 93-94% accuracy at near-zero cost and &lt;5ms latency.</li>
            <li>The human-in-the-loop step isn&apos;t a failure mode — it&apos;s a feature. It creates the training data that makes the system better over time.</li>
            <li>The full arc: few-shot (day 1) → fine-tuned LLM (month 2) → cascade (month 3) → distillation (at scale). Each stage builds on the last.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
