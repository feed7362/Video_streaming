import type { Comment, CommentPage } from './types';
import apiClient from "./clientApi";

export const getVideoComments = (videoId: string, page: number = 0, size: number = 20): Promise<CommentPage> =>
    apiClient.get<CommentPage>(`/videos/${videoId}/comments?page=${page}&size=${size}`).then(res => res.data);

export const postVideoComment = (videoId: string, content: string): Promise<Comment> =>
    apiClient.post<Comment>(`/videos/${videoId}/comments`, { content }).then(res => res.data);

export const updateVideoComment = (commentId: string, content: string): Promise<Comment> =>
    apiClient.put<Comment>(`/comments/${commentId}`, { content }).then(res => res.data);

export const deleteVideoComment = (commentId: string): Promise<void> =>
    apiClient.delete(`/comments/${commentId}`).then(() => { });

export default { getVideoComments, postVideoComment, updateVideoComment, deleteVideoComment };
