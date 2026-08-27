import { createContext, useContext, useMemo, useState } from "react";
import {
  clearSession,
  getSession,
  setSession,
  toClientSession,
} from "./storage.js";
import {
  loginAdmin as apiLoginAdmin,
  loginUser as apiLoginUser,
  loginVolunteer as apiLoginVolunteer,
  registerUser as apiRegisterUser,
  registerVolunteer as apiRegisterVolunteer,
  setVolunteerAvailability as apiSetAvailability,
  updateAdminProfile as apiUpdateAdminProfile,
} from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSessionState] = useState(() => getSession());

  const value = useMemo(() => {
    function persist(next) {
      setSession(next);
      setSessionState(next);
    }

    return {
      session,
      isSignedIn: !!session,
      isUser: session?.role === "user",
      isAdmin: session?.role === "admin",
      isVolunteer: session?.role === "volunteer",

      async loginAsUser(phone, password) {
        const apiUser = await apiLoginUser({ phone, password });
        const next = toClientSession(apiUser);
        persist(next);
        return next;
      },

      async signupUser(profile) {
        const apiUser = await apiRegisterUser({
          name: profile.name,
          phone: profile.phone,
          password: profile.password,
          zone_id: profile.countryCode || profile.zone_id || "KE",
          country: profile.country,
          country_code: profile.countryCode,
          zone: profile.zone || "",
          notification_consent: true,
        });
        const next = toClientSession(apiUser);
        persist(next);
        return next;
      },

      async loginAsVolunteer(phone, password) {
        const apiUser = await apiLoginVolunteer({ phone, password });
        const next = toClientSession(
          { ...apiUser, role: "volunteer", id: apiUser.volunteer_id },
          { available: apiUser.available }
        );
        persist(next);
        return next;
      },

      async signupVolunteer(profile) {
        const skillMap = {
          "First aid": "medical_support",
          Driving: "transportation",
          "Boat / water rescue": "rescue_support",
          Translation: "general_support",
          Logistics: "general_support",
          "Shelter setup": "evacuation",
        };
        const skills = (profile.skills || [])
          .map((s) => skillMap[s] || "general_support")
          .filter((v, i, a) => a.indexOf(v) === i);

        const apiUser = await apiRegisterVolunteer({
          name: profile.name,
          zone_id: profile.zone_id || profile.country || "KE",
          phone: profile.phone,
          password: profile.password,
          available: true,
          responder_level: "volunteer",
          vehicle_type: profile.vehicleType === "none" ? null : profile.vehicleType,
          capacity: Number(profile.capacity) || 1,
          skills,
        });
        const next = toClientSession(
          { ...apiUser, role: "volunteer", id: apiUser.volunteer_id },
          { available: apiUser.available }
        );
        persist(next);
        return next;
      },

      async loginAsAdmin(name, staffKey) {
        const apiUser = await apiLoginAdmin({
          name: name || "Operations",
          staff_key: staffKey,
        });
        const next = toClientSession(apiUser);
        persist(next);
        return next;
      },

      async updateAdminProfile(profile) {
        const apiUser = await apiUpdateAdminProfile({
          name: profile.name,
          phone: profile.phone || "",
          email: profile.email || "",
          organization: profile.organization || "",
          title: profile.title || "",
          country: profile.country || "",
          zone: profile.zone || "",
        });
        const next = toClientSession(apiUser);
        persist(next);
        return next;
      },

      logout() {
        clearSession();
        setSessionState(null);
      },

      async setAvailability(available) {
        if (session?.role !== "volunteer") return;
        const updated = await apiSetAvailability(session.id, available);
        const next = toClientSession(
          { ...updated, role: "volunteer", id: updated.volunteer_id },
          { available: updated.available }
        );
        persist(next);
      },

      updateProfile(patch) {
        if (!session) return null;
        const clean = { ...patch };
        delete clean.password;
        delete clean.role;
        delete clean.id;
        const next = { ...session, ...clean };
        persist(next);
        return next;
      },
    };
  }, [session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
