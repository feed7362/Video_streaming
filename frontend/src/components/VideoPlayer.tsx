import { useEffect, useRef } from "react";
import Hls from "hls.js";

interface VideoPlayerProps {
    src: string;
}

export default function VideoPlayer({ src }: VideoPlayerProps) {
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        if (Hls.isSupported()) {
            const hls = new Hls();
            hls.loadSource(src);
            hls.attachMedia(video);
            hls.on(Hls.Events.MANIFEST_PARSED, () => {
                video.play();
            });
            hls.on(Hls.Events.ERROR, (event, data) => {
                console.error("HLS.js error:", event, data);
            });
            return () => hls.destroy();
        } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
            video.src = src;
        }
    }, [src]);

    return (
        <video
            ref={videoRef}
            controls
            className="w-full block"
            style={{ aspectRatio: "16/9" }}
        />
    );
}
