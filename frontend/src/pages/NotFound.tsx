import {Separator} from "@/components/ui/separator";

export default function NotFound() {
    return (
        <div className="flex items-center justify-center min-h-screen ">
            <div className="flex items-center space-x-6 text-center">
                <h1 className="text-6xl font-bold">404</h1>
                <Separator orientation="vertical" className="!h-24 !bg-white w-px"/>
                <h2 className="text-2xl">This page could not be found.</h2>
            </div>
        </div>
    );
}
