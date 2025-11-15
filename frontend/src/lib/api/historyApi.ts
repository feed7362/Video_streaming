import clientApi from "./clientApi";
import type { VideoPreview } from "./types";

export const getUserHistory = (
    page: number = 1,
    size: number = 20
): Promise<{ items: VideoPreview[]; total: number }> => {
    return clientApi
        .get(`/videos/history`, { params: { page, size } })
        .then(res => res.data);
};

 export const clearUserHistory = (): Promise<void> => {
    return clientApi.delete('/videos/history').then(() => { });
};

export const removeVideoFromHistory = (videoId: string): Promise<void> => {
    return clientApi.delete(`/videos/history/${videoId}`).then(() => { });
};

export default { getUserHistory, clearUserHistory, removeVideoFromHistory };