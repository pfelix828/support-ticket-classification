"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const perClassData = [
  { category: "Billing", logreg: 0.87, xgboost: 0.91 },
  { category: "ChatGPT", logreg: 0.82, xgboost: 0.86 },
  { category: "Account", logreg: 0.80, xgboost: 0.85 },
  { category: "API Errors", logreg: 0.85, xgboost: 0.89 },
  { category: "Apps", logreg: 0.79, xgboost: 0.84 },
  { category: "Acct Mgmt", logreg: 0.72, xgboost: 0.78 },
  { category: "API Usage", logreg: 0.74, xgboost: 0.80 },
  { category: "Enterprise", logreg: 0.81, xgboost: 0.86 },
  { category: "GPTs", logreg: 0.77, xgboost: 0.83 },
  { category: "New Products", logreg: 0.83, xgboost: 0.87 },
  { category: "Privacy", logreg: 0.85, xgboost: 0.88 },
  { category: "Security", logreg: 0.68, xgboost: 0.73 },
];

const topFeatures = [
  { feature: "charged", weight: 2.31, category: "Billing" },
  { feature: "refund", weight: 2.18, category: "Billing" },
  { feature: "invoice", weight: 2.05, category: "Billing" },
  { feature: "429", weight: 1.95, category: "API Errors" },
  { feature: "rate limit", weight: 1.89, category: "API Errors" },
  { feature: "log in", weight: 1.82, category: "Account Access" },
  { feature: "password", weight: 1.76, category: "Account Access" },
  { feature: "ios", weight: 1.71, category: "ChatGPT Apps" },
  { feature: "sso", weight: 1.68, category: "Enterprise" },
  { feature: "sora", weight: 1.92, category: "Newer Products" },
  { feature: "gpt store", weight: 1.64, category: "GPTs" },
  { feature: "privacy", weight: 1.58, category: "Privacy" },
];

export default function BaselinePage() {
  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            TF-IDF + Logistic Regression / XGBoost
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            The baseline every classification project should start with. If you
            can&apos;t beat TF-IDF + XGBoost, you don&apos;t need deep learning.
          </p>
        </div>
      </section>

      {/* Method Overview */}
      <section className="px-12 pb-8">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border p-5" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
            <h3 className="text-sm font-medium mb-3" style={{ color: "var(--foreground)" }}>
              TF-IDF + Logistic Regression
            </h3>
            <p className="text-xs leading-relaxed mb-3" style={{ color: "var(--foreground-muted)" }}>
              Convert ticket text to TF-IDF vectors (unigrams + bigrams, max 10K features),
              then classify with logistic regression. Fully interpretable — you can see exactly
              which words drive each prediction.
            </p>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>84%</p>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>F1 (macro)</p>
              </div>
              <div>
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>&lt; 1ms</p>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>Latency</p>
              </div>
            </div>
          </div>
          <div className="rounded-lg border p-5" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
            <h3 className="text-sm font-medium mb-3" style={{ color: "var(--foreground)" }}>
              TF-IDF + XGBoost
            </h3>
            <p className="text-xs leading-relaxed mb-3" style={{ color: "var(--foreground-muted)" }}>
              Same TF-IDF features, but XGBoost as the classifier. Handles feature interactions
              better, built-in feature importance, handles class imbalance with sample weights.
              The stronger baseline.
            </p>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>88%</p>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>F1 (macro)</p>
              </div>
              <div>
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>&lt; 5ms</p>
                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>Latency</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Per-Class F1 */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-1" style={{ color: "var(--foreground-secondary)" }}>
            Per-Class F1 Score
          </h2>
          <p className="text-xs mb-6" style={{ color: "var(--foreground-muted)" }}>
            XGBoost outperforms logistic regression across all categories, especially on rarer classes like Security and Account Management.
          </p>
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={perClassData} margin={{ top: 5, right: 30, left: 10, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis
                dataKey="category"
                tick={{ fill: "var(--foreground-muted)", fontSize: 11 }}
                axisLine={{ stroke: "var(--border)" }}
                angle={-45}
                textAnchor="end"
                interval={0}
                height={70}
              />
              <YAxis
                domain={[0.5, 1.0]}
                tick={{ fill: "var(--foreground-muted)", fontSize: 12 }}
                axisLine={{ stroke: "var(--border)" }}
                tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--background-card)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                formatter={(v) => `${(Number(v) * 100).toFixed(1)}%`}
              />
              <Legend />
              <Bar dataKey="logreg" name="Logistic Regression" fill="var(--chart-baseline)" radius={[2, 2, 0, 0]} />
              <Bar dataKey="xgboost" name="XGBoost" fill="var(--chart-5)" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Top Features */}
      <section className="px-12 pb-8">
        <div className="rounded-lg border p-6" style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}>
          <h2 className="text-sm font-medium mb-1" style={{ color: "var(--foreground-secondary)" }}>
            Top Discriminating Features
          </h2>
          <p className="text-xs mb-4" style={{ color: "var(--foreground-muted)" }}>
            The most important TF-IDF features for each category. This interpretability is the key advantage of classical methods.
          </p>
          <div className="grid grid-cols-3 gap-2">
            {topFeatures.map((f) => (
              <div key={f.feature} className="flex items-center gap-3 px-3 py-2 rounded" style={{ backgroundColor: "var(--background-secondary)" }}>
                <code className="text-xs font-mono" style={{ color: "var(--accent)" }}>{f.feature}</code>
                <span className="text-xs ml-auto" style={{ color: "var(--foreground-muted)" }}>{f.category}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Takeaways */}
      <section className="px-12 pb-16">
        <div className="rounded-lg p-6" style={{ backgroundColor: "var(--accent-muted)" }}>
          <h3 className="text-sm font-medium mb-2" style={{ color: "var(--foreground)" }}>
            Key Takeaways
          </h3>
          <ul className="space-y-2 text-sm" style={{ color: "var(--foreground-secondary)" }}>
            <li>XGBoost gains 4 points over logistic regression — worth the switch for essentially zero added complexity.</li>
            <li>Both methods struggle with rare classes (Security: 68-73%) and semantically similar categories (Account Access vs. Account Management).</li>
            <li>Full interpretability: you can explain every prediction by pointing to specific words. This matters for compliance and debugging.</li>
            <li>At 100K tickets, this is a strong production baseline. The question is: does anything else justify the added complexity?</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
