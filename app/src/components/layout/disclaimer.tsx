"use client";

import { useState } from "react";

export function Disclaimer() {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div
      className="flex items-center justify-between gap-4 px-6 py-3"
      style={{ backgroundColor: "var(--accent-muted)", borderBottom: "1px solid var(--border)" }}
    >
      <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-secondary)" }}>
        <strong style={{ color: "var(--foreground)" }}>Note:</strong>{" "}
        This project uses synthetic support ticket data modeled after OpenAI&apos;s publicly visible help center categories.
        No real user data is used. The value is in the classification methodology and method comparison, not the specific tickets.
      </p>
      <button
        onClick={() => setDismissed(true)}
        className="shrink-0 px-2 py-1 rounded text-xs"
        style={{ color: "var(--foreground-muted)" }}
      >
        ✕
      </button>
    </div>
  );
}
