import clientApi from "./clientApi";

export const addLike = (videoId: string): Promise<void> =>
    clientApi.post(`/videos/${videoId}/like`).then(() => { });

export const removeLike = (videoId: string): Promise<void> =>
    clientApi.delete(`/videos/${videoId}/like`).then(() => { });

export const addDislike = (videoId: string): Promise<void> =>
    clientApi.post(`/videos/${videoId}/dislike`).then(() => { });

export const removeDislike = (videoId: string): Promise<void> =>
    clientApi.delete(`/videos/${videoId}/dislike`).then(() => { });

export default { addLike, removeLike, addDislike, removeDislike };
