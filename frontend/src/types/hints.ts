export interface SearchHintsResponse {
    hints: string[];
}

export interface UseSearchReturn {
    hints: string[];
    loadHints: (query: string) => Promise<void>;
    setHints: React.Dispatch<React.SetStateAction<string[]>>;
}