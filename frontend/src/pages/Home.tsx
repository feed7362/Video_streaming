import { useEffect, useState, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import categoriesApi from "@api/categoriesApi";
import videoApi from "@api/videoApi";
import { timeAgo } from "@/utils/timeAgo";
import type { VideoPreview, VideoPreviewWithTime } from "../types/video";
import type { Category } from "../types/category";

export default function Home() {
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
        <div className="my-4 mx-auto max-w-[1400px] px-4 sm:px-6">
            <div
                className="mb-6 flex overflow-x-auto overflow-y-hidden no-scrollbar cursor-grab active:cursor-grabbing select-none pb-2 sticky top-0 bg-white z-10 pt-2"
                onMouseDown={(e: React.MouseEvent<HTMLDivElement>) => {
                    const container = e.currentTarget;
                    const startX = e.pageX - container.offsetLeft;
                    const scrollLeft = container.scrollLeft;

                    const mouseMoveHandler = (eMove: MouseEvent) => {
                        eMove.preventDefault();
                        const x = eMove.pageX - container.offsetLeft;
                        const walk = (x - startX) * 1.5;
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
                        variant={activeCategory === cat.name ? "default" : "secondary"}
                        className={`mx-1.5 whitespace-nowrap rounded-lg px-4 transition-all ${activeCategory === cat.name
                                ? "bg-black text-white hover:bg-gray-800"
                                : "bg-gray-100 hover:bg-gray-200 text-black border-none"
                            }`}
                    >
                        {cat.name}
                    </Button>
                ))}
            </div>

            {videos.length === 0 && loading ? (
                <div className="grid gap-x-6 gap-y-10 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                    {Array.from({ length: size }).map((_, i) => (
                        <VideoCard key={i} loading />
                    ))}
                </div>
            ) : (
                <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                    <div className="grid gap-x-6 gap-y-10 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                        {videos.map((video) => (
                            <Link key={video.id} to={`/watch?v=${video.id}`} className="w-full">
                                <VideoCard
                                    id={video.id}
                                    title={video.title}
                                    thumbnail={video.previewUrl || video.thumbnail_url}
                                    channel_avatar={video.channel_avatar}
                                    channel_name={video.channel_name}
                                    views={video.views}
                                    timeAgo={video.timeAgo}
                                    privacy={video.privacy}
                                />
                            </Link>
                        ))}

                        {loading && videos.length > 0 && (
                            <div className="col-span-full w-full py-8 flex justify-center items-center">
                                <div className="text-gray-500 font-medium animate-pulse">
                                    Loading more videos...
                                </div>
                            </div>
                        )}
                    </div>
                </InfiniteScroll>
            )}

            {!loading && videos.length === 0 && (
                <div className="text-center py-20 text-gray-500 text-lg">
                    No videos found in this category.
                </div>
            )}
        </div>
    );
}