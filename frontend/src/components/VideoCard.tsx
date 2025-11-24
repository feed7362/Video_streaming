import { Skeleton } from "@/components/ui/skeleton";
import { formatViews } from "@/utils/formatters";
import { VideoPrivacyStatus } from "@/components/VideoPrivacyStatus";

interface VideoCardProps {
    id?: string;
    title?: string;
    thumbnail?: string;
    channel_avatar?: string;
    channel_name?: string;
    views?: number;
    timeAgo?: string;
    loading?: boolean;
    privacy?: string;
    description?: string; // Можна додати опис, якщо він є в даних
    // Новий проп для перемикання вигляду
    variant?: "vertical" | "horizontal";
}

export default function VideoCard({
    title,
    thumbnail,
    channel_avatar,
    channel_name,
    views,
    timeAgo,
    privacy,
    description,
    loading = false,
    variant = "vertical",
}: VideoCardProps) {

    const isHorizontal = variant === "horizontal";

    if (loading) {
        return (
            <div className={`flex w-full gap-3 p-2 ${isHorizontal ? 'flex-col sm:flex-row' : 'flex-col'}`}>
                <Skeleton
                    className={`rounded-xl aspect-video ${isHorizontal ? 'w-full sm:w-[360px] shrink-0' : 'w-full'}`}
                />
                <div className="flex gap-3 px-1 w-full">
                    {!isHorizontal && <Skeleton className="h-9 w-9 rounded-full shrink-0" />}
                    <div className="flex flex-col gap-2 w-full">
                        <Skeleton className="h-4 w-[90%]" />
                        <Skeleton className="h-4 w-[60%]" />
                    </div>
                </div>
            </div>
        );
    }

    const formattedViews = formatViews(views);
    const metaText = `${formattedViews} views • ${timeAgo || ''}`;
    const isPrivate = privacy && privacy.toLowerCase() !== 'public';

    return (
        <div
            className={`
                group flex w-full cursor-pointer rounded-xl overflow-hidden transition-colors duration-200 hover:bg-gray-100
                ${isHorizontal ? 'flex-col sm:flex-row gap-4 p-2' : 'flex-col gap-3'} 
            `}
        >

            <div
                className={`
                    relative bg-gray-100 aspect-video rounded-xl overflow-hidden
                    ${isHorizontal ? 'w-full sm:w-[360px] shrink-0' : 'w-full'}
                `}
            >
                <img
                    src={thumbnail}
                    alt={title}
                    className="h-full w-full object-cover transition-transform duration-200 group-hover:scale-105"
                />
            </div>

            <div className={`flex items-start gap-3 ${isHorizontal ? 'py-1' : 'p-3 rounded-b-xl'}`}>
                {!isHorizontal && (
                    <img
                        src={channel_avatar}
                        alt={channel_name}
                        className="h-9 w-9 rounded-full object-cover shrink-0"
                    />
                )}

                <div className="flex flex-col overflow-hidden gap-1">
                    <h3 className={`font-semibold text-black group-hover:text-gray-900 leading-snug ${isHorizontal ? 'text-lg line-clamp-2' : 'text-base truncate'}`} title={title}>
                        {title}
                    </h3>

                    <div className="text-sm text-gray-600 flex items-center flex-wrap gap-1">
                        {isPrivate && (
                            <VideoPrivacyStatus privacy={privacy!} className="mr-1 scale-90 origin-left" />
                        )}
                        <span>{metaText}</span>
                    </div>

                    {isHorizontal && (
                        <div className="flex items-center gap-2 mt-2 py-2">
                            <img
                                src={channel_avatar}
                                alt={channel_name}
                                className="h-6 w-6 rounded-full object-cover shrink-0"
                            />
                            <span className="text-sm text-gray-600 hover:text-gray-900">{channel_name}</span>
                        </div>
                    )}

                    {!isHorizontal && (
                        <div className="text-sm text-gray-600 hover:text-gray-900">
                            {channel_name}
                        </div>
                    )}

                    {isHorizontal && description && (
                        <p className="text-sm text-gray-500 line-clamp-2 mt-1 hidden sm:block">
                            {description}
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}