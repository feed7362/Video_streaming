import {
    Dialog,
    DialogContent,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import React from 'react';
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { useFetchCategories } from "@/hooks/useCategories";

type CategoryType = {
    id: string;
    name: string;
};

export function SearchFiltersDialog() {
    const { categories, active, setActive } = useFetchCategories();
    const [viewRange, setViewRange] = React.useState([0, 100000]);
    const [includeDescription, setIncludeDescription] = React.useState(false);

    const handleApplyFilters = () => {
        const filters = {
            category: active,
            minViews: viewRange[0],
            maxViews: viewRange[1000],
            includeDescription: includeDescription,
        };
        console.log("Applying filters:", filters);
    };

    const isCategoryStringArray = categories.length > 0 && typeof categories[0] === 'string';

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="h-full flex justify-center p-0">
                    <img src="/sliders-horizontal.svg" alt="Filters" className="w-5 h-5" />
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
                <DialogTitle>Search Filters</DialogTitle>

                <div className="flex items-center space-x-2 mt-4">
                    <Checkbox
                        id="has-description"
                        checked={includeDescription}
                        onCheckedChange={(checked) => setIncludeDescription(!!checked)}
                    />
                    <Label htmlFor="has-description">Videos with description</Label>
                </div>

                <div className="mt-6">
                    <Label className="mb-2 block font-medium">
                        View Count: {viewRange[0].toLocaleString()} - {viewRange[1].toLocaleString()}
                    </Label>
                    <Slider
                        value={viewRange}
                        min={0}
                        max={10000000}
                        step={1000}
                        className="w-full"
                        onValueChange={setViewRange}
                    />
                </div>

                <div className="mb-4 flex overflow-x-auto overflow-y-hidden no-scrollbar select-none">
                    {categories.map((category) => {
                        const data = category as CategoryType | string;
                        const name = isCategoryStringArray ? (data as string) : (data as CategoryType).name;
                        const key = isCategoryStringArray ? (data as string) : (data as CategoryType).id;

                        return (
                            <Button
                                key={key}
                                onClick={() => setActive(name)}
                                variant="ghost"
                                className={`mx-2 whitespace-nowrap transition-all ${active === name ? "text-black font-semibold hover:bg-transparent" : "text-gray-500 hover:text-gray-800 hover:bg-transparent"}`}
                            >
                                {name}
                            </Button>
                        )
                    })}
                </div>

                <DialogFooter className="mt-6 flex justify-end">
                    <Button onClick={handleApplyFilters}>
                        Apply
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}