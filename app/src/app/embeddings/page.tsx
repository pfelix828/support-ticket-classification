export default function EmbeddingsPage() {
  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            Embeddings + XGBoost
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            Use a pre-trained sentence transformer (e.g., all-MiniLM-L6-v2) to convert ticket
            text into dense embeddings, then classify with XGBoost. The hybrid: semantic
            understanding from the transformer, plus XGBoost&apos;s ability to incorporate
            structured metadata.
          </p>
        </div>
      </section>

      {/* Method Cards */}
      <section className="px-12 pb-8">
        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-lg border p-5" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
            <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>91%</p>
            <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>F1 (macro) at 100K tickets</p>
          </div>
          <div className="rounded-lg border p-5" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
            <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>~50ms</p>
            <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>Inference latency (embed + classify)</p>
          </div>
          <div className="rounded-lg border p-5" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
            <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>384 + 5</p>
            <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>Embedding dims + metadata features</p>
          </div>
        </div>
      </section>

      {/* Why This Works */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Why This Approach Works
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>Semantic Understanding</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                Unlike TF-IDF, embeddings capture semantic similarity. &ldquo;I can&apos;t sign in&rdquo; and
                &ldquo;unable to access my account&rdquo; get similar vectors even though they share no words.
                This is critical for support tickets where users describe the same problem in dozens of ways.
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>Metadata Integration</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                XGBoost can natively combine the 384-dim embedding vector with structured features:
                customer tier, account age, previous ticket count, urgency. An Enterprise customer
                asking about &ldquo;user access&rdquo; likely means SSO/SCIM; a Free user means login problems.
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>Calibrated Confidence</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                XGBoost probability outputs are well-calibrated and well-understood.
                You can set a confidence threshold and route low-confidence tickets to
                human review — a critical production pattern.
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>Fast Iteration</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                Embeddings are computed once, then XGBoost trains in seconds. You can
                retrain on new data, tune hyperparameters, and experiment with features
                without the GPU training time of BERT or LLM fine-tuning.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Importance */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Feature Importance: Embeddings vs. Metadata
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs leading-relaxed mb-3" style={{ color: "var(--foreground-muted)" }}>
                Embedding dimensions account for ~85% of total feature importance, but the 5 metadata
                features punch above their weight — especially <strong style={{ color: "var(--foreground)" }}>customer_tier</strong> which
                is the #3 most important feature overall.
              </p>
              <div className="space-y-2">
                {[
                  { feature: "Embedding dims (384)", importance: 85, color: "var(--chart-2)" },
                  { feature: "customer_tier", importance: 6, color: "var(--chart-5)" },
                  { feature: "account_age_days", importance: 4, color: "var(--chart-5)" },
                  { feature: "previous_tickets", importance: 3, color: "var(--chart-5)" },
                  { feature: "urgency", importance: 1.5, color: "var(--chart-5)" },
                ].map((f) => (
                  <div key={f.feature} className="flex items-center gap-3">
                    <span className="text-xs w-36 shrink-0" style={{ color: "var(--foreground-secondary)" }}>{f.feature}</span>
                    <div className="flex-1 h-4 rounded-full overflow-hidden" style={{ backgroundColor: "var(--background-secondary)" }}>
                      <div
                        className="h-full rounded-full"
                        style={{ width: `${f.importance}%`, backgroundColor: f.color, minWidth: "4px" }}
                      />
                    </div>
                    <span className="text-xs w-10 text-right" style={{ color: "var(--foreground-muted)" }}>{f.importance}%</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs leading-relaxed mb-3" style={{ color: "var(--foreground-muted)" }}>
                The metadata features are especially valuable for disambiguating tickets
                where the text alone is ambiguous:
              </p>
              <div className="space-y-3">
                {[
                  {
                    ticket: '"I need help with user access"',
                    metadata: "enterprise tier → SSO/SCIM",
                    without: "Account Access",
                    with: "Enterprise",
                  },
                  {
                    ticket: '"Something is wrong with my account"',
                    metadata: "0 previous tickets → new user",
                    without: "Account Mgmt",
                    with: "Account Access",
                  },
                  {
                    ticket: '"I was charged incorrectly"',
                    metadata: "api_only tier → API billing",
                    without: "Billing (ChatGPT)",
                    with: "Billing (API)",
                  },
                ].map((ex) => (
                  <div key={ex.ticket} className="p-3 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                    <p className="text-xs font-mono mb-1" style={{ color: "var(--foreground)" }}>{ex.ticket}</p>
                    <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                      {ex.metadata}
                    </p>
                  </div>
                ))}
              </div>
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
            <li>3 points over TF-IDF + XGBoost (91% vs 88%) — the semantic understanding matters.</li>
            <li>Metadata features provide meaningful lift, especially for ambiguous tickets. This is where the hybrid approach shines.</li>
            <li>This is the workhorse production pattern at many real support orgs — fast, accurate, and you can add business logic features incrementally.</li>
            <li>The question is whether BERT or a fine-tuned LLM can justify the added GPU infrastructure cost.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
