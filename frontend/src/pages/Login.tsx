import { GalleryVerticalEnd } from "lucide-react";
import { LoginForm } from "@/components/login-form";

export default function Login() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-gray-900 via-gray-800 to-black p-4 sm:p-6 md:p-10">
            <div className="flex w-full max-w-sm sm:max-w-md md:max-w-lg flex-col gap-8 bg-gray-950/80 border border-gray-800 shadow-lg rounded-2xl p-6 sm:p-8 backdrop-blur-md">
                <a
                    href="/"
                    className="flex items-center justify-center gap-2 text-white hover:text-primary transition-colors duration-200"
                >
                    <div className="bg-primary text-primary-foreground flex size-8 sm:size-9 items-center justify-center rounded-md">
                        <GalleryVerticalEnd className="size-4 sm:size-5" />
                    </div>
                    <span className="text-lg sm:text-xl md:text-2xl font-semibold">
                        Acme Inc.
                    </span>
                </a>

                <div className="w-full">
                    <LoginForm />
                </div>
            </div>
        </div>
    );
}
