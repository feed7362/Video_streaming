import { useCallback, useEffect, useState } from "react";
import type { Video } from "@/types/video";

export function useWatchLater() {
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);
    const [page, setPage] = useState(1);
    const pageSize = 20;

    const loadMore = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetch(`/api/watch-later?page=${page}&pageSize=${pageSize}`);
            if (!res.ok) throw new Error("Failed to fetch videos");
            const data: Video[] = await res.json();

            setVideos(prev => [...prev, ...data]);
            setHasMore(data.length === pageSize);
            setPage(prev => prev + 1);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [page]); 

    useEffect(() => {
        loadMore();
    }, [loadMore]);

    return {
        videos,
        loading,
        hasMore,
        loadMore,
    };
}