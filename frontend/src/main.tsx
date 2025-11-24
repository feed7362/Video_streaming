import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles/index.css";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "@/components/theme/theme-provider";
import AppRouter from "@/routes/AppRouter";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <BrowserRouter>
            <ThemeProvider>
                <AppRouter />
            </ThemeProvider>
        </BrowserRouter>
    </StrictMode>
);
