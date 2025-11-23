export interface UploadedFile {
    file_id: string;
    filename: string;
    size: number;
}

export interface UploadResponse {
    status: string;
    files?: UploadedFile[];
    message?: string;
}
