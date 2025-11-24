import { useMemo, useState } from "react";
import VideoCard from "@/components/cards/VideoCard";
import InfiniteScroll from "@/components/misc/infinite-scroll";
import { Link } from "react-router-dom";

interface Video {
    id: string;
    title: string;
    thumbnail: string;
    channel_avatar: string;
    channel_name: string;
}

export default function Liked() {
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);

    const allVideos: Video[] = useMemo(
        () =>
            Array.from({ length: 120 }).map((_, i) => ({
                id: `video-${i + 1}`,
                title: `Mock Video ${i + 1}`,
                thumbnail: `https://via.placeholder.com/250x125?text=Video+${i + 1}`,
                channel_avatar: "https://api.dicebear.com/7.x/identicon/svg?seed",
                channel_name: `Channel ${i + 1}`,
            })),
        []
    );

    const loadMore = () => {
        const pageSize = 20;
        setVideos(prevVideos => {
            const nextVideos = allVideos.slice(0, prevVideos.length + pageSize);
            setHasMore(nextVideos.length < allVideos.length);
            setLoading(false);
            return nextVideos;
        });
    };

    if (loading && videos.length === 0) {
        loadMore();
    }

    return (
        <div className="my-4 mx-auto max-w-[1400px] px-6">
            <h1 className="text-2xl font-bold mb-4">Liked videos</h1>
            <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5"
                style={{ gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))" }}>
                {loading
                    ? Array.from({ length: 12 }).map((_, i) => <VideoCard key={i} loading />)
                    : (
                        <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                            {videos.map(video => (
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
                        </InfiniteScroll>
                    )}
            </div>
        </div>
    );
}
