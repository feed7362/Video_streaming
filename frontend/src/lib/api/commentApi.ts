import type { VideoComment, CommentPage } from "../../types/comment";
import clientApi from "./clientApi"; // Тут ви імпортували як clientApi

// 1. Виправлено параметри функції та лапки URL
export const getComments = async ({
    videoId,       // Прибираємо "= string" (це не валідно в JS)
    page = 1,      // Прибираємо "= number"
    size = 10,
}: {
    page?: number;
    size?: number;
    videoId: string;
}): Promise<VideoComment[]> => {
    console.log("Fetching comments with params:", {
        page,
        size,
        videoId,
    });

    const res = await clientApi.get<CommentPage>(`/api/video/get_comments/${videoId}`, {
        params: { page, size },
    });

    console.log("getComments API response:", res.data);

    return (res.data.items || []);
};

// 2. Виправлено назви змінних та типів для інших функцій

// Замінив Comment на VideoComment (щоб типи збігалися)
// Замінив apiClient на clientApi (щоб відповідало імпорту зверху)

export const addComment = (videoId: string, content: string): Promise<VideoComment> =>
    clientApi.post<VideoComment>(`/videos/${videoId}/comments`, { content }).then(res => res.data);

export const updateComment = (commentId: string, content: string): Promise<VideoComment> =>
    clientApi.put<VideoComment>(`/comments/${commentId}`, { content }).then(res => res.data);

export const deleteComment = (commentId: string): Promise<void> =>
    clientApi.delete(`/comments/${commentId}`).then(() => { });

export const addReply = (commentId: string, content: string): Promise<VideoComment> =>
    clientApi.post<VideoComment>(`/comments/${commentId}/replies`, { content }).then(res => res.data);

export default { getComments, addComment, updateComment, deleteComment, addReply };