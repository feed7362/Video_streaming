export interface ChannelInfo {
    channelName: string;
    channelAvatar: string;
    channelBanner?: string;
    subscribersCount: number;
    videosCount: number;
    bio?: string;
    createdAt: string;
    isOwner?: boolean;
}

export interface VideoPreview {
    id: string;
    title: string;
    previewUrl?: string;
    createdAt: string;
    channel: string;
    views: number;
    channel_avatar?: string;
    privacy: "Public" | "Private";
    likesCount: number;
    dislikesCount: number;
}

export interface Video {
    id: string;
    title: string;
    size: number;
    hash: string;
    thumbnailUrl: string;
    createdAt: string;
    channelId: string;
    viewsCount: number;
    likesCount: number;
    dislikesCount: number;
    isPublic: boolean;
    category?: string;
    channelAvatar?: string;
    channelName: string;
    status: "Processing" | "Ready" | "Failed";
    comments?: VideoComment[];
    commentCount?: number;
    previewUrl?: string;
    description?: string;
}

export interface VideoComment {
    id: string;
    userId: string;
    content: string;
    createdAt: string;
    videoId: string;
    parentId?: string;
    likesCount: number;
    dislikesCount: number;
}

export interface Comment {
    id: string;
    userId: string;
    videoId: string;
    content: string;
    createdAt: string;
    updatedAt?: string;
    likesCount: number;
    dislikesCount: number;
}
export interface UserInfo {
    id: string;
    username: string;
    status: "active" | "banned" | "deleted";
    email?: string;
    createdAt: string;
    roleId: number;
    hashedPassword?: string;
}

export interface ChannelPreview {
channelName: string;
channelAvatar: string;
subscribersCount: number;
videosCount: number;
}
export interface CommentPage {
    items: Comment[];
    page: number;
    size: number;
    total: number;
}

export interface Playlist {
    id: string;
    title: string;
    description?: string;
    createdAt: string;
    updatedAt?: string;
    videoIds: string[];
    isPublic: boolean;
}

export interface PlaylistPreview {
    id: string;
    title: string;
    videoCount: number;
    createdAt: string;
    isPublic: boolean;
}

export interface Notification {
id: string;
userId: string;
type: "new_video" | "new_subscriber" | "comment_reply" | "like" | "dislike";
content: string;
isRead: boolean;
createdAt: string;
relatedEntityId?: string;
}
export interface ChangelogEntry {
    date: string;
    version: string;
    improvements?: string[];
    bugfixes?: string[];
    newFeatures?: string[];
    imageUrl?: string;
    tags?: string[];
}
export interface Category {
    id: string;
    name: string;
}