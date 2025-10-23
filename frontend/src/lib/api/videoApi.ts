import axios from "axios";

const api = axios.create({
    baseURL: "http://localhost/api",
});

// Тип для відео 
export interface Video {
    id: string;
    title: string;
    thumbnail: string;
    channel_avatar: string;
    channel_name: string;
    description?: string;
}

export const getVideos = async (page: number = 0): Promise<Video[]> => {
    try {
        const response = await api.get<Video[]>(`/videos?page=${page}`);
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

export const getVideo = async (id: string): Promise<Video> => {
    try {
        const response = await api.get<Video>(`/videos/${id}`);
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

export const addVideo = async (data: Video): Promise<Video> => {
    try {
        const response = await api.post<Video>("/videos", data);
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

const apis = {
    getVideos,
    getVideo,
    addVideo,
};

export default apis;
