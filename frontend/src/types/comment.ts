export interface VideoComment {
    id: string;
    userId: string;
    content: string;
    createdAt: string;
    videoId: string;
    parentId?: string;
    likesCount: number;
    dislikesCount: number;
    page?: number;
    size?: number;
}

export interface CommentPage {
    items: VideoComment[];
    page: number;
    size: number;
    total: number;
}
