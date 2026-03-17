import clientApi from "./clientApi";

export interface DailyMetric {
  date: string;
  count: number;
}

export interface TopVideo {
  id: string;
  title: string;
  thumbnail: string;
  views_count: number;
  likes_count: number;
  comments_count: number;
}

export interface VideoStat {
  id: string;
  title: string;
  thumbnail: string;
  privacy: "public" | "private";
  views_count: number;
  likes_count: number;
  dislikes_count: number;
  comments_count: number;
  created_at: string;
}

export interface OverviewData {
  total_views: number;
  total_subscribers: number;
  total_likes: number;
  total_comments: number;
  views_per_day: DailyMetric[];
  top_videos: TopVideo[];
}

export interface ContentData {
  videos: VideoStat[];
}

export interface AudienceData {
  subscribers_per_day: DailyMetric[];
  unique_viewers: number;
  returning_viewers: number;
  comments_per_day: DailyMetric[];
}

export const getOverview = (): Promise<OverviewData> =>
  clientApi.get<OverviewData>("/api/analytics/overview").then((r) => r.data);

export const getContent = (): Promise<ContentData> =>
  clientApi.get<ContentData>("/api/analytics/content").then((r) => r.data);

export const getAudience = (): Promise<AudienceData> =>
  clientApi.get<AudienceData>("/api/analytics/audience").then((r) => r.data);
