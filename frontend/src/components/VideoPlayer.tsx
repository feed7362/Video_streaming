import "plyr-react/plyr.css";
import Hls from "hls.js";
import {usePlyr, type APITypes, type PlyrProps} from "plyr-react";
import type {Options} from "plyr";
import {Card} from '@/components/ui/card';
import {forwardRef, useEffect, useRef, useState, type RefObject} from "react"

interface VideoPlayerProps {
    src: string;
}

const plyrOptions: Plyr.Options = {
    controls: [
        'play-large',
        'play',
        'progress',
        'current-time',
        'mute',
        'volume',
        'captions',
        'settings',
        'pip',
        'airplay',
        'fullscreen'
    ],
    ratio: "16:9",
    loadSprite: true,
    settings: ['captions', 'quality', 'speed', 'loop'],
    iconUrl: "https://cdn.plyr.io/3.8.3/plyr.svg",
    captions: {active: true, language: 'auto', update: false},
    speed: {selected: 1, options: [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 4]},
    quality: {
        default: 720,
        // These are just placeholders. HLS.js will dynamically update them.
        options: [2160, 1440, 1080, 720, 480, 360, 240],
        forced: true,
    },
    i18n: {
        restart: 'Restart',
        rewind: 'Rewind {seektime} secs',
        play: 'Play',
        pause: 'Pause',
        fastForward: 'Forward {seektime} secs',
        seek: 'Seek',
        played: 'Played',
        buffered: 'Buffered',
        currentTime: 'Current time',
        duration: 'Duration',
        volume: 'Volume',
        mute: 'Mute',
        unmute: 'Unmute',
        enableCaptions: 'Enable captions',
        disableCaptions: 'Disable captions',
        enterFullscreen: 'Enter fullscreen',
        exitFullscreen: 'Exit fullscreen',
        frameTitle: 'Player for {title}',
        captions: 'Captions',
        settings: 'Settings',
        speed: 'Speed',
        normal: 'Normal',
        quality: 'Quality',
        loop: 'Loop',
        start: 'Start',
        end: 'End',
        all: 'All',
        reset: 'Reset',
        disabled: 'Disabled',
        enabled: 'Enabled',
        advertisement: 'Ad'
    },
    tooltips: {controls: true, seek: true},
    ads: {enabled: false, publisherId: '', tagUrl: ''},
    previewThumbnails: {enabled: false, src: '', withCredentials: false},
    mediaMetadata: {title: '', artist: '', album: '', artwork: []},
    markers: {enabled: false, points: []},
    loop: {active: true},
    debug: false,
};

const useHls = (src: string, options: Options | null) => {
    const hls = useRef<Hls>(new Hls());
    const hasQuality = useRef<boolean>(false);
    const [plyrOptions, setPlyrOptions] = useState<Options | null>(options);

    useEffect(() => {
        hasQuality.current = false;
    }, [options]);

    useEffect(() => {
        hls.current.loadSource(src);
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-expect-error
        hls.current.attachMedia(document.querySelector(".plyr-react")!);
        hls.current.on(Hls.Events.MANIFEST_PARSED, () => {
            if (hasQuality.current) return;

            const levels = hls.current.levels;
            if (!levels || levels.length === 0) return;

            // 1) Build unique heights and sort DESC so UI shows highest -> lowest
            const heights = Array.from(
                new Set(levels.map(l => l.height).filter(h => Number.isFinite(h)))
            ).sort((a, b) => b - a); // highest first

            // 2) Map each height to the best level index (prefer highest bitrate if multiple levels have same height)
            const heightToIndex = new Map<number, number>();
            heights.forEach(height => {
                let bestIdx = -1;
                let bestBitrate = -1;
                levels.forEach((lvl, idx) => {
                    if (lvl.height === height) {
                        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                        // @ts-expect-error
                        const bitrate = lvl.bitrate ?? lvl.videoBitrate ?? 0;
                        if (bitrate > bestBitrate) {
                            bestBitrate = bitrate;
                            bestIdx = idx;
                        }
                    }
                });
                if (bestIdx !== -1) heightToIndex.set(height, bestIdx);
            });

            const quality: Options['quality'] = {
                default: heights[1],
                options: heights,         // shown in UI highest -> lowest
                forced: true,
                onChange: (newQuality: number) => {
                    const levelIdx = heightToIndex.get(newQuality);
                    if (typeof levelIdx === 'number') {
                        hls.current.currentLevel = levelIdx;
                    } else {
                        // fallback: try any matching level
                        const fallback = levels.findIndex(l => l.height === newQuality);
                        if (fallback !== -1) hls.current.currentLevel = fallback;
                    }
                },
            };

            setPlyrOptions(prev => ({...prev, quality}));
            hasQuality.current = true;
        });

    });

    return {options: plyrOptions};
};

const CustomPlyrInstance = forwardRef<
    APITypes,
    PlyrProps & { hlsSource: string }
>((props, ref) => {
    const {source, options = null, hlsSource} = props;
    const raptorRef = usePlyr(ref, {
        ...useHls(hlsSource, options),
        source,
    }) as RefObject<HTMLVideoElement>;
    return <video ref={raptorRef} className="plyr-react plyr"/>;
});

export default function VideoPlayer({src}: VideoPlayerProps) {
    const ref = useRef<APITypes>(null);
    const supported = Hls.isSupported();
    return (
        <Card className="w-full max-w-4xl mx-auto rounded-lg overflow-hidden p-0">
            <div className="aspect-video">
                {supported ? (
                    <CustomPlyrInstance
                        ref={ref}
                        source={null}
                        options={plyrOptions}
                        hlsSource={src}
                    />
                ) : (
                    "HLS is not supported in your browser"
                )}
            </div>
        </Card>
    );
}
