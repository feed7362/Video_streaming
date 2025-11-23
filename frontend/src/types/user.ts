export interface ChangelogEntry {
    date: string;
    version: string;
    improvements?: string[];
    bugfixes?: string[];
    newFeatures?: string[];
    imageUrl?: string;
    tags?: string[];
}

export interface UserInfo {
    id: string;
    username: string;
    status: "active" | "banned" | "deleted";
    email?: string;
    createdAt: string;
    roleId: number;
    hashedPassword?: string;
}