import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ArrowBigUpDash } from "lucide-react";
import { useUpload } from "@/hooks/upload/useUpload";
export default function Upload() {
    const {
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
        videoInputRef,
        thumbInputRef,
        theme,
        handleUpload,
    } = useUpload();

    return (
        <div className="flex items-center justify-center mt-12 px-4 min-h-screen">
            <Card className="w-full max-w-3xl text-center p-6">
                <CardHeader>
                    <CardTitle className="text-2xl mb-2">Upload Video</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-6">
                    <div className="flex justify-center w-full">
                        <ArrowBigUpDash
                            className={`h-24 w-24 ${theme === "dark" ? "text-white" : "text-black"}`}
                        />
                    </div>

                    <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" className="w-full p-2 rounded border border-input bg-background text-foreground" />
                    <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" className="w-full p-2 rounded border border-input bg-background text-foreground" />

                    <select value={category} onChange={(e) => setCategory(e.target.value)} className="w-full p-2 rounded border border-input bg-background text-foreground">
                        <option value="">Select category</option>
                        {categories.map((c) => (
                            <option key={c.id} value={c.name}>
                                {c.name}
                            </option>
                        ))}
                    </select>

                    <label className="flex gap-2 items-center">
                        <input type="checkbox" checked={isPrivate} onChange={(e) => setIsPrivate(e.target.checked)} /> Private
                    </label>

                    <input ref={thumbInputRef} type="file" accept="image/*" className="hidden" onChange={(e) => e.target.files && setThumbnailFile(e.target.files[0])} />
                    <Button onClick={() => thumbInputRef.current?.click()}>{thumbnailFile ? "Change thumbnail" : "Select thumbnail"}</Button>
                    {thumbnailFile && <img src={URL.createObjectURL(thumbnailFile)} className="max-h-40 rounded mt-2" alt="thumbnail preview" />}

                    <input ref={videoInputRef} type="file" accept="video/*" className="hidden" onChange={(e) => e.target.files && setVideoFile(e.target.files[0])} />
                    <Button onClick={() => videoInputRef.current?.click()}>{videoFile ? "Change video" : "Select video"}</Button>

                    {videoFile && (
                        <div>
                            <video src={URL.createObjectURL(videoFile)} controls className="w-full rounded max-h-80 mt-2" />
                            <Button className="mt-2" disabled={loading} onClick={handleUpload}>
                                {loading ? "Uploading..." : "Upload"}
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
