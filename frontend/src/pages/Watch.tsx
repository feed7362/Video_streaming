import { useCallback, useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import VideoPlayer from "@/components/VideoPlayer";
import VideoCard from "@/components/VideoCard";
import { Button } from "@/components/ui/button";
import InfiniteScroll from "@/components/infinite-scroll";
import type { VideoPreview, VideoComment } from "@api/videoApi";
import { getVideos, getVideo } from "@api/videoApi";

const categories = [
    "All", "Blogs", "Comedy", "Education", "Fashion", "Films", "Fitness",
    "Food", "Gaming", "Literature", "Movies", "Music", "Nature", "New for you",
    "News", "Online strim", "Podcasts", "Science", "Sports", "Technology", "Watched"
];

export default function Watch() {
    const [searchParams] = useSearchParams();
    const videoId = searchParams.get("v");

    const [video, setVideo] = useState<VideoPreview | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [active, setActive] = useState("All");

    const avatarSize = 40;

    const [comments, setComments] = useState<VideoComment[]>([]);
    const [videos, setVideos] = useState<VideoPreview[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);

    const loadMore = useCallback(async () => {
        try {
            const nextPage = page + 1;
            const newVideos = await getVideos(nextPage);
            setVideos(prev => [...prev, ...newVideos]);
            setPage(nextPage);
            setHasMore(newVideos.length > 0);
        } catch (err) {
            console.error(err);
        }
    }, [page]);

    useEffect(() => {
        if (!videoId) return;

        const fetchVideo = async () => {
            try {
                const data = await getVideo(videoId);
                setVideo({
                    id: data.id,
                    title: data.title,
                    previewUrl: data.thumbnailUrl || data.previewUrl,
                    createdAt: data.createdAt,
                    channel: data.channelName,
                    views: data.viewsCount,
                    channel_avatar: data.channelAvatar || "",
                });
                setComments(data.comments || []);
            } catch (err) {
                console.error(err);
                setError("Video not found");
            }
        };

        fetchVideo();
    }, [videoId]);

    useEffect(() => {
        loadMore().finally(() => setLoading(false));
    }, [loadMore]);

    if (error) return <p className="text-red-500">{error}</p>;
    if (!video) return <p>Loading video...</p>;

    return (
        <div className="flex flex-col lg:flex-row items-start gap-6 lg:gap-10 p-4 sm:p-6">
            <div className="w-full lg:flex-1 lg:max-w-4xl">
                <VideoPlayer src={video.previewUrl || ""} />
                <h1 className="text-xl sm:text-2xl md:text-3xl font-bold my-4">{video.title}</h1>
                <div className="flex items-center gap-3 mb-4">
                    <img
                        className="rounded-full"
                        src={video.channel_avatar || ""}
                        alt={video.channel}
                        width={avatarSize}
                        height={avatarSize}
                        style={{ objectFit: "cover" }}
                    />
                    <span className="text-gray-700 font-medium">{video.channel}</span>
                    <span className="text-gray-500 text-sm ml-2">{video.createdAt}</span>
                </div>
                <div className="mb-6 text-gray-700 text-sm sm:text-base">
                    <p>This is a mock description for <strong>{video.title}</strong>.</p>
                </div>

                <div className="mt-6">
                    <h2 className="text-lg sm:text-xl font-semibold mb-3">{comments.length} Comments</h2>
                    <div className="space-y-4">
                        {comments.map(comment => (
                            <div key={comment.id} className="border-b pb-2">
                                <p className="font-medium">{comment.author}</p>
                                <p className="text-gray-600 text-sm sm:text-base">{comment.text}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="w-full lg:w-80 mt-6 lg:mt-0">
                <h2 className="font-semibold mb-2">Up Next</h2>
                <div className="mb-4 flex overflow-x-auto overflow-y-hidden no-scrollbar cursor-grab active:cursor-grabbing select-none">
                    {categories.map(category => (
                        <Button
                            key={category}
                            onClick={() => setActive(category)}
                            variant={active === category ? "default" : "outline"}
                            className={`mx-2 whitespace-nowrap transition-all ${active === category ? "bg-black text-white" : ""}`}
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
                            {videos.map(vid => (
                                <Link key={vid.id} to={`/watch?v=${vid.id}`}>
                                    <VideoCard
                                        id={vid.id}
                                        title={vid.title}
                                        thumbnail={vid.previewUrl || ""}
                                        channel_avatar={vid.channel_avatar || ""}
                                        channel_name={vid.channel}
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
