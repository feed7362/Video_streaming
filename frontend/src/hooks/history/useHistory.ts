import { useEffect, useState, useCallback } from "react";
import type { VideoPreview } from "../../types/video";
import { getUserHistory, clearUserHistory, removeVideoFromHistory } from "@api/historyApi";
export function useHistory() {
    const [videos, setVideos] = useState<VideoPreview[]>([]);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);
    const [page, setPage] = useState(1);
    const pageSize = 20;

    const loadMore = useCallback(async () => {
        if (!hasMore) return;
        setLoading(true);
        try {
            const response = await getUserHistory(page, pageSize);
            setVideos(prev => [...prev, ...response.items]);
            setHasMore(videos.length + response.items.length < response.total);
            setPage(prev => prev + 1);
        } catch (err: unknown) {
            console.error("Failed to load history:", err);
        } finally {
            setLoading(false);
        }
    }, [hasMore, page, pageSize, videos]);

    useEffect(() => {
        loadMore();
    }, [loadMore]);

    const handleRemoveVideo = async (videoId: string) => {
        try {
            await removeVideoFromHistory(videoId);
            setVideos(prev => prev.filter(v => v.id !== videoId));
        } catch (err) {
            console.error("Failed to remove video from history:", err);
        }
    };

    const handleClearHistory = async () => {
        try {
            await clearUserHistory();
            setVideos([]);
            setHasMore(false);
        } catch (err) {
            console.error("Failed to clear history:", err);
        }
    };

    return {
        videos,
        loading,
        hasMore,
        page,
        loadMore,
        handleRemoveVideo,
        handleClearHistory,
    };
}