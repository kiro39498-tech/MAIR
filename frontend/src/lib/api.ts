const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "";

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  let res: Response;
  try {
    res = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch (e) {
    throw new ApiError(`Network error contacting ${url}`);
  }
  if (!res.ok) {
    throw new ApiError(`Request failed (${res.status})`, res.status);
  }
  return (await res.json()) as T;
}

export type MaterialStatus =
  | "Healthy"
  | "Near Reorder"
  | "Safety Stock Warning"
  | "Shortage"
  | "Excess"
  | string;

export interface DashboardSummary {
  total_rows?: number;
  status_counts?: Record<string, number>;
  [k: string]: unknown;
}

export interface MaterialRow {
  material_id: string;
  plant_id: string;
  status: MaterialStatus;
  usable_inventory?: number;
  safety_stock?: number;
  reorder_point?: number;
  description?: string;
  [k: string]: unknown;
}

export interface MaterialDetail extends MaterialRow {
  projected_shortage_date?: string | null;
  projected_shortage_qty?: number | null;
  production_impact?: unknown;
  po_coverage?: unknown;
  [k: string]: unknown;
}

export interface Recommendation {
  material_id: string;
  plant_id: string;
  recommended_action: string;
  priority: string;
  reason: string;
  recommended_qty?: number;
  suggested_supplier_id?: string;
  lead_time_days?: number;
  [k: string]: unknown;
}

export interface ReplenishmentAction {
  action_id: string;
  material_id: string;
  plant_id: string;
  recommended_action: string;
  recommended_qty: number;
  suggested_supplier_id?: string;
  priority_score: number;
  rationale: string;
  status: string;
  approval_token: string;
  notified_at?: string;
  decided_at?: string;
  decision_note?: string;
  created_at: string;
  updated_at: string;
  [k: string]: unknown;
}

export interface ProductRiskRow {
  material_id: string;
  material_name: string;
  plant_id: string;
  on_hand_qty: number;
  safety_stock: number;
  reorder_point: number;
  max_stock: number;
  health_status: string;
  days_of_supply: number;
  priority_score: number;
}

export interface BlockingComponent {
  material_id: string;
  health_status: string;
  usable_qty: number;
  reorder_point: number;
  safety_stock: number;
  shortfall: number;
}

export interface ProductBomRiskRow {
  product_id: string;
  product_name: string;
  plant_id: string;
  risk_status: string;
  blocking_components: BlockingComponent[];
  priority_score: number;
}

export const api = {
  summary: () => request<DashboardSummary>("/api/dashboard/summary"),
  productRisk: () => request<ProductRiskRow[]>("/api/dashboard/product-risk"),
  productBomRisk: () => request<ProductBomRiskRow[]>("/api/dashboard/product-bom-risk"),
  materials: (params?: { status?: string; risky_only?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.risky_only) q.set("risky_only", "true");
    const qs = q.toString();
    return request<MaterialRow[]>(`/api/dashboard/materials${qs ? `?${qs}` : ""}`);
  },
  material: (materialId: string, plantId: string) =>
    request<MaterialDetail>(
      `/api/dashboard/materials/${encodeURIComponent(materialId)}/${encodeURIComponent(plantId)}`,
    ),
  recommendations: () => request<Recommendation[]>("/api/dashboard/recommendations"),
  chat: (message: string) =>
    request<{ reply?: string; response?: string; message?: string; [k: string]: unknown }>(
      "/api/copilot/chat",
      { method: "POST", body: JSON.stringify({ message }) },
    ),
  
  // Phase 2: Actions Workflow
  actions: {
    list: async (status?: string): Promise<ReplenishmentAction[]> => {
      let url = `${BASE_URL}/api/replenishment/actions`;
      if (status) url += `?status=${encodeURIComponent(status)}`;
      const res = await fetch(url);
      if (!res.ok) throw new ApiError(`Failed to fetch actions`, res.status);
      return res.json();
    },
    create: async (materialId: string, plantId: string, suggestedQty?: number): Promise<ReplenishmentAction> => {
      const res = await fetch(`${BASE_URL}/api/replenishment/actions/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ material_id: materialId, plant_id: plantId, suggested_qty_override: suggestedQty }),
      });
      if (!res.ok) throw new ApiError(`Failed to create action`, res.status);
      return res.json();
    },
    runPipeline: () => 
      request<ReplenishmentAction[]>("/api/replenishment/run", { method: "POST" }),
    approve: async (actionId: string, token: string) => {
      const url = `${BASE_URL}/api/replenishment/actions/${encodeURIComponent(actionId)}/approve?token=${encodeURIComponent(token)}`;
      const res = await fetch(url);
      if (!res.ok) throw new ApiError(`Failed to approve`, res.status);
      return res.text();
    },
    reject: async (actionId: string, token: string) => {
      const url = `${BASE_URL}/api/replenishment/actions/${encodeURIComponent(actionId)}/reject?token=${encodeURIComponent(token)}`;
      const res = await fetch(url);
      if (!res.ok) throw new ApiError(`Failed to reject`, res.status);
      return res.text();
    },
    execute: (actionId: string) =>
      request<ReplenishmentAction>(`/api/replenishment/actions/${encodeURIComponent(actionId)}/execute`, { method: "POST" }),
  },
};

export const API_BASE_URL = BASE_URL;