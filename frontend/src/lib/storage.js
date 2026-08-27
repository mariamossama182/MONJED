/** Session storage + local ops inbox helpers used by staff dashboards. */

const SESSION_KEY = "monjed_session";
const USERS_KEY = "monjed_volunteers";
const REPORTS_KEY = "monjed_reports";
const HELP_KEY = "monjed_help_requests";

export const ADMIN_STAFF_KEY = "MONJED-OPS";

export function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

export function getSession() {
  return readJson(SESSION_KEY, null);
}

export function setSession(session) {
  writeJson(SESSION_KEY, session);
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

/** Map API session user → frontend session shape */
export function toClientSession(apiUser, extras = {}) {
  return {
    role: apiUser.role,
    id: apiUser.id || apiUser.volunteer_id || apiUser.user_id,
    name: apiUser.name,
    phone: apiUser.phone || "",
    email: apiUser.email || "",
    organization: apiUser.organization || "",
    title: apiUser.title || "",
    zone_id: apiUser.zone_id || "",
    country: apiUser.country || "",
    countryCode: apiUser.country_code || apiUser.countryCode || "",
    zone: apiUser.zone || "",
    available: apiUser.available,
    vehicleType: apiUser.vehicle_type || apiUser.vehicleType,
    capacity: apiUser.capacity,
    skills: apiUser.skills || [],
    ...extras,
  };
}

export function listVolunteers() {
  return readJson(USERS_KEY, []);
}

export function listReports() {
  return readJson(REPORTS_KEY, []);
}

export function addReport(report) {
  const next = [{ ...report, id: `rep-${Date.now()}` }, ...listReports()];
  writeJson(REPORTS_KEY, next);
  return next[0];
}

export function patchReport(id, patch) {
  const next = listReports().map((r) => (r.id === id ? { ...r, ...patch } : r));
  writeJson(REPORTS_KEY, next);
  return next;
}

export function listHelpRequests() {
  return readJson(HELP_KEY, []);
}

export function addHelpRequest(request) {
  const next = [{ ...request, id: `help-${Date.now()}` }, ...listHelpRequests()];
  writeJson(HELP_KEY, next);
  return next[0];
}

export function patchHelpRequest(id, patch) {
  const next = listHelpRequests().map((r) =>
    r.id === id ? { ...r, ...patch } : r
  );
  writeJson(HELP_KEY, next);
  return next;
}
