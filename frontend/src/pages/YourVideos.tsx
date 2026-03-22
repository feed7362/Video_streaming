import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Eye, ThumbsUp, MessageSquare, MoreVertical, Search } from "lucide-react";
import { timeAgo } from "@/utils/timeAgo";
import videoApi from "@api/videoApi";
import type { VideoPreview } from "@api/types";

type StatusFilter = "all" | "public" | "private" | "processing";

const STATUS_LABEL: Record<string, { label: string; color: string }> = {
    Ready:      { label: "Published",  color: "text-green-500" },
    Processing: { label: "Processing", color: "text-yellow-500" },
    Failed:     { label: "Failed",     color: "text-red-500" },
    Queued:     { label: "Processing", color: "text-yellow-500" },
};

export default function YourVideos() {
    const [videos, setVideos] = useState<VideoPreview[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<StatusFilter>("all");
    const [search, setSearch] = useState("");

    useEffect(() => {
        videoApi.getVideos({ page: 1, size: 50 })
            .then(setVideos)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const filtered = videos.filter((v) => {
        const matchSearch = v.title?.toLowerCase().includes(search.toLowerCase()) ?? true;
        const matchFilter =
            filter === "all" ? true
            : filter === "public" ? v.privacy?.toLowerCase() === "public"
            : filter === "private" ? v.privacy?.toLowerCase() === "private"
            : filter === "processing" ? false
            : true;
        return matchSearch && matchFilter;
    });

    const tabs: { key: StatusFilter; label: string }[] = [
        { key: "all", label: "All" },
        { key: "public", label: "Public" },
        { key: "private", label: "Private" },
        { key: "processing", label: "Processing" },
    ];

    return (
        <div className="px-4 py-6">
            <h1 className="text-2xl font-bold mb-6">Your videos</h1>

            {/* Tabs */}
            <div className="flex gap-1 mb-4 border-b border-border">
                {tabs.map((t) => (
                    <button
                        key={t.key}
                        onClick={() => setFilter(t.key)}
                        className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
                            filter === t.key
                                ? "border-foreground text-foreground"
                                : "border-transparent text-muted-foreground hover:text-foreground"
                        }`}
                    >
                        {t.label}
                    </button>
                ))}
            </div>

            {/* Search */}
            <div className="relative mb-4 max-w-sm">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search your videos"
                    className="w-full pl-9 pr-4 py-2 text-sm rounded-md border border-border bg-background focus:outline-none focus:ring-1 focus:ring-ring"
                />
            </div>

            {/* Table */}
            {loading ? (
                <div className="space-y-3">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="flex gap-4 animate-pulse">
                            <div className="rounded-xl bg-muted shrink-0" style={{ width: 160, height: 90 }} />
                            <div className="flex-1 space-y-2 pt-2">
                                <div className="h-4 bg-muted rounded w-1/2" />
                                <div className="h-3 bg-muted rounded w-1/4" />
                            </div>
                        </div>
                    ))}
                </div>
            ) : filtered.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-24 text-center">
                    <h2 className="text-lg font-semibold mb-1">No videos found</h2>
                    <p className="text-sm text-muted-foreground">
                        {search ? "Try a different search term." : "Upload a video to get started."}
                    </p>
                </div>
            ) : (
                <div className="divide-y divide-border">
                    {filtered.map((v) => {
                        const statusKey = (v as any).status ?? "Ready";
                        const status = STATUS_LABEL[statusKey] ?? { label: statusKey, color: "text-muted-foreground" };
                        return (
                            <div key={v.id} className="flex gap-4 py-3 group">
                                {/* Thumbnail */}
                                <Link to={`/watch?v=${v.id}`} className="shrink-0">
                                    <div className="relative rounded-xl overflow-hidden bg-muted" style={{ width: 160, height: 90 }}>
                                        <img
                                            src={v.thumbnail_url || v.previewUrl || ""}
                                            alt={v.title}
                                            className="w-full h-full object-cover"
                                            loading="lazy"
                                        />
                                    </div>
                                </Link>

                                {/* Info */}
                                <div className="flex-1 min-w-0">
                                    <Link to={`/watch?v=${v.id}`}>
                                        <h3 className="font-semibold text-sm line-clamp-2 hover:underline leading-snug">
                                            {v.title || v.name}
                                        </h3>
                                    </Link>
                                    <p className={`text-xs mt-0.5 font-medium ${status.color}`}>{status.label}</p>
                                    <p className="text-xs text-muted-foreground mt-0.5">
                                        {v.createdAt ? timeAgo(v.createdAt) : ""}
                                    </p>
                                </div>

                                {/* Stats */}
                                <div className="hidden md:flex items-center gap-6 text-sm text-muted-foreground shrink-0">
                                    <div className="flex items-center gap-1.5 w-20">
                                        <Eye className="h-4 w-4" />
                                        <span>{(v.views ?? 0).toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5 w-20">
                                        <ThumbsUp className="h-4 w-4" />
                                        <span>{(v.likesCount ?? 0).toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5 w-20">
                                        <MessageSquare className="h-4 w-4" />
                                        <span>{((v as any).commentCount ?? 0).toLocaleString()}</span>
                                    </div>
                                </div>

                                {/* Menu */}
                                <button className="shrink-0 p-1.5 rounded-full hover:bg-muted transition-colors opacity-0 group-hover:opacity-100">
                                    <MoreVertical className="h-4 w-4 text-muted-foreground" />
                                </button>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
