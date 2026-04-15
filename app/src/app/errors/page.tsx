export default function ErrorsPage() {
  const confusionPairs = [
    { actual: "API Usage", predicted: "API Errors", rate: "10–12%", why: "'How do I fix 429 errors?' is technically a question (usage) about an error. Every model confuses these — the boundary between asking about API behavior and reporting an API problem is genuinely ambiguous." },
    { actual: "API Errors", predicted: "API Usage", rate: "5–11%", why: "The reverse direction is nearly as bad. 'My API call returns unexpected results' could be a usage question or an error report depending on intent." },
    { actual: "Account Mgmt", predicted: "Account Access", rate: "7%", why: "'I need to change my account settings but can't log in' — both categories involve accounts. The distinction between managing an account and accessing it blurs constantly." },
    { actual: "Account Mgmt", predicted: "Enterprise", rate: "5–8%", why: "'How do I add users to my workspace?' — enterprise workspace management vs general account management. XGBoost struggles most here (7.8%)." },
    { actual: "Security", predicted: "API Errors", rate: "5%", why: "Security tickets mentioning API keys or authentication errors get pulled toward API categories. Only 98 security tickets in the dataset makes this harder." },
    { actual: "Security", predicted: "Account Mgmt", rate: "11%", why: "Embeddings + XGBoost confuses these most. 'Someone accessed my account' is both a security concern and an account issue." },
  ];

  const methodErrorProfiles = [
    {
      method: "TF-IDF + Logistic Regression",
      strength: "Clear keyword signals (e.g., 'refund' → Billing). Fastest to train and interpret.",
      weakness: "Fails when the same words appear across categories ('account', 'access', 'settings'). Worst on API Usage → API Errors (11.6%).",
    },
    {
      method: "TF-IDF + XGBoost",
      strength: "Boosting captures feature interactions that logistic regression misses.",
      weakness: "Both API confusion directions are bad (11.1% and 10.8%). Struggles with Account Mgmt → Enterprise (7.8%).",
    },
    {
      method: "Embeddings + XGBoost",
      strength: "Semantic similarity helps with paraphrasing. Metadata features disambiguate some edge cases.",
      weakness: "Security → Account Mgmt is its worst pair (11.2%). Embeddings alone can't distinguish overlapping intents.",
    },
    {
      method: "Fine-Tuned BERT",
      strength: "Learns subtle contextual cues from fine-tuning on domain text. Best overall F1 (91.2%) among non-LLM methods.",
      weakness: "Still confused by API Usage → API Errors (9.7%) and the reverse (8.8%). Account Mgmt errors spread across multiple categories (Access, API Usage, Enterprise).",
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
            Each method has a distinct error signature — where it fails reveals what it actually learns.
          </p>
          <div className="grid grid-cols-2 gap-3">
            {methodErrorProfiles.map((m) => (
              <div key={m.method} className="rounded-lg border p-4" style={{ borderColor: "var(--border)" }}>
                <div className="mb-2">
                  <h3 className="text-sm font-medium" style={{ color: "var(--foreground)" }}>{m.method}</h3>
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
            Security tickets make up only 1.5% of the dataset. Despite this, all three trained models handle rare categories
            better than you might expect — but the error patterns differ.
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
                  { method: "TF-IDF + LogReg", security: "82.8%", privacy: "86.6%", newer: "96.0%" },
                  { method: "TF-IDF + XGBoost", security: "85.6%", privacy: "83.3%", newer: "97.9%" },
                  { method: "Emb + XGBoost", security: "85.7%", privacy: "88.2%", newer: "96.7%" },
                  { method: "Fine-Tuned BERT", security: "88.9%", privacy: "90.8%", newer: "98.8%" },
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
            BERT leads all rare categories: Security (88.9%), Privacy (90.8%), Newer Products (98.8%).
            Fine-tuning on domain text gives it a clear edge on low-frequency classes despite limited examples.
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
            <li>The hardest errors are semantic, not lexical. API Usage vs API Errors is the top confusion pair across every model (10–12%), because the boundary is genuinely ambiguous.</li>
            <li>Each model has a distinct error signature. LogReg struggles most on API confusion; Embeddings + XGBoost has a unique Security → Account Mgmt problem (11.2%) that other models avoid.</li>
            <li>Rare categories perform better than expected. Security F1 ranges from 82.8% (LogReg) to 88.9% (BERT) despite only 98 training examples — careful feature engineering and fine-tuning matter more than raw volume.</li>
            <li>The production answer: don&apos;t try to eliminate all errors. Route low-confidence predictions to human agents and use their decisions as training data.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
