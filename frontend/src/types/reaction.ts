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

