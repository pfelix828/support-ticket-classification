import Link from "next/link";
import {
  Database,
  BarChart3,
  Scan,
  Brain,
  Sparkles,
  Cpu,
  Zap,
  GitCompare,
  AlertTriangle,
  Network,
  FileText,
  ArrowRight,
} from "lucide-react";
const sections = [
  {
    href: "/data",
    icon: Database,
    title: "Data Explorer",
    description:
      "12,091 synthetic support tickets modeled after OpenAI's help center taxonomy. Browse examples, see class distributions, and understand the classification challenge.",
  },
  {
    href: "/llm",
    icon: Sparkles,
    title: "LLM Zero/Few-Shot",
    description:
      "No training data needed — just a well-crafted prompt. The starting point when you have no labeled data. ~78% F1 (zero-shot).",
  },
  {
    href: "/baseline",
    icon: BarChart3,
    title: "TF-IDF + Logistic / XGBoost",
    description:
      "The baseline that every ML project should start with. TF-IDF features with logistic regression and XGBoost — fast, interpretable, and surprisingly competitive. 86-87% F1.",
  },
  {
    href: "/embeddings",
    icon: Scan,
    title: "Embeddings + XGBoost",
    description:
      "BERT embeddings as features for XGBoost. Combines semantic understanding with structured metadata like customer tier and account age. 89% F1.",
  },
  {
    href: "/bert",
    icon: Brain,
    title: "Fine-Tuned BERT",
    description:
      "End-to-end fine-tuning on ticket text. Gains over the hybrid approach are narrow — and you lose metadata integration. 92% F1 (projected).",
  },
  {
    href: "/finetune",
    icon: Cpu,
    title: "Fine-Tuned LLM",
    description:
      "Fine-tuning GPT-4o-mini on ~9.5K tickets. The clear winner at 96.1% F1 — 7 points above the best classical method. At a company with internal LLM access, the cost calculus changes entirely.",
  },
  {
    href: "/distillation",
    icon: Zap,
    title: "Distillation (o1 → 4o-mini)",
    description:
      "Use o1 as a reasoning teacher, distill into GPT-4o-mini. With only 855 teacher labels, 69.9% F1 — proving distillation needs scale. The architecture is sound; the data volume wasn't.",
  },
  {
    href: "/comparison",
    icon: GitCompare,
    title: "Volume vs. Method",
    description:
      "How does accuracy change as labeled data grows from 100 to ~10K tickets? Learning curves reveal where each method's advantage kicks in — and which one you should use at your scale.",
  },
  {
    href: "/errors",
    icon: AlertTriangle,
    title: "Error Analysis",
    description:
      "What does each method get wrong? Ambiguous tickets, multi-intent requests, and the long tail of rare categories.",
  },
  {
    href: "/architecture",
    icon: Network,
    title: "Production Architecture",
    description:
      "The cascade system: XGBoost handles the confident 80%, the fine-tuned LLM handles the ambiguous 20%. At OpenAI's scale with internal LLM access, what does the optimal system look like?",
  },
  {
    href: "/methodology",
    icon: FileText,
    title: "Methodology",
    description:
      "Data generation, model training details, evaluation protocol, and assumptions.",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1
            className="text-4xl font-semibold tracking-tight leading-tight"
            style={{ color: "var(--foreground)" }}
          >
            Support Ticket
            <br />
            <span style={{ color: "var(--accent)" }}>Classification</span>
          </h1>
          <p
            className="mt-5 text-lg leading-relaxed max-w-2xl"
            style={{ color: "var(--foreground-secondary)" }}
          >
            When a support ticket arrives, it needs to reach the right team fast.
            But the right classification method depends on how many labeled
            tickets you have. This project compares seven approaches — from
            TF-IDF baselines to fine-tuned LLMs — across data volumes from 100
            to ~10K tickets, on synthetic data modeled after OpenAI&apos;s help
            center.
          </p>
        </div>
      </section>

      {/* The problem statement */}
      <section className="px-12 pb-12">
        <div
          className="rounded-lg border p-6"
          style={{
            backgroundColor: "var(--background-card)",
            borderColor: "var(--border)",
          }}
        >
          <h2
            className="text-sm font-medium mb-3"
            style={{ color: "var(--foreground-secondary)" }}
          >
            The Classification Challenge
          </h2>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <p className="text-2xl font-semibold" style={{ color: "var(--accent)" }}>12</p>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                Tier 1 categories spanning billing, API, ChatGPT, enterprise, and newer products
              </p>
            </div>
            <div>
              <p className="text-2xl font-semibold" style={{ color: "var(--accent)" }}>12K</p>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                Synthetic tickets with realistic language, ambiguity, and class imbalance
              </p>
            </div>
            <div>
              <p className="text-2xl font-semibold" style={{ color: "var(--accent)" }}>7</p>
              <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                Methods compared — from logistic regression to o1-distilled GPT-4o-mini
              </p>
            </div>
          </div>

          <div
            className="mt-5 p-5 rounded-lg"
            style={{ backgroundColor: "var(--background-secondary)" }}
          >
            <p className="text-sm leading-relaxed" style={{ color: "var(--foreground-secondary)" }}>
              The key question isn&apos;t &ldquo;which model has the highest F1 score.&rdquo;
              It&apos;s: given your ticket volume, latency budget, and infrastructure —{" "}
              <strong style={{ color: "var(--foreground)" }}>
                which approach should you actually deploy?
              </strong>{" "}
              At a company like OpenAI with internal LLM access, the calculus changes entirely.
            </p>
          </div>
        </div>
      </section>

      {/* Section Cards */}
      <section className="px-12 pb-16">
        <h2
          className="text-sm font-medium uppercase tracking-wide mb-6"
          style={{ color: "var(--foreground-muted)" }}
        >
          Explore
        </h2>
        <div className="grid grid-cols-2 gap-3">
          {sections.map(({ href, icon: Icon, title, description }) => (
            <Link
              key={href}
              href={href}
              className="group rounded-lg border p-5 transition-colors"
              style={{
                backgroundColor: "var(--background-card)",
                borderColor: "var(--border)",
              }}
            >
              <div className="flex items-start gap-3">
                <Icon
                  size={18}
                  className="mt-0.5 shrink-0"
                  style={{ color: "var(--accent)" }}
                />
                <div>
                  <h3
                    className="text-sm font-medium flex items-center gap-2"
                    style={{ color: "var(--foreground)" }}
                  >
                    {title}
                    <ArrowRight
                      size={14}
                      className="opacity-0 -translate-x-1 transition-all group-hover:opacity-100 group-hover:translate-x-0"
                      style={{ color: "var(--accent)" }}
                    />
                  </h3>
                  <p
                    className="text-xs mt-1 leading-relaxed"
                    style={{ color: "var(--foreground-muted)" }}
                  >
                    {description}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
