import { useCallback, useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import VideoPlayer from "@/components/VideoPlayer";
import VideoCard from "@/components/VideoCard";
import { Button }  from "@/components/ui/button";
import InfiniteScroll from "@/components/infinite-scroll";

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

interface Video {
    id: string;
    title: string;
    thumbnail: string;
    src: string;
    channel_avatar?: string;
    channel_name?: string;
}

interface Comment {
    id: string;
    author: string;
    text: string;
}

export default function Watch() {
    const [searchParams] = useSearchParams();
    const videoId = searchParams.get("v");

    const [video, setVideo] = useState<Video | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [active, setActive] = useState("All");

    const avatarSize = 40;

    // Comments
    const [comments, setComments] = useState<Comment[]>([]);

    // Sidebar video state
    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);

    const allVideos: Video[] = Array.from({ length: 120 }).map((_, i) => ({
        id: `video-${i + 1}`,
        title: `Mock Video ${i + 1}`,
        thumbnail: `https://via.placeholder.com/250x125?text=Video+${i + 1}`,
        src: "https://www.w3schools.com/html/mov_bbb.mp4",
        channel_avatar: "https://api.dicebear.com/7.x/identicon/svg?seed",
        channel_name: `Channel ${i + 1}`,
    }));

    const loadMore = useCallback(() => {
        const nextPage = page + 1;
        const pageSize = 20;
        const newVideos = allVideos.slice(0, nextPage * pageSize);

        setVideos(newVideos);
        setPage(nextPage);
        setHasMore(newVideos.length < allVideos.length);
    }, [page, allVideos]);

    useEffect(() => {
        if (!videoId) return;

        // =============================
        // Оригінальний fetch закоментований
        /*
        const fetchVideoData = async () => {
            try {
                const res = await fetch(`/api/video/info/${videoId}`);
                if (!res.ok) throw new Error("Video not found");
                const data = await res.json();

                setVideo({
                    id: data.id,
                    title: data.name,
                    thumbnail: data.thumbnail_url,
                    src: data.master_hls_url,
                    channel_avatar: data.avatar_url,
                    channel_name: data.channel_name,
                });

                setComments(data.comments || []);
            } catch (err) {
                setError((err as Error).message);
            }
        };

        fetchVideoData();
        */
        // =============================

        // Використовуємо мокові дані
        const vid = allVideos.find(v => v.id === videoId);
        if (vid) {
            setVideo(vid);
            setComments([
                { id: "1", author: "Alice", text: "Great video!" },
                { id: "2", author: "Bob", text: "Thanks for sharing." },
            ]);
        } else {
            setError("Video not found");
        }
    }, [videoId, allVideos]);

    // Initial sidebar load
    useEffect(() => {
        const timer = setTimeout(() => {
            loadMore();
            setLoading(false);
        }, 500); // трохи швидше, ніж 1000ms

        return () => clearTimeout(timer);
    }, [loadMore]);

    if (error) return <p className="text-red-500">{error}</p>;
    if (!video) return <p>Loading video...</p>;

    return (
        <div className="flex flex-col lg:flex-row items-start gap-6 lg:gap-10 p-4 sm:p-6">
            {/* Main content */}
            <div className="w-full lg:flex-1 lg:max-w-4xl">
                <VideoPlayer src={video.src} />
                <h1 className="text-xl sm:text-2xl md:text-3xl font-bold my-4">{video.title}</h1>

                {/* Channel info */}
                <div className="flex items-center gap-3 mb-4">
                    <img
                        className="rounded-full"
                        src={video.channel_avatar}
                        alt={video.channel_name}
                        width={avatarSize}
                        height={avatarSize}
                        style={{ objectFit: "cover" }}
                    />
                    <span className="text-gray-700 font-medium">{video.channel_name}</span>
                </div>

                {/* Description */}
                <div className="mb-6 text-gray-700 text-sm sm:text-base">
                    <p>This is a mock description for <strong>{video.title}</strong>.</p>
                </div>

                {/* Comments */}
                <div className="mt-6">
                    <h2 className="text-lg sm:text-xl font-semibold mb-3">{comments.length} Comments</h2>
                    <div className="space-y-4">
                        {comments.map((comment) => (
                            <div key={comment.id} className="border-b pb-2">
                                <p className="font-medium">{comment.author}</p>
                                <p className="text-gray-600 text-sm sm:text-base">{comment.text}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Sidebar */}
            <div className="w-full lg:w-80 mt-6 lg:mt-0">
                <h2 className="font-semibold mb-2">Up Next</h2>

                {/* Горизонтальні кнопки категорій з drag-to-scroll */}
                <div
                    className="mb-4 flex overflow-x-auto overflow-y-hidden no-scrollbar cursor-grab active:cursor-grabbing select-none"
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

                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                        <div className="space-y-4">
                            {videos.map((vid) => (
                                <Link
                                    key={vid.id}
                                    to={`/watch?v=${vid.id}&ab_channel=${encodeURIComponent(
                                        vid.channel_name || ""
                                    )}`}
                                >
                                    <VideoCard
                                        id={vid.id}
                                        title={vid.title}
                                        thumbnail={vid.thumbnail}
                                        channel_avatar={vid.channel_avatar || ""}
                                        channel_name={vid.channel_name || ""}
                                    />
                                </Link>
                            ))}
                        </div>
                    </InfiniteScroll>
                )}
            </div>
        </div>
    );
}
