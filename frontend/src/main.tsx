import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles/index.css";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "@/components/theme-provider";
import { AuthProvider } from "@/contexts/AuthContext";
import AppRouter from "@/routes/AppRouter";
import { Toaster as SonnerToaster } from "@/components/ui/sonner";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <BrowserRouter>
            <AuthProvider>
                <ThemeProvider>
                    <AppRouter />
                    <SonnerToaster position="top-right" richColors closeButton />
                </ThemeProvider>
            </AuthProvider>
        </BrowserRouter>
    </StrictMode>
);
