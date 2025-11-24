import { useRef, useState, useEffect } from "react";
import { useTheme } from "@/components/theme/theme-provider";
import api from "@api/videoApi";
import categoriesApi from "@api/categoriesApi";
import { useToast } from "@/components/ui/toast/use-toast";
import type { Category } from "../../types/category";
import { getErrorMessage } from "@/utils/error";

export function useUpload() {
    const [videoFile, setVideoFile] = useState<File | undefined>();
    const [thumbnailFile, setThumbnailFile] = useState<File | undefined>();
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [isPrivate, setIsPrivate] = useState(false);
    const [category, setCategory] = useState<string>("");
    const [categories, setCategories] = useState<Category[]>([]);

    const [loading, setLoading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<string | null>(null);
    const { theme } = useTheme();
    const { toast } = useToast();

    const videoInputRef = useRef<HTMLInputElement | null>(null);
    const thumbInputRef = useRef<HTMLInputElement | null>(null);

    useEffect(() => {
        categoriesApi
            .getCategories()
            .then((data: Category[]) => setCategories(data))
            .catch((err) => {
                console.error("Failed to load categories", err);
                toast({ title: "Failed to load categories", variant: "destructive" });
            });
    }, [toast]);

    useEffect(() => {
        if (!uploadStatus) return;
        toast({ title: uploadStatus });
    }, [uploadStatus, toast]);

    const handleUpload = async () => {
        if (!videoFile) {
            toast({ title: "Select video", variant: "destructive" });
            return;
        }
        if (!category) {
            toast({ title: "Select category", variant: "destructive" });
            return;
        }

        setLoading(true);
        try {
            const isPublic = !isPrivate;
            const res = await api.uploadVideo(videoFile, {
                title,
                description,
                thumbnail: thumbnailFile,
                isPublic,
                category,
            });

            const successMessage = res?.status ?? "Uploaded successfully";
            setUploadStatus(successMessage);
            toast({ title: "Upload complete", description: successMessage, variant: "default" });

            setVideoFile(undefined);
            setThumbnailFile(undefined);
            setTitle("");
            setDescription("");
            setIsPrivate(false);
            setCategory("");
        } catch (err: unknown) {
            const msg = getErrorMessage(err);
            setUploadStatus(msg);
            toast({ title: "Upload error", description: msg, variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };
    return {
        videoFile,
        setVideoFile,
        thumbnailFile,
        setThumbnailFile,
        title,
        setTitle,
        description,
        setDescription,
        isPrivate,
        setIsPrivate,
        category,
        setCategory,
        categories,
        loading,
        uploadStatus,
        videoInputRef,
        thumbInputRef,
        theme,
        handleUpload,
    };
}