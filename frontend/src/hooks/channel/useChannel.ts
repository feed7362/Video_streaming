import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import type { VideoPreview } from "../../types/video";
import type { ChannelInfo } from "../../types/channel";
import channelApi from "@api/channelApi";
import videoApi from "@api/videoApi";

export function useChannel() {
    const { channel_name } = useParams<{ channel_name: string }>();
    const [channel, setChannel] = useState<ChannelInfo | null>(null);
    const [videos, setVideos] = useState<VideoPreview[]>([]);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [loading, setLoading] = useState(false);

    const loadChannelInfo = useCallback(async () => {
        if (!channel_name) return;
        const data = await channelApi.getChannelInfo(channel_name);
        setChannel(data);
    }, [channel_name]);

    useEffect(() => {
        loadChannelInfo();
    }, [loadChannelInfo]);


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
    }, [loadChannelInfo, loadMore, channel_name]);

    return {
        loadMore,
        channel,
        videos,
        hasMore,
        loadChannelInfo,
        loading,
    };    
}