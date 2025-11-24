export interface Category {
    id: string;
    name: string;
}

export type CategoryType = {
    id: string;
    name: string;
};

export interface UseFetchCategoriesResult {
    categories: string[];
    active: string;
    setActive: React.Dispatch<React.SetStateAction<string>>;
}