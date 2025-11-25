import { useState, useCallback, useEffect, useMemo } from "react";
import { getVideos, getVideo } from "@api/videoApi";
import { timeAgo } from "@/utils/timeAgo";
import type { VideoDetail, VideoPreviewWithTime } from "../../types/video";
import type { VideoComment } from "../../types/comment";
import { useSearchParams } from "react-router-dom";
import { formatViews } from "@/utils/formatters";

export function useVideo() {
    const [searchParams] = useSearchParams();
    const videoId = searchParams.get("v");

    const [video, setVideo] = useState<VideoDetail | null>(null);
    const [videos, setVideos] = useState<VideoPreviewWithTime[]>([]);
    const [comments, setComments] = useState<VideoComment[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    const [searchQuery, setSearchQuery] = useState("");

    const metaDataText = useMemo(() => {
        if (!video) return '';
        const viewCountText = formatViews(video.views);
        return `${viewCountText} views ${video.timeAgo ? '' + video.timeAgo : ''}`;
    }, [video]);

    const fetchVideo = useCallback(async () => {
        if (!videoId) return;
        try {
            const data = await getVideo(videoId);
            const createdDate = data.created_at || new Date().toISOString();
            setError(null);

            const apiPrivacy = data.privacy?.toLowerCase();
            const mappedPrivacy =
                apiPrivacy === "private" ? "Private" :
                    "Public";

            setVideo({
                id: data.id || "",
                title: data.title || "",
                previewUrl: data.thumbnail_url || data.preview_url || "",
                createdAt: createdDate,
                channel_avatar: data.channel_avatar || "",
                channel: data.channel_name || "Unknown Channel",
                views: data.views_count ?? 0,
                hlsUrl: data.master_hls_url || "",
                privacy: mappedPrivacy,
                likesCount: data.likes_count ?? 0,
                dislikesCount: data.dislikes_count ?? 0,
                description: data.description || "No description provided for this video.",
                timeAgo: timeAgo(createdDate),
            } as VideoDetail);
            setComments(data.comments ?? []);
        } catch (err) {
            console.error(err);
            setError("Video not found");
        } finally {
            setLoading(false);
        }
    }, [videoId]);

    const loadMore = useCallback(async () => {
        if (!hasMore || loading) return;

        try {
            const nextPage = page + 1;
            const newVideos = await getVideos({ page: nextPage });

            const videosWithTime: VideoPreviewWithTime[] = newVideos.map(v => ({
                ...v,
                timeAgo: timeAgo(v.createdAt || new Date().toISOString()),
                thumbnail: v.thumbnail_url || v.previewUrl || "",
                thumbnail_url: v.thumbnail_url || v.previewUrl || "",
                description: v.description || "",
                publishedAt: v.publishedAt || v.createdAt || new Date().toISOString(),
                channel_name: v.channel_name || v.channel || "Unknown Channel",
            }));

            setVideos((prev) => [...prev, ...videosWithTime]);
            setPage(nextPage);
            setHasMore(newVideos.length > 0);
        } catch (err) {
            console.error(err);
        }
    }, [page, hasMore, loading]);

    const fetchInitialVideos = useCallback(async () => {
        try {
            setLoading(true);
            const firstVideos = await getVideos({ page: 1 });

            const initialVideosWithTime: VideoPreviewWithTime[] = firstVideos.map(v => ({
                ...v,
                timeAgo: timeAgo(v.createdAt || new Date().toISOString()),
                thumbnail: v.thumbnail_url || v.previewUrl || "",
                thumbnail_url: v.thumbnail_url || v.previewUrl || "",
                description: v.description || "",
                publishedAt: v.publishedAt || v.createdAt || new Date().toISOString(),
                channel_name: v.channel_name || v.channel || "Unknown Channel",
            }));

            setVideos(initialVideosWithTime);
            setPage(1);
            setHasMore(firstVideos.length > 0);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchVideo();
        window.scrollTo({ top: 0, behavior: "smooth" });
    }, [fetchVideo]);

    useEffect(() => {
        fetchInitialVideos();
    }, [fetchInitialVideos]);

    return {
        video,
        videos,
        comments,
        error,
        loading,
        hasMore,
        loadMore,
        formatViews,
        metaDataText,
        setVideos,
        setSearchQuery,
        searchQuery,
        setPage,
        setLoading,
        setHasMore,
        page,
        setVideo,
    };
}