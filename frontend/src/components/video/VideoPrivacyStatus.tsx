import { Badge } from "@/components/ui/badge";
import type { VideoPrivacyStatusProps } from "../../types/video";
import React from "react";

const Icons_Paths = {
    Private: "/lock-keyhole.svg",
    Public: "/lock-keyhole-open.svg",
}

export const VideoPrivacyStatus: React.FC<VideoPrivacyStatusProps & { className?: string }> = ({
    privacy,
    className = ""
}) => {
    const status = privacy?.toLowerCase() || 'Public';
    let iconSrc: string = Icons_Paths.Public;
    let text: string = "Public";

    if (status === "Private") {
        iconSrc = Icons_Paths.Private;
        text = "Private";
    } else {
        iconSrc = Icons_Paths.Public;
        text = "Public";
    }

    return (
        <Badge
            variant="secondary"
            className={`flex items-center space-x-1 ${className}`}
        >
            <img
                src={iconSrc}
                alt={`${text} icon`}
                className="w-4 h-4"
            />
            <span className={`text-xs font-medium`}>{text}</span>
        </Badge>
    );
};