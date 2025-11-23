export interface Notification {
    id: string;
    userId: string;
    type: "new_video" | "new_subscriber" | "comment_reply" | "like" | "dislike";
    content: string;
    isRead: boolean;
    createdAt: string;
    relatedEntityId?: string;
}
