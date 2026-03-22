import clientApi from "./clientApi";
import type { Category } from "./types";

export const getCategories = async (
  p: { plain?: boolean } = {},
): Promise<Category[]> => {
  const res = await clientApi.get<string[]>("/api/videos/categories", {
    params: { plain: p.plain ? "true" : "false" },
  });

  if (Array.isArray(res.data)) {
    return res.data.map((name) => ({
      id: name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
      name,
    }));
  }

  throw new Error("Invalid categories format: Expected an array of strings");
};

export default { getCategories };
