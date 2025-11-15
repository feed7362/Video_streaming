import { Outlet } from "react-router-dom";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";
import { SiteHeader } from "@/components/site-header";
import { Toaster } from "@/components/ui/toast/toaster";

export default function AppLayout() {
    return (
        <div className="h-screen flex flex-col [--header-height:calc(--spacing(14))]">
            <SidebarProvider className="flex flex-col" defaultOpen={false}>
                <AppSidebar />
                <SiteHeader />
                <main className="flex-1 overflow-y-auto">
                    <Outlet />
                </main>
                <Toaster />
            </SidebarProvider>
        </div>
    );
}
