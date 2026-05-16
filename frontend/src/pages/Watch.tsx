import React, { useState, useEffect, useCallback } from "react";
import VideoPlayer from "@/components/VideoPlayer";
import VideoCard from "@/components/VideoCard";
import { Button } from "@/components/ui/button";
import InfiniteScroll from "@/components/infinite-scroll";
import { Link, useSearchParams } from "react-router-dom";
import { ThumbsUp, ThumbsDown, Download, Share2, ChevronDown, ChevronUp } from "lucide-react";

import { useFetchCategories } from "@/hooks/useCategories";
import { useVideo } from "@/hooks/useVideos";
import { useReactions } from "@/hooks/useReactions";
import { useDownload } from "@/hooks/useDownload";
import { useAuth } from "@/contexts/AuthContext";
import { useSidebar } from "@/components/ui/sidebar";
import { getComments, addComment, deleteComment, addReply, reactToComment } from "@api/commentApi";
import type { VideoDetail, VideoComment, VideoPreviewWithTime } from "@api/types";
import { timeAgo } from "@/utils/timeAgo";

function Avatar({ src, name, size }: { src?: string; name?: string; size: number }) {
    const initial = (name ?? "?").charAt(0).toUpperCase();
    if (src) return <img src={src} alt={name} width={size} height={size} className="rounded-full object-cover shrink-0" style={{ width: size, height: size }} />;
    return (
        <div className="rounded-full bg-muted flex items-center justify-center shrink-0 text-sm font-semibold text-muted-foreground" style={{ width: size, height: size }}>
            {initial}
        </div>
    );
}

interface ApiCommentRaw {
    id: string | number;
    user_id?: string;
    userId?: string;
    content: string;
    created_at?: string;
    createdAt?: string;
    likes_count?: number;
    likesCount?: number;
    dislikes_count?: number;
    dislikesCount?: number;
    user_name?: string;
    user_avatar?: string;
    replies?: ApiCommentRaw[];
}

function formatCount(n: number) {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return String(n);
}

export default function Watch() {
    const [searchParams] = useSearchParams();
    const videoId = searchParams.get("v") ?? "";

    const { categories, active, setActive } = useFetchCategories();
    const { user } = useAuth();
    const { setOpen } = useSidebar();

    // Collapse the nav sidebar on the watch page (YouTube-style)
    useEffect(() => {
        setOpen(false);
    }, [setOpen]);

    const { video, videos, error, loading, hasMore, loadMore, metaDataText, setVideo } = useVideo();

    const [comments, setComments] = useState<VideoComment[]>([]);
    const [commentText, setCommentText] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [replyingTo, setReplyingTo] = useState<string | null>(null);
    const [replyText, setReplyText] = useState("");
    const [replySubmitting, setReplySubmitting] = useState(false);
    const [showDesc, setShowDesc] = useState(false);
    const [resolution, setResolution] = useState("720p");

    const fromApi = useCallback(
        (c: ApiCommentRaw): VideoComment => ({
            id: String(c.id),
            userId: String(c.user_id ?? c.userId ?? ""),
            content: c.content,
            createdAt: c.created_at ?? c.createdAt ?? "",
            videoId,
            likesCount: c.likes_count ?? c.likesCount ?? 0,
            dislikesCount: c.dislikes_count ?? c.dislikesCount ?? 0,
            user_name: c.user_name,
            user_avatar: c.user_avatar,
            ...(Array.isArray(c.replies) ? { replies: c.replies.map(fromApi) } : {}),
        }),
        [videoId],
    );

    useEffect(() => {
        if (!videoId) return;
        setComments([]);
        getComments(videoId, 1, 100)
            .then((page) => setComments((page.items as unknown as ApiCommentRaw[]).map(fromApi)))
            .catch(() => {});
    }, [videoId, fromApi]);

    const handleAddComment = async (e: React.FormEvent) => {
        e.preventDefault();
        const text = commentText.trim();
        if (!text || !videoId) return;
        setSubmitting(true);
        try {
            const c = await addComment(videoId, text);
            setComments((prev) => [{ ...fromApi(c), replies: [] }, ...prev]);
            setCommentText("");
        } finally { setSubmitting(false); }
    };

    const handleAddReply = async (e: React.FormEvent, parentId: string) => {
        e.preventDefault();
        const text = replyText.trim();
        if (!text || !videoId) return;
        setReplySubmitting(true);
        try {
            const r = await addReply(videoId, parentId, text);
            setComments((prev) => prev.map((c) =>
                c.id === parentId ? { ...c, replies: [...(c.replies ?? []), fromApi(r)] } : c
            ));
            setReplyText(""); setReplyingTo(null);
        } finally { setReplySubmitting(false); }
    };

    const handleDeleteComment = async (commentId: string, parentId?: string) => {
        try {
            await deleteComment(commentId);
            if (parentId) {
                setComments((prev) => prev.map((c) =>
                    c.id === parentId ? { ...c, replies: (c.replies ?? []).filter((r) => r.id !== commentId) } : c
                ));
            } else {
                setComments((prev) => prev.filter((c) => c.id !== commentId));
            }
        } catch { /* ignore */ }
    };

    const handleCommentReaction = async (commentId: string, reaction: "like" | "dislike", parentId?: string) => {
        try {
            const data = await reactToComment(commentId, reaction);
            const likes = data.reactions["like"] ?? 0;
            const dislikes = data.reactions["dislike"] ?? 0;
            const update = (c: VideoComment) => c.id === commentId ? { ...c, likesCount: likes, dislikesCount: dislikes } : c;
            if (parentId) {
                setComments((prev) => prev.map((c) => c.id === parentId ? { ...c, replies: (c.replies ?? []).map(update) } : c));
            } else {
                setComments((prev) => prev.map(update));
            }
        } catch { /* ignore */ }
    };

    const { handleDownload } = useDownload({ video: video as unknown as VideoDetail, resolution });
    const { handleReaction } = useReactions({
        initialVideo: video as unknown as VideoDetail,
        initialUserReaction: null,
        onVideoUpdate: (v: VideoDetail) => setVideo?.(v),
    });

    if (error) return <p className="text-red-500 p-6">{error}</p>;
    if (loading || !video) return (
        <div className="flex flex-col lg:flex-row gap-6 p-4 animate-pulse">
            <div className="w-full lg:w-2/3 space-y-4">
                <div className="aspect-video rounded-xl bg-muted" />
                <div className="h-6 bg-muted rounded w-3/4" />
                <div className="h-4 bg-muted rounded w-1/2" />
            </div>
            <div className="w-full lg:w-[360px] space-y-4">
                {Array.from({ length: 5 }).map((_, i) => <div key={i} className="flex gap-2"><div className="rounded-xl bg-muted shrink-0" style={{ width: 168, height: 94 }} /><div className="flex-1 space-y-2 pt-1"><div className="h-3 bg-muted rounded" /><div className="h-3 bg-muted rounded w-2/3" /></div></div>)}
            </div>
        </div>
    );

    return (
        <div className="flex flex-col lg:flex-row gap-6 p-4">
            {/* ── Main column ────────────────────────────────── */}
            <div className="w-full lg:flex-1 min-w-0">
                {/* Player */}
                <div className="rounded-xl overflow-hidden bg-black">
                    <VideoPlayer src={video.hlsUrl} />
                </div>

                {/* Title */}
                <h1 className="mt-3 text-lg sm:text-xl font-bold leading-snug">{video.title}</h1>

                {/* Channel row + actions */}
                <div className="flex flex-wrap items-center justify-between gap-3 mt-3">
                    {/* Channel */}
                    <div className="flex items-center gap-3">
                        <Avatar src={video.channel_avatar} name={video.channel} size={40} />
                        <div>
                            <p className="font-semibold text-sm leading-tight">{video.channel}</p>
                            <p className="text-xs text-muted-foreground">{metaDataText}</p>
                        </div>
                    </div>

                    {/* Reactions + Download */}
                    <div className="flex items-center gap-2 flex-wrap">
                        {/* Like / Dislike pill */}
                        <div className="flex items-center rounded-full bg-muted overflow-hidden divide-x divide-border">
                            <button
                                onClick={() => handleReaction("like")}
                                className="flex items-center gap-1.5 px-4 py-2 hover:bg-muted/70 transition-colors text-sm font-medium"
                            >
                                <ThumbsUp className="h-4 w-4" />
                                <span>{formatCount(video.likesCount ?? 0)}</span>
                            </button>
                            <button
                                onClick={() => handleReaction("dislike")}
                                className="flex items-center gap-1.5 px-4 py-2 hover:bg-muted/70 transition-colors text-sm font-medium"
                            >
                                <ThumbsDown className="h-4 w-4" />
                                <span>{formatCount(video.dislikesCount ?? 0)}</span>
                            </button>
                        </div>

                        {/* Share */}
                        <button className="flex items-center gap-1.5 rounded-full bg-muted px-4 py-2 text-sm font-medium hover:bg-muted/70 transition-colors">
                            <Share2 className="h-4 w-4" />
                            Share
                        </button>

                        {/* Download */}
                        <div className="flex items-center gap-1 rounded-full bg-muted overflow-hidden">
                            <button
                                onClick={() => handleDownload()}
                                className="flex items-center gap-1.5 px-4 py-2 hover:bg-muted/70 transition-colors text-sm font-medium"
                            >
                                <Download className="h-4 w-4" />
                                Download
                            </button>
                            <select
                                value={resolution}
                                onChange={(e) => setResolution(e.target.value)}
                                className="bg-transparent pr-2 py-2 text-sm focus:outline-none cursor-pointer"
                            >
                                {["360p", "720p", "1080p"].map((r) => <option key={r} value={r}>{r}</option>)}
                            </select>
                        </div>
                    </div>
                </div>

                {/* Description box */}
                <div
                    className="mt-3 rounded-xl bg-muted/50 hover:bg-muted/70 transition-colors p-3 cursor-pointer"
                    onClick={() => setShowDesc((v) => !v)}
                >
                    <p className={`text-sm ${showDesc ? "" : "line-clamp-2"} whitespace-pre-wrap`}>
                        {video.description || "No description."}
                    </p>
                    <button className="flex items-center gap-1 text-xs font-medium mt-1 text-muted-foreground">
                        {showDesc ? <><ChevronUp className="h-3 w-3" />Show less</> : <><ChevronDown className="h-3 w-3" />Show more</>}
                    </button>
                </div>

                {/* Comments */}
                <div className="mt-6">
                    <h2 className="font-semibold text-base mb-4">{comments.length} Comments</h2>

                    {user ? (
                        <form onSubmit={handleAddComment} className="flex gap-3 mb-6">
                            <Avatar name={user.username} size={36} />
                            <div className="flex-1">
                                <input
                                    value={commentText}
                                    onChange={(e) => setCommentText(e.target.value)}
                                    placeholder="Add a comment…"
                                    className="w-full border-b border-border bg-transparent pb-1 text-sm focus:outline-none focus:border-foreground transition-colors placeholder:text-muted-foreground"
                                />
                                {commentText && (
                                    <div className="flex justify-end gap-2 mt-2">
                                        <Button type="button" variant="ghost" size="sm" className="rounded-full" onClick={() => setCommentText("")}>Cancel</Button>
                                        <Button type="submit" size="sm" className="rounded-full" disabled={submitting || !commentText.trim()}>
                                            {submitting ? "Posting…" : "Comment"}
                                        </Button>
                                    </div>
                                )}
                            </div>
                        </form>
                    ) : (
                        <p className="text-sm text-muted-foreground mb-4">
                            <Link to="/login" className="text-blue-500 hover:underline">Sign in</Link> to leave a comment.
                        </p>
                    )}

                    <div className="space-y-4">
                        {comments.map((comment) => {
                            const replies = comment.replies ?? [];
                            const displayName = comment.user_name || comment.userId;
                            const isOwn = user && user.id === comment.userId;

                            return (
                                <div key={comment.id} className="flex gap-3">
                                    <Avatar src={comment.user_avatar} name={displayName} size={36} />
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-0.5">
                                            <span className="text-sm font-semibold">{displayName}</span>
                                            <span className="text-xs text-muted-foreground">{timeAgo(comment.createdAt)}</span>
                                        </div>
                                        <p className="text-sm">{comment.content}</p>
                                        <div className="flex items-center gap-3 mt-1">
                                            <button onClick={() => handleCommentReaction(comment.id, "like")} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
                                                <ThumbsUp className="h-3.5 w-3.5" /><span>{comment.likesCount}</span>
                                            </button>
                                            <button onClick={() => handleCommentReaction(comment.id, "dislike")} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
                                                <ThumbsDown className="h-3.5 w-3.5" /><span>{comment.dislikesCount}</span>
                                            </button>
                                            {user && (
                                                <button onClick={() => { setReplyingTo(replyingTo === comment.id ? null : comment.id); setReplyText(""); }} className="text-xs font-medium text-muted-foreground hover:text-foreground transition-colors">
                                                    Reply
                                                </button>
                                            )}
                                            {isOwn && (
                                                <button onClick={() => handleDeleteComment(comment.id)} className="text-xs text-red-400 hover:text-red-600 transition-colors">Delete</button>
                                            )}
                                        </div>

                                        {/* Reply form */}
                                        {replyingTo === comment.id && (
                                            <form onSubmit={(e) => handleAddReply(e, comment.id)} className="flex gap-2 mt-3">
                                                <Avatar name={user?.username} size={28} />
                                                <div className="flex-1">
                                                    <input
                                                        value={replyText}
                                                        onChange={(e) => setReplyText(e.target.value)}
                                                        placeholder={`Reply to ${displayName}…`}
                                                        className="w-full border-b border-border bg-transparent pb-1 text-sm focus:outline-none focus:border-foreground transition-colors placeholder:text-muted-foreground"
                                                    />
                                                    <div className="flex justify-end gap-2 mt-2">
                                                        <Button type="button" variant="ghost" size="sm" className="rounded-full" onClick={() => setReplyingTo(null)}>Cancel</Button>
                                                        <Button type="submit" size="sm" className="rounded-full" disabled={replySubmitting || !replyText.trim()}>
                                                            {replySubmitting ? "…" : "Reply"}
                                                        </Button>
                                                    </div>
                                                </div>
                                            </form>
                                        )}

                                        {/* Nested replies */}
                                        {replies.length > 0 && (
                                            <div className="mt-3 space-y-3">
                                                {replies.map((reply) => {
                                                    const rName = reply.user_name || reply.userId;
                                                    const rIsOwn = user && user.id === reply.userId;
                                                    return (
                                                        <div key={reply.id} className="flex gap-2 pl-2">
                                                            <Avatar src={reply.user_avatar} name={rName} size={28} />
                                                            <div className="flex-1 min-w-0">
                                                                <div className="flex items-center gap-2 mb-0.5">
                                                                    <span className="text-xs font-semibold">{rName}</span>
                                                                    <span className="text-xs text-muted-foreground">{timeAgo(reply.createdAt)}</span>
                                                                </div>
                                                                <p className="text-sm">{reply.content}</p>
                                                                <div className="flex items-center gap-3 mt-1">
                                                                    <button onClick={() => handleCommentReaction(reply.id, "like", comment.id)} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
                                                                        <ThumbsUp className="h-3 w-3" /><span>{reply.likesCount}</span>
                                                                    </button>
                                                                    <button onClick={() => handleCommentReaction(reply.id, "dislike", comment.id)} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
                                                                        <ThumbsDown className="h-3 w-3" /><span>{reply.dislikesCount}</span>
                                                                    </button>
                                                                    {rIsOwn && (
                                                                        <button onClick={() => handleDeleteComment(reply.id, comment.id)} className="text-xs text-red-400 hover:text-red-600 transition-colors">Delete</button>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                        {comments.length === 0 && <p className="text-sm text-muted-foreground">No comments yet. Be the first!</p>}
                    </div>
                </div>
            </div>

            {/* ── Sidebar ─────────────────────────────────────── */}
            <div className="w-full lg:w-[360px] xl:w-[400px] shrink-0">
                {/* Category pills */}
                <div className="flex gap-2 overflow-x-auto no-scrollbar pb-3 mb-3">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setActive(cat)}
                            className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition-colors shrink-0
                                ${active === cat ? "bg-foreground text-background" : "bg-muted hover:bg-muted/80"}`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>

                <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                    <div className="space-y-3">
                        {videos.map((v: VideoPreviewWithTime) => (
                            <Link key={v.id} to={`/watch?v=${v.id}`}>
                                <VideoCard
                                    id={v.id}
                                    title={v.title}
                                    thumbnail={v.previewUrl || v.thumbnail_url}
                                    channel_avatar={v.channel_avatar}
                                    channel_name={v.channel_name}
                                    views={v.views}
                                    timeAgo={v.timeAgo}
                                    horizontal
                                />
                            </Link>
                        ))}
                        {loading && Array.from({ length: 5 }).map((_, i) => <VideoCard key={i} loading horizontal />)}
                    </div>
                </InfiniteScroll>
            </div>
        </div>
    );
}
