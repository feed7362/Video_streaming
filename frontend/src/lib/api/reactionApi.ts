import clientApi from "./clientApi";
import type { ReactionResponse } from "./types";

export const sendReaction = async (
  videoId: string,
  reaction: "like" | "dislike",
): Promise<ReactionResponse> => {
  const res = await clientApi.post<ReactionResponse>(
    `/api/videos/${videoId}/reactions`,
    { reaction_name: reaction },
  );
  return res.data;
};

export default { sendReaction };
