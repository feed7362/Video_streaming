import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { ArrowBigUpDash } from "lucide-react";
import { useTheme } from "@/components/theme-provider";

export default function Upload() {
    const [file, setFile] = useState<File | null>(null);
    const { theme } = useTheme();

    return (
        <div className="flex items-center justify-center mt-12 sm:mt-20 px-4">
            <Card className="w-full max-w-3xl text-center p-4 sm:p-6 md:p-8 max-h-[90vh] sm:max-h-[80vh] overflow-auto">
                <CardHeader className="mb-4">
                    <CardTitle className="text-xl sm:text-2xl md:text-3xl mb-2">Upload Video</CardTitle>
                    <CardDescription className="text-sm sm:text-base md:text-lg">
                        Drag files here or click the button below to select them from your computer.
                    </CardDescription>
                </CardHeader>

                <CardContent className="flex flex-col items-center justify-center space-y-6">
                    <ArrowBigUpDash
                        className={`h-20 w-20 sm:h-24 sm:w-24 md:h-28 md:w-28 ${theme === "dark" ? "text-white" : "text-black"}`}
                    />
                    <input
                        id="file-upload"
                        type="file"
                        accept="video/*"
                        className="hidden"
                        onChange={(e) => {
                            if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
                        }}
                    />
                    <label htmlFor="file-upload">
                        <Button type="button" size="lg">
                            {file ? "Change file" : "Select files"}
                        </Button>
                    </label>

                    {file && (
                        <div className="mt-4 text-left w-full sm:max-w-md overflow-auto">
                            <p><strong>File:</strong> {file.name}</p>
                            <p><strong>Size:</strong> {(file.size / 1024 / 1024).toFixed(2)} MB</p>
                            <video
                                src={URL.createObjectURL(file)}
                                controls
                                className="w-full mt-2 rounded max-h-60 sm:max-h-80"
                            />
                            <Button
                                type="button"
                                variant="destructive"
                                className="mt-2"
                                onClick={() => setFile(null)}
                            >
                                Remove file
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
