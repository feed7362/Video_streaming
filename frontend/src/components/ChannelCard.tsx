import { Card } from "@/components/ui/card";
import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChannelCardProps {
    id?: string;
    channel_avatar?: string;
    channel_name?: string;
    handle?: string;
    subscribers?: string;
    description?: string;
}

export default function ChannelCard({
    channel_avatar,
    channel_name,
    handle = "@channel",
    subscribers = "1m subscribers",
    description = "Channel description...",
}: ChannelCardProps) {
    return (
        <Card className="flex items-start justify-between w-full p-4 border border-border rounded-xl">
            <div className="flex items-start gap-4">
                <img
                    src={channel_avatar}
                    alt={channel_name}
                    className="w-20 h-20 rounded-full object-cover"
                />
                <div className="flex flex-col">
                    <h3 className="text-sm text-gray-500">{channel_name}</h3>
                    <p className="text-sm text-muted-foreground">
                        {handle} • {subscribers}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2 max-w-[700px]">
                        {description}
                    </p>
                </div>
            </div>
            <div className="flex items-center ml-auto">
                <Button
                    variant="outline"
                    className="rounded-full flex items-center gap-2"
                >
                    <Bell className="w-4 h-4" />
                    You are subscribed
                </Button>
            </div>
        </Card>
    );
}
