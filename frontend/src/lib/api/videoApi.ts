import clientApi from "./clientApi";
import { timeAgo } from "@/utils/timeAgo";
import type {
  Video,
  VideoPreview,
} from "../../types/video";

import type {
    UploadResponse,
} from "../../types/upload";
import type {
    DownloadResponse,
} from "../../types/download";

interface VideosResponse {
  items: Video[];
  page: number;
  size: number;
  total: number;
}

export const mapToPreview = (video: Video): VideoPreview => ({
    id: video.id,
    previewUrl: video.thumbnail_url || "/placeholder.jpg",
    title: video.name || video.title || "Untitled",
    name: video.name || video.title || "Untitled",
    createdAt: video.created_at || new Date().toISOString(),
    publishedAt: video.publishedAt || video.created_at || new Date().toISOString(),
    channel: video.channel_name || "Unknown Channel",
    channel_avatar: video.avatar_url || "",
    views: video.views_count ?? 0,
    likesCount: video.likes_count ?? 0,
    dislikesCount: video.dislikes_count ?? 0,
    privacy: video.privacy === "public" ? "Public" : "Private",
});

export const mapToDetail = (video: Video): Video => ({
  ...video,
  preview_url: video.thumbnail_url || video.preview_url || "/placeholder.jpg",
  master_hls_url: video.master_hls_url || "",
  created_at: video.created_at || "",
  timeAgo: timeAgo(video.created_at || new Date().toISOString()),
  channel_avatar: video.avatar_url || video.channel_avatar || "",
  comments: video.comments || [],
  likes_count: video.likes_count ?? 0,
  dislikes_count: video.dislikes_count ?? 0,
  views_count: video.views_count ?? 0,
  channel_name: video.channel_name || "Unknown Channel",
  title: video.name || video.title || "Untitled",
  privacy: video.privacy === "public" ? "Public" : "Private",
});

export const getVideos = async ({
  page = 1,
  size = 9,
  category,
  channel_name,
}: {
  page?: number;
  size?: number;
  category?: string;
  channel_name?: string;
}): Promise<VideoPreview[]> => {
  console.log("Fetching videos with params:", {
    page,
    size,
    category,
    channel_name,
  });

  const res = await clientApi.get<VideosResponse>("/api/video/get_videos", {
    params: { page, size, category, channel_name },
  });

  console.log("getVideos API response:", res.data);

  return (res.data.items || []).map(mapToPreview);
};

export const getVideo = async (id: string): Promise<Video> => {
  const res = await clientApi.get<Video>(`/api/video/info/${id}`);
  console.log(res.data.thumbnail_url);
  return {
    ...res.data,
    timeAgo: timeAgo(res.data.created_at),
    thumbnail_url: res.data.thumbnail_url || "",
    channel_avatar: res.data.channel_avatar || "",
    master_hls_url: res.data.master_hls_url || "",
    preview_url: res.data.preview_url || res.data.thumbnail_url || "",
    comments: res.data.comments || [],
  };
};

export const getVideoPreviewsByCategory = async (
  category: string,
  page = 1,
  size = 9,
): Promise<VideoPreview[]> => {
  const res = await clientApi.get<VideosResponse>("/api/video/get_videos", {
    params: { category, page, size },
  });
  return (res.data.items || []).map(mapToPreview);
};

export const uploadVideo = async (
  file: File,
  options?: {
    title?: string;
    description?: string;
    thumbnail?: File;
    isPublic?: boolean;
    category?: string;
  },
): Promise<UploadResponse> => {
  try {
    const formData = new FormData();
    formData.append("video", file);
    if (options?.thumbnail) formData.append("thumbnail", options.thumbnail);

    const params = new URLSearchParams({
      name: options?.title || "",
      description: options?.description || "",
      privacy: options?.isPublic ? "public" : "private",
      category: options?.category || "general",
    });

    const res = await clientApi.post<UploadResponse>(
      `/files/upload_video?${params}`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } },
    );

    return res.data;
  } catch (err: unknown) {
    if (typeof err === "object" && err && "response" in err) {
      const axiosError = err as { response?: { data?: unknown } };
      return Promise.reject(axiosError.response?.data);
    }

    return Promise.reject({ message: "Upload failed" });
  }
};

export const addVideo = async (data: {
  title: string;
  description?: string;
  videoUrl: string;
  thumbnailUrl?: string;
  isPublic: boolean;
}): Promise<Video> => clientApi.post("/videos", data).then((res) => res.data);

export const deleteVideo = async (id: string): Promise<void> =>
  clientApi.delete(`/api/files/delete_video/${id}`).then(() => {});

export const updateVideo = async (
  id: string,
  data: {
    title?: string;
    description?: string;
    thumbnailUrl?: string;
    isPublic?: boolean;
  },
): Promise<Video> =>
  clientApi.put(`/videos/${id}`, data).then((res) => res.data);

//export const generateThumbnail = async (videoId: string): Promise<string> =>
//    clientApi.post(`/videos/${videoId}/generate-thumbnail`)
//        .then(res => res.data.thumbnailUrl);

//export const getThumbnail = async (videoId: string): Promise<string> =>
//    clientApi.get(`/videos/${videoId}/thumbnail`)
//        .then(res => res.data.thumbnailUrl);

//export const checkVideoStatus = async (videoId: string): Promise<string> =>
//    clientApi.get(`/videos/${videoId}/status`)
//        .then(res => res.data.status);

export const getVideoDownloadInfo = async (
  videoId: string,
): Promise<DownloadResponse> => {
  const res = await clientApi.get<DownloadResponse>(
    `/api/files/download_video/${videoId}`,
  );
  return res.data;
};

export const downloadVideo = async (
  videoId: string,
  resolution = "720p",
): Promise<Blob> => {
  try {
    const res = await clientApi.get(`/api/files/download_video`, {
      params: { video_id: videoId, resolution },
      responseType: "blob",
    });
    return res.data;
  } catch (err) {
    console.error("Download error:", err);
    return Promise.reject({ message: "Failed to download video" });
  }
};

//для використання в іншому файлі
//const handleDownload = async () => {
//    try {
//        const blob = await downloadVideo(videoId);
//        const url = window.URL.createObjectURL(blob);
//        const a = document.createElement("a");
//        a.href = url;
//        a.download = `video_${videoId}.mp4`; // or use filename from API
//        a.click();
//    } catch (e) {
//        toast({ title: "Download failed", variant: "destructive" });
//    }
//};

export default {
  getVideos,
  getVideo,
  uploadVideo,
  addVideo,
  updateVideo,
  deleteVideo,
  downloadVideo,
  getVideoDownloadInfo,
  getVideoPreviewsByCategory,
  //generateThumbnail,
  //getThumbnail,
  //checkVideoStatus,
};
