import {useCallback, useMemo, useState} from "react";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import {Link} from "react-router-dom";
import { Button } from "@/components/ui/button";
interface Video {
    id: string;
    title: string;
    thumbnail: string;
    channel_avatar: string;
    channel_name: string;
}

const categories = [
    "All",
    "Music",
    "Gaming",
    "News",
    "Movies",
    "Sports",
    "Podcasts",
    "Education",
    "Fashion",
    "Comedy",
    "Technology",
    "Nature",
    "Fitness",
    "New for you",
];

export default function Home() {
    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(0);
    const [loading] = useState(true);
    const [hasMore, setHasMore] = useState(true);
    const [active, setActive] = useState("All");

    const allVideos: Video[] = useMemo(
        () =>
            Array.from({length: 120}).map((_, i) => ({
                id: `video-${i + 1}`,
                title: `Mock Video ${i + 1}`,
                thumbnail: `https://via.placeholder.com/250x125?text=Video+${i + 1}`,
                channel_avatar: "https://api.dicebear.com/7.x/identicon/svg?seed",
                channel_name: `Channel ${i + 1}`,
            })),
        []
    );

    const loadMore = useCallback(() => {
        const nextPage = page + 1;
        const pageSize = 20;
        const newVideos = allVideos.slice(0, nextPage * pageSize);

        setVideos(newVideos);
        setPage(nextPage);
        setHasMore(newVideos.length < allVideos.length);
    }, [page, allVideos]);

    if (loading && videos.length === 0) {
        loadMore();
    }

    return (
        <div className="my-4">
            <div className="ml-13 mb-4 overflow-x-auto overflow-y-hidden flex no-scrollbar">
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
            <div className="max-w-[1400px] mx-auto">
                <div
                    className="grid auto-rows-min gap-6"
                    style={{gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))"}}
                >
                    {loading
                        ? Array.from({length: 12}).map((_, i) => <VideoCard key={i} loading/>)
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
