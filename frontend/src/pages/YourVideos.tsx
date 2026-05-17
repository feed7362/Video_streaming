import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Eye, ThumbsUp, MessageSquare, MoreVertical, Search, Trash2, Lock, Globe } from "lucide-react";
import { toast } from "sonner";
import { timeAgo } from "@/utils/timeAgo";
import { Button } from "@/components/ui/button";
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
    const [selected, setSelected] = useState<Set<string>>(new Set());
    const [bulkBusy, setBulkBusy] = useState(false);

    useEffect(() => {
        videoApi.getVideos({ page: 1, size: 50 })
            .then(setVideos)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const toggleOne = (id: string) =>
        setSelected((s) => {
            const next = new Set(s);
            next.has(id) ? next.delete(id) : next.add(id);
            return next;
        });

    const clearSelection = () => setSelected(new Set());

    const runBulk = async (
        label: string,
        action: (id: string) => Promise<unknown>,
        applyLocal: (succeededIds: Set<string>) => void,
    ) => {
        if (selected.size === 0) return;
        if (!confirm(`${label} ${selected.size} video(s)?`)) return;
        setBulkBusy(true);
        const ids = Array.from(selected);
        const results = await Promise.allSettled(ids.map(action));
        const succeeded = new Set(
            results.flatMap((r, i) => (r.status === "fulfilled" ? [ids[i]] : [])),
        );
        const failed = ids.length - succeeded.size;
        toast[failed ? "error" : "success"](
            `${label}: ${succeeded.size} succeeded${failed ? `, ${failed} failed` : ""}`,
        );
        applyLocal(succeeded);
        setBulkBusy(false);
        clearSelection();
    };

    const onBulkDelete = () =>
        runBulk(
            "Delete",
            (id) => videoApi.deleteVideo(id),
            (ok) => setVideos((vs) => vs.filter((v) => !ok.has(v.id))),
        );
    const onBulkMakePrivate = () =>
        runBulk(
            "Make private",
            (id) => videoApi.updateVideoPrivacy(id, false),
            (ok) =>
                setVideos((vs) =>
                    vs.map((v) => (ok.has(v.id) ? { ...v, privacy: "Private" } : v)),
                ),
        );
    const onBulkMakePublic = () =>
        runBulk(
            "Make public",
            (id) => videoApi.updateVideoPrivacy(id, true),
            (ok) =>
                setVideos((vs) =>
                    vs.map((v) => (ok.has(v.id) ? { ...v, privacy: "Public" } : v)),
                ),
        );

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

    const allFilteredIds = useMemo(() => filtered.map((v) => v.id), [filtered]);
    const allSelected =
        allFilteredIds.length > 0 && allFilteredIds.every((id) => selected.has(id));
    const toggleAll = () =>
        setSelected(allSelected ? new Set() : new Set(allFilteredIds));

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

            {/* Bulk action bar — shown when anything is selected */}
            {selected.size > 0 && (
                <div className="sticky top-0 z-10 mb-3 flex items-center gap-2 rounded-md border bg-background/90 backdrop-blur px-3 py-2 text-sm">
                    <span className="font-medium">{selected.size} selected</span>
                    <span className="flex-1" />
                    <Button size="sm" variant="outline" disabled={bulkBusy} onClick={onBulkMakePublic}>
                        <Globe className="h-3.5 w-3.5 mr-1" /> Make public
                    </Button>
                    <Button size="sm" variant="outline" disabled={bulkBusy} onClick={onBulkMakePrivate}>
                        <Lock className="h-3.5 w-3.5 mr-1" /> Make private
                    </Button>
                    <Button size="sm" variant="destructive" disabled={bulkBusy} onClick={onBulkDelete}>
                        <Trash2 className="h-3.5 w-3.5 mr-1" /> Delete
                    </Button>
                    <Button size="sm" variant="ghost" onClick={clearSelection}>Cancel</Button>
                </div>
            )}

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
                    {/* Select-all header */}
                    <div className="flex items-center gap-3 py-2 text-xs text-muted-foreground">
                        <input
                            type="checkbox"
                            checked={allSelected}
                            onChange={toggleAll}
                            className="h-4 w-4 cursor-pointer"
                            aria-label="Select all"
                        />
                        <span>{allSelected ? "Deselect all" : "Select all"}</span>
                    </div>
                    {filtered.map((v) => {
                        const statusKey = (v as any).status ?? "Ready";
                        const status = STATUS_LABEL[statusKey] ?? { label: statusKey, color: "text-muted-foreground" };
                        const isSelected = selected.has(v.id);
                        return (
                            <div
                                key={v.id}
                                className={`flex gap-4 py-3 group ${isSelected ? "bg-muted/30" : ""}`}
                            >
                                {/* Checkbox */}
                                <input
                                    type="checkbox"
                                    checked={isSelected}
                                    onChange={() => toggleOne(v.id)}
                                    className="self-center h-4 w-4 cursor-pointer shrink-0"
                                    aria-label={`Select ${v.title}`}
                                />

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
