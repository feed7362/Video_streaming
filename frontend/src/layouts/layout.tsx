import { Toaster } from "@/components/ui/toast/toaster";

export default function Layout({ children }: { children: React.ReactNode }) {
    return (
        <>
            {children}
            <Toaster />
        </>
    );
}
