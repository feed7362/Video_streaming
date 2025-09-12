import {useEffect, useState} from "react";
import {useSearchParams} from "react-router-dom";
import VideoPlayer from "@/components/VideoPlayer";

interface Video {
    id: string;
    title: string;
    thumbnail: string;
    src: string;
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
            }
        }, 800);

        return () => clearTimeout(timer);
    }, [videoId]);

    if (error) return <p className="text-red-500">{error}</p>;
    if (!video) return <p>Loading video...</p>;

    return (
        <div className="p-6">
            <VideoPlayer src={video.src}/>
            <h1 className="text-2xl font-bold mb-4">{video.title}</h1>

            <div className="flex items-center gap-3 mb-2">
                <img
                    className="avatar-img rounded-full"
                    src={channel_avatar}
                    alt={channel_name || "channel avatar"}
                    width={avatarSize}
                    height={avatarSize}
                    decoding="async"
                    loading="lazy"
                    style={{width: avatarSize, height: avatarSize, display: "block", objectFit: "cover"}}
                />

                <span className="text-gray-700 font-medium">{channel_name}</span>
            </div>
            {channel && <p className="text-gray-500">Channel: {channel}</p>}
        </div>
    );
}
