import { timeAgo } from '@/utils/timeAgo';
import type { VideoPreview, ChannelPreview } from './types';
import clientApi from "./clientApi";

export const searchVideos = (query: string, page: number = 0): Promise<VideoPreview[]> =>
    clientApi
        .get<VideoPreview[]>(`/search/videos`, { params: { q: query, page } })
        .then(res =>
            res.data.map(video => ({
                ...video,
                createdAt: timeAgo(video.createdAt),
            }))
        );

export const searchChannels = (query: string, page: number = 0): Promise<ChannelPreview[]> =>
    clientApi
        .get<ChannelPreview[]>(`/search/channels`, { params: { q: query, page } })
        .then(res => res.data);

export const getRecommendedVideos = (videoId: string): Promise<VideoPreview[]> =>
    clientApi
        .get<VideoPreview[]>(`/videos/${videoId}/recommended`)
        .then(res =>
            res.data.map(video => ({
                ...video,
                createdAt: timeAgo(video.createdAt),
            }))
        );

export const getPopularVideos = (page: number = 0): Promise<VideoPreview[]> =>
    clientApi
        .get<VideoPreview[]>(`/videos/popular`, { params: { page } })
        .then(res =>
            res.data.map(video => ({
                ...video,
                createdAt: timeAgo(video.createdAt),
            }))
        );

export default {
    searchVideos,
    searchChannels,
    getRecommendedVideos,
    getPopularVideos,
};
