import type { Comment, CommentPage } from './types';
import apiClient from "./clientApi";

export const getComments = (videoId: string, page: number = 0, size: number = 20): Promise<CommentPage> =>
    apiClient.get<CommentPage>(`/videos/${videoId}/comments?page=${page}&size=${size}`).then(res => res.data);

export const addComment = (videoId: string, content: string): Promise<Comment> =>
    apiClient.post<Comment>(`/videos/${videoId}/comments`, { content }).then(res => res.data);

export const updateComment = (commentId: string, content: string): Promise<Comment> =>
    apiClient.put<Comment>(`/comments/${commentId}`, { content }).then(res => res.data);

export const deleteComment = (commentId: string): Promise<void> =>
    apiClient.delete(`/comments/${commentId}`).then(() => { });

//code addReply const
export const addReply = (commentId: string, content: string): Promise<Comment> =>
    apiClient.post<Comment>(`/comments/${commentId}/replies`, { content }).then(res => res.data);


export default { getComments, addComment, updateComment, deleteComment, addReply };
