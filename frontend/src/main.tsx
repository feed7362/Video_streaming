import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles/index.css";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "@/components/theme-provider";
import { AuthProvider } from "@/contexts/AuthContext";
import AppRouter from "@/routes/AppRouter";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <BrowserRouter>
            <AuthProvider>
                <ThemeProvider>
                    <AppRouter />
                </ThemeProvider>
            </AuthProvider>
        </BrowserRouter>
    </StrictMode>
);
