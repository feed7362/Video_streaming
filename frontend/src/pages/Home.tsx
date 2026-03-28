import React, { useEffect, useState, useRef, useCallback } from "react";
import { Link } from "react-router-dom";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import categoriesApi from "@api/categoriesApi";
import type { Category } from "@api/types";
import videoApi from "@api/videoApi";
import { timeAgo } from "@/utils/timeAgo";

interface Video {
    id: string;
    title: string;
    thumbnail: string;
    channel_avatar: string;
    channel_name: string;
    views?: number;
    timeAgo?: string;
}

const PAGE_SIZE = 12;

export default function Home() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [activeCategory, setActiveCategory] = useState<string>("All");
    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const isFetchingRef = useRef(false);
    const pillsRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        categoriesApi
            .getCategories()
            .then((data) => setCategories([{ id: "all", name: "All" }, ...data]))
            .catch(console.error);
    }, []);

    const fetchVideos = useCallback(async (currentPage: number, category: string, isReset = false) => {
        if (isFetchingRef.current || (!hasMore && !isReset)) return;
        isFetchingRef.current = true;
        setLoading(true);
        try {
            const fetchedData = category && category !== "All"
                ? await videoApi.getVideoPreviewsByCategory(category, currentPage, PAGE_SIZE)
                : await videoApi.getVideos({ page: currentPage, size: PAGE_SIZE });

            const mapped: Video[] = fetchedData.map((v) => ({
                id: v.id,
                title: v.title || "Untitled",
                thumbnail: v.previewUrl || "/placeholder.jpg",
                channel_avatar: v.channel_avatar || "",
                channel_name: v.channel_name || v.channel || "Unknown",
                views: v.views,
                timeAgo: v.createdAt ? timeAgo(v.createdAt) : undefined,
            }));

            setHasMore(mapped.length >= PAGE_SIZE);
            setVideos((prev) => {
                const base = isReset ? [] : prev;
                const ids = new Set(base.map((v) => v.id));
                return [...base, ...mapped.filter((v) => !ids.has(v.id))];
            });
            setPage(currentPage + 1);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
            isFetchingRef.current = false;
        }
    }, [hasMore]);

    useEffect(() => {
        fetchVideos(1, activeCategory, true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeCategory]);

    const loadMore = useCallback(() => {
        if (!loading && hasMore) fetchVideos(page, activeCategory);
    }, [fetchVideos, page, activeCategory, loading, hasMore]);

    /* drag-scroll pills */
    const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
        const el = e.currentTarget;
        const startX = e.pageX - el.offsetLeft;
        const scrollLeft = el.scrollLeft;
        const onMove = (ev: MouseEvent) => { el.scrollLeft = scrollLeft - (ev.pageX - el.offsetLeft - startX) * 1.2; };
        const onUp = () => { document.removeEventListener("mousemove", onMove); document.removeEventListener("mouseup", onUp); };
        document.addEventListener("mousemove", onMove);
        document.addEventListener("mouseup", onUp);
    };

    return (
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6">
            {/* Category pills — NOT sticky, scrolls with page */}
            <div
                ref={pillsRef}
                className="flex gap-3 overflow-x-auto no-scrollbar py-3 cursor-grab active:cursor-grabbing select-none"
                onMouseDown={handleMouseDown}
            >
                {categories.map((cat) => (
                    <button
                        key={cat.id}
                        onClick={() => setActiveCategory(cat.name)}
                        className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition-colors shrink-0
                            ${activeCategory === cat.name
                                ? "bg-foreground text-background"
                                : "bg-muted hover:bg-muted/80 text-foreground"
                            }`}
                    >
                        {cat.name}
                    </button>
                ))}
            </div>

            {/* Video grid */}
            <div className="grid gap-x-4 gap-y-8 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 pb-10">
                {videos.length === 0 && loading ? (
                    Array.from({ length: PAGE_SIZE }).map((_, i) => <VideoCard key={i} loading />)
                ) : (
                    <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                        {videos.map((video) => (
                            <Link key={video.id} to={`/watch?v=${video.id}`}>
                                <VideoCard
                                    id={video.id}
                                    title={video.title}
                                    thumbnail={video.thumbnail}
                                    channel_avatar={video.channel_avatar}
                                    channel_name={video.channel_name}
                                    views={video.views}
                                    timeAgo={video.timeAgo}
                                />
                            </Link>
                        ))}
                        {loading && videos.length > 0 && (
                            <>
                                {Array.from({ length: 4 }).map((_, i) => <VideoCard key={`sk-${i}`} loading />)}
                            </>
                        )}
                    </InfiniteScroll>
                )}
            </div>
        </div>
    );
}
