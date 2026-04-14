"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface Ticket {
  id: number;
  text: string;
  category: string;
  secondary_category: string | null;
  customer_tier: string;
  account_age_days: number;
  previous_tickets: number;
  is_ambiguous: boolean;
  urgency: string;
}

interface CategoryStats {
  [key: string]: {
    count: number;
    percentage: number;
    description: string;
  };
}

const CATEGORY_COLORS: Record<string, string> = {
  billing: "var(--chart-1)",
  chatgpt_product: "var(--chart-2)",
  account_access: "var(--chart-4)",
  api_errors: "var(--chart-3)",
  chatgpt_apps: "var(--chart-5)",
  account_management: "var(--chart-6)",
  api_usage: "var(--chart-baseline)",
  enterprise: "var(--chart-1)",
  gpts: "var(--chart-2)",
  newer_products: "var(--chart-4)",
  privacy_policy: "var(--chart-5)",
  security: "var(--chart-3)",
};

const CATEGORY_LABELS: Record<string, string> = {
  billing: "Billing",
  chatgpt_product: "ChatGPT Product",
  account_access: "Account Access",
  api_errors: "API Errors",
  chatgpt_apps: "ChatGPT Apps",
  account_management: "Account Mgmt",
  api_usage: "API Usage",
  enterprise: "Enterprise",
  gpts: "GPTs",
  newer_products: "Newer Products",
  privacy_policy: "Privacy",
  security: "Security",
};

export default function DataExplorerPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<CategoryStats>({});
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [filterAmbiguous, setFilterAmbiguous] = useState<boolean>(false);

  useEffect(() => {
    fetch("/data/tickets_sample.json")
      .then((r) => r.json())
      .then(setTickets);
    fetch("/data/category_stats.json")
      .then((r) => r.json())
      .then(setStats);
  }, []);

  const chartData = Object.entries(stats)
    .map(([key, val]) => ({
      name: CATEGORY_LABELS[key] || key,
      key,
      count: val.count,
      pct: val.percentage,
    }))
    .sort((a, b) => b.count - a.count);

  const filteredTickets = tickets.filter((t) => {
    if (filterCategory !== "all" && t.category !== filterCategory) return false;
    if (filterAmbiguous && !t.is_ambiguous) return false;
    return true;
  });

  const displayTickets = filteredTickets.slice(0, 50);

  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1
            className="text-3xl font-semibold tracking-tight"
            style={{ color: "var(--foreground)" }}
          >
            Data Explorer
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            100,000 synthetic support tickets across 12 categories, modeled
            after OpenAI&apos;s public help center taxonomy. Realistic class
            imbalance, ambiguous tickets, and structured metadata.
          </p>
        </div>
      </section>

      {/* Distribution Chart */}
      <section className="px-12 pb-8">
        <div
          className="rounded-lg border p-6"
          style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}
        >
          <h2 className="text-sm font-medium mb-1" style={{ color: "var(--foreground-secondary)" }}>
            Category Distribution
          </h2>
          <p className="text-xs mb-6" style={{ color: "var(--foreground-muted)" }}>
            100,000 tickets. Billing and ChatGPT dominate; Security is the rarest class.
          </p>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={chartData} margin={{ top: 5, right: 30, left: 10, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis
                dataKey="name"
                tick={{ fill: "var(--foreground-muted)", fontSize: 11 }}
                axisLine={{ stroke: "var(--border)" }}
                angle={-35}
                textAnchor="end"
                interval={0}
              />
              <YAxis
                tick={{ fill: "var(--foreground-muted)", fontSize: 12 }}
                axisLine={{ stroke: "var(--border)" }}
                tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}K`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--background-card)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                formatter={(value, _name, props) => {
                  const v = Number(value);
                  const pct = (props as { payload?: { pct?: number } })?.payload?.pct ?? 0;
                  return [`${v.toLocaleString()} tickets (${pct}%)`, "Count"];
                }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {chartData.map((entry) => (
                  <Cell key={entry.key} fill={CATEGORY_COLORS[entry.key] || "var(--chart-baseline)"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Dataset Stats */}
      <section className="px-12 pb-8">
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "Total Tickets", value: "100,000" },
            { label: "Categories", value: "12" },
            { label: "Ambiguous Tickets", value: "~10%" },
            { label: "Metadata Fields", value: "5" },
          ].map((stat) => (
            <div
              key={stat.label}
              className="rounded-lg border p-4"
              style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}
            >
              <p className="text-xl font-semibold" style={{ color: "var(--accent)" }}>{stat.value}</p>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Ticket Browser */}
      <section className="px-12 pb-16">
        <div
          className="rounded-lg border"
          style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}
        >
          <div className="p-5 border-b flex items-center gap-4" style={{ borderColor: "var(--border)" }}>
            <h2 className="text-sm font-medium" style={{ color: "var(--foreground-secondary)" }}>
              Sample Tickets
            </h2>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="text-xs px-3 py-1.5 rounded-md border"
              style={{
                backgroundColor: "var(--background-secondary)",
                borderColor: "var(--border)",
                color: "var(--foreground-secondary)",
              }}
            >
              <option value="all">All categories</option>
              {Object.keys(CATEGORY_LABELS).map((key) => (
                <option key={key} value={key}>{CATEGORY_LABELS[key]}</option>
              ))}
            </select>
            <label className="flex items-center gap-2 text-xs" style={{ color: "var(--foreground-muted)" }}>
              <input
                type="checkbox"
                checked={filterAmbiguous}
                onChange={(e) => setFilterAmbiguous(e.target.checked)}
              />
              Ambiguous only
            </label>
            <span className="text-xs ml-auto" style={{ color: "var(--foreground-muted)" }}>
              Showing {Math.min(displayTickets.length, 50)} of {filteredTickets.length} sample tickets
            </span>
          </div>
          <div className="divide-y" style={{ borderColor: "var(--border)" }}>
            {displayTickets.map((ticket) => (
              <div key={ticket.id} className="px-5 py-3 flex gap-4 items-start">
                <div className="flex-1 min-w-0">
                  <p className="text-sm leading-relaxed" style={{ color: "var(--foreground)" }}>
                    {ticket.text}
                  </p>
                  <div className="flex items-center gap-4 mt-2">
                    {/* Category labels */}
                    <div className="flex gap-1.5">
                      <span
                        className="inline-flex px-2 py-0.5 rounded text-xs"
                        style={{
                          backgroundColor: "var(--accent-muted)",
                          color: "var(--accent)",
                        }}
                      >
                        {CATEGORY_LABELS[ticket.category] || ticket.category}
                      </span>
                      {ticket.secondary_category && (
                        <span
                          className="inline-flex px-2 py-0.5 rounded text-xs"
                          style={{
                            backgroundColor: "rgba(196, 112, 90, 0.1)",
                            color: "var(--chart-3)",
                          }}
                        >
                          + {CATEGORY_LABELS[ticket.secondary_category] || ticket.secondary_category}
                        </span>
                      )}
                    </div>
                    {/* Separator */}
                    <div className="w-px h-4" style={{ backgroundColor: "var(--border)" }} />
                    {/* Metadata */}
                    <div className="flex gap-1.5 text-xs" style={{ color: "var(--foreground-muted)" }}>
                      <span>{ticket.customer_tier}</span>
                      <span style={{ color: "var(--border)" }}>/</span>
                      <span style={{ color: ticket.urgency === "high" ? "var(--chart-3)" : "var(--foreground-muted)" }}>
                        {ticket.urgency} urgency
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
