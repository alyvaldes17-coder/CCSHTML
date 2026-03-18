import { UserSession } from "./types";

export const AUTH_MOCK: Record<string, UserSession> = {
  "NK-TEST-2026":  { token: "NK-TEST-2026",  email: "test@aoda.cl",    plan: "elite",   max_accounts: 10, expires: "2026-04-17" },
  "NK-PRO-2026":   { token: "NK-PRO-2026",   email: "pro@aoda.cl",     plan: "pro",     max_accounts: 6,  expires: "2026-04-17" },
  "NK-START-2026": { token: "NK-START-2026",  email: "starter@aoda.cl", plan: "starter", max_accounts: 3,  expires: "2026-04-17" },
};
