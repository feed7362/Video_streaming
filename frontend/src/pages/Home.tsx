/* eslint-disable react-hooks/exhaustive-deps */
import { useCallback, useState } from "react";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import api from "@api/videoApi";

interface Video {
    id: string;
    title: string;
    thumbnail: string;
    channel_avatar: string;
    channel_name: string;
}

const categories = [
    "All",
    "Blogs",
    "Comedy",
    "Education",
    "Fashion",
    "Films",
    "Fitness",
    "Food",
    "Gaming",
    "Literature",
    "Movies",
    "Music",
    "Nature",
    "New for you",
    "News",
    "Online strim",
    "Podcasts",
    "Science",
    "Sports",
    "Technology",
    "Watched",
];

export default function Home() {
    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);
    const [active, setActive] = useState("All");

    const loadMore = useCallback(async () => {
        setLoading(true);
        try {
            const newVideosPreview = await api.getVideos(page);

            const newVideos: Video[] = newVideosPreview.map(v => ({
                id: v.id,
                title: v.title,
                thumbnail: v.previewUrl || "",
                channel_avatar: v.channel_avatar || "",
                channel_name: v.channel,
            }));

            setVideos(prev => [...prev, ...newVideos]);
            setHasMore(newVideos.length > 0);
            setPage(prev => prev + 1);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [page]);

    if (loading && videos.length === 0) {
        loadMore();
    }

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
                {categories.map((category) => (
                    <Button
                        key={category}
                        onClick={() => setActive(category)}
                        variant={active === category ? "default" : "outline"}
                        className={`mx-2 whitespace-nowrap transition-all ${active === category ? "bg-black text-white" : ""
                            }`}
                    >
                        {category}
                    </Button>
                ))}
            </div>
            <div>
                <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5"
                    style={{ gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))" }}
                >
                    {loading
                        ? Array.from({ length: 12 }).map((_, i) => <VideoCard key={i} loading />)
                        : (
                            <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                                {videos.map((video) => (
                                    <Link
                                        key={video.id}
                                        to={`/watch?v=${video.id}`}
                                        className="w-full"
                                    >
                                        <VideoCard
                                            key={video.id}
                                            id={video.id}
                                            title={video.title}
                                            thumbnail={video.thumbnail}
                                            channel_avatar={video.channel_avatar}
                                            channel_name={video.channel_name}
                                        />
                                    </Link>
                                ))}
                            </InfiniteScroll>
                        )}
                </div>
            </div>
        </div>
    );
}
