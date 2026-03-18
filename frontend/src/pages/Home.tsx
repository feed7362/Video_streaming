import React, {useEffect, useState, useRef, useCallback} from "react";
import {Link} from "react-router-dom";
import {Button} from "@/components/ui/button";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import categoriesApi from "@api/categoriesApi";
import type {Category} from "@api/types";
import videoApi from "@api/videoApi";

interface Video {
    id: string;
    title: string;
    thumbnail: string;
    channel_avatar: string;
    channel_name: string;
}

const PAGE_SIZE = 9;

export default function Home() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [activeCategory, setActiveCategory] = useState<string>("All");

    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);

    const isFetchingRef = useRef(false);

    useEffect(() => {
        categoriesApi
            .getCategories()
            .then((data) => {
                setCategories([{id: "all", name: "All"}, ...data]);
            })
            .catch(console.error);
    }, []);

    const fetchVideos = useCallback(async (currentPage: number, category: string, isReset: boolean = false) => {
        if (isFetchingRef.current || (!hasMore && !isReset)) return;

        isFetchingRef.current = true;
        setLoading(true);

        try {
            let fetchedData;
            if (category && category !== "All") {
                fetchedData = await videoApi.getVideoPreviewsByCategory(category, currentPage, PAGE_SIZE);
            } else {
                fetchedData = await videoApi.getVideos({page: currentPage, size: PAGE_SIZE});
            }

            const mappedVideos: Video[] = fetchedData.map((v) => ({
                id: v.id,
                title: v.title || "Untitled Video",
                thumbnail: v.previewUrl || "/placeholder.jpg",
                channel_avatar: v.channel_avatar || "",
                channel_name: v.channel_name || v.channel || "Unknown Channel",
            }));

            if (mappedVideos.length < PAGE_SIZE) {
                setHasMore(false);
            } else {
                setHasMore(true);
            }

            setVideos((prev) => {
                const baseArray = isReset ? [] : prev;
                const existingIds = new Set(baseArray.map((v) => v.id));
                const uniqueNewVideos = mappedVideos.filter((v) => !existingIds.has(v.id));
                return [...baseArray, ...uniqueNewVideos];
            });

            setPage(currentPage + 1);
        } catch (err) {
            console.error("Failed to load videos:", err);
        } finally {
            setLoading(false);
            isFetchingRef.current = false;
        }
    }, [hasMore]);

    useEffect(() => {
        fetchVideos(1, activeCategory, true);
    }, [activeCategory, fetchVideos]);

    const loadMore = useCallback(() => {
        if (!loading && hasMore) {
            fetchVideos(page, activeCategory, false);
        }
    }, [fetchVideos, page, activeCategory, loading, hasMore]);

    const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
        const container = e.currentTarget;
        const startX = e.pageX - container.offsetLeft;
        const scrollLeft = container.scrollLeft;

        const handleMouseMove = (eMove: MouseEvent) => {
            const walk = (eMove.pageX - container.offsetLeft - startX) * 1.2;
            container.scrollLeft = scrollLeft - walk;
        };

        const handleMouseUp = () => {
            document.removeEventListener("mousemove", handleMouseMove);
            document.removeEventListener("mouseup", handleMouseUp);
        };

        document.addEventListener("mousemove", handleMouseMove);
        document.addEventListener("mouseup", handleMouseUp);
    };

    return (
        <div className="my-4 mx-auto max-w-[1400px] px-6">
            <div
                className="mb-6 flex overflow-x-auto overflow-y-hidden no-scrollbar cursor-grab active:cursor-grabbing select-none"
                onMouseDown={handleMouseDown}
            >
                {categories.map((cat) => (
                    <Button
                        key={cat.id}
                        onClick={() => setActiveCategory(cat.name)}
                        variant={activeCategory === cat.name ? "default" : "outline"}
                        className={`mx-2 whitespace-nowrap transition-all ${
                            activeCategory === cat.name ? "bg-black text-white" : ""
                        }`}
                    >
                        {cat.name}
                    </Button>
                ))}
            </div>

            <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {videos.length === 0 && loading ? (
                    Array.from({length: PAGE_SIZE}).map((_, i) => <VideoCard key={`skeleton-${i}`} loading/>)
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
