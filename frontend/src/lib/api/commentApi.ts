import type { Comment, CommentPage } from "./types";
import apiClient from "./clientApi";

export interface OwnerComment {
  id: string;
  user_id: string;
  user_name: string;
  user_avatar?: string | null;
  content: string;
  created_at: string;
  likes_count: number;
  dislikes_count: number;
  parent_id?: string | null;
  video_id: string;
  video_title: string;
}

export interface OwnerCommentPage {
  items: OwnerComment[];
  page: number;
  size: number;
  total: number;
}

export const getOwnerComments = async (
  page = 1,
  size = 20,
  videoId?: string,
): Promise<OwnerCommentPage> => {
  const res = await apiClient.get<OwnerCommentPage>(
    "/api/comments/owner/list",
    {
      params: { page, size, ...(videoId ? { video_id: videoId } : {}) },
    },
  );
  return res.data;
};

export const getComments = async (
  videoId: string,
  page: number = 1,
  size: number = 20,
): Promise<CommentPage> => {
  const res = await apiClient.get<CommentPage>(`/api/comments/${videoId}`, {
    params: { page, size },
  });
  return res.data;
};

export const addComment = async (
  videoId: string,
  content: string,
): Promise<Comment> => {
  const res = await apiClient.post<Comment>(`/api/comments/${videoId}`, {
    content,
  });
  return res.data;
};

/*
export const updateComment = async (
  commentId: string,
  content: string,
): Promise<Comment> => {
  const res = await apiClient.put<Comment>(`/api/comments/${commentId}`, { content });
  return res.data;
};
*/

export const deleteComment = async (commentId: string): Promise<void> => {
  await apiClient.delete(`/api/comments/${commentId}`);
};

export const addReply = async (
  videoId: string,
  commentId: string,
  content: string,
): Promise<Comment> => {
  const res = await apiClient.post<Comment>(`/api/comments/${videoId}`, {
    content,
    parent_id: commentId,
  });
  return res.data;
};

export const reactToComment = async (
  commentId: string,
  reactionName: "like" | "dislike",
): Promise<{ reactions: Record<string, number> }> => {
  const res = await apiClient.post(`/api/comments/${commentId}/reaction`, {
    reaction_name: reactionName,
  });
  return res.data;
};

export default {
  getComments,
  getOwnerComments,
  addComment,
  // updateComment,
  deleteComment,
  addReply,
  reactToComment,
};
