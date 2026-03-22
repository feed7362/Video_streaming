import React, {useCallback, useRef, useState, useEffect} from "react";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Label} from "@/components/ui/label";
import {Upload, X, ImagePlus, Film, CheckCircle2, Lock, Globe, ChevronDown} from "lucide-react";
import api from "@api/videoApi";
import categoriesApi from "@api/categoriesApi";
import {useToast} from "@/components/ui/toast/use-toast";
import type {Category} from "@api/types";
import {getErrorMessage} from "@/utils/error";

type Privacy = "public" | "private";

export default function UploadPage() {
    const [videoFile, setVideoFile] = useState<File | null>(null);
    const [thumbnailFile, setThumbnailFile] = useState<File | null>(null);
    const [thumbnailPreview, setThumbnailPreview] = useState<string | null>(null);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [privacy, setPrivacy] = useState<Privacy>("public");
    const [category, setCategory] = useState("");
    const [categories, setCategories] = useState<Category[]>([]);
    const [dragging, setDragging] = useState(false);
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);
    const [showCategoryMenu, setShowCategoryMenu] = useState(false);

    const videoInputRef = useRef<HTMLInputElement>(null);
    const thumbInputRef = useRef<HTMLInputElement>(null);
    const categoryRef = useRef<HTMLDivElement>(null);
    const {toast} = useToast();

    useEffect(() => {
        categoriesApi.getCategories({ plain: true }).then(setCategories).catch(() => {
            toast({title: "Failed to load categories", variant: "destructive"});
        });
    }, [toast]);

    // Close category dropdown on outside click
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (categoryRef.current && !categoryRef.current.contains(e.target as Node)) {
                setShowCategoryMenu(false);
            }
        };
        document.addEventListener("mousedown", handler);
        return () => document.removeEventListener("mousedown", handler);
    }, []);

    const pickVideo = (file: File) => {
        setVideoFile(file);
        if (!title) setTitle(file.name.replace(/\.[^.]+$/, ""));
        setDone(false);
    };

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file?.type.startsWith("video/")) pickVideo(file);
    }, []);

    const onDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setDragging(true);
    };
    const onDragLeave = () => setDragging(false);

    const onThumbChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        setThumbnailFile(file);
        setThumbnailPreview(URL.createObjectURL(file));
    };

    const reset = () => {
        setVideoFile(null);
        setThumbnailFile(null);
        setThumbnailPreview(null);
        setTitle("");
        setDescription("");
        setPrivacy("public");
        setCategory("");
        setDone(false);
    };

    const handleUpload = async () => {
        if (!videoFile) return;
        if (!category) {
            toast({title: "Select a category", variant: "destructive"});
            return;
        }
        setLoading(true);
        try {
            await api.uploadVideo(videoFile, {
                title: title || videoFile.name,
                description,
                thumbnail: thumbnailFile ?? undefined,
                isPublic: privacy === "public",
                category,
            });
            setDone(true);
            toast({title: "Upload complete", description: "Your video has been submitted for processing."});
        } catch (err) {
            toast({title: "Upload failed", description: getErrorMessage(err), variant: "destructive"});
        } finally {
            setLoading(false);
        }
    };

    const formatSize = (bytes: number) => {
        if (bytes >= 1_000_000_000) return `${(bytes / 1_000_000_000).toFixed(1)} GB`;
        return `${(bytes / 1_000_000).toFixed(1)} MB`;
    };

    const selectedCategory = categories.find((c) => c.name.toLowerCase() === category);

    /* ── Phase 1: Drop zone ─────────────────────────────────────── */
    if (!videoFile) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-background px-4">
                <div className="w-full max-w-lg text-center">
                    <h1 className="text-2xl font-semibold mb-2">Upload video</h1>
                    <p className="text-muted-foreground text-sm mb-8">
                        Share your video with the world
                    </p>

                    <div
                        onDrop={onDrop}
                        onDragOver={onDragOver}
                        onDragLeave={onDragLeave}
                        onClick={() => videoInputRef.current?.click()}
                        className={`
                            relative cursor-pointer flex flex-col items-center justify-center
                            rounded-2xl border-2 border-dashed py-20 px-8
                            transition-colors select-none
                            ${dragging
                            ? "border-blue-500 bg-blue-500/10"
                            : "border-border hover:border-muted-foreground/60 hover:bg-muted/30"}
                        `}
                    >
                        <div className="mb-5 rounded-full bg-muted p-5">
                            <Upload className="h-10 w-10 text-muted-foreground"/>
                        </div>
                        <p className="text-base font-medium mb-1">
                            {dragging ? "Drop to upload" : "Drag and drop video files to upload"}
                        </p>
                        <p className="text-muted-foreground text-sm mb-6">
                            Your videos will be private until you publish them
                        </p>
                        <Button variant="default" className="rounded-full px-6" onClick={(e) => {
                            e.stopPropagation();
                            videoInputRef.current?.click();
                        }}>
                            SELECT FILE
                        </Button>
                    </div>

                    <input
                        ref={videoInputRef}
                        type="file"
                        accept="video/*"
                        className="hidden"
                        onChange={(e) => {
                            if (e.target.files?.[0]) pickVideo(e.target.files[0]);
                        }}
                    />
                </div>
            </div>
        );
    }

    /* ── Phase 2: Details ───────────────────────────────────────── */
    return (
        <div className="min-h-screen bg-background flex flex-col">
            {/* Top bar */}
            <div className="flex items-center justify-between border-b px-6 py-4 sticky top-0 bg-background z-10">
                <div className="flex items-center gap-3">
                    <button onClick={reset} className="rounded-full p-1.5 hover:bg-muted transition-colors">
                        <X className="h-5 w-5"/>
                    </button>
                    <div>
                        <p className="font-semibold leading-none">{title || videoFile.name}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">{formatSize(videoFile.size)}</p>
                    </div>
                </div>
                {done ? (
                    <div className="flex items-center gap-2 text-green-500 font-medium text-sm">
                        <CheckCircle2 className="h-4 w-4"/>
                        Uploaded
                    </div>
                ) : (
                    <Button onClick={handleUpload} disabled={loading} className="rounded-full px-6">
                        {loading ? "Uploading…" : "UPLOAD"}
                    </Button>
                )}
            </div>

            {/* Body */}
            <div className="flex flex-1 gap-8 px-8 py-8 max-w-6xl w-full mx-auto">
                {/* Left: form */}
                <div className="flex-1 flex flex-col gap-6 min-w-0">
                    {/* Title */}
                    <div>
                        <Label className="text-sm font-medium mb-1.5 block">Title <span
                            className="text-destructive">*</span></Label>
                        <Input
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Add a title that describes your video"
                            maxLength={100}
                        />
                        <p className="text-xs text-muted-foreground text-right mt-1">{title.length}/100</p>
                    </div>

                    {/* Description */}
                    <div>
                        <Label className="text-sm font-medium mb-1.5 block">Description</Label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Tell viewers about your video"
                            maxLength={5000}
                            rows={5}
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                        <p className="text-xs text-muted-foreground text-right">{description.length}/5000</p>
                    </div>

                    {/* Thumbnail */}
                    <div>
                        <Label className="text-sm font-medium mb-1.5 block">Thumbnail</Label>
                        <p className="text-xs text-muted-foreground mb-3">
                            Upload a picture that shows what's in your video
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => thumbInputRef.current?.click()}
                                className="flex flex-col items-center justify-center w-36 h-24 rounded-lg border-2 border-dashed border-border hover:border-muted-foreground/60 hover:bg-muted/30 transition-colors text-muted-foreground"
                            >
                                <ImagePlus className="h-6 w-6 mb-1"/>
                                <span className="text-xs">Upload thumbnail</span>
                            </button>
                            {thumbnailPreview && (
                                <div className="relative w-36 h-24 rounded-lg overflow-hidden border border-border">
                                    <img src={thumbnailPreview} alt="Thumbnail" className="w-full h-full object-cover"/>
                                    <button
                                        onClick={() => {
                                            setThumbnailFile(null);
                                            setThumbnailPreview(null);
                                        }}
                                        className="absolute top-1 right-1 rounded-full bg-black/60 p-0.5 hover:bg-black/80"
                                    >
                                        <X className="h-3 w-3 text-white"/>
                                    </button>
                                </div>
                            )}
                        </div>
                        <input ref={thumbInputRef} type="file" accept="image/*" className="hidden"
                               onChange={onThumbChange}/>
                    </div>

                    {/* Category */}
                    <div>
                        <Label className="text-sm font-medium mb-1.5 block">Category</Label>
                        <div ref={categoryRef} className="relative">
                            <button
                                onClick={() => setShowCategoryMenu((v) => !v)}
                                className="w-full flex items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm hover:bg-muted/50 transition-colors"
                            >
                                <span className={selectedCategory ? "" : "text-muted-foreground"}>
                                    {selectedCategory?.name ?? "Select a category"}
                                </span>
                                <ChevronDown className="h-4 w-4 text-muted-foreground"/>
                            </button>
                            {showCategoryMenu && (
                                <div
                                    className="absolute z-20 mt-1 w-full max-h-56 overflow-y-auto rounded-md border border-border bg-popover shadow-md">
                                    {categories.map((c) => (
                                        <button
                                            key={c.id}
                                            onClick={() => {
                                                setCategory(c.name.toLowerCase());
                                                setShowCategoryMenu(false);
                                            }}
                                            className={`w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors ${category === c.name.toLowerCase() ? "bg-muted font-medium" : ""}`}
                                        >
                                            {c.name}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Privacy */}
                    <div>
                        <Label className="text-sm font-medium mb-3 block">Visibility</Label>
                        <div className="flex flex-col gap-2">
                            {(["public", "private"] as Privacy[]).map((p) => (
                                <label
                                    key={p}
                                    className={`flex items-center gap-3 rounded-lg border px-4 py-3 cursor-pointer transition-colors ${privacy === p ? "border-blue-500 bg-blue-500/5" : "border-border hover:bg-muted/40"}`}
                                >
                                    <input
                                        type="radio"
                                        name="privacy"
                                        value={p}
                                        checked={privacy === p}
                                        onChange={() => setPrivacy(p)}
                                        className="hidden"
                                    />
                                    <div
                                        className={`flex h-4 w-4 items-center justify-center rounded-full border-2 ${privacy === p ? "border-blue-500" : "border-muted-foreground"}`}>
                                        {privacy === p && <div className="h-2 w-2 rounded-full bg-blue-500"/>}
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {p === "public" ? <Globe className="h-4 w-4"/> : <Lock className="h-4 w-4"/>}
                                        <span className="capitalize text-sm font-medium">{p}</span>
                                    </div>
                                    <span className="text-xs text-muted-foreground ml-auto">
                                        {p === "public" ? "Everyone can watch" : "Only you can watch"}
                                    </span>
                                </label>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right: preview */}
                <div className="w-72 shrink-0 flex flex-col gap-4">
                    <div
                        className="rounded-xl overflow-hidden border border-border bg-black aspect-video flex items-center justify-center">
                        <video
                            src={URL.createObjectURL(videoFile)}
                            controls
                            className="w-full h-full object-contain"
                        />
                    </div>

                    <div className="rounded-lg border border-border bg-muted/30 p-4 text-sm space-y-2">
                        <div className="flex items-start gap-2">
                            <Film className="h-4 w-4 mt-0.5 shrink-0 text-muted-foreground"/>
                            <div className="min-w-0">
                                <p className="font-medium truncate">{videoFile.name}</p>
                                <p className="text-xs text-muted-foreground">{formatSize(videoFile.size)}</p>
                            </div>
                        </div>
                    </div>

                    {done && (
                        <div
                            className="flex items-center gap-2 rounded-lg bg-green-500/10 border border-green-500/30 text-green-600 dark:text-green-400 px-4 py-3 text-sm font-medium">
                            <CheckCircle2 className="h-4 w-4 shrink-0"/>
                            Video uploaded! Processing in background.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
