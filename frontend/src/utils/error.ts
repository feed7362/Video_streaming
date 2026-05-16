import { AxiosError } from "axios";
import type { ApiErrorEnvelope, ApiErrorFieldIssue } from "@/lib/api/types";

export interface ParsedApiError {
  status: number | null;
  title: string;
  description?: string;
  fieldIssues: string[];
}

function formatIssue(issue: ApiErrorFieldIssue): string {
  const msg = issue.message ?? issue.msg ?? "Invalid value";
  const path =
    issue.field ??
    (Array.isArray(issue.loc)
      ? issue.loc.filter((p) => p !== "body").join(".")
      : "");
  return path ? `${path}: ${msg}` : msg;
}

export function parseApiError(err: unknown): ParsedApiError {
  if (err instanceof AxiosError) {
    const status = err.response?.status ?? null;
    const data = err.response?.data as ApiErrorEnvelope | string | undefined;

    if (typeof data === "string" && data.trim()) {
      return { status, title: data, fieldIssues: [] };
    }

    if (data && typeof data === "object") {
      const title =
        data.message ??
        (typeof data.detail === "string" ? data.detail : undefined) ??
        err.message ??
        "Request failed";

      let fieldIssues: string[] = [];
      const raw =
        data.errors ?? (Array.isArray(data.detail) ? data.detail : undefined);

      if (Array.isArray(raw)) {
        fieldIssues = raw.map(formatIssue);
      } else if (raw && typeof raw === "object") {
        fieldIssues = Object.entries(raw).map(([k, v]) => `${k}: ${String(v)}`);
      } else if (typeof raw === "string" && raw.trim()) {
        fieldIssues = [raw];
      }

      return {
        status,
        title,
        description: fieldIssues.length ? fieldIssues.join("\n") : undefined,
        fieldIssues,
      };
    }

    return { status, title: err.message || "Network error", fieldIssues: [] };
  }

  if (err instanceof Error)
    return { status: null, title: err.message, fieldIssues: [] };
  return { status: null, title: "Something went wrong", fieldIssues: [] };
}

export function getErrorMessage(err: unknown): string {
  const p = parseApiError(err);
  return p.description ? `${p.title} — ${p.description}` : p.title;
}
