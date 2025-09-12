import {useEffect, useState} from "react";
import {useSearchParams, Link} from "react-router-dom";
import VideoPlayer from "@/components/VideoPlayer";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";

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
    const channel = searchParams.get("ab_channel");

    const [video, setVideo] = useState<Video | null>(null);
    const [error, setError] = useState<string | null>(null);

    const channel_name = channel ?? "Unknown Channel";
    const channel_avatar = `https://api.dicebear.com/7.x/identicon/svg?seed`;
    const avatarSize = 40;

    // Comments
    const [comments, setComments] = useState<Comment[]>([]);

    // Sidebar video state
    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);

    // All available sidebar videos
    const allVideos: Video[] = Array.from({length: 120}).map((_, i) => ({
        id: `video-${i + 1}`,
        title: `Mock Video ${i + 1}`,
        thumbnail: `https://via.placeholder.com/250x125?text=Video+${i + 1}`,
        src: "https://www.w3schools.com/html/mov_bbb.mp4",
        channel_avatar: "https://api.dicebear.com/7.x/identicon/svg?seed",
        channel_name: `Channel ${i + 1}`,
    }));

    // Load next page of videos (20 at a time)
    const loadMore = () => {
        const nextPage = page + 1;
        const pageSize = 20;
        const newVideos = allVideos.slice(0, nextPage * pageSize);

        setVideos(newVideos);
        setPage(nextPage);
        setHasMore(newVideos.length < allVideos.length);
    };

    useEffect(() => {
        if (!videoId) return;

        const timer = setTimeout(() => {
            const mockVideo: Video = {
                id: videoId,
                title: `Mock Video ${videoId}`,
                thumbnail: `https://via.placeholder.com/640x360?text=Video+${videoId}`,
                src: "https://www.w3schools.com/html/mov_bbb.mp4",
            };

            if (videoId === "404") {
                setError("Video not found");
            } else {
                setVideo(mockVideo);

                // Mock comments
                setComments([
                    {id: "c1", author: "User123", text: "Great video!"},
                    {id: "c2", author: "JaneDoe", text: "Really helpful tutorial."},
                    {id: "c3", author: "CoderGuy", text: "Can you explain more about hooks?"},
                ]);
            }
        }, 800);

        return () => clearTimeout(timer);
    }, [videoId]);

    // Initial sidebar load
    useEffect(() => {
        const timer = setTimeout(() => {
            loadMore();
            setLoading(false);
        }, 1000);

        return () => clearTimeout(timer);
    }, []);

    if (error) return <p className="text-red-500">{error}</p>;
    if (!video) return <p>Loading video...</p>;

    return (
        <div className="flex items-start gap-10 p-6">
            {/* Main content */}
            <div className="flex-1 max-w-4xl ml-[80px]">
                {/* Video player */}
                <VideoPlayer src={video.src}/>
                <h1 className="text-2xl font-bold my-4">{video.title}</h1>

                {/* Channel info */}
                <div className="flex items-center gap-3 mb-4">
                    <img
                        className="rounded-full"
                        src={channel_avatar}
                        alt={channel_name || "channel avatar"}
                        width={avatarSize}
                        height={avatarSize}
                        style={{objectFit: "cover"}}
                    />
                    <span className="text-gray-700 font-medium">{channel_name}</span>
                </div>

                {/* Description */}
                <div className="mb-6 text-gray-700">
                    <p className="text-sm">
                        This is a mock description for <strong>{video.title}</strong>.
                    </p>
                </div>

                {/* Comments */}
                <div className="mt-6">
                    <h2 className="text-lg font-semibold mb-3">{comments.length} Comments</h2>
                    <div className="space-y-4">
                        {comments.map((comment) => (
                            <div key={comment.id} className="border-b pb-2">
                                <p className="font-medium">{comment.author}</p>
                                <p className="text-gray-600">{comment.text}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Sidebar (Video bar) */}
            <div className="w-100">
                <h2 className="font-semibold mb-2">Up Next</h2>
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                        {videos.map((vid) => (
                            <Link
                                key={vid.id}
                                to={`/watch?v=${vid.id}&ab_channel=${encodeURIComponent(vid.channel_name || "")}`}
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
                    </InfiniteScroll>
                )}
            </div>
        </div>
    );
}
