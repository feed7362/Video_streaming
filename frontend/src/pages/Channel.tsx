import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import type { VideoPreview } from "../types/video";
import type { ChannelInfo} from "../types/channel";
import channelApi from "@api/channelApi";
import videoApi from "@api/videoApi";

export default function Channel() {
    const { channel_name } = useParams<{ channel_name: string }>();
    const [channel, setChannel] = useState<ChannelInfo | null>(null);
    const [videos, setVideos] = useState<VideoPreview[]>([]);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [loading, setLoading] = useState(false);

    const loadChannelInfo = async () => {
        if (!channel_name) return;
        const data = await channelApi.getChannelInfo(channel_name);
        setChannel(data);
    };

    const loadMore = useCallback(async () => {
        if (loading || !channel_name) return;
        setLoading(true);

        const data = await videoApi.getVideos({ page, channel_name });

        if (!data || data.length === 0) {
            setHasMore(false);
            setLoading(false);
            return;
        }

        setVideos(prev => [...prev, ...data]);
        setPage(prev => prev + 1);
        setLoading(false);
    }, [page, loading, channel_name]);

    useEffect(() => {
        setVideos([]);
        setPage(1);
        setHasMore(true);

        loadChannelInfo();
        loadMore();
    }, [channel_name]);

    if (!channel) return <div className="text-center py-20">Loading...</div>;

    return (
        <div className="min-h-screen w-full">
            <SiteHeader />

            <div className="w-full h-48 sm:h-60 md:h-72 bg-gray-800">
                {channel.channelBanner && <img src={channel.channelBanner} alt="Channel Banner" className="w-full h-full object-cover" />}
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between px-6 py-6 border-b border-gray-700">
                <div className="flex items-center gap-4">
                    <img src={channel.channel_avatar} alt="Avatar" className="w-20 h-20 rounded-full border" />
                    <div>
                        <h1 className="text-2xl font-bold">{channel.name}</h1>
                        <p className="text-gray-400">{channel.subscribersCount} subscribers</p>
                    </div>
                </div>

                {channel.isOwner && (
                    <Link to="/upload">
                        <Button>Upload Video</Button>
                    </Link>
                )}
            </div>

            <div className="px-6 py-8">
                <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                        {videos.map(v => (
                            <Link key={v.id} to={`/watch?v=${v.id}`}>
                                <VideoCard
                                    id={v.id}
                                    title={v.title}
                                    thumbnail={v.previewUrl}
                                    channel_name={channel.name}
                                    channel_avatar={channel.channel_avatar}
                                />
                            </Link>
                        ))}

                        {loading && Array.from({ length: 6 }).map((_, i) => <VideoCard key={i} loading />)}
                    </div>
                </InfiniteScroll>
            </div>
        </div>
    );
}
