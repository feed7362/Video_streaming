import { useEffect, useState, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import categoriesApi from "@api/categoriesApi";
import type { Category, VideoPreview, VideoPreviewWithTime } from "@api/types";
import videoApi from "@api/videoApi";
import { timeAgo } from "@/utils/timeAgo";

export default function Home() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [activeCategory, setActiveCategory] = useState<string>("All");

    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);
    const [videos, setVideos] = useState<VideoPreviewWithTime[]>([]);

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
            const newVideosPreview = await videoApi.getVideos({
                page,
                size,
                category: activeCategory !== "All" ? activeCategory : undefined,
            });

            const newVideosWithTime: VideoPreviewWithTime[] = newVideosPreview.map((v: VideoPreview) => {
                const createdDate = v.createdAt || new Date().toISOString();

                return {
                    ...v,
                    thumbnail: v.previewUrl || v.thumbnail_url || "/placeholder.jpg",
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
                                    privacy={video.privacy}
                                    views={video.views}
                                    timeAgo={video.timeAgo}
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