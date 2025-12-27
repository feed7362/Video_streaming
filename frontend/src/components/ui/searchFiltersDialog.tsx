import {
    Dialog,
    DialogContent,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
    DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { useCallback, useState } from 'react';
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { useFetchCategories } from "@/hooks/useCategories";
import { useSearch } from "@/hooks/useSearch";

const MAX_VIEW_LIMIT = 10000000;

type CategoryType = {
    id: string;
    name: string;
};

export function SearchFiltersDialog() {
    const [open, setOpen] = useState(false);

    const {
        searchQuery,
        searchFilters,
        setSearchFilters,
        runSearch,
    } = useSearch();

    const [viewRange, setViewRange] = useState<number[]>(() => {
        const min = searchFilters?.minViews ?? 0;
        const max = searchFilters?.maxViews ?? MAX_VIEW_LIMIT;
        return [min, max];
    });

    const [includeDescription, setIncludeDescription] = useState(searchFilters?.includeDescription || false);
    const [smartSearch, setSmartSearch] = useState(searchFilters?.smartSearch || false);

    const { categories, active, setActive } = useFetchCategories();

    const handleApplyFilters = useCallback(() => {
        const maxViewsValue = viewRange[1] >= MAX_VIEW_LIMIT ? undefined : viewRange[1];

        const filters = {
            category: active === "All" ? undefined : active,
            minViews: viewRange[0],
            maxViews: maxViewsValue,
            includeDescription: includeDescription,
            smartSearch: smartSearch
        };

        setSearchFilters(filters);
        runSearch(searchQuery, filters);
        setOpen(false);

    }, [active, viewRange, includeDescription, smartSearch, runSearch, searchQuery, setSearchFilters]);

    const formatNumber = (num: number) => {
        if (num >= 1000000) return (num / 1000000).toFixed(0) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(0) + 'k';
        return num.toString();
    };

    const isCategoryStringArray = Array.isArray(categories) && categories.length > 0 && typeof categories[0] === 'string';

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button type="button" variant="ghost" size="icon" className="h-full flex justify-center p-0">
                    <img src="/sliders-horizontal.svg" alt="Filters" className="w-5 h-5" />
                </Button>
            </DialogTrigger>

            <DialogContent aria-describedby="filters-desc" className="sm:max-w-md">
                <DialogTitle>Search Filters</DialogTitle>
                <DialogDescription id="filters-desc">
                    Customize your search results.
                </DialogDescription>

                <div className="flex flex-col gap-3 mt-4">
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="has-description"
                            checked={includeDescription}
                            onCheckedChange={(checked) => setIncludeDescription(!!checked)}
                        />
                        <Label htmlFor="has-description">Has description</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="smartSearch"
                            checked={smartSearch}
                            onCheckedChange={(checked) => setSmartSearch(!!checked)}
                        />
                        <Label htmlFor="smartSearch">Smart Search (AI)</Label>
                    </div>
                </div>

                <div className="mt-6 space-y-3">
                    <div className="flex justify-between">
                        <Label className="font-medium">Min Views: {formatNumber(viewRange[0])}</Label>
                        <Label className="font-medium">
                            Max Views: {viewRange[1] >= MAX_VIEW_LIMIT ? "Any" : formatNumber(viewRange[1])}
                        </Label>
                    </div>
                    <Slider
                        value={viewRange}
                        min={0}
                        max={MAX_VIEW_LIMIT}
                        step={10000}
                        minStepsBetweenThumbs={1}
                        className="w-full"
                        onValueChange={setViewRange}
                    />
                </div>

                <div className="mt-4">
                    <Label className="mb-2 block text-sm font-medium text-muted-foreground">Category</Label>
                    <div className="flex overflow-x-auto pb-2 no-scrollbar gap-2">
                        <Button
                            key="all"
                            type="button"
                            onClick={() => setActive("All")}
                            variant={active === "All" ? "default" : "outline"}
                            size="sm"
                        >
                            All
                        </Button>
                        {Array.isArray(categories) && categories
                            .filter((cat) => {
                                const name = isCategoryStringArray ? (cat as string) : (cat as unknown as CategoryType).name;
                                return name.toLowerCase() !== 'all';
                            })
                            .map((category) => {
                                let name: string;
                                let key: string;

                                if (isCategoryStringArray) {
                                    name = category as string;
                                    key = category as string;
                                } else {
                                    const catObj = category as unknown as CategoryType;
                                    name = catObj.name;
                                    key = catObj.id;
                                }

                                return (
                                    <Button
                                        key={key}
                                        type="button"
                                        onClick={() => setActive(name)}
                                        variant={active === name ? "default" : "outline"}
                                        size="sm"
                                        className="whitespace-nowrap"
                                    >
                                        {name}
                                    </Button>
                                );
                            })}
                    </div>
                </div>

                <DialogFooter className="mt-4">
                    <Button type="button" onClick={handleApplyFilters} className="w-full sm:w-auto">
                        Apply Filters
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
