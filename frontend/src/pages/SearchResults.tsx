import { Link, useSearchParams } from "react-router-dom";
import { useSearch } from "@/hooks/search/useSearch";
import NoSearchResults from "@/pages/NoSearchResults";
import InfiniteScroll from "@/components/misc/infinite-scroll";
import VideoCard from "@/components/cards/VideoCard";

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
        <div className="my-4 mx-auto w-full max-w-[900px] px-4 sm:px-6">
            <h1 className="text-2xl font-bold mb-6">
                {headerTitle}
            </h1>

            <div className="flex flex-col gap-4 w-full">

                {loading && videos.length === 0 && (
                    // Передаємо loading + variant="horizontal" для скелетонів
                    Array.from({ length: 5 }).map((_, i) => (
                        <VideoCard key={i} loading variant="horizontal" />
                    ))
                )}

                <InfiniteScroll loadMore={loadMoreSearchResults} hasMore={hasMore}>
                    <div className="flex flex-col gap-4">
                        {videos.map((video) => (
                            <Link key={video.id} to={`/watch?v=${video.id}`} className="w-full block">
                                {/* ОСЬ ТУТ ГОЛОВНА ЗМІНА: variant="horizontal" */}
                                <VideoCard
                                    id={video.id}
                                    title={video.title}
                                    thumbnail={video.previewUrl}
                                    channel_avatar={video.channel_avatar}
                                    channel_name={video.channel}
                                    views={video.views}
                                    timeAgo={video.timeAgo}
                                    variant="horizontal"
                                // description={video.description} // Можна розкоментувати, якщо useSearch повертає опис
                                />
                            </Link>
                        ))}
                    </div>

                    {loading && videos.length > 0 && (
                        <div className="text-center py-6 text-gray-500 w-full">
                            Loading more...
                        </div>
                    )}
                </InfiniteScroll>
            </div>
        </div>
    );
}