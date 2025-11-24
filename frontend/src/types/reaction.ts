import type { VideoDetail } from "./video";

export interface ReactionResponse {
    likesCount: number;
    dislikesCount: number;
    target_id: string;
    target_type: string;
    reactions: {
        like: number;
        dislike: number;
        [key: string]: number;
    };
}

export type ReactionType = "like" | "dislike";
export type UserReactionState = ReactionType | null;

export interface UseReactionsProps {
    initialVideo: VideoDetail | null;
    initialUserReaction: UserReactionState;
    onVideoUpdate: (newVideo: VideoDetail) => void;
}

export interface UseReactionsResult {
    userReaction: UserReactionState;
    handleReaction: (reactionType: ReactionType) => Promise<void>;
    isPending: boolean;
}