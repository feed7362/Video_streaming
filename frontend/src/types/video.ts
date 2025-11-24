import type { VideoComment } from "./comment";
import type { SearchFilters } from "./search";
export interface VideoPreview {
    name?: string;
    thumbnail_url?: string;
    channel_name?: string;
    id: string;
    title: string;
    previewUrl: string;
    channel_avatar: string;
    createdAt: string;
    channel: string;
    views: number;
    likesCount: number;
    publishedAt: string;
    dislikesCount: number;
    privacy: VideoPrivacyStatus;
}

export interface Video {
    publishedAt: string;
    id: string;
    title: string;
    size: number;
    hash: string;
    name: string;
    avatar_url?: string;
    master_hls_url: string;
    thumbnail_url: string;
    created_at: string;
    channelId: string;
    views_count: number;
    likes_count: number;
    dislikes_count: number;
    privacy: VideoPrivacyStatus;
    category?: string;
    channel_avatar?: string;
    channel_name: string;
    master_url?: string;
    status: "Processing" | "Ready" | "Failed";
    comments?: VideoComment[];
    commentCount?: number;
    preview_url?: string;
    description?: string;
    timeAgo?: string;
}

export type VideoPrivacyStatus = "Private" | "Public" | string;

export type VideoDetail = VideoPreview & {
    timeAgo?: string;
    description: string;
    likesCount: number;
    dislikesCount: number;
    hlsUrl: string;
    userReaction: 'like' | 'dislike' | null;
    privacy: VideoPrivacyStatus;
};

export type VideoPreviewWithTime = VideoPreview & {
    timeAgo: string;
    thumbnail: string;
};

type SetVideoState = React.Dispatch<React.SetStateAction<VideoDetail | null>>;
export interface UseVideoResult {
    video: VideoDetail | null;
    videos: VideoPreviewWithTime[];
    comments: VideoComment[];
    error: string | null;
    loading: boolean;
    hasMore: boolean;
    page: number;
    setVideo: SetVideoState;
    loadMore: () => Promise<void>;
    loadMoreSearchResults: () => Promise<void>;
    formatViews: (views: number | undefined) => string;
    metaDataText: string;

    setVideos: React.Dispatch<React.SetStateAction<VideoPreviewWithTime[]>>;
    setPage: React.Dispatch<React.SetStateAction<number>>;
    setLoading: React.Dispatch<React.SetStateAction<boolean>>;
    setHasMore: React.Dispatch<React.SetStateAction<boolean>>;

    searchQuery: string;
    setSearchQuery: React.Dispatch<React.SetStateAction<string>>;
    setSearchFilters: React.Dispatch<React.SetStateAction<SearchFilters | undefined>>;
}

export interface VideoPrivacyStatusProps {
    privacy: VideoPrivacyStatus;
}

export interface ApiVideoItem extends VideoPreview {
    name?: string;
}