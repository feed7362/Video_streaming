import { useEffect, useState, useCallback } from "react";
import categoriesApi from "@api/categoriesApi";
import type { Category } from "@api/types";
import { useToast } from "@/components/ui/toast/use-toast";

interface UseFetchCategoriesResult {
  categories: string[];
  active: string;
  setActive: React.Dispatch<React.SetStateAction<string>>;
}

export function useFetchCategories(): UseFetchCategoriesResult {
  const [categories, setCategories] = useState<string[]>([]);
  const [active, setActive] = useState<string>("All");
  const { toast } = useToast();

  const fetchCategories = useCallback(async () => {
    try {
      const data: Category[] = await categoriesApi.getCategories();
      setCategories(["All", ...data.map((c) => c.name)]);
      setActive("All");
    } catch (err) {
      console.error("Failed to load categories", err);
      toast({
        title: "Failed to load categories",
        variant: "destructive",
      });
    }
  }, [toast]);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  return { categories, active, setActive };
}
