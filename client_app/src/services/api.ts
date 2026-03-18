import axios from "axios";
import type { UserSession, Plan } from "../types";

const API_BASE = "https://nike-bot-pro-production.up.railway.app";

const http = axios.create({
  baseURL: API_BASE,
  timeout: 8000,
  headers: { "Content-Type": "application/json" },
});

/* ─── Responses del backend ─── */

interface LoginResponse {
  token: string;
  expires: string;
  plan: Plan;
  max_accounts: number;
}

interface RegisterResponse {
  token: string;
  plan: Plan;
  expires_in: number;
  max_accounts: number;
}

interface ValidateResponse {
  valid: boolean;
  email: string;
  plan: Plan;
  max_accounts: number;
  expires: string;
}

/* ─── API pública ─── */

export async function apiLogin(
  email: string,
  password: string,
): Promise<UserSession> {
  const { data } = await http.post<LoginResponse>("/auth/login", {
    email,
    password,
  });
  return {
    token: data.token,
    email,
    plan: data.plan,
    max_accounts: data.max_accounts,
    expires: data.expires,
  };
}

export async function apiRegister(
  email: string,
  password: string,
): Promise<UserSession> {
  const { data } = await http.post<RegisterResponse>("/auth/register", {
    email,
    password,
  });
  const expires = new Date(
    Date.now() + data.expires_in * 1000,
  ).toISOString().slice(0, 10);
  return {
    token: data.token,
    email,
    plan: data.plan,
    max_accounts: data.max_accounts,
    expires,
  };
}

export async function apiValidateToken(
  token: string,
): Promise<UserSession> {
  const { data } = await http.get<ValidateResponse>("/auth/validate", {
    headers: {
      Authorization: `Bearer ${token}`,
      "X-HWID": "00000000-0000-0000-0000-000000000000",
    },
  });
  return {
    token,
    email: data.email,
    plan: data.plan,
    max_accounts: data.max_accounts,
    expires: data.expires,
  };
}

export async function apiRevoke(token: string): Promise<void> {
  await http.post("/auth/revoke", null, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

/* ─── Fallback offline: decodifica JWT sin verificar firma ─── */

export function validateTokenOffline(token: string): UserSession | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const payload = JSON.parse(atob(parts[1]));
    if (payload.exp && payload.exp * 1000 < Date.now()) return null;
    return {
      token,
      email: payload.email ?? payload.sub ?? "",
      plan: payload.plan ?? "starter",
      max_accounts: payload.max_accounts ?? 3,
      expires: payload.exp
        ? new Date(payload.exp * 1000).toISOString().slice(0, 10)
        : "—",
    };
  } catch {
    return null;
  }
}

/* ─── Persistencia local (Tauri Store) ─── */

import { load } from "@tauri-apps/plugin-store";

const STORE_PATH = "session.json";
const SESSION_KEY = "aoda_session";
const VERIFIED_KEY = "aoda_verified";

let _store: Awaited<ReturnType<typeof load>> | null = null;

async function getStore() {
  if (!_store) {
    _store = await load(STORE_PATH, { autoSave: true, defaults: {} });
  }
  return _store;
}

export async function saveSession(session: UserSession, verified = false) {
  const store = await getStore();
  await store.set(SESSION_KEY, session);
  if (verified) await store.set(VERIFIED_KEY, true);
}

export async function loadSession(): Promise<UserSession | null> {
  try {
    const store = await getStore();
    const val = await store.get<UserSession>(SESSION_KEY);
    return val ?? null;
  } catch {
    return null;
  }
}

export async function isSessionVerified(): Promise<boolean> {
  try {
    const store = await getStore();
    const val = await store.get<boolean>(VERIFIED_KEY);
    return val === true;
  } catch {
    return false;
  }
}

export async function clearSession() {
  try {
    const store = await getStore();
    await store.delete(SESSION_KEY);
    await store.delete(VERIFIED_KEY);
  } catch {
    // ignore
  }
}
