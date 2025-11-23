import type { ChannelInfo } from "../../types/channel";
import clientApi from "./clientApi";

export const getChannelInfo = (channelName: string): Promise<ChannelInfo> =>
    clientApi.get<ChannelInfo>(`/channels/${channelName}`).then(res => res.data);

export const refreshChannelInfo = (channelName: string): Promise<ChannelInfo> =>
    clientApi.post<ChannelInfo>(`/channels/${channelName}/refresh`).then(res => res.data);

export const subscribeToChannel = (channelName: string): Promise<void> =>
    clientApi.post(`/channels/${channelName}/subscribe`).then(() => { });

export const unsubscribeFromChannel = (channelName: string): Promise<void> =>
    clientApi.post(`/channels/${channelName}/unsubscribe`).then(() => { });

export const getMySubscriptions = (): Promise<ChannelInfo[]> =>
    clientApi.get<ChannelInfo[]>(`/channels/subscriptions`).then(res => res.data);

export default {
    getChannelInfo,
    refreshChannelInfo,
    subscribeToChannel,
    unsubscribeFromChannel,
    getMySubscriptions,
};
