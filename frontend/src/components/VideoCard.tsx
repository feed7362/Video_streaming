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
}

export default function VideoCard({
    title,
    thumbnail,
    channel_avatar,
    channel_name,
    views,
    timeAgo,
    privacy,
    loading = false,
}: VideoCardProps) {

    // Скелетон
    if (loading) {
        return (
            <div className="flex flex-col gap-3 w-full p-2">
                <Skeleton className="w-full aspect-video rounded-xl" />
                <div className="flex gap-3 px-1">
                    <Skeleton className="h-9 w-9 rounded-full shrink-0" />
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
        // Головний контейнер:
        // rounded-xl overflow-hidden: Задає загальну форму картки.
        // hover:bg-gray-100: Вмикає сірий фон при наведенні.
        <div className="group flex flex-col w-full hover:bg-gray-100 cursor-pointer rounded-xl overflow-hidden transition-colors duration-200">

            {/* Картинка */}
            <div className="relative w-full aspect-video bg-gray-100">
                <img
                    src={thumbnail}
                    alt={title}
                    className="h-full w-full object-cover transition-transform duration-200 group-hover:scale-105"
                />
            </div>

            {/* Інформація під картинкою */}
            {/* ЗМІНА: Додано rounded-b-xl. 
               Це явно заокруглює нижні кути цього блоку, гарантуючи, 
               що сірий фон при наведенні буде мати правильну форму внизу. */}
            <div className="flex items-start gap-3 p-3 rounded-b-xl">
                {/* Аватар */}
                <img
                    src={channel_avatar}
                    alt={channel_name}
                    className="h-9 w-9 rounded-full object-cover shrink-0"
                />

                {/* Текст */}
                <div className="flex flex-col overflow-hidden">
                    <h3 className="font-semibold text-base leading-snug truncate text-black group-hover:text-gray-900" title={title}>
                        {title}
                    </h3>

                    <div className="mt-1 text-sm text-gray-600 flex flex-col">
                        <span className="hover:text-gray-900">{channel_name}</span>

                        <div className="flex items-center flex-wrap gap-1 mt-0.5">
                            {isPrivate && (
                                <VideoPrivacyStatus privacy={privacy!} className="mr-1 scale-90 origin-left" />
                            )}
                            <span>{metaText}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}