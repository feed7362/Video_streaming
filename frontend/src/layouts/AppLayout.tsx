import { Outlet } from "react-router-dom";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarProvider, useSidebar } from "@/components/ui/sidebar";
import { SiteHeader } from "@/components/site-header";
import { Toaster } from "@/components/ui/toast/toaster";

function LayoutInner() {
    const { open } = useSidebar();
    return (
        <div className="h-screen flex flex-col [--header-height:56px]">
            <SiteHeader />
            <AppSidebar />
            <main
                className="flex-1 min-h-0 overflow-y-auto transition-all duration-200"
                style={{
                    marginTop: "var(--header-height)",
                    marginLeft: open ? "224px" : "72px",
                }}
            >
                <Outlet />
            </main>
            <Toaster />
        </div>
    );
}

export default function AppLayout() {
    return (
        <SidebarProvider defaultOpen={false}>
            <LayoutInner />
        </SidebarProvider>
    );
}
