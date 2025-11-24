import ChannelCard from "@/components/cards/ChannelCard";
import InfiniteScroll from "@/components/misc/infinite-scroll";
import { useSubscriptions } from "@/hooks/subscriptions/useSubscriptions";
export default function Subscriptions() {
    const { channels,
        loadMore,
        hasMore, } = useSubscriptions();

    return (
        <div className="my-8 mx-auto max-w-[1100px] px-6">
            <h1 className="text-3xl font-bold mb-6">
                Channels you’re subscribed to
            </h1>

            <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                <div className="flex flex-col gap-4">
                    {channels.map((channel) => (
                        <ChannelCard
                            key={channel.id}
                            channel_avatar={channel.channel_avatar}
                            channel_name={channel.channel_name}
                            handle={channel.handle}
                            subscribers={channel.subscribers}
                            description={channel.description}
                        />
                    ))}
                </div>
            </InfiniteScroll>
        </div>
    );
}
