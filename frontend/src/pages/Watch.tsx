import React, { useState, useEffect } from "react";
import VideoPlayer from "@/components/VideoPlayer";
import VideoCard from "@/components/VideoCard";
import { Button } from "@/components/ui/button";
import InfiniteScroll from "@/components/infinite-scroll";
import { Link, useSearchParams } from "react-router-dom";

import { useFetchCategories } from "@/hooks/useCategories";
import { useVideo } from "@/hooks/useVideos";
import { useReactions } from "@/hooks/useReactions";
import { useDownload } from "@/hooks/useDownload";
import { useAuth } from "@/contexts/AuthContext";
import { getComments, addComment, deleteComment, addReply, reactToComment } from "@api/commentApi";
import type { VideoDetail, VideoComment, VideoPreviewWithTime } from "@api/types";
import { timeAgo } from "@/utils/timeAgo";

export default function Watch() {
    const [searchParams] = useSearchParams();
    const videoId = searchParams.get("v") ?? "";

    const { categories, active, setActive } = useFetchCategories();
    const { user } = useAuth();

    const {
        video,
        videos,
        error,
        loading,
        hasMore,
        loadMore,
        metaDataText,
        setVideo,
    } = useVideo();

    // Each entry is a top-level comment; replies are nested inside comment.replies
    const [comments, setComments] = useState<VideoComment[]>([]);
    const [commentText, setCommentText] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [commentError, setCommentError] = useState<string | null>(null);
    const [replyingTo, setReplyingTo] = useState<string | null>(null);
    const [replyText, setReplyText] = useState("");
    const [replySubmitting, setReplySubmitting] = useState(false);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const fromApi = (c: any): VideoComment => ({
        id: String(c.id),
        userId: String(c.user_id ?? c.userId ?? ""),
        content: c.content,
        createdAt: c.created_at ?? c.createdAt ?? "",
        videoId: videoId,
        likesCount: c.likes_count ?? c.likesCount ?? 0,
        dislikesCount: c.dislikes_count ?? c.dislikesCount ?? 0,
        user_name: c.user_name,
        user_avatar: c.user_avatar,
        // replies come nested from the API for top-level comments
        ...(Array.isArray(c.replies) ? { replies: c.replies.map(fromApi) } : {}),
    });

    useEffect(() => {
        if (!videoId) return;
        setComments([]);
        getComments(videoId, 1, 100)
            .then((page) => setComments(page.items.map(fromApi)))
            .catch(() => {/* non-critical */});
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [videoId]);

    const handleAddComment = async (e: React.FormEvent) => {
        e.preventDefault();
        const text = commentText.trim();
        if (!text || !videoId) return;
        setSubmitting(true);
        setCommentError(null);
        try {
            const newComment = await addComment(videoId, text);
            setComments((prev) => [{ ...fromApi(newComment), replies: [] }, ...prev]);
            setCommentText("");
        } catch {
            setCommentError("Failed to post comment. Please try again.");
        } finally {
            setSubmitting(false);
        }
    };

    const handleAddReply = async (e: React.FormEvent, parentId: string) => {
        e.preventDefault();
        const text = replyText.trim();
        if (!text || !videoId) return;
        setReplySubmitting(true);
        try {
            const newReply = await addReply(videoId, parentId, text);
            const replyComment = fromApi(newReply);
            setComments((prev) => prev.map((c) =>
                c.id === parentId
                    ? { ...c, replies: [...(c.replies ?? []), replyComment] }
                    : c
            ));
            setReplyText("");
            setReplyingTo(null);
        } catch {
            // ignore
        } finally {
            setReplySubmitting(false);
        }
    };

    const handleDeleteComment = async (commentId: string, parentId?: string) => {
        try {
            await deleteComment(commentId);
            if (parentId) {
                // remove a reply
                setComments((prev) => prev.map((c) =>
                    c.id === parentId
                        ? { ...c, replies: (c.replies ?? []).filter((r) => r.id !== commentId) }
                        : c
                ));
            } else {
                // remove a top-level comment (cascade deletes its replies in DB)
                setComments((prev) => prev.filter((c) => c.id !== commentId));
            }
        } catch {
            // ignore
        }
    };

    const handleCommentReaction = async (
        commentId: string,
        reaction: "like" | "dislike",
        parentId?: string,
    ) => {
        try {
            const data = await reactToComment(commentId, reaction);
            const likes = data.reactions["like"] ?? 0;
            const dislikes = data.reactions["dislike"] ?? 0;
            const update = (c: VideoComment) =>
                c.id === commentId ? { ...c, likesCount: likes, dislikesCount: dislikes } : c;
            if (parentId) {
                setComments((prev) => prev.map((c) =>
                    c.id === parentId ? { ...c, replies: (c.replies ?? []).map(update) } : c
                ));
            } else {
                setComments((prev) => prev.map(update));
            }
        } catch {
            // ignore
        }
    };

    const [resolution, setResolution] = useState("720p");

    const { handleDownload } = useDownload({ video: video as unknown as VideoDetail, resolution });

    const { handleReaction } = useReactions({
        initialVideo: video as unknown as VideoDetail,
        initialUserReaction: null,

        onVideoUpdate: (newVideo: VideoDetail) => {
            if (setVideo) {
                setVideo(newVideo);
            } else {
                console.error("setVideo function is not available.");
            }
        }
    });

    if (error) return <p className="text-red-500">{error}</p>;
    if (loading || !video) return <p>Loading video...</p>;

    const avatarSize = 40;

    return (
        <div className="flex flex-col lg:flex-row items-start gap-6 lg:gap-10 p-4 sm:p-6">
            <div className="w-full lg:w-2/3 lg:max-w-6xl">
                <VideoPlayer src={video.hlsUrl} />
                <h1 className="text-xl sm:text-2xl md:text-3xl font-bold my-4">{video.title}</h1>
                <div className="flex items-center gap-3 mb-4">
                    <img
                        className="rounded-full"
                        src={video.channel_avatar || ""}
                        alt={video.channel}
                        width={avatarSize}
                        height={avatarSize}
                        style={{ objectFit: "cover" }}
                    />
                    <span className="text-gray-700 font-medium">{video.channel}</span>

                    <span className="text-gray-500 text-sm ml-2">
                        {metaDataText}
                    </span>
                </div>
                <div className="mb-6 text-gray-700 text-sm sm:text-base">
                    <h4 className="font-semibold">Description:</h4>
                    <p>{video.description}</p>
                </div>
                <div className="flex items-center gap-4 mt-4 mb-6">
                    <Button onClick={() => handleReaction("like")} className="flex items-center gap-2">
                        <img src="/thumbs_up.svg" alt="Like" />
                        <span>{video.likesCount}</span>
                    </Button>
                    <Button onClick={() => handleReaction("dislike")} className="flex items-center gap-2">
                        <img src="/thumbs-down.svg" alt="Dislike" />
                        <span>{video.dislikesCount}</span>
                    </Button>
                    <select
                        value={resolution}
                        onChange={(e) => setResolution(e.target.value)}
                        className="p-2 rounded border border-gray-300 text-sm"
                    >
                        <option value="360p">360p</option>
                        <option value="720p">720p</option>
                        <option value="1080p">1080p</option>
                    </select>
                    <Button
                        className="text-gray-900 bg-white border border-gray-300 focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-100 font-medium rounded-full text-sm px-5 py-2.5 me-2 mb-2 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700 flex items-center justify-center gap-2"
                        onClick={() => handleDownload()}
                    >
                        <img src="/arrow-big-down.svg" alt="Download" className="w-5 h-5" />
                        <span>Download</span>
                    </Button>
                </div>
                <div className="mt-6">
                    <h2 className="text-lg sm:text-xl font-semibold mb-4">{comments.length} Comments</h2>

                    {/* Comment form */}
                    {user ? (
                        <form onSubmit={handleAddComment} className="mb-6 flex flex-col gap-2">
                            <textarea
                                value={commentText}
                                onChange={(e) => setCommentText(e.target.value)}
                                placeholder="Add a comment..."
                                rows={3}
                                className="w-full rounded border border-gray-300 p-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-gray-300 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                            />
                            {commentError && (
                                <p className="text-sm text-red-500">{commentError}</p>
                            )}
                            <div className="flex justify-end">
                                <Button type="submit" disabled={submitting || !commentText.trim()} size="sm">
                                    {submitting ? "Posting..." : "Comment"}
                                </Button>
                            </div>
                        </form>
                    ) : (
                        <p className="text-sm text-gray-500 mb-4">
                            <Link to="/login" className="underline">Sign in</Link> to leave a comment.
                        </p>
                    )}

                    {/* Comment list */}
                    <div className="space-y-5">
                        {comments.map((comment: VideoComment) => {
                            const replies = comment.replies ?? [];
                            const displayName = comment.user_name || comment.userId;
                            const initial = displayName.charAt(0).toUpperCase();
                            const isOwn = user && (user.id === comment.userId);

                            return (
                                <div key={comment.id}>
                                    {/* Top-level comment */}
                                    <div className="flex gap-3">
                                        {/* Avatar */}
                                        {comment.user_avatar ? (
                                            <img
                                                src={comment.user_avatar}
                                                alt={displayName}
                                                className="w-8 h-8 rounded-full object-cover shrink-0"
                                            />
                                        ) : (
                                            <div className="w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center shrink-0 text-sm font-semibold text-gray-700 dark:text-gray-200">
                                                {initial}
                                            </div>
                                        )}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-0.5">
                                                <span className="font-medium text-sm">{displayName}</span>
                                                <span className="text-xs text-gray-400">{timeAgo(comment.createdAt)}</span>
                                            </div>
                                            <p className="text-gray-700 dark:text-gray-300 text-sm">{comment.content}</p>
                                            <div className="flex items-center gap-3 mt-1">
                                                <button
                                                    onClick={() => handleCommentReaction(comment.id, "like")}
                                                    className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                                                >
                                                    <img src="/thumbs_up.svg" alt="Like" className="w-3.5 h-3.5" />
                                                    <span>{comment.likesCount}</span>
                                                </button>
                                                <button
                                                    onClick={() => handleCommentReaction(comment.id, "dislike")}
                                                    className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                                                >
                                                    <img src="/thumbs-down.svg" alt="Dislike" className="w-3.5 h-3.5" />
                                                    <span>{comment.dislikesCount}</span>
                                                </button>
                                                {user && (
                                                    <button
                                                        onClick={() => {
                                                            setReplyingTo(replyingTo === comment.id ? null : comment.id);
                                                            setReplyText("");
                                                        }}
                                                        className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                                                    >
                                                        Reply
                                                    </button>
                                                )}
                                                {isOwn && (
                                                    <button
                                                        onClick={() => handleDeleteComment(comment.id)}
                                                        className="text-xs text-red-400 hover:text-red-600"
                                                    >
                                                        Delete
                                                    </button>
                                                )}
                                            </div>

                                            {/* Reply form */}
                                            {replyingTo === comment.id && (
                                                <form
                                                    onSubmit={(e) => handleAddReply(e, comment.id)}
                                                    className="mt-2 flex gap-2"
                                                >
                                                    <textarea
                                                        value={replyText}
                                                        onChange={(e) => setReplyText(e.target.value)}
                                                        placeholder={`Reply to ${displayName}...`}
                                                        rows={2}
                                                        className="flex-1 rounded border border-gray-300 p-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-gray-300 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                                                    />
                                                    <div className="flex flex-col gap-1">
                                                        <Button type="submit" size="sm" disabled={replySubmitting || !replyText.trim()}>
                                                            {replySubmitting ? "..." : "Reply"}
                                                        </Button>
                                                        <Button type="button" size="sm" variant="ghost" onClick={() => setReplyingTo(null)}>
                                                            Cancel
                                                        </Button>
                                                    </div>
                                                </form>
                                            )}

                                            {/* Replies */}
                                            {replies.length > 0 && (
                                                <div className="mt-3 space-y-3 pl-4 border-l border-gray-200 dark:border-gray-700">
                                                    {replies.map((reply) => {
                                                        const rName = reply.user_name || reply.userId;
                                                        const rInitial = rName.charAt(0).toUpperCase();
                                                        const rIsOwn = user && user.id === reply.userId;
                                                        return (
                                                            <div key={reply.id} className="flex gap-2">
                                                                {reply.user_avatar ? (
                                                                    <img
                                                                        src={reply.user_avatar}
                                                                        alt={rName}
                                                                        className="w-6 h-6 rounded-full object-cover shrink-0"
                                                                    />
                                                                ) : (
                                                                    <div className="w-6 h-6 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center shrink-0 text-xs font-semibold text-gray-700 dark:text-gray-200">
                                                                        {rInitial}
                                                                    </div>
                                                                )}
                                                                <div className="flex-1 min-w-0">
                                                                    <div className="flex items-center gap-2 mb-0.5">
                                                                        <span className="font-medium text-xs">{rName}</span>
                                                                        <span className="text-xs text-gray-400">{timeAgo(reply.createdAt)}</span>
                                                                        {rIsOwn && (
                                                                            <button
                                                                                onClick={() => handleDeleteComment(reply.id, comment.id)}
                                                                                className="text-xs text-red-400 hover:text-red-600"
                                                                            >
                                                                                Delete
                                                                            </button>
                                                                        )}
                                                                    </div>
                                                                    <p className="text-gray-700 dark:text-gray-300 text-xs sm:text-sm">{reply.content}</p>
                                                                    <div className="flex items-center gap-3 mt-1">
                                                                        <button
                                                                            onClick={() => handleCommentReaction(reply.id, "like", comment.id)}
                                                                            className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                                                                        >
                                                                            <img src="/thumbs_up.svg" alt="Like" className="w-3 h-3" />
                                                                            <span>{reply.likesCount}</span>
                                                                        </button>
                                                                        <button
                                                                            onClick={() => handleCommentReaction(reply.id, "dislike", comment.id)}
                                                                            className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                                                                        >
                                                                            <img src="/thumbs-down.svg" alt="Dislike" className="w-3 h-3" />
                                                                            <span>{reply.dislikesCount}</span>
                                                                        </button>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                        {comments.length === 0 && !loading && (
                            <p className="text-sm text-gray-400">No comments yet. Be the first!</p>
                        )}
                    </div>
                </div>
            </div>
            <div className="w-full lg:w-1/3 mt-6 lg:mt-0">
                <h2 className="font-semibold mb-2">Up Next</h2>
                <div className="mb-4 flex overflow-x-auto overflow-y-hidden no-scrollbar cursor-grab active:cursor-grabbing select-none">
                    {categories.map((category) => (
                        <Button
                            key={category}
                            onClick={() => setActive(category)}
                            variant={active === category ? "default" : "outline"}
                            className={`mx-2 whitespace-nowrap transition-all ${active === category ? "bg-black text-white" : ""}`}
                        >
                            {category}
                        </Button>
                    ))}
                </div>

                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <InfiniteScroll loadMore={loadMore} hasMore={hasMore}>
                        <div className="space-y-4">
                            {videos.map((video: VideoPreviewWithTime) => (
                                <Link key={video.id} to={`/watch?v=${video.id}`} className="w-full">
                                    <VideoCard
                                        id={video.id}
                                        title={video.title}
                                        thumbnail={video.previewUrl || video.thumbnail_url}
                                        channel_avatar={video.channel_avatar}
                                        channel_name={video.channel_name}
                                        views={video.views}
                                        timeAgo={video.timeAgo}
                                    />
                                </Link>
                            ))}
                        </div>
                    </InfiniteScroll>
                )}
            </div>
        </div>
    );
}
