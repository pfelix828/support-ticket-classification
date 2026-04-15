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
  { category: "Billing", logreg: 0.9057, xgboost: 0.9 },
  { category: "ChatGPT", logreg: 0.9032, xgboost: 0.8612 },
  { category: "Account", logreg: 0.8606, xgboost: 0.8556 },
  { category: "API Errors", logreg: 0.8398, xgboost: 0.8182 },
  { category: "Apps", logreg: 0.903, xgboost: 0.8925 },
  { category: "Acct Mgmt", logreg: 0.8075, xgboost: 0.7753 },
  { category: "API Usage", logreg: 0.8009, xgboost: 0.7671 },
  { category: "Enterprise", logreg: 0.8739, xgboost: 0.8603 },
  { category: "GPTs", logreg: 0.9404, xgboost: 0.9585 },
  { category: "New Products", logreg: 0.9595, xgboost: 0.9787 },
  { category: "Privacy", logreg: 0.8662, xgboost: 0.8328 },
  { category: "Security", logreg: 0.828, xgboost: 0.8556 },
];

const topFeatures = [
  { feature: "charged", weight: 5.78, category: "Billing" },
  { feature: "card", weight: 5.79, category: "Billing" },
  { feature: "login", weight: 4.85, category: "Account Access" },
  { feature: "password", weight: 4.24, category: "Account Access" },
  { feature: "api", weight: 6.03, category: "API Errors" },
  { feature: "app", weight: 7.35, category: "ChatGPT Apps" },
  { feature: "admin", weight: 5.89, category: "Enterprise" },
  { feature: "codex", weight: 11.54, category: "Newer Products" },
  { feature: "sora", weight: 7.41, category: "Newer Products" },
  { feature: "gpt", weight: 14.61, category: "GPTs" },
  { feature: "data", weight: 6.43, category: "Privacy" },
  { feature: "key", weight: 6.74, category: "Security" },
  { feature: "tokens", weight: 3.57, category: "API Usage" },
  { feature: "org", weight: 5.28, category: "Acct Mgmt" },
  { feature: "chatgpt", weight: 6.25, category: "ChatGPT" },
  { feature: "image", weight: 3.95, category: "ChatGPT" },
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
            can&apos;t beat TF-IDF + logistic regression, you don&apos;t need deep learning.
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
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>87.4%</p>
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
            </p>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-lg font-semibold" style={{ color: "var(--accent)" }}>86.3%</p>
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
            Logistic regression outperforms XGBoost on macro F1 (87.4% vs 86.3%), though XGBoost edges ahead on rare categories like GPTs, Newer Products, and Security.
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
            <li>Logistic regression beats XGBoost on macro F1 (87.4% vs 86.3%) — the simpler model wins overall, a useful reminder to always check.</li>
            <li>XGBoost has an edge on rare categories (Newer Products: 97.9% vs 96.0%, GPTs: 95.9% vs 94.0%, Security: 85.6% vs 82.8%) where tree-based feature interactions help.</li>
            <li>Both methods struggle most with semantically similar categories (Account Management: 77-81%, API Usage: 77-80%).</li>
            <li>Full interpretability: you can explain every prediction by pointing to specific words. This matters for compliance and debugging.</li>
            <li>At 87.4% macro F1 with sub-millisecond latency, this is already a strong production baseline. The question is: does anything else justify the added complexity?</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
