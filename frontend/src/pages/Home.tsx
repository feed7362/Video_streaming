import {useEffect, useState} from "react";
import VideoCard from "@/components/VideoCard";

// import axios from "axios";

interface Video {
    id: string;
    title: string;
    thumbnail: string;
    channel_avatar: string;
    channel_name: string;
}

export default function Home() {
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState(true);

    // Mock video data
    const mockVideos: Video[] = Array.from({length: 120}).map((_, i) => ({
        id: `video-${i + 1}`,
        title: `Mock Video ${i + 1}`,
        thumbnail: `https://via.placeholder.com/250x125?text=Video+${i + 1}`,
        channel_avatar: "https://via.placeholder.com/40x40?text=A",
        channel_name: `Channel ${i + 1}`,
    }));

    useEffect(() => {
        // Simulate API loading delay
        const timer = setTimeout(() => {
            setVideos(mockVideos);
            setLoading(false);
        }, 1500);

        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="p-4">
            <div className="max-w-[1400px] mx-auto">
                <div
                    className="grid auto-rows-min gap-6"
                    style={{gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))"}}
                >
                    {loading
                        ? Array.from({length: 24}).map((_, i) => (
                            <VideoCard key={i} loading/>
                        ))
                        : videos.map(video => (
                            <VideoCard
                                key={video.id}
                                id={video.id}
                                title={video.title}
                                thumbnail={video.thumbnail}
                                channel_avatar={video.channel_avatar}
                                channel_name={video.channel_name}
                            />
                        ))}
                </div>
            </div>
        </div>
    );
}
