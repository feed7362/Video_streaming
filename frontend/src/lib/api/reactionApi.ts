import clientApi from "./clientApi";
import type { ReactionResponse } from "./types";

export const sendReaction = async (
  videoId: string,
  reaction: "like" | "dislike",
): Promise<ReactionResponse> => {
  const res = await clientApi.post<ReactionResponse>(
    `/api/video/reaction/video/${videoId}`,
    { reaction_name: reaction },
  );
  return res.data;
};

export default { sendReaction };
