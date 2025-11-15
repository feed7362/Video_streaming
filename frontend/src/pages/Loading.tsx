import { Loader } from "lucide-react";

export default function Loading() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-black text-white">
            <Loader className="h-28 w-28 color-white animate-spin" style={{ animationDuration: "3s" }} />
            <p className="mt-4 text-lg opacity-80">
                Please wait while we load the content for you...
            </p>
        </div>
    );
}
