import { useCallback, useMemo, useState } from "react";
import type { Channel } from "../../types/channel";

export function useSubscriptions() {
    const [channels, setChannels] = useState<Channel[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(true);

    const allChannels: Channel[] = useMemo(
        () =>
            Array.from({ length: 60 }).map((_, i) => ({
                id: `channel-${i + 1}`,
                channel_avatar: `https://api.dicebear.com/7.x/identicon/svg?seed=${i + 1}`,
                channel_name: `Channel ${i + 1}`,
                handle: `@channel${i + 1}`,
                subscribers: `${(Math.random() * 100 + 10).toFixed(1)}K subscribers`,
                description:
                    "This is a mock channel description that shows how the subscriptions page looks.",
            })),
        []
    );

    const loadMore = useCallback(() => {
        const nextPage = page + 1;
        const pageSize = 10;
        const newChannels = allChannels.slice(0, nextPage * pageSize);

        setChannels(newChannels);
        setPage(nextPage);
        setHasMore(newChannels.length < allChannels.length);
        setLoading(false);
    }, [page, allChannels]);

    if (loading && channels.length === 0) {
        loadMore();
    }

    return {
        channels,
        loadMore,
        hasMore,
    };
}