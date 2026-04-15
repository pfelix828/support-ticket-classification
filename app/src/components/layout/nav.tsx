"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Database,
  BarChart3,
  Scan,
  Brain,
  Cpu,
  Sparkles,
  Zap,
  GitCompare,
  AlertTriangle,
  Network,
  FileText,
} from "lucide-react";

interface NavEntry {
  href?: string;
  label: string;
  icon?: typeof Home;
  separator?: boolean;
}

const navItems: NavEntry[] = [
  { href: "/", label: "Overview", icon: Home },
  { href: "/data", label: "Data Explorer", icon: Database },

  { label: "Methods", separator: true },
  { href: "/llm", label: "LLM Zero/Few-Shot", icon: Sparkles },
  { href: "/baseline", label: "TF-IDF + Logistic / XGBoost", icon: BarChart3 },
  { href: "/embeddings", label: "Embeddings + XGBoost", icon: Scan },
  { href: "/bert", label: "Fine-Tuned BERT", icon: Brain },
  { href: "/finetune", label: "Fine-Tuned LLM", icon: Cpu },
  { href: "/distillation", label: "Distillation (o1 → 4o-mini)", icon: Zap },

  { label: "Analysis", separator: true },
  { href: "/comparison", label: "Volume vs. Method", icon: GitCompare },
  { href: "/errors", label: "Error Analysis", icon: AlertTriangle },
  { href: "/architecture", label: "Production Architecture", icon: Network },
  { href: "/methodology", label: "Methodology", icon: FileText },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <nav className="fixed left-0 top-0 h-full w-60 border-r flex flex-col"
      style={{
        backgroundColor: "var(--background-secondary)",
        borderColor: "var(--border)",
      }}
    >
      {/* Logo / Title */}
      <div className="p-5 border-b" style={{ borderColor: "var(--border)" }}>
        <Link href="/" className="block">
          <h1 className="text-sm font-semibold tracking-wide uppercase"
            style={{ color: "var(--foreground-secondary)" }}
          >
            Support Ticket
          </h1>
          <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
            Classification
          </p>
        </Link>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 overflow-y-auto py-3 px-3">
        {navItems.map((item) => {
          if (item.separator) {
            return (
              <div key={`sep-${item.label}`} className="mt-3 mb-2 px-3">
                <p className="text-xs font-medium uppercase tracking-wide" style={{ color: "var(--foreground-muted)", fontSize: "10px" }}>
                  {item.label}
                </p>
              </div>
            );
          }
          const Icon = item.icon!;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href!}
              className="flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors mb-0.5"
              style={{
                color: isActive ? "var(--foreground)" : "var(--foreground-secondary)",
                backgroundColor: isActive ? "var(--accent-muted)" : "transparent",
              }}
            >
              <Icon
                size={16}
                style={{
                  color: isActive ? "var(--accent)" : "var(--foreground-muted)",
                }}
              />
              {item.label}
            </Link>
          );
        })}
      </div>

      {/* Footer */}
      <div className="p-4 border-t" style={{ borderColor: "var(--border)" }}>
        <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
          Built by{" "}
          <a
            href="https://pfelix828.github.io"
            target="_blank"
            rel="noopener noreferrer"
            className="underline transition-colors"
            style={{ color: "var(--chart-1)" }}
          >
            Philip Felix
          </a>
        </p>
        <div className="flex gap-3 mt-2">
          <a
            href="https://github.com/pfelix828"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs underline"
            style={{ color: "var(--foreground-muted)" }}
          >
            GitHub
          </a>
          <a
            href="https://www.linkedin.com/in/pfelix1"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs underline"
            style={{ color: "var(--foreground-muted)" }}
          >
            LinkedIn
          </a>
        </div>
      </div>
    </nav>
  );
}
