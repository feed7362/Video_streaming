import { useEffect, useState } from "react";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import { Link } from "react-router-dom";
import type { VideoPreview } from "../types/video";
import { getUserHistory, clearUserHistory, removeVideoFromHistory } from "@api/historyApi";
import { Button } from "@/components/ui/button";

export default function History() {
    const [videos, setVideos] = useState<VideoPreview[]>([]);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);
    const [page, setPage] = useState(1);
    const pageSize = 20;

    const loadMore = async () => {
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
    };

    useEffect(() => {
        loadMore();
    }, []);

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

    return (
        <div className="my-4 mx-auto max-w-[1400px] px-6">
            <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold">History</h1>
                {videos.length > 0 && (
                    <Button variant="destructive" onClick={handleClearHistory}>
                        Clear History
                    </Button>
                )}
            </div>

            <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5"
                style={{ gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))" }}>
                {loading && videos.length === 0
                    ? Array.from({ length: 12 }).map((_, i) => <VideoCard key={i} loading />)
                    : (
                        <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                            {videos.map(video => (
                                <div key={video.id} className="relative w-full">
                                    <Link to={`/watch?v=${video.id}`} className="w-full block">
                                        <VideoCard
                                            id={video.id}
                                            title={video.title}
                                            thumbnail={video.previewUrl || ""}
                                            channel_avatar={video.channel_avatar || ""}
                                            channel_name={video.channel}
                                        />
                                    </Link>
                                    <Button
                                        size="sm"
                                        variant="destructive"
                                        className="absolute top-2 right-2"
                                        onClick={() => handleRemoveVideo(video.id)}
                                    >
                                        Remove
                                    </Button>
                                </div>
                            ))}
                        </InfiniteScroll>
                    )}
            </div>
        </div>
    );
}
