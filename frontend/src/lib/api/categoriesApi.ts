import clientApi from "./clientApi";
import type { Category } from "./types";

export const getCategories = (): Promise<Category[]> => {
    return clientApi.get("/categories").then(res => res.data);
};

export default { getCategories };
