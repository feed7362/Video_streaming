import { useEffect, useRef, useState } from "react";
import ReactPlayer from "react-player";
import { Card } from "@/components/ui/card";
import {
    Play,
    Pause,
    Volume2,
    VolumeX,
    Maximize,
    Minimize,
    Settings,
    SkipForward,
    ChevronsRight,
    ChevronsLeft,
    /*    Subtitles*/
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Quality {
    label: string;
    url: string;
}

interface VideoPlayerProps {
    videoId: string;
    qualities: Quality[];
    onNext?: () => void;
}

type ProgressState = {
    played: number;
    playedSeconds: number;
    loaded: number;
    loadedSeconds: number;
};

const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return "0:00";
    const date = new Date(seconds * 1000);
    const hh = date.getUTCHours();
    const mm = date.getUTCMinutes();
    const ss = date.getUTCSeconds().toString().padStart(2, "0");
    if (hh) {
        return `${hh}:${mm.toString().padStart(2, "0")}:${ss}`;
    }
    return `${mm}:${ss}`;
};

export default function VideoPlayer({ videoId, qualities, onNext }: VideoPlayerProps) {
    const playerRef = useRef<ReactPlayer | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const lastTapTimeRef = useRef<number>(0);

    const [currentQuality, setCurrentQuality] = useState(qualities[0].url);
    const [playing, setPlaying] = useState(true);
    const [volume, setVolume] = useState(0.8);
    const [muted, setMuted] = useState(false);
    const [played, setPlayed] = useState(0);
    const [duration, setDuration] = useState(0);
    const [seeking, setSeeking] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [showControls, setShowControls] = useState(true);

    const [doubleTapAnimation, setDoubleTapAnimation] = useState<"left" | "right" | null>(null);

    const storageKey = `video-progress-${videoId}`;
    let controlsTimeout: NodeJS.Timeout;

    useEffect(() => {
        const src = currentQuality;
        if (!src) return;

        console.log("[VideoPlayer] Checking src:", src);

        const validateManifest = async () => {
            try {
                const res = await fetch(src, { method: "GET", credentials: "same-origin" });
                const ct = res.headers.get("content-type") || "";

                if (res.ok) {
                    console.log("[VideoPlayer] Manifest check OK. Content-Type:", ct);
                } else {
                    console.error("[VideoPlayer] Manifest check failed:", res.status);
                }
            } catch (err) {
                console.error("[VideoPlayer] Error fetching manifest diagnostic:", err);
            }
        };

        validateManifest();
    }, [currentQuality]);

    // Відновлення позиції
    useEffect(() => {
        const saved = localStorage.getItem(storageKey);
        if (saved && playerRef.current) {
            const seconds = parseFloat(saved);
            playerRef.current.seekTo(seconds, "seconds");
        }
    }, [currentQuality, storageKey]);

    const handleMouseMove = () => {
        setShowControls(true);
        clearTimeout(controlsTimeout);
        controlsTimeout = setTimeout(() => {
            if (playing) setShowControls(false);
        }, 3000);
    };

    const handlePlayPause = () => setPlaying(!playing);

    const handleSeekRelative = (seconds: number) => {
        const current = playerRef.current?.getCurrentTime() || 0;
        playerRef.current?.seekTo(current + seconds, "seconds");
    };

    const handleVideoAreaClick = (e: React.MouseEvent<HTMLDivElement>) => {
        const now = Date.now();
        const DOUBLE_TAP_DELAY = 300;

        if (now - lastTapTimeRef.current < DOUBLE_TAP_DELAY) {
            const rect = containerRef.current?.getBoundingClientRect();
            if (!rect) return;

            const x = e.clientX - rect.left;
            const isRightSide = x > rect.width / 2;

            if (isRightSide) {
                handleSeekRelative(10);
                triggerDoubleTapAnimation('right');
            } else {
                handleSeekRelative(-10);
                triggerDoubleTapAnimation('left');
            }
            setPlaying(true);
        } else {
            handlePlayPause();
        }
        lastTapTimeRef.current = now;
    };

    const triggerDoubleTapAnimation = (side: "left" | "right") => {
        setDoubleTapAnimation(side);
        setTimeout(() => setDoubleTapAnimation(null), 500);
    };

    const handleProgress = (state: ProgressState) => {
        if (!seeking) {
            setPlayed(state.played);
            localStorage.setItem(storageKey, state.playedSeconds.toString());
        }
    };

    const handleDuration = (duration: number) => setDuration(duration);

    const handleSeekChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setPlayed(parseFloat(e.target.value));
    };

    const handleSeekMouseDown = () => setSeeking(true);

    const handleSeekMouseUp = (e: React.MouseEvent<HTMLInputElement> | React.TouchEvent<HTMLInputElement>) => {
        setSeeking(false);
        const target = e.target as HTMLInputElement;
        playerRef.current?.seekTo(parseFloat(target.value));
    };

    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            containerRef.current?.requestFullscreen();
            setIsFullscreen(true);
        } else {
            document.exitFullscreen();
            setIsFullscreen(false);
        }
    };

    const handleQualityChange = (url: string) => {
        const currentTime = playerRef.current?.getCurrentTime() || 0;
        setCurrentQuality(url);
        setShowSettings(false);
        setTimeout(() => {
            playerRef.current?.seekTo(currentTime, "seconds");
        }, 200);
    };

    const handleEnded = () => {
        setPlaying(false);
    }

    return (
        <Card
            ref={containerRef}
            className="relative w-full max-w-4xl mx-auto rounded-xl overflow-hidden bg-black group aspect-video border-none shadow-2xl ring-offset-background focus-visible:outline-none select-none"
            onMouseMove={handleMouseMove}
            onMouseLeave={() => playing && setShowControls(false)}
        >
            <div className="absolute inset-0 z-0 cursor-pointer" onClick={handleVideoAreaClick}>
                <ReactPlayer
                    ref={playerRef}
                    url={currentQuality}
                    width="100%"
                    height="100%"
                    playing={playing}
                    volume={volume}
                    muted={muted}
                    onProgress={handleProgress}
                    onDuration={handleDuration}
                    onEnded={handleEnded}
                    controls={false}
                    light={false}
                    style={{ pointerEvents: 'none' }}
                    config={{
                        file: {
                            forceHLS: true,
                            hlsOptions: {
                                xhrSetup: function (xhr: XMLHttpRequest) {
                                    xhr.withCredentials = true;
                                }
                            }
                        }
                    }}
                />
            </div>

            {doubleTapAnimation && (
                <div className={cn(
                    "absolute inset-y-0 w-1/2 flex items-center justify-center bg-white/10 z-10 transition-opacity duration-500 pointer-events-none",
                    doubleTapAnimation === 'left' ? "left-0 rounded-r-full" : "right-0 rounded-l-full"
                )}>
                    <div className="flex flex-col items-center justify-center text-white animate-in zoom-in duration-300">
                        {doubleTapAnimation === 'left' ? (
                            <>
                                <ChevronsLeft size={48} />
                                <span className="text-sm font-bold">-10s</span>
                            </>
                        ) : (
                            <>
                                <ChevronsRight size={48} />
                                <span className="text-sm font-bold">+10s</span>
                            </>
                        )}
                    </div>
                </div>
            )}

            <div
                className={cn(
                    "absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/90 via-black/40 to-transparent transition-opacity duration-300 z-10 pointer-events-none",
                    showControls ? "opacity-100" : "opacity-0"
                )}
            />

            <div
                className={cn(
                    "absolute bottom-0 left-0 right-0 px-4 pb-3 transition-opacity duration-300 z-20 flex flex-col gap-2",
                    showControls ? "opacity-100" : "opacity-0"
                )}
                onClick={(e) => e.stopPropagation()}
            >
                <div className="relative w-full h-1.5 group/slider cursor-pointer flex items-center">
                    <input
                        type="range"
                        min={0}
                        max={0.999999}
                        step="any"
                        value={played}
                        onMouseDown={handleSeekMouseDown}
                        onChange={handleSeekChange}
                        onMouseUp={handleSeekMouseUp}
                        onTouchEnd={handleSeekMouseUp}
                        className="absolute w-full h-full opacity-0 z-20 cursor-pointer"
                    />
                    <div className="w-full h-1 bg-white/30 rounded-full group-hover/slider:h-1.5 transition-all">
                        <div
                            className="h-full bg-[#f00] rounded-l-full relative"
                            style={{ width: `${played * 100}%` }}
                        >
                            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-[#f00] rounded-full scale-0 group-hover/slider:scale-100 transition-transform shadow-md" />
                        </div>
                    </div>
                </div>

                <div className="flex items-center justify-between text-white">
                    <div className="flex items-center gap-2 sm:gap-4">

                        <button onClick={handlePlayPause} className="hover:bg-white/10 p-2 rounded-full transition">
                            {playing ? <Pause size={28} fill="white" /> : <Play size={28} fill="white" />}
                        </button>

                        {onNext && (
                            <button onClick={onNext} className="hover:bg-white/10 p-2 rounded-full transition hidden sm:block ml-1">
                                <SkipForward size={20} fill="white" />
                            </button>
                        )}

                        <div className="flex items-center gap-2 group/volume ml-2">
                            <button onClick={() => setMuted(!muted)} className="hover:bg-white/10 p-2 rounded-full transition">
                                {muted || volume === 0 ? <VolumeX size={24} /> : <Volume2 size={24} />}
                            </button>
                            <input
                                type="range"
                                min={0}
                                max={1}
                                step={0.1}
                                value={muted ? 0 : volume}
                                onChange={(e) => {
                                    setVolume(parseFloat(e.target.value));
                                    setMuted(false);
                                }}
                                className="w-0 group-hover/volume:w-20 transition-all duration-300 h-1 accent-white bg-white/30 rounded-lg cursor-pointer"
                            />
                        </div>

                        <div className="text-xs sm:text-sm font-medium tabular-nums ml-2">
                            {formatTime(duration * played)} / {formatTime(duration)}
                        </div>
                    </div>

                    <div className="flex items-center gap-2 sm:gap-4">

                        <div className="relative">
                            <button
                                onClick={() => setShowSettings(!showSettings)}
                                className={`hover:bg-white/10 p-2 rounded-full transition ${showSettings ? 'rotate-45' : ''}`}
                            >
                                <Settings size={20} />
                            </button>

                            {showSettings && (
                                <div className="absolute bottom-12 right-0 bg-black/90 border border-white/10 rounded-xl p-2 min-w-[120px] shadow-xl backdrop-blur-md flex flex-col gap-1">
                                    {qualities.map((q) => (
                                        <button
                                            key={q.label}
                                            onClick={() => handleQualityChange(q.url)}
                                            className={cn(
                                                "text-left px-3 py-2 rounded-lg text-sm hover:bg-white/20 transition",
                                                currentQuality === q.url ? "text-[#f00] font-bold" : "text-white"
                                            )}
                                        >
                                            {q.label}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        <button onClick={toggleFullscreen} className="hover:bg-white/10 p-2 rounded-full transition">
                            {isFullscreen ? <Minimize size={20} /> : <Maximize size={20} />}
                        </button>
                    </div>
                </div>
            </div>
        </Card>
    );
}