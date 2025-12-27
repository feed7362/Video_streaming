import React, { useState, useEffect, useRef } from "react";
import { Search } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { SearchFiltersDialog } from "@/components/ui/searchFiltersDialog";
import { useSearch } from "@/hooks/useSearch";

const SidebarInput = Input;

interface SearchFormProps {
    className?: string;
}

export function SearchForm({ className }: SearchFormProps) {
    const {
        searchQuery,
        setSearchQuery,
        runSearch,
        searchFilters,
        hints,
        loadHints,
        setHints
    } = useSearch();

    const [isFocused, setIsFocused] = useState(false);
    const wrapperRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            console.log("[SearchForm] Debounce fired. Query:", searchQuery);

            if (searchQuery.trim().length >= 1) {
                console.log("[SearchForm] Calling loadHints...");
                loadHints(searchQuery);
            } else {
                setHints([]);
            }
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [searchQuery, loadHints, setHints]);

    const handleHintClick = (hint: string) => {
        setSearchQuery(hint);
        runSearch(hint, searchFilters);
        setHints([]);
        setIsFocused(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            e.preventDefault();
            e.stopPropagation();
            setHints([]);
            runSearch(searchQuery, searchFilters);
        }
    };

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setIsFocused(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <div ref={wrapperRef} className={`relative w-full ${className || ""}`} role="search">
            <div className="relative flex items-center">
                <Search className="pointer-events-none absolute left-3 size-4 opacity-50 select-none z-10" />
                <Label htmlFor="search" className="sr-only">Search</Label>

                <SidebarInput
                    id="search"
                    placeholder="Type to search..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onFocus={() => setIsFocused(true)}
                    className="h-10 w-full pl-10 pr-10 rounded-lg border-2 shadow-sm"
                    autoComplete="off"
                />

                <div className="absolute inset-y-0 right-0 flex items-center z-10">
                    <SearchFiltersDialog />
                </div>
            </div>

            {isFocused && hints.length > 0 && (
                <div className="absolute top-full mt-1 w-full bg-background border rounded-md shadow-lg z-50 overflow-hidden">
                    <ul>
                        {hints.map((hint, index) => (
                            <li key={index}>
                                <button
                                    type="button"
                                    className="w-full text-left px-4 py-2 text-sm hover:bg-muted flex items-center gap-2 transition-colors"
                                    onMouseDown={() => handleHintClick(hint)}
                                >
                                    <Search className="size-3 opacity-50" />
                                    <span className="truncate">{hint}</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
