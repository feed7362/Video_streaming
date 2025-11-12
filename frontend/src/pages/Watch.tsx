import { useState } from "react";
import VideoPlayer from "@/components/VideoPlayer";
import VideoCard from "@/components/VideoCard";
import { Button } from "@/components/ui/button";
import InfiniteScroll from "@/components/infinite-scroll";
import { Link } from "react-router-dom";

import { useFetchCategories } from "@/hooks/useCategories";
import { useVideo } from "@/hooks/useVideos";
import { useReactions } from "@/hooks/useReactions";
import { useDownload } from "@/hooks/useDownload";
import type { VideoDetail } from "@api/types";

/*import type { getComments, addComment, deleteComment, addReply, updateComment } from "@api/commentApi";*/
/*import { useFetchCategories } from "@/hooks/useCategories";*/

export default function Watch() {
    const { categories, active, setActive } = useFetchCategories();

    const {
        video,
        videos,
        comments,
        error,
        loading,
        hasMore,
        loadMore,
        metaDataText,
        setVideo,
    } = useVideo();

    const [resolution, setResolution] = useState("720p");

    const { handleDownload } = useDownload({ video: video as unknown as VideoDetail, resolution });

    const { handleReaction } = useReactions({
        initialVideo: video as unknown as VideoDetail,
        initialUserReaction: null,

        onVideoUpdate: (newVideo: VideoDetail) => {
            if (setVideo) {
                setVideo(newVideo as unknown as VideoDetail | null);
            } else {
                console.error("setVideo function is not available.");
            }
        }
    });

    if (error) return <p className="text-red-500">{error}</p>;
    if (loading || !video) return <p>Loading video...</p>;

    const avatarSize = 40;

    return (
        <div className="flex flex-col lg:flex-row items-start gap-6 lg:gap-10 p-4 sm:p-6">
            <div className="w-full lg:w-2/3 lg:max-w-6xl">
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

                    <span className="text-gray-500 text-sm ml-2">
                        {metaDataText}
                    </span>
                </div>
                <div className="mb-6 text-gray-700 text-sm sm:text-base">
                    <h4 className="font-semibold">Description:</h4>
                    <p>{video.description}</p>
                </div>
                <div className="flex items-center gap-4 mt-4 mb-6">
                    <Button onClick={() => handleReaction("like")} className="flex items-center gap-2">
                        <img src="/thumbs_up.svg" alt="Like" />
                        <span>{video.likesCount}</span>
                    </Button>
                    <Button onClick={() => handleReaction("dislike")} className="flex items-center gap-2">
                        <img src="/thumbs-down.svg" alt="Dislike" />
                        <span>{video.dislikesCount}</span>
                    </Button>
                    <select
                        value={resolution}
                        onChange={(e) => setResolution(e.target.value)}
                        className="p-2 rounded border border-gray-300 text-sm"
                    >
                        <option value="360p">360p</option>
                        <option value="720p">720p</option>
                        <option value="1080p">1080p</option>
                    </select>
                    <Button
                        className="text-gray-900 bg-white border border-gray-300 focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-100 font-medium rounded-full text-sm px-5 py-2.5 me-2 mb-2 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700 flex items-center justify-center gap-2"
                        onClick={() => handleDownload()}
                    >
                        <img src="/arrow-big-down.svg" alt="Download" className="w-5 h-5" />
                        <span>Download</span>
                    </Button>
                </div>
                <div className="mt-6">
                    <h2 className="text-lg sm:text-xl font-semibold mb-3">{comments.length} Comments</h2>
                    <div className="space-y-4">
                        {comments.map((comment) => (
                            <div key={comment.id} className="border-b pb-2">
                                <p className="font-medium">{comment.userId}</p>
                                <p className="text-gray-600 text-sm sm:text-base">{comment.content}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            <div className="w-full lg:w-1/3 mt-6 lg:mt-0">
                <h2 className="font-semibold mb-2">Up Next</h2>
                <div className="mb-4 flex overflow-x-auto overflow-y-hidden no-scrollbar cursor-grab active:cursor-grabbing select-none">
                    {categories.map((category) => (
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
                            {videos.map((video) => (
                                <Link key={video.id} to={`/watch?v=${video.id}`} className="w-full">
                                    <VideoCard
                                        id={video.id}
                                        title={video.title}
                                        thumbnail={video.thumbnail_url}
                                        channel_avatar={video.channel_avatar}
                                        channel_name={video.channel_name}
                                        views={video.views}
                                        timeAgo={video.timeAgo}
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
