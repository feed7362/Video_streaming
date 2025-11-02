import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { ArrowBigUpDash } from "lucide-react";
import { useTheme } from "@/components/theme-provider";
import api from "@api/videoApi";

export default function Upload() {
    const [videoFile, setVideoFile] = useState<File | undefined>(undefined);
    const [thumbnailFile, setThumbnailFile] = useState<File | undefined>(undefined);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [isPrivate, setIsPrivate] = useState(false);
    const [loading, setLoading] = useState(false);
    const { theme } = useTheme();

    const videoInputRef = useRef<HTMLInputElement>(null);
    const thumbInputRef = useRef<HTMLInputElement>(null);

    const handleVideoSelect = () => videoInputRef.current?.click();
    const handleThumbSelect = () => thumbInputRef.current?.click();

    const handleUpload = async () => {
        if (!videoFile) return alert("Please, choose a video");

        setLoading(true);
        try {
            const url = await api.uploadVideo(videoFile, {
                title,
                description,
                thumbnail: thumbnailFile,
                isPrivate,
            });
            alert(`Video uploaded successfully!\nURL: ${url}`);
            setVideoFile(undefined);
            setThumbnailFile(undefined);
            setTitle("");
            setDescription("");
            setIsPrivate(false);
        } catch (err) {
            console.error(err);
            alert("Error uploading video");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="overflow-y-auto h-screen flex items-center justify-center mt-12 sm:mt-20 px-4">
            <Card className="w-full max-w-3xl text-center p-4 sm:p-6 md:p-8">
                <CardHeader className="mb-4">
                    <CardTitle className="text-xl sm:text-2xl md:text-3xl mb-2">
                        Upload Video
                    </CardTitle>
                </CardHeader>

                <CardContent className="flex flex-col items-center justify-center space-y-6">
                    <ArrowBigUpDash
                        className={`h-20 w-20 sm:h-24 sm:w-24 md:h-28 md:w-28 ${theme === "dark" ? "text-white" : "text-black"}`}
                    />

                    <div className="w-full sm:max-w-md text-left space-y-4">
                        <div>
                            <label className="block mb-1 font-medium">Video name:</label>
                            <input
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                placeholder="Enter video title"
                                required
                                className="w-full bg-gray-800 border border-gray-700 text-white px-3 py-2 rounded focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block mb-1 font-medium">Video description:</label>
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="Enter short description"
                                required
                                className="w-full bg-gray-800 border border-gray-700 text-white px-3 py-2 rounded focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block mb-1 font-medium">Choose thumbnail:</label>
                            <input
                                ref={thumbInputRef}
                                type="file"
                                accept="image/*"
                                style={{ display: "none" }}
                                onChange={(e) => {
                                    if (e.target.files && e.target.files[0]) {
                                        setThumbnailFile(e.target.files[0]);
                                    }
                                }}
                            />
                            <Button type="button" onClick={handleThumbSelect}>
                                {thumbnailFile ? "Change thumbnail" : "Select thumbnail"}
                            </Button>
                            {thumbnailFile && (
                                <img
                                    src={URL.createObjectURL(thumbnailFile)}
                                    alt="Thumbnail preview"
                                    className="mt-2 rounded max-h-40"
                                />
                            )}
                        </div>

                        <div className="flex items-center gap-2 mt-4">
                            <input
                                type="checkbox"
                                id="private"
                                checked={isPrivate}
                                onChange={(e) => setIsPrivate(e.target.checked)}
                                className="w-4 h-4 accent-blue-500"
                            />
                            <label htmlFor="private" className="text-sm sm:text-base">
                                Make video private (default is public)
                            </label>
                        </div>

                        <div className="mt-4">
                            <input
                                ref={videoInputRef}
                                type="file"
                                accept="video/*"
                                style={{ display: "none" }}
                                onChange={(e) => {
                                    if (e.target.files && e.target.files[0]) {
                                        setVideoFile(e.target.files[0]);
                                    }
                                }}
                            />
                            <Button type="button" size="lg" onClick={handleVideoSelect}>
                                {videoFile ? "Change video" : "Select video"}
                            </Button>
                        </div>

                        {videoFile && (
                            <div className="mt-4">
                                <p><strong>File:</strong> {videoFile.name}</p>
                                <p><strong>Size:</strong> {(videoFile.size / 1024 / 1024).toFixed(2)} MB</p>
                                <video
                                    src={URL.createObjectURL(videoFile)}
                                    controls
                                    className="w-full mt-2 rounded max-h-60 sm:max-h-80"
                                />
                                <div className="flex gap-2 mt-2">
                                    <Button type="button" variant="destructive" onClick={() => setVideoFile(undefined)}>
                                        Remove file
                                    </Button>
                                    <Button type="button" onClick={handleUpload} disabled={loading}>
                                        {loading ? "Uploading..." : "Upload video"}
                                    </Button>
                                </div>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
