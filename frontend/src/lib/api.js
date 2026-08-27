const DEFAULT_BASE = "http://127.0.0.1:8000";

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE
).replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, { status, body } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status ?? 0;
    this.body = body ?? null;
  }
}

function detailMessage(body, fallback) {
  if (body == null) return fallback;
  if (typeof body === "string") return body;
  const detail = body.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || item?.message || JSON.stringify(item))
      .join("; ");
  }
  if (typeof body.message === "string") return body.message;
  try {
    return JSON.stringify(body);
  } catch {
    return fallback;
  }
}

export async function request(path, { method = "GET", body, headers } = {}) {
  const url = `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;

  let response;
  try {
    response = await fetch(url, {
      method,
      headers: {
        Accept: "application/json",
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...headers,
      },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    });
  } catch (err) {
    throw new ApiError(
      "Cannot reach the MONJED API. Confirm the backend is running and CORS allows this origin.",
      { status: 0, body: { cause: err?.message } }
    );
  }

  const raw = await response.text();
  let parsed = null;
  if (raw) {
    try {
      parsed = JSON.parse(raw);
    } catch {
      parsed = raw;
    }
  }

  if (!response.ok) {
    throw new ApiError(detailMessage(parsed, response.statusText || "Request failed"), {
      status: response.status,
      body: parsed,
    });
  }

  return parsed;
}

export function get(path) {
  return request(path, { method: "GET" });
}

export function post(path, body) {
  return request(path, { method: "POST", body });
}

export function put(path, body) {
  return request(path, { method: "PUT", body });
}

export function healthCheck() {
  return get("/health");
}

/** POST /risk/flood */
export function assessFloodRisk(payload) {
  return post("/risk/flood", payload);
}

/** POST /risk/earthquake */
export function assessEarthquakeRisk(payload) {
  return post("/risk/earthquake", payload);
}

/** POST /api/community-reports/analyze */
export function analyzeCommunityReport(payload) {
  return post("/api/community-reports/analyze", payload);
}

/** POST /api/community-reports/submit */
export function submitCommunityReport(payload) {
  return post("/api/community-reports/submit", payload);
}

/** GET /api/community-reports */
export function listCommunityReports() {
  return get("/api/community-reports");
}

/** GET /api/community-reports/recent/{zone_id} */
export function recentCommunityReports(zoneId) {
  return get(`/api/community-reports/recent/${encodeURIComponent(zoneId)}`);
}

/** POST /api/community-reports/{id}/verify */
export function verifyCommunityReport(id) {
  return post(`/api/community-reports/${encodeURIComponent(id)}/verify`);
}

/** POST /api/community-reports/{id}/resolve */
export function resolveCommunityReport(id) {
  return post(`/api/community-reports/${encodeURIComponent(id)}/resolve`);
}

export function submitContact(payload) {
  return post("/auth/contact", payload);
}

/** Auth */
export function registerUser(payload) {
  return post("/auth/register", payload);
}

export function loginUser(payload) {
  return post("/auth/login", payload);
}

export function loginAdmin(payload) {
  return post("/auth/admin", payload);
}

export function getAdminProfile() {
  return get("/auth/admin/profile");
}

export function updateAdminProfile(payload) {
  return put("/auth/admin/profile", payload);
}

/** Assistance / volunteers */
export function registerVolunteer(payload) {
  return post("/assistance/volunteers", payload);
}

export function loginVolunteer(payload) {
  return post("/assistance/volunteers/login", payload);
}

export function listVolunteers() {
  return get("/assistance/volunteers");
}

export function setVolunteerAvailability(volunteerId, available) {
  return post(
    `/assistance/volunteers/${encodeURIComponent(volunteerId)}/availability?available=${available}`
  );
}

export function createAssistanceRequest(payload) {
  return post("/assistance/requests", payload);
}

export function listAssistanceRequests() {
  return get("/assistance/requests");
}

export function listPendingAssistance() {
  return get("/assistance/requests/pending");
}

export function getAssistanceRequest(id) {
  return get(`/assistance/requests/${encodeURIComponent(id)}`);
}

export function matchAssistanceRequest(id) {
  return post(`/assistance/requests/${encodeURIComponent(id)}/match`);
}

export function startAssistanceRequest(id) {
  return post(`/assistance/requests/${encodeURIComponent(id)}/start`);
}

export function resolveAssistanceRequest(id) {
  return post(`/assistance/requests/${encodeURIComponent(id)}/resolve`);
}

/** Dashboard */
export function dashboardOverview() {
  return get("/dashboard/overview");
}

export function dashboardRisks(params = {}) {
  const q = new URLSearchParams();
  if (params.zone_id) q.set("zone_id", params.zone_id);
  if (params.hazard) q.set("hazard", params.hazard);
  if (params.limit) q.set("limit", String(params.limit));
  const qs = q.toString();
  return get(`/dashboard/risks${qs ? `?${qs}` : ""}`);
}

export function dashboardZone(zoneId) {
  return get(`/dashboard/zones/${encodeURIComponent(zoneId)}`);
}

export function dashboardAlerts(params = {}) {
  const q = new URLSearchParams();
  if (params.zone_id) q.set("zone_id", params.zone_id);
  if (params.limit) q.set("limit", String(params.limit));
  const qs = q.toString();
  return get(`/dashboard/alerts${qs ? `?${qs}` : ""}`);
}

export function dashboardDecisions(params = {}) {
  const q = new URLSearchParams();
  if (params.zone_id) q.set("zone_id", params.zone_id);
  if (params.limit) q.set("limit", String(params.limit));
  const qs = q.toString();
  return get(`/dashboard/decisions${qs ? `?${qs}` : ""}`);
}

/** POST /pipeline/flood */
export function pipelineFlood(payload, accessibilityNeeds = []) {
  const q = new URLSearchParams();
  accessibilityNeeds.forEach((n) => q.append("accessibility_needs", n));
  const qs = q.toString();
  return post(`/pipeline/flood${qs ? `?${qs}` : ""}`, payload);
}

export const api = {
  get,
  post,
  healthCheck,
  assessFloodRisk,
  assessEarthquakeRisk,
  analyzeCommunityReport,
  submitCommunityReport,
  listCommunityReports,
  recentCommunityReports,
  verifyCommunityReport,
  resolveCommunityReport,
  submitContact,
  registerUser,
  loginUser,
  loginAdmin,
  getAdminProfile,
  updateAdminProfile,
  registerVolunteer,
  loginVolunteer,
  listVolunteers,
  setVolunteerAvailability,
  createAssistanceRequest,
  listAssistanceRequests,
  listPendingAssistance,
  matchAssistanceRequest,
  startAssistanceRequest,
  resolveAssistanceRequest,
  dashboardOverview,
  dashboardRisks,
  dashboardZone,
  dashboardAlerts,
  dashboardDecisions,
  pipelineFlood,
};

export default api;
