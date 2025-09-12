import {Skeleton} from "@/components/ui/skeleton";
import {Card} from "@/components/ui/card";

interface VideoCardProps {
    id?: string;
    title?: string;
    thumbnail?: string;
    channel_avatar?: string;
    channel_name?: string;
    loading?: boolean; // if true, render skeleton
}

export const CARD_CONFIG = {
    width: 420,
    height: 315,
    avatarSize: 36,
    metaRatio: 0.25,
};

export default function VideoCard({
                                      title,
                                      thumbnail,
                                      channel_avatar,
                                      channel_name,
                                      loading = false,
                                  }: VideoCardProps) {
    const {height, avatarSize, metaRatio} = CARD_CONFIG;

    const metaHeight = height * metaRatio;
    const thumbnailHeight = height * (1 - metaRatio);

    if (loading) {
        return (
            <div className="w-full">
                <div className="flex flex-col gap-0 w-full" style={{height}}>
                    <Skeleton
                        className="rounded-t-xl block w-full"
                        style={{height: thumbnailHeight}}
                    />
                    <div className="flex items-center gap-3 px-2" style={{height: metaHeight}}>
                        <Skeleton className="rounded-full" style={{width: avatarSize, height: avatarSize}}/>
                        <div className="flex-1 min-w-0">
                            <Skeleton className="h-4 mb-2" style={{width: "60%"}}/>
                            <Skeleton className="h-4" style={{width: "40%"}}/>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (

        <Card className="p-0 gap-0 rounded-xl overflow-hidden w-full" style={{height}}>
            <img
                src={thumbnail}
                alt={title}
                className="rounded-t-xl block w-full"
                style={{height: thumbnailHeight, objectFit: "cover", display: "block"}}
            />
            <div className="flex items-start gap-3 px-3 py-2" style={{height: metaHeight}}>
                <img
                    className="avatar-img rounded-full"
                    src={channel_avatar}
                    alt={channel_name || "channel avatar"}
                    width={avatarSize}
                    height={avatarSize}
                    decoding="async"
                    loading="lazy"
                    style={{width: avatarSize, height: avatarSize, display: "block", objectFit: "cover"}}
                />
                <div className="flex flex-col flex-1 min-w-0">
                    <h2 className="font-semibold truncate">{title}</h2>
                    <h4 className="text-sm text-gray-500 truncate">{channel_name}</h4>
                    <h3 className="text-sm text-gray-500">Views · date</h3>
                </div>
            </div>
        </Card>
    );
}
