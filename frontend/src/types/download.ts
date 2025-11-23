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
