// ──────────────────────────────────────────
// API Response Types — mirrors backend Pydantic schemas
// ──────────────────────────────────────────

// ── Subscriptions ──
export interface Subscription {
  subscription_id: string;
  display_name: string;
}

export interface ResourceGroup {
  name: string;
  location: string;
}

// ── Analysis ──
export type AnalysisStatus =
  | "queued"
  | "running"
  | "discovering_resources"
  | "resources_discovered"
  | "retrieving_costs"
  | "costs_retrieved"
  | "retrieving_recommendations"
  | "retrieving_metrics"
  | "evaluating_findings"
  | "scoring"
  | "completed"
  | "failed";

export interface AnalysisCreateRequest {
  subscription_id: string;
  resource_group: string;
}

export interface AnalysisCreateResponse {
  analysis_id: string;
  job_id: string | null;
  status: string;
  resource_count: number;
}

export interface AnalysisStatusResponse {
  analysis_id: string;
  job_id: string | null;
  status: AnalysisStatus;
  progress_percentage: number;
  current_stage: string | null;
  error_message: string | null;
}

export interface Analysis {
  id: string;
  subscription_id: string;
  resource_group: string;
  job_id: string | null;
  status: AnalysisStatus;
  progress_percentage: number;
  current_stage: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

// ── Cost ──
export interface DailyCost {
  date: string;
  amount: number;
}

export interface ResourceCostBreakdown {
  resource_id: string;
  resource_name: string;
  service_name: string;
  monthly_cost: number;
  currency: string;
  billing_period: string;
  daily_costs: DailyCost[];
}

export interface CostSummary {
  total_monthly_cost: number;
  potential_savings: number;
  resource_count: number;
}

// ── Findings ──
export type FindingSeverity = "Critical" | "High" | "Medium" | "Low" | "Info";
export type FindingCategory = "Compute" | "Storage" | "Network" | "Database" | "General";

export interface Finding {
  id: string;
  analysis_id: string;
  resource_id: string;
  severity: FindingSeverity;
  category: FindingCategory;
  title: string;
  description: string;
  estimated_monthly_savings: number;
  confidence_score: number;
  created_at: string;
}

// ── FinOps Score ──
export interface FinOpsScore {
  id: string | null;
  analysis_id: string | null;
  overall_score: number;
  compute_score: number;
  storage_score: number;
  network_score: number;
  recommendation_count: number;
  created_at: string | null;
}

// ── Tenant ──
export interface TenantMe {
  tenant_id: string;
}

export interface TenantStats {
  tenant_id: string;
  user_count: number;
  analysis_count: number;
  resource_count: number;
}

// ── Users ──
export type UserRole = "admin" | "analyst" | "viewer";

export interface User {
  id: string;
  email: string;
  display_name: string;
  role: UserRole;
}

export interface RoleUpdateRequest {
  role: UserRole;
}

// ── WebSocket Progress ──
export interface ProgressMessage {
  analysis_id: string;
  status: AnalysisStatus;
  progress: number;
  stage: string | null;
  error: string | null;
}

// ── Health ──
export interface HealthCheck {
  status: string;
  database: string;
  redis: string;
  azure: string;
}
