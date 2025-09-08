import {useEffect, useState} from "react";
import {useParams} from "react-router-dom";
import VideoPlayer from "@/components/VideoPlayer";
import axios from "axios";

interface Video {
    id: string;
    title: string;
    thumbnail: string;
    src: string;
}

export default function Watch() {
    const {videoId} = useParams<{ videoId: string }>();
    const [video, setVideo] = useState<Video | null>(null);

    useEffect(() => {
        if (videoId) {
            axios.get(`http://localhost:8000/api/videos/streaming/${videoId}`)
                .then(res => setVideo(res.data))
                .catch(err => console.error(err));
        }
    }, [videoId]);

    if (!video) return <p>Loading video...</p>;

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">{video.title}</h1>
            <VideoPlayer src={video.src}/>
        </div>
    );
}
