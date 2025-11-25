import { useEffect, useState, useCallback, useRef } from "react";
import categoriesApi from "@api/categoriesApi";
import videoApi from "@api/videoApi";
import { timeAgo } from "@/utils/timeAgo";
import type { VideoPreview, VideoPreviewWithTime } from "../../types/video";
import type { Category } from "../../types/category";

export function useHome() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [activeCategory, setActiveCategory] = useState<string>("All");

    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);
    const [videos, setVideos] = useState<VideoPreviewWithTime[]>([]);

    const isFetchingRef = useRef(false);
    const size = 12;

    useEffect(() => {
        categoriesApi
            .getCategories()
            .then((data) => {
                setCategories([{ id: "all", name: "All" }, ...data]);
            })
            .catch(console.error);
    }, []);

    const loadMore = useCallback(async () => {
        if (isFetchingRef.current || !hasMore) return;

        isFetchingRef.current = true;
        setLoading(true);

        try {
            const newVideosPreview = await videoApi.getVideos({
                page,
                size,
                category: activeCategory !== "All" ? activeCategory : undefined,
            });

            const newVideosWithTime: VideoPreviewWithTime[] = newVideosPreview.map((v: VideoPreview) => {
                const createdDate = v.createdAt || new Date().toISOString();
                // Визначаємо безпечний URL для тумбнейлу
                const safeThumbnailUrl = v.thumbnail_url || v.previewUrl || "";

                return {
                    ...v,
                    thumbnail: safeThumbnailUrl || "/placeholder.jpg",
                    // ВИПРАВЛЕНО: Явно задаємо thumbnail_url як рядок
                    thumbnail_url: safeThumbnailUrl,
                    title: v.title || v.name || "Untitled Video",
                    channel_name: v.channel || "Unknown Channel",
                    timeAgo: timeAgo(createdDate),
                    channel_avatar: v.channel_avatar || "",
                    previewUrl: v.previewUrl || v.thumbnail_url || "",
                    createdAt: createdDate,
                    views: v.views ?? 0,
                    likesCount: v.likesCount ?? 0,
                    dislikesCount: v.dislikesCount ?? 0,
                    privacy: v.privacy,
                    // Додаємо publishedAt, якщо його немає в ...v
                    publishedAt: v.publishedAt || createdDate
                };
            });

            if (newVideosWithTime.length < size) {
                setHasMore(false);
            }

            if (newVideosWithTime.length > 0) {
                setVideos((prev) => {
                    const existingIds = new Set(prev.map((v) => v.id));
                    const uniqueNewVideos = newVideosWithTime.filter((v) => !existingIds.has(v.id));
                    return [...prev, ...uniqueNewVideos];
                });
                setPage((prev) => prev + 1);
            } else {
                setHasMore(false);
            }

        } catch (err) {
            console.error("Failed to load videos:", err);
        } finally {
            setLoading(false);
            isFetchingRef.current = false;
        }
    }, [page, activeCategory, hasMore]);

    useEffect(() => {
        setVideos([]);
        setPage(1);
        setHasMore(true);
        isFetchingRef.current = false;
    }, [activeCategory]);

    useEffect(() => {
        if (videos.length === 0 && hasMore && !isFetchingRef.current) {
            loadMore();
        }
    }, [activeCategory, loadMore, videos.length, hasMore]);

    return {
        categories,
        activeCategory,
        setActiveCategory,
        videos,
        loadMore,
        loading,
        size,
        hasMore,
    };
}