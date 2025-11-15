import { Link, useSearchParams } from "react-router-dom";
import { useSearch } from "@/hooks/useSearch";
import NoSearchResults from "@/pages/NoSearchResults";
import InfiniteScroll from "@/components/infinite-scroll";
import VideoCard from "@/components/VideoCard";

export default function SearchResults() {
    const [searchParams] = useSearchParams();
    const queryFromUrl = searchParams.get("q")?.trim() || "";

    const {
        videos,
        loading,
        loadMoreSearchResults,
        hasMore,
    } = useSearch({ enabled: true });

    if (!loading && videos.length === 0) {
        return (
            <div className="my-4 mx-auto max-w-[1400px] px-6">
                <NoSearchResults query={queryFromUrl || "your filters"} />
            </div>
        );
    }

    const headerTitle = queryFromUrl
        ? `Results for "${queryFromUrl}"`
        : "Search Results";

    return (
        <div className="my-4 mx-auto max-w-[1400px] px-6">
            <h1 className="text-2xl font-bold mb-6">
                {headerTitle}
            </h1>

            <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5"
                style={{ gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))" }}>

                {loading && videos.length === 0 && (
                    Array.from({ length: 8 }).map((_, i) => <VideoCard key={i} loading />)
                )}

                <InfiniteScroll loadMore={loadMoreSearchResults} hasMore={hasMore}>
                    {videos.map((video) => (
                        <Link key={video.id} to={`/watch?v=${video.id}`} className="w-full">
                            <VideoCard
                                id={video.id}
                                title={video.title}
                                thumbnail={video.previewUrl}
                                channel_avatar={video.channel_avatar}
                                channel_name={video.channel}
                                views={video.views}
                                timeAgo={video.timeAgo}
                            />
                        </Link>
                    ))}

                    {loading && videos.length > 0 && (
                        <div className="text-center py-4 text-gray-500 col-span-full">
                            Loading more...
                        </div>
                    )}
                </InfiniteScroll>
            </div>
        </div>
    );
}