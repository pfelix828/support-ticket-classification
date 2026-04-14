export interface MethodResult {
  method: string;
  accuracy: number;
  f1_macro: number;
  f1_weighted: number;
  latency_ms: number;
  cost_per_ticket: number;
  training_time: string;
  strengths: string[];
  weaknesses: string[];
}

export interface ConfusionEntry {
  actual: string;
  predicted: string;
  count: number;
}

export interface LearningCurvePoint {
  volume: number;
  f1: number;
}

export const CATEGORY_LABELS: Record<string, string> = {
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
