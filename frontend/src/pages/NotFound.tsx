import { Separator } from "@/components/ui/separator";

export default function NotFound() {
    return (
        <div className="flex items-center justify-center min-h-screen px-4">
            <div className="flex flex-col sm:flex-row items-center text-center sm:space-x-6 space-y-4 sm:space-y-0">
                <h1 className="text-6xl sm:text-7xl font-bold">404</h1>
                <Separator orientation="vertical" className="hidden sm:block h-24 bg-white w-px" />
                <h2 className="text-xl sm:text-2xl">This page could not be found.</h2>
            </div>
        </div>
    );
}
