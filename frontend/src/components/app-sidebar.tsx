import {
    Sidebar,
    SidebarContent,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarFooter,
    SidebarHeader,
    useSidebar,
} from "@/components/ui/sidebar"
import {SidebarIcon, Command} from "lucide-react";
import {Button} from "@/components/ui/button.tsx";
import * as React from "react";

const data = {
    navMain: [
        {
            title: "Getting Started",
            url: "/register",
            items: [
                {
                    title: "Home",
                    url: "/",
                    isActive: true,
                },
                {
                    title: "Upload new video",
                    url: "/upload",
                },
                {
                    title: "Subscriptions",
                    url: "#",
                },
                {
                    title: "History",
                    url: "#",  
                },
                {
                    title: "Liked",
                    url: "#",
                },
                {
                    title: "Watch later",
                    url: "#",
                },
                {
                    title: "Settings",
                    url: "#",
                },
            ],
        },
    ],
}

export function AppSidebar({...props}: React.ComponentProps<typeof Sidebar>) {
    const {toggleSidebar} = useSidebar()

    return (
        <Sidebar
            {...props}
            className="fixed top-0 left-0 h-full z-60" variant="floating" // higher than header
        >
            <SidebarContent>
                <SidebarHeader>
                    <div className="flex items-left">
                        <Button
                            className="h-10 w-10"
                            variant="ghost"
                            size="icon"
                            onClick={toggleSidebar}
                        >
                            <SidebarIcon/>
                        </Button>

                        <SidebarMenuButton size="lg" asChild>
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
                        </SidebarMenuButton>
                    </div>
                </SidebarHeader>

                <SidebarMenu>
                    {data.navMain.flatMap((section) =>
                        section.items.map((item) => (
                            <SidebarMenuItem key={item.title}>
                                <SidebarMenuButton asChild isActive={item.isActive}>
                                    <a href={item.url}>{item.title}</a>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        ))
                    )}
                </SidebarMenu>
            </SidebarContent>

            <SidebarFooter>
                {/*<NavUser user={data.user}/>*/}
            </SidebarFooter>
        </Sidebar>
    )
}
