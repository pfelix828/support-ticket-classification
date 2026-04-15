export default function MethodologyPage() {
  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            Methodology
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            How the data was generated, how models were evaluated, and what
            assumptions underlie the results.
          </p>
        </div>
      </section>

      {/* Data Generation */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Data Generation
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--foreground)" }}>Taxonomy Source</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                Categories and subcategories are modeled after OpenAI&apos;s public help center
                at help.openai.com. The 12 Tier-1 categories were derived from the help center&apos;s
                collection structure: Account/Login/Billing, API, ChatGPT, ChatGPT Atlas,
                ChatGPT Business, ChatGPT Enterprise/Edu, Codex, Open Models, Privacy, Secure Sign In,
                Sora, and SSO/SCIM — then consolidated into categories that map to realistic
                support team routing.
              </p>
            </div>
            <div>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--foreground)" }}>LLM-Generated Tickets</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                12,091 unique tickets generated using Claude Haiku, with structured prompts
                specifying category, customer tier, urgency, and account metadata. Each ticket
                is a unique natural-language formulation — no templates. This produces realistic
                variation in phrasing, tone, and specificity that template-based approaches cannot match.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mt-6">
            <div>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--foreground)" }}>Class Imbalance</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                Weights reflect estimated real-world volume: Billing (16%) and ChatGPT Product (15%)
                dominate, while Security (1%) and Privacy (3%) are rare. This imbalance is a
                deliberate design choice — it&apos;s the central challenge in real support ticket classification.
              </p>
            </div>
            <div>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--foreground)" }}>Ambiguous Tickets</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                10% of tickets are multi-intent or ambiguous, drawn from 30 hand-crafted templates
                (e.g., &ldquo;I was charged twice AND my API key stopped working&rdquo;). Each has a primary
                and secondary category label. These test the classifier&apos;s ability to handle real-world
                ticket complexity.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Metadata */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Metadata Features
          </h2>
          <div className="overflow-hidden rounded-lg border" style={{ borderColor: "var(--border)" }}>
            <table className="w-full text-sm">
              <thead>
                <tr style={{ backgroundColor: "var(--background-secondary)" }}>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Feature</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Type</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Distribution</th>
                  <th className="text-left px-5 py-3 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>Why It Matters</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { feature: "customer_tier", type: "Categorical", dist: "Free 30%, Plus 25%, Pro 10%, Go 10%, Enterprise 10%, API 15%", why: "Enterprise users asking about 'access' likely mean SSO, not login" },
                  { feature: "account_age_days", type: "Numeric", dist: "Gamma(2, 180), capped at 1500", why: "New accounts → onboarding issues; old accounts → billing/management" },
                  { feature: "previous_tickets", type: "Numeric", dist: "Exponential(0.5), capped at 20", why: "Repeat tickets suggest unresolved issues, influences urgency routing" },
                  { feature: "urgency", type: "Categorical", dist: "High 15%, Medium 60%, Low 25%", why: "Urgent billing tickets need different routing than casual how-to questions" },
                  { feature: "is_ambiguous", type: "Boolean", dist: "~10% True", why: "Ground truth for evaluating multi-intent detection" },
                ].map((row, i) => (
                  <tr key={row.feature} style={{ borderTop: "1px solid var(--border)", backgroundColor: i % 2 === 0 ? "var(--background-card)" : "var(--background-secondary)" }}>
                    <td className="px-5 py-2.5 text-xs font-mono" style={{ color: "var(--accent)" }}>{row.feature}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-secondary)" }}>{row.type}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-muted)" }}>{row.dist}</td>
                    <td className="px-5 py-2.5 text-xs" style={{ color: "var(--foreground-muted)" }}>{row.why}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Evaluation Protocol */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Evaluation Protocol
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--foreground)" }}>Train / Test Split</h3>
              <ul className="space-y-1.5 text-xs" style={{ color: "var(--foreground-muted)" }}>
                <li>~12K total tickets (80/20 split = ~9,557 train / ~2,390 test, stratified by category)</li>
                <li>Test set held out entirely during development</li>
                <li>Ambiguous tickets present in both splits proportionally</li>
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--foreground)" }}>Metrics</h3>
              <ul className="space-y-1.5 text-xs" style={{ color: "var(--foreground-muted)" }}>
                <li><strong style={{ color: "var(--foreground-secondary)" }}>F1 macro</strong> — primary metric, treats all classes equally (important given imbalance)</li>
                <li><strong style={{ color: "var(--foreground-secondary)" }}>F1 weighted</strong> — secondary, accounts for class frequency</li>
                <li><strong style={{ color: "var(--foreground-secondary)" }}>Per-class F1</strong> — for understanding rare category performance</li>
                <li><strong style={{ color: "var(--foreground-secondary)" }}>Latency</strong> — measured as p50 inference time</li>
              </ul>
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-xs font-medium mb-2" style={{ color: "var(--foreground)" }}>Learning Curve Protocol</h3>
            <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
              For the Volume vs. Method analysis, models are trained on random subsets of 100, 500, 1K, 5K,
              and ~9.5K tickets (stratified sampling to preserve class distribution). Each is evaluated on the same
              held-out test set. This isolates the effect of training data volume from model capacity.
            </p>
          </div>
        </div>
      </section>

      {/* Limitations */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Limitations &amp; Assumptions
          </h2>
          <div className="space-y-3">
            {[
              { title: "Synthetic data", detail: "LLM-generated tickets are more coherent and consistent than real support tickets. Real tickets have typos, code snippets, screenshots, conversation threads, and emotional language that synthetic generation can't fully capture. Results on real data would likely be lower across all methods." },
              { title: "Measured vs. projected results", detail: "Local model results (TF-IDF + Logistic Regression, TF-IDF + XGBoost, Embeddings + XGBoost) and LLM zero-shot are real measured results from actual training runs on this dataset. Fine-tuned BERT curves are projected based on published benchmarks. Fine-tuned LLM and distillation evaluations are in progress." },
              { title: "No multi-label evaluation", detail: "Ambiguous tickets are labeled with primary + secondary category, but evaluation uses only the primary label. A production system might want true multi-label classification." },
              { title: "Static categories", detail: "Real support categories evolve. New products launch, old ones deprecate. This dataset is a snapshot. A production system needs drift detection and category management." },
              { title: "No ticket context", detail: "Real tickets often include images, attachments, conversation history, and account state. This dataset uses text + metadata only." },
            ].map((item) => (
              <div key={item.title} className="p-4 rounded-lg" style={{ backgroundColor: "var(--background-secondary)" }}>
                <h3 className="text-xs font-medium mb-1" style={{ color: "var(--foreground)" }}>{item.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>{item.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stack */}
      <section className="px-12 pb-16">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-3" style={{ color: "var(--foreground-secondary)" }}>
            Technology Stack
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--foreground)" }}>Data Generation &amp; Analysis</h3>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                Python 3.12+ with standard library only (no ML dependencies for generation).
                Analysis pipeline would use pandas, scikit-learn, XGBoost, sentence-transformers,
                Hugging Face transformers, and OpenAI API for fine-tuning.
              </p>
            </div>
            <div>
              <h3 className="text-xs font-medium mb-2" style={{ color: "var(--foreground)" }}>Interactive App</h3>
              <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                Next.js 16, TypeScript, React 19, Tailwind CSS 4, shadcn/ui (base-nova),
                Recharts for data visualization, Framer Motion for animations,
                Vercel for deployment.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
