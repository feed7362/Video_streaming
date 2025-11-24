import VideoCard from "@/components/cards/VideoCard";
import InfiniteScroll from "@/components/misc/infinite-scroll";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useHistory } from "@/hooks/history/useHistory";
export default function History() {
    const {
        videos,
        loading,
        hasMore,
        loadMore,
        handleRemoveVideo,
        handleClearHistory,
    } = useHistory();

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
