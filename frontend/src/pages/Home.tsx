import {useEffect, useState} from "react";
import VideoPlayer from "@/components/VideoPlayer";
import VideoCard from "@/components/VideoCard";
import axios from "axios";

interface Video {
    id: string;
    title: string;
    thumbnail: string;
}

export default function Home() {
    const [videos, setVideos] = useState<Video[]>([]);

    useEffect(() => {
        axios.get("http://localhost:8000/api/videos")
            .then(res => setVideos(res.data))
            .catch(err => console.error(err));
    }, []);

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">My VOD MVP</h1>

            {/* Featured video */}
            <VideoPlayer src="http://localhost:8000/videos/123/playlist.m3u8"/>

            <h2 className="mt-6 mb-4 text-xl font-semibold">All Videos</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {videos.map(video => (
                    <VideoCard key={video.id} {...video} />
                ))}
            </div>
        </div>
    );
}
