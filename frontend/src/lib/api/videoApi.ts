import axios from "axios";
import { timeAgo } from "@/utils/timeAgo";

const api = axios.create({
    baseURL: "http://localhost/api",
});

export interface VideoComment {
    id: string;
    author: string;
    text: string;
}

export interface Video {
    id: string;
    title: string;
    thumbnailUrl?: string;
    previewUrl?: string;
    createdAt: string;
    channelName: string;
    channelAvatar?: string;
    viewsCount: number;
    isPublic: boolean;
    comments?: VideoComment[];
}

export interface VideoPreview {
    id: string;
    title: string;
    previewUrl?: string;
    createdAt: string;
    channel: string;
    views: number;
    channel_avatar?: string;
}

export const getVideos = async (page: number = 0): Promise<VideoPreview[]> => {
    try {
        const response = await api.get<Video[]>(`/videos?page=${page}`);
        return response.data
            .filter(video => video.isPublic)
            .map(video => ({
                id: video.id,
                title: video.title,
                previewUrl: video.thumbnailUrl || video.previewUrl || "",
                createdAt: timeAgo(video.createdAt),
                channel: video.channelName,
                views: video.viewsCount,
                channel_avatar: video.channelAvatar || "",
            }));
    } catch (error) {
        console.error("Error fetching videos:", error);
        throw error;
    }
};
//предпоказ назва дата створення (рахується типу 5 хв назад) канал к-сть переглядів тільки публічні відео

export const getVideo = async (id: string): Promise<Video> => {
    try {
        const response = await api.get<Video>(`/videos/${id}`);
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
};
//не повертає предпоказ

export const addVideo = async (data: Video): Promise<Video> => {
    try {
        const response = await api.post<Video>("/videos", data);
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

export const uploadVideo = async (
    file: File,
    options?: {
        title?: string;
        description?: string;
        thumbnail?: File;
        isPrivate?: boolean;
    }
): Promise<string> => {
    try {
        const formData = new FormData();
        formData.append("uploaded_files", file);
        if (options?.thumbnail) formData.append("thumbnail", options.thumbnail);
        if (options?.title) formData.append("title", options.title);
        if (options?.description) formData.append("description", options.description);
        if (options?.isPrivate !== undefined) formData.append("isPrivate", String(options.isPrivate));

        const response = await api.post("/files/upload", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });

        const uploadedFile = response.data.files[0];
        return `http://localhost/uploads/${uploadedFile.filename}`;
    } catch (error) {
        console.error("Error while uploading a video", error);
        throw error;
    }
};

export default { getVideos, getVideo, addVideo, uploadVideo };
//імя опис доступ 
