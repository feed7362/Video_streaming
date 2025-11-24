export interface ChannelInfo {
    channel_name: string;
    channel_avatar: string;
    channelBanner?: string;
    subscribersCount: number;
    videosCount: number;
    bio?: string;
    createdAt: string;
    name: string;
    isOwner?: boolean;
}
export interface ChannelPreview {
    channel_name: string;
    channel_avatar: string;
    subscribersCount: number;
    videosCount: number;
}

export interface Channel {
    id: string;
    channel_avatar: string;
    channel_name: string;
    handle: string;
    subscribers: string;
    description: string;
}