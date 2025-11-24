import { useCallback, useEffect, useState } from "react";
import { useToast } from "@/components/ui/toast/use-toast";
import reactionApi from "@api/reactionApi";
import type { VideoDetail } from "../../types/video";
import type { UserReactionState, ReactionType, UseReactionsProps, UseReactionsResult } from "../../types/reaction";

export function useReactions({
    initialVideo,
    initialUserReaction,
    onVideoUpdate,
}: UseReactionsProps): UseReactionsResult {
    const [userReaction, setUserReaction] = useState(initialUserReaction);
    const [isPending, setIsPending] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        setUserReaction(initialUserReaction);
    }, [initialUserReaction]);

    const handleReaction = useCallback(
        async (reactionType: ReactionType) => {
            if (!initialVideo) return;

            setIsPending(true);

            const prevReaction = userReaction;
            const currentLikes = initialVideo.likesCount;
            const currentDislikes = initialVideo.dislikesCount;

            let newLikes = currentLikes;
            let newDislikes = currentDislikes;
            let nextReaction: UserReactionState;

            if (prevReaction === reactionType) {
                nextReaction = null;
                if (reactionType === "like") newLikes = Math.max(0, currentLikes - 1);
                else newDislikes = Math.max(0, currentDislikes - 1);
            } else {
                nextReaction = reactionType;
                if (reactionType === "like") {
                    newLikes += 1;
                    if (prevReaction === "dislike") newDislikes = Math.max(0, currentDislikes - 1);
                } else {
                    newDislikes += 1;
                    if (prevReaction === "like") newLikes = Math.max(0, currentLikes - 1);
                }
            }

            const newVideoData: VideoDetail = {
                ...initialVideo,
                likesCount: newLikes,
                dislikesCount: newDislikes,
                userReaction: nextReaction,
            };

            onVideoUpdate(newVideoData);
            setUserReaction(nextReaction);

            try {
                await reactionApi.sendReaction(initialVideo.id, reactionType);
            } catch (error) {
                console.error("Error sending reaction:", error);
                toast({ title: "Error sending reaction (500)", variant: "destructive" });
                onVideoUpdate(initialVideo);
                setUserReaction(prevReaction);
            } finally {
                setIsPending(false);
            }
        },
        [initialVideo, userReaction, onVideoUpdate, toast]
    );

    return { userReaction, handleReaction, isPending };
}