import VideoCard from "@/components/cards/VideoCard";
import InfiniteScroll from "@/components/misc/infinite-scroll";
import { Link } from "react-router-dom";
import { useWatchLater } from "@/hooks/watchLater/useWatchLater";
export default function WatchLater() {
    const {
        videos,
        loading,
        hasMore,
        loadMore,
    } = useWatchLater();

    return (
        <div className="my-4 mx-auto max-w-[1400px] px-6">
            <h1 className="text-2xl font-bold mb-4">Watch later</h1>
            <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5"
                    style={{ gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))" }}>
                    {videos.map(video => (
                        <Link key={video.id} to={`/watch?v=${video.id}`} className="w-full">
                            <VideoCard
                                id={video.id}
                                title={video.title}
                                thumbnail={video.thumbnail_url}
                                channel_avatar={video.channel_avatar}
                                channel_name={video.channel_name}
                            />
                        </Link>
                    ))}
                    {loading && Array.from({ length: 6 }).map((_, i) => <VideoCard key={i} loading />)}
                </div>
            </InfiniteScroll>
        </div>
    );
}
