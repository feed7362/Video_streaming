import { Outlet } from "react-router-dom";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarProvider, useSidebar } from "@/components/ui/sidebar";
import { SiteHeader } from "@/components/site-header";
import { Toaster } from "@/components/ui/toast/toaster";

function MainContent() {
    const { open } = useSidebar();
    return (
        <main
            className="absolute bottom-0 right-0 top-[var(--header-height)] overflow-y-auto transition-all duration-200"
            style={{ left: open ? "224px" : "72px" }}
        >
            <Outlet />
        </main>
    );
}

export default function AppLayout() {
    return (
        <div className="h-screen overflow-hidden [--header-height:calc(--spacing(14))]">
            <SidebarProvider defaultOpen={false}>
                <AppSidebar />
                <SiteHeader />
                <MainContent />
                <Toaster />
            </SidebarProvider>
        </div>
    );
}
