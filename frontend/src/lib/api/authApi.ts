import clientApi from "./clientApi";
import type { ChangelogEntry, UserInfo } from "./types";

export const getChangelog = async (): Promise<ChangelogEntry[]> => {
  const res = await clientApi.get<ChangelogEntry[]>("/api/changelog");
  return res.data;
};

export const registerUser = (email: string, password: string): Promise<void> =>
  clientApi
    .post("/api/auth/register", {
      email,
      username: email.split("@")[0],
      password,
    })
    .then(() => {});

export const loginUser = (email: string, password: string): Promise<string> =>
  clientApi
    .post<{ token: string }>("/api/auth/login", { email, password })
    .then((res) => {
      localStorage.setItem("token", res.data.token);
      return res.data.token;
    });

export const logoutUser = async (): Promise<void> => {
  localStorage.removeItem("token");
  try {
    await clientApi.post("/api/auth/logout");
  } catch (err) {
    console.warn("Logout API error:", err);
  }
};

export const getCurrentUser = (): Promise<UserInfo> =>
  clientApi.get<UserInfo>("/api/auth/me").then((res) => res.data);

export const getOtherUserInfo = (username: string): Promise<UserInfo> =>
  clientApi
    .get<UserInfo>(`/api/auth/users/${username}`)
    .then((res) => res.data);

export const checkUserExists = async (
  username: string,
  email: string,
): Promise<{ usernameExists: boolean; emailExists: boolean }> => {
  return clientApi
    .post("/api/auth/check-user", { username, email })
    .then((res) => res.data);
};

export const sendPasswordReset = async (email: string): Promise<void> => {
  await clientApi.post("/api/auth/forgot-password", { email });
};

export const resetPassword = async (
  token: string,
  password: string,
): Promise<void> => {
  await clientApi.post("/api/auth/reset-password", { token, password });
};

export const getGithubAuthUrl = (): Promise<string> =>
  clientApi
    .get<{ authorization_url: string }>("/api/auth/github/authorize")
    .then((res) => res.data.authorization_url);

export default {
  registerUser,
  loginUser,
  logoutUser,
  getCurrentUser,
  getOtherUserInfo,
  checkUserExists,
  getChangelog,
  sendPasswordReset,
  resetPassword,
  getGithubAuthUrl,
};
