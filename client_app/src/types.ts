export type Page = "login" | "app";
export type Section = "home" | "skus" | "drop" | "wallet" | "config";
export type Plan = "starter" | "pro" | "elite";
export type Theme = "dark" | "light";

export interface UserSession {
  token: string;
  email: string;
  plan: Plan;
  max_accounts: number;
  expires: string;
}