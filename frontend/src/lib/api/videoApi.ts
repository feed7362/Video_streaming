import clientApi from "./clientApi";
import { timeAgo } from "@/utils/timeAgo";
import type {
  Video,
  VideoPreview,
  UploadResponse,
  DownloadResponse,
} from "./types";

interface VideosResponse {
  items: VideoPreview[];
  page: number;
  size: number;
  total: number;
}

export const mapToPreview = (data: any): VideoPreview => ({
  id: data.id,
  previewUrl: data.thumbnail || "/placeholder.jpg",
  title: data.title || "Untitled",
  name: data.title || "Untitled",
  createdAt: data.created_at || new Date().toISOString(),
  publishedAt: data.created_at || new Date().toISOString(),
  channel: data.channel_name || "Unknown Channel",
  channel_name: data.channel_name || "Unknown Channel",
  channel_avatar: data.channel_avatar || "",
  views: data.views_count ?? 0,
  likesCount: data.likes_count ?? 0,
  dislikesCount: data.dislikes_count ?? 0,
  privacy: data.privacy === "public" ? "Public" : "Private",
});

export const mapToDetail = (data: any): Video => ({
  ...data,
  preview_url: data.thumbnail_url || "/placeholder.jpg",
  master_hls_url: data.master_hls_url || "",
  created_at: data.created_at || "",
  timeAgo: timeAgo(data.created_at || new Date().toISOString()),
  channel_avatar: data.avatar_url || "",
  comments: data.comments || [],
  likes_count: data.likes_count ?? 0,
  dislikes_count: data.dislikes_count ?? 0,
  views_count: data.views_count ?? 0,
  channel_name: data.channel_name || "Unknown Channel",
  title: data.name || "Untitled",
  privacy: data.privacy === "public" ? "Public" : "Private",
});

export const getVideos = async ({
  page = 1,
  size = 10,
  channel_name,
}: {
  page?: number;
  size?: number;
  channel_name?: string;
}): Promise<VideoPreview[]> => {
  const res = await clientApi.get<VideosResponse>("/api/videos/", {
    params: { page, size, channel_name },
  });
  return (res.data.items || []).map(mapToPreview);
};

export const getVideo = async (id: string): Promise<Video> => {
  const res = await clientApi.get<any>(`/api/videos/${id}`);
  return mapToDetail(res.data);
};

export const getVideoPreviewsByCategory = async (
  category: string,
  page = 1,
  size = 10,
): Promise<VideoPreview[]> => {
  const res = await clientApi.get<VideosResponse>(
    `/api/videos/categories/${category}`,
    { params: { page, size } },
  );
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
  const formData = new FormData();
  formData.append("video", file);
  if (options?.thumbnail) formData.append("thumbnail", options.thumbnail);
  // Backend schema uses Form(...) — these must be in the multipart body, not the query.
  // See backend/src/schemas/video.py:VideoUploadParams.
  formData.append("name", (options?.title || file.name || "Untitled").trim());
  formData.append("description", options?.description?.trim() || "");
  formData.append("privacy", options?.isPublic ? "public" : "private");
  formData.append("category", options?.category || "entertainment");

  // Let the browser set Content-Type (including multipart boundary).
  const res = await clientApi.post<UploadResponse>(
    `/api/files/videos`,
    formData,
  );
  return res.data;
};

export const deleteVideo = async (id: string): Promise<void> => {
  await clientApi.delete(`/api/files`, {
    params: { video_id: id },
  });
};

export const updateVideoPrivacy = async (
  id: string,
  isPublic: boolean,
): Promise<any> => {
  const res = await clientApi.patch(`/api/videos/${id}/privacy`, null, {
    params: { updated_privacy: isPublic ? "public" : "private" },
  });
  return res.data;
};

export const getVideoDownloadInfo = async (
  videoId: string,
): Promise<DownloadResponse> => {
  const res = await clientApi.get<DownloadResponse>(
    `/api/files/videos/${videoId}/download`,
  );
  return res.data;
};

export const downloadVideo = async (
  videoId: string,
  resolution = "720p",
): Promise<Blob> => {
  try {
    const res = await clientApi.get(`/api/files/videos/${videoId}/download`, {
      params: { resolution },
      responseType: "blob",
    });
    return res.data;
  } catch (err) {
    console.error("Download error:", err);
    return Promise.reject({ message: "Failed to download video" });
  }
};

export default {
  getVideos,
  getVideo,
  uploadVideo,
  updateVideoPrivacy,
  deleteVideo,
  downloadVideo,
  getVideoDownloadInfo,
  getVideoPreviewsByCategory,
  //generateThumbnail,
  //getThumbnail,
  //checkVideoStatus,
};
