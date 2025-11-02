import { timeAgo } from "@/utils/timeAgo";
import type { Video, VideoPreview } from "./types";
import clientApi from "./clientApi";

const mapToPreview = (video: Video): VideoPreview => ({
    id: video.id,
    title: video.title,
    previewUrl: video.thumbnailUrl || video.previewUrl || "",
    createdAt: timeAgo(video.createdAt),
    channel: video.channelName,
    views: video.viewsCount,
    likesCount: video.likesCount,
    dislikesCount: video.dislikesCount,
    privacy: video.isPublic ? "Public" : "Private",
});

export const getVideos = (
    page = 0,
    category?: string
): Promise<VideoPreview[]> => {
    return clientApi
        .get<Video[]>("/videos", { params: { page, category } })
        .then(res => res.data.filter(v => v.isPublic).map(mapToPreview));
};

export const getVideo = (id: string): Promise<Video> =>
    clientApi.get<Video>(`/videos/${id}`).then(res => ({
        ...res.data,
        createdAt: timeAgo(res.data.createdAt),
        thumbnailUrl: res.data.thumbnailUrl || "",
        channelAvatar: res.data.channelAvatar || "",
        previewUrl: res.data.previewUrl || res.data.thumbnailUrl || "",
        comments: res.data.comments || [],
    }));

export const uploadVideo = (
    file: File,
    options?: { title?: string; description?: string; thumbnail?: File; isPublic?: boolean; }
): Promise<string> => {
    const formData = new FormData();
    formData.append("uploaded_files", file);

    if (options?.thumbnail) formData.append("thumbnail", options.thumbnail);
    if (options?.title) formData.append("title", options.title);
    if (options?.description) formData.append("description", options.description);
    if (options?.isPublic !== undefined) formData.append("isPublic", String(options.isPublic));

    return clientApi
        .post("/files/upload", formData, { headers: { "Content-Type": "multipart/form-data" } })
        .then(res => {
            const file = res.data?.files?.[0]?.filename;
            const base = (clientApi.defaults.baseURL || "").replace(/\/api\/?$/, "");
            return `${base}/uploads/${file}`;
        });
};

export const addVideo = (data: {
    title: string;
    description?: string;
    videoUrl: string;
    thumbnailUrl?: string;
    isPublic: boolean;
}): Promise<Video> => clientApi.post("/videos", data).then(res => res.data);

export const deleteVideo = (id: string): Promise<void> =>
    clientApi.delete(`/videos/${id}`).then(() => { });

export const updateVideo = (id: string, data: {
    title?: string;
    description?: string;
    thumbnailUrl?: string;
    isPublic?: boolean;
}): Promise<Video> =>
    clientApi.put(`/videos/${id}`, data).then(res => res.data);

export const generateThumbnail = (videoId: string): Promise<string> =>
    clientApi.post(`/videos/${videoId}/generate-thumbnail`)
        .then(res => res.data.thumbnailUrl);

export const getThumbnail = (videoId: string): Promise<string> =>
    clientApi.get(`/videos/${videoId}/thumbnail`)
        .then(res => res.data.thumbnailUrl);

export const checkVideoStatus = (videoId: string): Promise<string> =>
    clientApi.get(`/videos/${videoId}/status`)
        .then(res => res.data.status);

export default {
    getVideos,
    getVideo,
    addVideo,
    uploadVideo,
    updateVideo,
    deleteVideo,
    generateThumbnail,
    getThumbnail,
    checkVideoStatus,
};
