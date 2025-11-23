import { useEffect, useRef } from "react";

import Hls from "hls.js";
import { Card } from "@/components/ui/card";

interface VideoPlayerProps {
    src: string;
}

export default function VideoPlayer({ src }: VideoPlayerProps) {
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        // Diagnostic log
        console.log("[VideoPlayer] src:", src);

        const validateAndAttach = async () => {
            try {
                // Quick fetch to inspect response before handing to Hls
                const res = await fetch(src, { method: "GET", credentials: "same-origin" });
                const ct = res.headers.get("content-type") || "";
                const text = await res.text();
                console.log("[VideoPlayer] fetched manifest content-type:", ct);
                console.log("[VideoPlayer] fetched manifest first chars:", text.slice(0, 128));

                if (!text.startsWith("#EXTM3U")) {
                    console.error("[VideoPlayer] Manifest fetch did not return an HLS playlist — aborting Hls load. Response preview:", text.slice(0, 200));
                    // don't proceed to attach Hls if manifest is not valid
                    return;
                }

                // If manifest looks valid, proceed with Hls
                if (Hls.isSupported()) {
                    const hls = new Hls();
                    hls.loadSource(src);
                    hls.attachMedia(video);
                    hls.on(Hls.Events.MANIFEST_PARSED, () => {
                        video.play();
                    });
                    hls.on(Hls.Events.ERROR, function (event, data) {
                        console.error("HLS.js error:", event, data);
                    });
                    return () => hls.destroy();
                } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
                    video.src = src;
                }
            } catch (err) {
                console.error("[VideoPlayer] Error fetching manifest before Hls:", err);
            }
        };

        validateAndAttach();
    }, [src]);

    return (<Card className="w-full max-w-4xl mx-auto rounded-lg overflow-hidden p-0">
        <video
            ref={videoRef}
            controls
            className="w-full h-auto block"
            style={{ aspectRatio: "16/9", display: "block" }}
        />
    </Card>);
}
