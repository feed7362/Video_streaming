import type { VideoDetail, VideoPreviewWithTime, VideoPreview } from "./video";
import type { VideoComment } from "./comment";
export interface SearchFilters {
    category?: string;
    minViews?: number;
    maxViews?: number;
    includeDescription: boolean;
    smartSearch: boolean;
}

export interface UseSearchOptions {
    enabled?: boolean;
    initialPage?: number;
}

export interface SearchResponse {
    results: VideoPreview[];
}

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

export interface NoSearchResultsProps {
    query: string;
}
export interface SearchApiResponse {
    results: VideoPreview[];
}

export interface SearchFormProps {
    className?: string;
}