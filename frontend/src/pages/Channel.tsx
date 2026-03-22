import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import type { ChannelInfo, VideoPreview } from "@api/types";
import channelApi from "@api/channelApi";
import videoApi from "@api/videoApi";

export default function Channel() {
    const { channel_name } = useParams<{ channel_name: string }>();
    const [channel, setChannel] = useState<ChannelInfo | null>(null);
    const [videos, setVideos] = useState<VideoPreview[]>([]);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [loading, setLoading] = useState(false);
    const [subscribed, setSubscribed] = useState(false);

    useEffect(() => {
        if (!channel_name) return;
        channelApi.getChannelInfo(channel_name).then(setChannel).catch(console.error);
        setVideos([]);
        setPage(1);
        setHasMore(true);
    }, [channel_name]);

    const loadMore = useCallback(async () => {
        if (loading || !channel_name) return;
        setLoading(true);
        try {
            const data = await videoApi.getVideos({ page, channel_name });
            if (!data || data.length === 0) { setHasMore(false); return; }
            setVideos((prev) => [...prev, ...data]);
            setPage((p) => p + 1);
        } finally {
            setLoading(false);
        }
    }, [page, loading, channel_name]);

    useEffect(() => { loadMore(); }, [channel_name]); // eslint-disable-line react-hooks/exhaustive-deps

    const formatSubs = (n?: number) => {
        if (!n) return "0 subscribers";
        if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M subscribers`;
        if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K subscribers`;
        return `${n} subscriber${n !== 1 ? "s" : ""}`;
    };

    return (
        <div className="min-h-screen">
            {/* Banner */}
            <div className="w-full h-36 sm:h-48 md:h-56 bg-gradient-to-r from-muted to-muted/50 overflow-hidden">
                {channel?.channelBanner && (
                    <img src={channel.channelBanner} alt="Banner" className="w-full h-full object-cover" />
                )}
            </div>

            {/* Channel info */}
            <div className="max-w-[1200px] mx-auto px-4 sm:px-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 py-5 border-b border-border">
                    {/* Avatar */}
                    {channel ? (
                        <img
                            src={channel.channel_avatar}
                            alt={channel.name}
                            className="w-20 h-20 sm:w-24 sm:h-24 rounded-full border-4 border-background object-cover -mt-10 sm:-mt-12 ring-2 ring-border"
                        />
                    ) : (
                        <Skeleton className="w-20 h-20 sm:w-24 sm:h-24 rounded-full -mt-10 sm:-mt-12" />
                    )}

                    <div className="flex flex-1 flex-col sm:flex-row sm:items-center sm:justify-between gap-3 min-w-0">
                        <div>
                            {channel ? (
                                <>
                                    <h1 className="text-xl sm:text-2xl font-bold">{channel.name}</h1>
                                    <p className="text-sm text-muted-foreground mt-0.5">
                                        @{channel.name.toLowerCase().replace(/\s+/g, "")} · {formatSubs(channel.subscribersCount)}
                                    </p>
                                    {channel.bio && (
                                        <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{channel.bio}</p>
                                    )}
                                </>
                            ) : (
                                <div className="space-y-2">
                                    <Skeleton className="h-6 w-48" />
                                    <Skeleton className="h-4 w-32" />
                                </div>
                            )}
                        </div>

                        <div className="flex items-center gap-2">
                            {channel?.isOwner ? (
                                <Button asChild className="rounded-full" variant="outline">
                                    <Link to="/upload">Upload video</Link>
                                </Button>
                            ) : (
                                <Button
                                    className="rounded-full"
                                    variant={subscribed ? "outline" : "default"}
                                    onClick={() => setSubscribed((v) => !v)}
                                >
                                    {subscribed ? "Subscribed" : "Subscribe"}
                                </Button>
                            )}
                        </div>
                    </div>
                </div>

                {/* Videos grid */}
                <div className="py-6">
                    <h2 className="text-base font-semibold mb-4">Videos</h2>
                    <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                        <div className="grid gap-x-4 gap-y-7 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                            {videos.map((v) => (
                                <Link key={v.id} to={`/watch?v=${v.id}`}>
                                    <VideoCard
                                        id={v.id}
                                        title={v.title}
                                        thumbnail={v.previewUrl}
                                        channel_name={channel?.name}
                                        channel_avatar={channel?.channel_avatar}
                                    />
                                </Link>
                            ))}
                            {loading && Array.from({ length: 8 }).map((_, i) => <VideoCard key={i} loading />)}
                        </div>
                    </InfiniteScroll>

                    {!hasMore && videos.length === 0 && !loading && (
                        <p className="text-center text-muted-foreground py-16 text-sm">No videos uploaded yet.</p>
                    )}
                </div>
            </div>
        </div>
    );
}
