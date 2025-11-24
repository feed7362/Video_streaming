import type { VideoDetail } from "./video";
export interface DownloadVideo {
    file_id: string;
    filename: string;
    size: number;
}

export interface DownloadResponse {
    status: string;
    files: DownloadVideo[];
    message?: string;
}

export interface UseDownloadProps {
    video: VideoDetail | null;
    resolution: string;
}