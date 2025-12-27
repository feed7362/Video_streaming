import clientApi from "./clientApi";
import type { ChangelogEntry, UserInfo } from "./types";

export const getChangelog = async (): Promise<ChangelogEntry[]> => {
  const res = await clientApi.get<ChangelogEntry[]>("/api/changelog");
  return res.data;
};

export const registerUser = (
  username: string,
  password: string,
): Promise<string> =>
  clientApi
    .post<{ token: string }>("/auth/register", { username, password })
    .then((res) => {
      localStorage.setItem("token", res.data.token);
      return res.data.token;
    });

export const loginUser = (
  username: string,
  password: string,
): Promise<string> =>
  clientApi
    .post<{ token: string }>("/auth/login", { username, password })
    .then((res) => {
      localStorage.setItem("token", res.data.token);
      return res.data.token;
    });

export const logoutUser = async (): Promise<void> => {
  localStorage.removeItem("token");
  try {
    await clientApi.post("/auth/logout");
  } catch (err) {
    console.warn("Logout API error:", err);
  }
};

export const refreshToken = (): Promise<string> =>
  clientApi.post<{ token: string }>("/auth/refresh-token").then((res) => {
    localStorage.setItem("token", res.data.token);
    return res.data.token;
  });

export const getCurrentUser = (): Promise<UserInfo> =>
  clientApi.get<UserInfo>("/auth/me").then((res) => res.data);

export const refreshCurrentUser = (): Promise<UserInfo> =>
  clientApi.post<UserInfo>("/auth/me/refresh").then((res) => res.data);

export const refreshUsersAvatar = (username: string): Promise<string> =>
  clientApi
    .post<{ avatarUrl: string }>(`/auth/users/${username}/refresh-avatar`)
    .then((res) => res.data.avatarUrl);

export const getOtherUserInfo = (username: string): Promise<UserInfo> =>
  clientApi.get<UserInfo>(`/auth/users/${username}`).then((res) => res.data);

export const getUserAvatar = (username: string): Promise<string | undefined> =>
  refreshUsersAvatar(username);

export const checkUserExists = async (
  username: string,
  email: string,
): Promise<{ usernameExists: boolean; emailExists: boolean }> => {
  return clientApi
    .post("/auth/check-user", { username, email })
    .then((res) => res.data);
};

export const sendPasswordReset = async (email: string): Promise<void> => {
  await clientApi.post("/auth/forgot-password", { email });
};

export default {
  registerUser,
  loginUser,
  logoutUser,
  refreshToken,
  getCurrentUser,
  refreshCurrentUser,
  refreshUsersAvatar,
  getOtherUserInfo,
  getUserAvatar,
  checkUserExists,
  getChangelog,
  sendPasswordReset,
};
