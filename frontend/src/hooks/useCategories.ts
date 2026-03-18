import React, { useEffect, useState } from "react";
import categoriesApi from "@api/categoriesApi";
import type { Category } from "@api/types";
import { useToast } from "@/components/ui/toast/use-toast";

interface UseFetchCategoriesResult {
  categories: string[];
  active: string;
  setActive: React.Dispatch<React.SetStateAction<string>>;
  isLoading: boolean;
}

export function useFetchCategories(): UseFetchCategoriesResult {
  const [categories, setCategories] = useState<string[]>(["All"]);
  const [active, setActive] = useState<string>("All");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchCategories = async () => {
      setIsLoading(true);
      try {
        const data: Category[] = await categoriesApi.getCategories();
        setCategories(["All", ...data.map((c) => c.name)]);
      } catch (err) {
        console.error("Failed to load categories", err);
        toast({
          title: "Failed to load categories",
          description: "Please check your connection and try again.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategories();
  }, [toast]);

  return { categories, active, setActive, isLoading };
}
