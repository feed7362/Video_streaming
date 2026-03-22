import clientApi from "@api/clientApi";
import type {
  SearchFilters,
  SearchResponse,
  VideoPreview,
  VideoPreviewWithTime,
  SearchHintsResponse,
} from "@api/types";
import { timeAgo } from "@/utils/timeAgo";

interface ApiVideoItem extends VideoPreview {
  name?: string;
}

export const search = async (
  query: string,
  filters?: SearchFilters,
): Promise<VideoPreviewWithTime[]> => {
  const body = {
    query,
    limit: 9,
    category: filters?.category === "All" ? undefined : filters?.category,
    min_views: filters?.minViews,
    max_views: filters?.maxViews,
    smart_search: filters?.smartSearch ?? false,
    has_description: filters?.includeDescription ?? false,
  };

  try {
    const response = await clientApi.post<SearchResponse>(
      `/api/search/video`,
      body,
    );

    const results = response.data?.results || [];

    return results.map((item: VideoPreview) => {
      const serverItem = item as ApiVideoItem;
      const title = serverItem.name || item.title || "Untitled Video";

      return {
        ...item,
        title: title,
        timeAgo: timeAgo(
          item.publishedAt || item.createdAt || new Date().toISOString(),
        ),
        previewUrl: item.thumbnail_url || item.previewUrl || "/placeholder.jpg",
      } as VideoPreviewWithTime;
    });
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const getHints = async (query: string): Promise<string[]> => {
  if (!query || query.length < 1) return [];

  console.log(
    "[searchApi] Sending GET request to /api/search/video_hints?q=" + query,
  );

  try {
    const response = await clientApi.get<SearchHintsResponse>(
      `/api/search/video_hints`,
      {
        params: { query },
      },
    );
    return response.data.hints || [];
  } catch (error) {
    console.error("[SearchApi] Failed to get hints:", error);
    return [];
  }
};

export default {
  search,
  getHints,
};
