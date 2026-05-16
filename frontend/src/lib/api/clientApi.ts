import axios, {
  type AxiosInstance,
  AxiosError,
  type InternalAxiosRequestConfig,
} from "axios";
import { toast } from "sonner";
import { parseApiError } from "@/utils/error";

declare module "axios" {
  export interface AxiosRequestConfig {
    // Opt-out: skip the global error toast for this request (e.g. background auth checks).
    silent?: boolean;
  }
}

// Empty string = same-origin → works behind the nginx gateway in any env.
// Override only when the API lives on a different origin (e.g. local dev with
// `vite` on :5173 talking directly to bff on :8000). Set in frontend/.env*.
const baseURL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";

const apiClient: AxiosInstance = axios.create({
  baseURL,
  withCredentials: true,
});

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error),
);

apiClient.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    const parsed = parseApiError(error);
    const method = (error.config?.method ?? "").toUpperCase();
    const url = error.config?.url ?? "(unknown)";
    const rid = error.response?.headers?.["x-request-id"];

    // Expanded group so the actual server payload is visible without clicking around.
    console.groupCollapsed(
      `%cAPI ${parsed.status ?? "ERR"} ${method} ${url}`,
      "color:#f43f5e;font-weight:bold",
    );
    console.log("title:      ", parsed.title);
    if (parsed.description) console.log("description:", parsed.description);
    if (parsed.fieldIssues.length)
      console.log("fields:     ", parsed.fieldIssues);
    if (rid) console.log("request-id: ", rid);
    console.log("response:   ", error.response?.data);
    console.log("request:    ", {
      url,
      method,
      params: error.config?.params,
      data: error.config?.data,
    });
    console.groupEnd();

    const silent = error.config?.silent === true;
    const isCanceled = axios.isCancel(error);

    // ── 401 handling: clear token + bounce to /login ───────────────────────
    // No refresh-token flow exists on the backend yet, so we drop session and
    // let the user re-authenticate. We avoid this on the login/register pages
    // themselves (the 401 there is the user's wrong password) and on silent
    // background checks (e.g. /api/auth/me on page load).
    if (parsed.status === 401 && !silent && !isCanceled) {
      const path = window.location.pathname;
      const onAuthPage =
        /^\/(login|register|forgotpass|reset-password|auth\/)/i.test(path);
      if (!onAuthPage) {
        localStorage.removeItem("token");
        toast.error("Session expired", {
          description: "Please sign in again.",
          duration: 4000,
        });
        const next = encodeURIComponent(path + window.location.search);
        window.location.assign(`/login?next=${next}`);
        return Promise.reject(error);
      }
    }

    if (!silent && !isCanceled) {
      const code = parsed.status ? `${parsed.status} · ` : "";
      toast.error(`${code}${parsed.title}`, {
        description: parsed.description,
        duration: parsed.fieldIssues.length > 1 ? 8000 : 5000,
      });
    }

    return Promise.reject(error);
  },
);

export default apiClient;
