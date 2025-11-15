import { useState, useCallback, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import type { SearchFilters, VideoPreviewWithTime, SearchResponse, VideoPreview, SearchHintsResponse } from "@api/types";
import { timeAgo } from "@/utils/timeAgo";
import clientApi from "@api/clientApi";
import React from "react";

type SetBooleanState = React.Dispatch<React.SetStateAction<boolean>>;
type SetNumberState = React.Dispatch<React.SetStateAction<number>>;

export interface UseSearchReturn {
    videos: VideoPreviewWithTime[];
    loading: boolean;
    hasMore: boolean;
    page: number;
    searchQuery: string;
    searchFilters: SearchFilters | undefined;

    loadMoreSearchResults: () => Promise<void>;
    runSearch: (query: string, filters?: SearchFilters) => void;

    setSearchFilters: React.Dispatch<React.SetStateAction<SearchFilters | undefined>>;
    setSearchQuery: React.Dispatch<React.SetStateAction<string>>;
    setLoading: SetBooleanState;
    setPage: SetNumberState;
    setVideos: React.Dispatch<React.SetStateAction<VideoPreviewWithTime[]>>;
    setHasMore: SetBooleanState;

    // Нові поля для підказок
    hints: string[];
    loadHints: (query: string) => Promise<void>;
    setHints: React.Dispatch<React.SetStateAction<string[]>>;
}

interface ApiVideoItem extends VideoPreview {
    name?: string;
}

const PAGE_SIZE = 9;

// Функція пошуку відео
const fetchSearchResults = async (query: string, page: number, filters?: SearchFilters): Promise<VideoPreviewWithTime[]> => {
    const params = {
        q: query,
        page: page,
        size: PAGE_SIZE,
        category: filters?.category === "All" ? undefined : filters?.category,
        min_views: filters?.minViews,
        max_views: filters?.maxViews,
        smart_search: filters?.smartSearch,
        has_description: filters?.includeDescription
    };

    try {
        const response = await clientApi.post<SearchResponse>(`/api/search/video`, {}, {
            params: params
        });

        const results = response.data?.results || [];

        return results.map((item: VideoPreview) => {
            const serverItem = item as ApiVideoItem;
            const title = serverItem.name || item.title || "Untitled Video";

            return {
                ...item,
                title: title,
                timeAgo: timeAgo(item.publishedAt || item.createdAt || new Date().toISOString()),
                previewUrl: item.thumbnail_url || item.previewUrl || "/placeholder.jpg",
            } as VideoPreviewWithTime;
        });
    } catch (error) {
        console.error(error);
        return [];
    }
};

// Функція отримання підказок
const getHints = async (query: string): Promise<string[]> => {
    if (!query || query.length < 1) return [];
    try {
        const response = await clientApi.get<SearchHintsResponse>(`/api/search/video_hints`, {
            params: { q: query }
        });
        return response.data.hints || [];
    } catch (error) {
        console.error("[SearchApi] Failed to get hints:", error);
        return [];
    }
};

interface UseSearchOptions {
    enabled?: boolean;
    initialPage?: number;
}

export function useSearch({ enabled = false, initialPage = 1 }: UseSearchOptions = {}): UseSearchReturn {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const [videos, setVideos] = useState<VideoPreviewWithTime[]>([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(initialPage);
    const [hasMore, setHasMore] = useState(true);

    const [searchQuery, setSearchQuery] = useState(searchParams.get("q") || "");

    const [searchFilters, setSearchFilters] = useState<SearchFilters | undefined>(() => {
        const category = searchParams.get("category") || undefined;
        const minViews = searchParams.get("min_views") ? Number(searchParams.get("min_views")) : undefined;
        const maxViews = searchParams.get("max_views") ? Number(searchParams.get("max_views")) : undefined;
        const smartSearch = searchParams.get("smart_search") === "true";
        const includeDescription = searchParams.get("has_description") === "true";

        if (!category && !minViews && !maxViews && !smartSearch && !includeDescription) return undefined;

        return { category, minViews, maxViews, smartSearch, includeDescription };
    });

    // Стан для підказок
    const [hints, setHints] = useState<string[]>([]);

    // Функція завантаження підказок
    const loadHints = useCallback(async (query: string) => {
        // --- ЛОГ 2: Чи доходить виклик до хука? ---
        console.log("[useSearch] 🎣 loadHints called with:", query);

        if (!query || query.trim().length < 1) {
            setHints([]);
            return;
        }
        const results = await getHints(query);

        // --- ЛОГ 4: Що повернув API? ---
        console.log("[useSearch] Hints received:", results);

        setHints(results);
    }, []);

    const loadMoreSearchResults = useCallback(async () => {
        if (!enabled) return;

        const nextPage = page + 1;
        if (!hasMore || loading) return;
        if (!searchQuery && !searchFilters) return;

        setLoading(true);

        try {
            const newResults = await fetchSearchResults(searchQuery, nextPage, searchFilters);

            if (newResults.length < PAGE_SIZE) {
                setHasMore(false);
            }

            if (newResults.length > 0) {
                setVideos((prev) => {
                    const existingIds = new Set(prev.map(v => v.id));
                    const uniqueNew = newResults.filter(v => !existingIds.has(v.id));
                    return [...prev, ...uniqueNew];
                });
                setPage(nextPage);
            } else {
                setHasMore(false);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [page, hasMore, loading, searchQuery, searchFilters, enabled]);

    const runSearch = useCallback((query: string, filters?: SearchFilters) => {
        setSearchQuery(query);
        if (filters) setSearchFilters(filters);

        const urlParams = new URLSearchParams();
        if (query) urlParams.set('q', query);

        if (filters) {
            if (filters.category && filters.category !== "All") urlParams.set('category', filters.category);
            if (filters.minViews) urlParams.set('min_views', filters.minViews.toString());
            if (filters.maxViews) urlParams.set('max_views', filters.maxViews.toString());
            if (filters.smartSearch) urlParams.set('smart_search', 'true');
            if (filters.includeDescription) urlParams.set('has_description', 'true');
        }

        navigate(`/search-results?${urlParams.toString()}`);
    }, [navigate]);

    useEffect(() => {
        if (!enabled) return;

        const queryFromUrl = searchParams.get("q") || "";

        if (queryFromUrl !== searchQuery) {
            setSearchQuery(queryFromUrl);
        }

        const hasFiltersInUrl = searchParams.has("category") || searchParams.has("min_views") || searchParams.has("smart_search");

        if (queryFromUrl || hasFiltersInUrl) {
            setVideos([]);
            setPage(1);
            setHasMore(true);
            setLoading(true);

            fetchSearchResults(queryFromUrl, 1, searchFilters)
                .then(newResults => {
                    setVideos(newResults);
                    setHasMore(newResults.length === PAGE_SIZE);
                    setPage(2);
                })
                .catch(err => console.error(err))
                .finally(() => setLoading(false));
        }
    }, [searchParams, searchFilters, enabled]);

    return {
        videos, loading, hasMore, page,
        searchQuery, searchFilters,
        setSearchFilters, setSearchQuery,
        runSearch, loadMoreSearchResults,
        setLoading, setPage, setVideos, setHasMore,

        // Нові властивості
        hints,
        loadHints,
        setHints
    };
}