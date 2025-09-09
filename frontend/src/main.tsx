import {StrictMode} from "react";
import {createRoot} from "react-dom/client";
import "./styles/index.css";
import AppRouter from "@/routes/AppRouter";
import {AppSidebar} from "@/components/app-sidebar";
import {SidebarProvider} from "@/components/ui/sidebar";
import {SiteHeader} from "@/components/site-header";
import {ThemeProvider} from "@/components/theme-provider";
import {BrowserRouter, useLocation} from "react-router-dom";

function AppContent() {
    const location = useLocation();

    const hideLayout = ["/login", "/register", "/reset", "/forgot", "/privacy", "/terms"];
    const showLayout = !hideLayout.includes(location.pathname);

    return (
        <div className="h-screen flex flex-col [--header-height:calc(--spacing(14))]">
            {showLayout ? (
                <SidebarProvider className="flex flex-col" defaultOpen={false}>
                    <AppSidebar/>
                    <SiteHeader/>
                    <main className="flex-1 overflow-y-auto">
                        <AppRouter/>
                    </main>
                </SidebarProvider>
            ) : (
                <AppRouter/>
            )}
        </div>
    );
}

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <BrowserRouter>
            <ThemeProvider>
                <AppContent/>
            </ThemeProvider>
        </BrowserRouter>
    </StrictMode>
);
