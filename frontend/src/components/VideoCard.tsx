import { Skeleton } from "@/components/ui/skeleton";
import { Card } from "@/components/ui/card";
import { CARD_CONFIG } from "@/components/CARD_CONFIG.tsx";

interface VideoCardProps {
    id?: string;
    title?: string;
    thumbnail?: string;
    channel_avatar?: string;
    channel_name?: string;
    // ✅ ДОДАНО: Перегляди
    views?: number;
    // ✅ ДОДАНО: Відносна дата (наприклад, "3 дні тому")
    timeAgo?: string;
    loading?: boolean; // if true, render skeleton
}

// Функція для форматування числа переглядів (наприклад, 12000 -> 12K)
const formatViews = (views: number | undefined): string => {
    if (views === undefined) return '';
    if (views < 1000) return views.toString();
    if (views < 1000000) return `${(views / 1000).toFixed(1)}K`;
    return `${(views / 1000000).toFixed(1)}M`;
};


export default function VideoCard({
    title,
    thumbnail,
    channel_avatar,
    channel_name,
    views, // ✅ Прийняття нового пропсу
    timeAgo, // ✅ Прийняття нового пропсу
    loading = false,
}: VideoCardProps) {
    const { height, avatarSize, metaRatio } = CARD_CONFIG;

    const metaHeight = height * metaRatio;
    const thumbnailHeight = height * (1 - metaRatio);

    // Форматуємо перегляди для відображення
    const formattedViews = formatViews(views);
    // Створюємо рядок метаданих: "1.2K переглядів · 3 дні тому"
    const metaText = `${formattedViews} переглядів${timeAgo ? ` · ${timeAgo}` : ''}`;


    if (loading) {
        return (
            <div className="w-full">
                <div className="flex flex-col gap-0 w-full" style={{ height }}>
                    <Skeleton
                        className="rounded-t-xl block w-full"
                        style={{ height: thumbnailHeight }}
                    />
                    <div className="flex items-center gap-3 px-2" style={{ height: metaHeight }}>
                        <Skeleton className="rounded-full" style={{ width: avatarSize, height: avatarSize }} />
                        <div className="flex-1 min-w-0">
                            <Skeleton className="h-4 mb-2" style={{ width: "60%" }} />
                            {/* Скелетон для метаданих */}
                            <Skeleton className="h-4" style={{ width: "40%" }} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (

        <Card className="p-0 gap-0 rounded-xl overflow-hidden w-full" style={{ height }}>
            <img
                src={thumbnail}
                alt={title}
                className="rounded-t-xl block w-full"
                style={{ height: thumbnailHeight, objectFit: "cover", display: "block" }}
            />
            <div className="flex items-start gap-3 px-3 py-2" style={{ height: metaHeight }}>
                <img
                    className="avatar-img rounded-full"
                    src={channel_avatar}
                    alt={channel_name || "channel avatar"}
                    width={avatarSize}
                    height={avatarSize}
                    decoding="async"
                    loading="lazy"
                    style={{ width: avatarSize, height: avatarSize, display: "block", objectFit: "cover" }}
                />
                <div className="flex flex-col flex-1 min-w-0">
                    <h2 className="font-semibold truncate">{title}</h2>
                    <h4 className="text-sm text-gray-500 truncate">{channel_name}</h4>
                    {/* ✅ ВИПРАВЛЕНО: Використання обчисленого metaText */}
                    <h3 className="text-sm text-gray-500">
                        {metaText}
                    </h3>
                </div>
            </div>
        </Card>
    );
}