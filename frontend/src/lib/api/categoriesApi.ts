import clientApi from "./clientApi";
import type { Category } from "./types";

export const getCategories = async (): Promise<Category[]> => {
    const res = await clientApi.get("/api/video/get_categories");

    console.log("Categories API response:", res.data);

    if (Array.isArray(res.data)) {
        return res.data.map((name: string, index: number) => ({
            id: String(index),
            name,
        }));
    }

    if (Array.isArray(res.data.items)) {
        return res.data.items.map((name: string, index: number) => ({
            id: String(index),
            name,
        }));
    }

    throw new Error("Invalid categories format");
};

export default { getCategories };
