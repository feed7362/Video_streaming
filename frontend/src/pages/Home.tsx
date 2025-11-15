/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import categoriesApi from "@api/categoriesApi";
import type { Category, VideoPreview } from "@api/types";
import videoApi from "@api/videoApi";

interface Video {
    id: string;
    title: string;
    thumbnail: string;
    channel_avatar: string;
    channel_name: string;
}

export default function Home() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [activeCategory, setActiveCategory] = useState<string>("All");

    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);

    const isFetchingRef = useRef(false);
    const size = 9;

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
            console.log(`Fetching page ${page}...`);

            const newVideosPreview = await videoApi.getVideos({
                page,
                size,
                category: activeCategory !== "All" ? activeCategory : undefined,
            });

            const newVideos: Video[] = newVideosPreview.map((v: VideoPreview) => {
                const item = v as VideoPreview & { name?: string; thumbnail?: string; avatar_url?: string };

                return {
                    id: item.id,
                    title: item.title || item.name || "Untitled Video",
                    thumbnail: item.previewUrl || item.thumbnail_url || item.thumbnail || "/placeholder.jpg",
                    channel_avatar: item.channel_avatar || item.avatar_url || "",
                    channel_name: item.channel || "Unknown Channel",
                };
            });

            if (newVideos.length < size) {
                setHasMore(false);
            }

            if (newVideos.length > 0) {
                setVideos((prev) => {
                    const existingIds = new Set(prev.map((v) => v.id));
                    const uniqueNewVideos = newVideos.filter((v) => !existingIds.has(v.id));
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

    return (
        <div className="my-4 mx-auto max-w-[1400px] px-6">
            <div
                className="mb-6 flex overflow-x-auto overflow-y-hidden no-scrollbar cursor-grab active:cursor-grabbing select-none"
                onMouseDown={(e: React.MouseEvent<HTMLDivElement>) => {
                    const container = e.currentTarget;
                    const startX = e.pageX - container.offsetLeft;
                    const scrollLeft = container.scrollLeft;

                    const mouseMoveHandler = (eMove: MouseEvent) => {
                        const x = eMove.pageX - container.offsetLeft;
                        const walk = (x - startX) * 1.2;
                        container.scrollLeft = scrollLeft - walk;
                    };
                    const mouseUpHandler = () => {
                        document.removeEventListener("mousemove", mouseMoveHandler);
                        document.removeEventListener("mouseup", mouseUpHandler);
                    };

                    document.addEventListener("mousemove", mouseMoveHandler);
                    document.addEventListener("mouseup", mouseUpHandler);
                }}
            >
                {categories.map((cat) => (
                    <Button
                        key={cat.id}
                        onClick={() => setActiveCategory(cat.name)}
                        variant={activeCategory === cat.name ? "default" : "outline"}
                        className={`mx-2 whitespace-nowrap transition-all ${activeCategory === cat.name ? "bg-black text-white" : ""}`}
                    >
                        {cat.name}
                    </Button>
                ))}
            </div>

            <div
                className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5"
                style={{ gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))" }}
            >
                {videos.length === 0 && loading ? (
                    Array.from({ length: size }).map((_, i) => <VideoCard key={i} loading />)
                ) : (
                    <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                        {videos.map((video) => (
                            <Link key={video.id} to={`/watch?v=${video.id}`} className="w-full">
                                <VideoCard
                                    id={video.id}
                                    title={video.title}
                                    thumbnail={video.thumbnail}
                                    channel_avatar={video.channel_avatar}
                                    channel_name={video.channel_name}
                                />
                            </Link>
                        ))}

                        {loading && videos.length > 0 && (
                            <div className="text-center py-4 text-gray-500 col-span-full w-full">
                                Loading more videos...
                            </div>
                        )}
                    </InfiniteScroll>
                )}
            </div>
        </div>
    );
}