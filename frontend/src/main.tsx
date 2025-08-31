import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import './styles/index.css'
import AppRouter from './routes/AppRouter'
import {ThemeProvider} from "@/components/theme-provider"

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
            <AppRouter/>
        </ThemeProvider>
    </StrictMode>,
)
