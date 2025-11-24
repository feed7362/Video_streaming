import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import VideoCard from "@/components/cards/VideoCard";
import InfiniteScroll from "@/components/misc/infinite-scroll";
import { useHome } from "@/hooks/home/useHome";
export default function Home() {
   
    const {
        categories,
        activeCategory,
        setActiveCategory,
        videos,
        loadMore,
        loading,
        size,
        hasMore,
    } = useHome();

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