export interface ChannelInfo {
  channel_name: string;
  channel_avatar: string;
  channelBanner?: string;
  subscribersCount: number;
  videosCount: number;
  bio?: string;
  createdAt: string;
  name: string;
  isOwner?: boolean;
}

export interface VideoPreview {
  // name can be present from some server responses but isn't always required
  name?: string;
  thumbnail_url?: string;
  channel_name?: string;
  id: string;
  title: string;
  previewUrl: string;
  channel_avatar: string;
  createdAt: string;
  channel: string;
  views: number;
  likesCount: number;
  publishedAt: string;
  dislikesCount: number;
  privacy: string;
}

export interface Video {
  publishedAt: string;
  id: string;
  title: string;
  size: number;
  hash: string;
  name: string;
  avatar_url?: string;
  master_hls_url: string;
  thumbnail_url: string;
  created_at: string;
  channelId: string;
  views_count: number;
  likes_count: number;
  dislikes_count: number;
  privacy: string;
  category?: string;
  channel_avatar?: string;
  channel_name: string;
  status: "Processing" | "Ready" | "Failed";
  comments?: VideoComment[];
  commentCount?: number;
  preview_url?: string;
  description?: string;
  timeAgo?: string;
}

export interface VideoComment {
  id: string;
  userId: string;
  content: string;
  createdAt: string;
  videoId: string;
  parentId?: string;
  likesCount: number;
  dislikesCount: number;
}

export interface Comment {
  id: string;
  userId: string;
  videoId: string;
  content: string;
  createdAt: string;
  updatedAt?: string;
  likesCount: number;
  dislikesCount: number;
}
export interface UserInfo {
  id: string;
  username: string;
  status: "active" | "banned" | "deleted";
  email?: string;
  createdAt: string;
  roleId: number;
  hashedPassword?: string;
}

export interface ChannelPreview {
  channel_name: string;
  channel_avatar: string;
  subscribersCount: number;
  videosCount: number;
}

export interface CommentPage {
  items: Comment[];
  page: number;
  size: number;
  total: number;
}

export interface Playlist {
  id: string;
  title: string;
  description?: string;
  createdAt: string;
  updatedAt?: string;
  videoIds: string[];
  isPublic: boolean;
}

export interface PlaylistPreview {
  id: string;
  title: string;
  videoCount: number;
  createdAt: string;
  isPublic: boolean;
}

export interface Notification {
  id: string;
  userId: string;
  type: "new_video" | "new_subscriber" | "comment_reply" | "like" | "dislike";
  content: string;
  isRead: boolean;
  createdAt: string;
  relatedEntityId?: string;
}
export interface ChangelogEntry {
  date: string;
  version: string;
  improvements?: string[];
  bugfixes?: string[];
  newFeatures?: string[];
  imageUrl?: string;
  tags?: string[];
}
export interface Category {
  id: string;
  name: string;
}

export interface UploadedFile {
  file_id: string;
  filename: string;
  size: number;
}

export interface UploadResponse {
  status: string;
  files?: UploadedFile[];
  message?: string;
}

export interface DownloadVideo {
  file_id: string;
  filename: string;
  size: number;
}

export interface DownloadResponse {
  status: string;
  files: DownloadVideo[];
  message?: string;
}

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

export type VideoDetail = VideoPreview & {
  timeAgo?: string;
  description: string;
  hlsUrl: string;
  likesCount: number;
  dislikeCount: number;
  userReaction: "like" | "dislike" | null;
};

export type VideoPreviewWithTime = VideoPreview & {
  timeAgo: string;
};

export interface SearchFilters {
  category?: string;
  minViews?: number; // �������� ������������
  maxViews?: number; // �������� ������������
  includeDescription: boolean; // �������� ����'�������
  smartSearch: boolean;
}

export interface SearchResponse {
  results: VideoPreview[];
}
type SetVideoState = React.Dispatch<React.SetStateAction<VideoDetail | null>>;
export interface UseVideoResult {
  // --- ������ ����� ---
  video: VideoDetail | null;
  videos: VideoPreviewWithTime[];
  comments: VideoComment[];
  error: string | null;
  loading: boolean;
  hasMore: boolean;
  page: number; // ������� ������� ��� ��������
  setVideo: SetVideoState;
  // --- ������� ����������� �� ����� ---
  loadMore: () => Promise<void>;
  loadMoreSearchResults: () => Promise<void>;
  formatViews: (views: number | undefined) => string;
  metaDataText: string;

  // --- ������� ��� ���������� ����� ---
  setVideos: React.Dispatch<React.SetStateAction<VideoPreviewWithTime[]>>;
  setPage: React.Dispatch<React.SetStateAction<number>>;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setHasMore: React.Dispatch<React.SetStateAction<boolean>>;

  // --- ���� �� ������� ��� ������ ---
  searchQuery: string; // �������� ��������� �����
  setSearchQuery: React.Dispatch<React.SetStateAction<string>>;
  setSearchFilters: React.Dispatch<
    React.SetStateAction<SearchFilters | undefined>
  >;
}

export interface NoSearchResultsProps {
  query: string;
}
export interface SearchApiResponse {
  results: VideoPreview[];
}
export interface SearchHintsResponse {
  hints: string[];
}
