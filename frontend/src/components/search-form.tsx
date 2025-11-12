import { Search } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { SearchFiltersDialog } from "@/components/ui/searchFiltersDialog"; // Ваш діалог

// Припускаємо, що SidebarInput - це просто стилізований Input
const SidebarInput = Input;

export function SearchForm({ ...props }: React.ComponentProps<"form">) {
    return (
        <form {...props} className="w-full">
            <div className="relative flex items-center">

                {/* Іконка Search (ліворуч) */}
                <Search
                    className="pointer-events-none absolute left-3 size-4 opacity-50 select-none z-10" // Додав z-index
                />

                <Label htmlFor="search" className="sr-only">
                    Search
                </Label>

                {/* Поле вводу з коректними відступами */}
                <SidebarInput
                    id="search"
                    placeholder="Type to search..."
                    // pl-10: Збільшив відступ для кращого вигляду іконки
                    // pr-10: Відступ для іконки фільтрів
                    className="h-10 w-full pl-10 pr-10 rounded-lg border-2 shadow-sm"
                />

                {/* Тригер діалогу (праворуч) */}
                <div className="absolute inset-y-0 right-0 flex items-center z-10">
                    {/* Використовуємо ваш діалог. Важливо: ми вирівнюємо діалог по центру і 
                        додаємо невеликий відступ від краю через pr-1 у самому діалозі (якщо він є),
                        або прямо тут. */}
                    <SearchFiltersDialog />
                </div>
            </div>
        </form>
    );
}