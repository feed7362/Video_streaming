import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import VideoCard from "@/components/VideoCard";
import InfiniteScroll from "@/components/infinite-scroll";
import type { ChannelInfo, VideoPreview } from "@api/types";
import channelApi from "@api/channelApi";
import videoApi from "@api/videoApi";

export default function Channel() {
    const { channelName } = useParams<{ channelName: string }>();
    const [channel, setChannel] = useState<ChannelInfo | null>(null);
    const [videos, setVideos] = useState<VideoPreview[]>([]);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [loading, setLoading] = useState(false);

    const loadChannelInfo = async () => {
        if (!channelName) return;
        const data = await channelApi.getChannelInfo(channelName);
        setChannel(data);
    };

    const loadMore = useCallback(async () => {
        if (loading || !channelName) return;
        setLoading(true);

        const data = await videoApi.getVideos({ page, channelName });

        if (!data || data.length === 0) {
            setHasMore(false);
            setLoading(false);
            return;
        }

        setVideos(prev => [...prev, ...data]);
        setPage(prev => prev + 1);
        setLoading(false);
    }, [page, loading, channelName]);

    useEffect(() => {
        setVideos([]);
        setPage(1);
        setHasMore(true);

        loadChannelInfo();
        loadMore();
    }, [channelName]);

    if (!channel) return <div className="text-center py-20">Loading...</div>;

    return (
        <div className="min-h-screen w-full">
            <SiteHeader />

            <div className="w-full h-48 sm:h-60 md:h-72 bg-gray-800">
                {channel.banner && <img src={channel.banner} alt="Channel Banner" className="w-full h-full object-cover" />}
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between px-6 py-6 border-b border-gray-700">
                <div className="flex items-center gap-4">
                    <img src={channel.avatar} alt="Avatar" className="w-20 h-20 rounded-full border" />
                    <div>
                        <h1 className="text-2xl font-bold">{channel.name}</h1>
                        <p className="text-gray-400">{channel.subscribers} subscribers</p>
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
                                    channel_avatar={channel.avatar}
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
