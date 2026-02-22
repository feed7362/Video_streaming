import type { Comment, CommentPage } from "./types";
import apiClient from "./clientApi";

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
  const res = await apiClient.post<Comment>(
    `/api/comments/${videoId}`,
    { content },
    { params: { parent_id: commentId } },
  );
  return res.data;
};

export default {
  getComments,
  addComment,
  // updateComment,
  deleteComment,
  addReply,
};
