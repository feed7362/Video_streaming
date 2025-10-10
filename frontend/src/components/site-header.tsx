import {Command, SidebarIcon} from "lucide-react"
import {SearchForm} from "@/components/search-form"
import {Button} from "@/components/ui/button"
import {useSidebar} from "@/components/ui/sidebar"
import {NavUser} from "@/components/nav-user";
import {ModeToggle} from "@/components/mode-toggle";

const data = {
    user: {
        name: "shadcn",
        email: "m@example.com",
        avatar: "/avatars/shadcn.jpg",
    }
}

export function SiteHeader() {
    const {toggleSidebar} = useSidebar()

    return (
        <header className="bg-background sticky top-0 z-50 border-b">
            <div className="flex h-[var(--header-height)] w-full items-center px-4">
                {/* LEFT: Brand */}
                <div className="flex items-center gap-2">
                    <Button
                        className="h-8 w-8"
                        variant="ghost"
                        size="icon"
                        onClick={toggleSidebar}
                    >
                        <SidebarIcon/>
                    </Button>
                    <Button size="lg" variant="ghost" asChild>
                        <a href="/" className="flex items-right gap-2 w-auto px-4">
                            <div
                                className="bg-sidebar-primary text-sidebar-primary-foreground flex size-8 items-center justify-center rounded-lg">
                                <Command className="size-5"/>
                            </div>
                            <div className="grid text-left text-sm leading-tight">
                                <span className="truncate font-medium">Acme Inc</span>
                                <span className="truncate text-xs">Enterprise</span>
                            </div>
                        </a>
                    </Button>

                </div>

                {/* CENTER: Search */}
                <div className="flex-1 flex justify-center">
                    <SearchForm className="w-full sm:w-150 mx-auto"/>
                </div>

                {/* RIGHT: ModeToggle, NavUser, Sidebar Toggler */}
                <div className="flex items-center gap-2">
                    <ModeToggle/>
                    <NavUser user={data.user}/>
                </div>
            </div>
        </header>

    )
}
