import { useState, useCallback } from "react";
import type { SearchHintsResponse, UseSearchReturn } from "../../types/hints";
import clientApi from "@api/clientApi";

export function useHints(): UseSearchReturn {
    const [hints, setHints] = useState<string[]>([]);

    const loadHints = useCallback(async (query: string) => {
        console.log("[useSearch] loadHints called with:", query);

        if (!query || query.trim().length < 1) {
            setHints([]);
            return;
        }
        const results = await getHints(query);

        console.log("[useSearch] Hints received:", results);

        setHints(results);
    }, []);

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

    return {
        hints,
        loadHints,
        setHints
    };
}