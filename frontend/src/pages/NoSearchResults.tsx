import type { NoSearchResultsProps } from "../types/search";

export default function NoSearchResults({ query }: NoSearchResultsProps) {
    return (
        <div className="text-center py-10">
            <h2 className="text-2xl font-bold">
                No results found for "{query}"
            </h2>
            <p className="text-gray-500 mt-2">Try adjusting your search or filters.</p>
        </div>
    );
}