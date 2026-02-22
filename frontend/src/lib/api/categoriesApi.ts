import clientApi from "./clientApi";
import type { Category } from "./types";

export const getCategories = async (): Promise<Category[]> => {
  const res = await clientApi.get<string[]>("/api/videos/categories");

  console.log("Categories API response:", res.data);

  if (Array.isArray(res.data)) {
    return res.data.map((name) => ({
      id: name.toLowerCase().replace(/\s+/g, "-"),
      name,
    }));
  }

  throw new Error("Invalid categories format: Expected an array of strings");
};

export default { getCategories };
