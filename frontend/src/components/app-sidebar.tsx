import * as React from "react";
import { Link, useLocation } from "react-router-dom";
import { useSidebar } from "@/components/ui/sidebar";
import {
    Home,
    PlaySquare,
    Clock,
    ThumbsUp,
    BookMarked,
    Users,
    MonitorPlay,
    Upload,
    Clapperboard,
} from "lucide-react";

const NAV_ITEMS = [
    { icon: Home,        label: "Home",          to: "/" },
    { icon: Users,       label: "Subscriptions", to: "/subscriptions" },
];

const LIBRARY_ITEMS = [
    { icon: Clock,       label: "History",       to: "/history" },
    { icon: PlaySquare,  label: "Watch Later",   to: "/watch-later" },
    { icon: ThumbsUp,    label: "Liked videos",  to: "/liked" },
    { icon: BookMarked,  label: "Playlists",     to: "/playlists" },
];

const CREATOR_ITEMS = [
    { icon: Upload,      label: "Upload",        to: "/upload" },
    { icon: Clapperboard,label: "Creator Studio",to: "/studio" },
    { icon: MonitorPlay, label: "Your videos",   to: "/your-videos" },
];

function NavItem({ icon: Icon, label, to }: { icon: React.ElementType; label: string; to: string }) {
    const { open } = useSidebar();
    const location = useLocation();
    const active = location.pathname === to || (to !== "/" && location.pathname.startsWith(to));

    return (
        <Link
            to={to}
            className={`flex items-center gap-5 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors
                ${active
                    ? "bg-muted font-semibold"
                    : "hover:bg-muted/60 text-foreground/80 hover:text-foreground"
                }
                ${!open ? "justify-center px-2" : ""}
            `}
            title={!open ? label : undefined}
        >
            <Icon className="h-5 w-5 shrink-0" />
            {open && <span className="truncate">{label}</span>}
        </Link>
    );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
    const { open } = useSidebar();
    if (!open) return <div className="my-1 border-t border-border mx-2" />;
    return <p className="px-3 pt-4 pb-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">{children}</p>;
}

export function AppSidebar() {
    const { open } = useSidebar();

    return (
        <aside
            className={`fixed top-[var(--header-height)] left-0 bottom-0 z-40 flex flex-col overflow-y-auto overflow-x-hidden border-r border-border bg-background transition-all duration-200 ${open ? "w-56" : "w-[72px]"}`}
        >
            <nav className="flex flex-col gap-0.5 px-2 py-3">
                {NAV_ITEMS.map((item) => <NavItem key={item.to} {...item} />)}

                <SectionLabel>Library</SectionLabel>
                {LIBRARY_ITEMS.map((item) => <NavItem key={item.to} {...item} />)}

                <SectionLabel>Creator</SectionLabel>
                {CREATOR_ITEMS.map((item) => <NavItem key={item.to} {...item} />)}
            </nav>
        </aside>
    );
}
