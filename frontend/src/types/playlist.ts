export interface Playlist {
    id: string;
    title: string;
    description?: string;
    createdAt: string;
    updatedAt?: string;
    videoIds: string[];
    isPublic: boolean;
}

export interface PlaylistPreview {
    id: string;
    title: string;
    videoCount: number;
    createdAt: string;
    isPublic: boolean;
}
