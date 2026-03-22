import { Skeleton } from "@/components/ui/skeleton";

const THUMB_H = 190;   // px — fixed thumbnail height
const META_H  =  88;   // px — fixed meta row height

interface VideoCardProps {
    id?: string;
    title?: string;
    thumbnail?: string;
    channel_avatar?: string;
    channel_name?: string;
    views?: number;
    timeAgo?: string;
    loading?: boolean;
    /** Render as a compact horizontal row (Watch sidebar) */
    horizontal?: boolean;
}

const formatViews = (views: number | undefined): string => {
    if (views === undefined) return "";
    if (views < 1000) return `${views} views`;
    if (views < 1_000_000) return `${(views / 1000).toFixed(1)}K views`;
    return `${(views / 1_000_000).toFixed(1)}M views`;
};

const Avatar = ({ src, name, size }: { src?: string; name?: string; size: number }) => {
    const initial = (name ?? "?").charAt(0).toUpperCase();
    if (src) {
        return (
            <img
                src={src}
                alt={name}
                width={size}
                height={size}
                className="rounded-full object-cover shrink-0"
                style={{ width: size, height: size }}
                loading="lazy"
                decoding="async"
            />
        );
    }
    return (
        <div
            className="rounded-full bg-muted flex items-center justify-center shrink-0 text-xs font-semibold text-muted-foreground"
            style={{ width: size, height: size }}
        >
            {initial}
        </div>
    );
};

/* ── Skeletons ─────────────────────────────────────────────────────── */
function CardSkeleton({ horizontal }: { horizontal?: boolean }) {
    if (horizontal) {
        return (
            <div className="flex gap-2">
                <Skeleton className="rounded-xl shrink-0" style={{ width: 168, height: 94 }} />
                <div className="flex-1 min-w-0 pt-1 space-y-2">
                    <Skeleton className="h-3.5 w-full" />
                    <Skeleton className="h-3 w-2/3" />
                    <Skeleton className="h-3 w-1/2" />
                </div>
            </div>
        );
    }
    return (
        <div className="flex flex-col" style={{ height: THUMB_H + META_H }}>
            <Skeleton className="rounded-t-xl w-full shrink-0" style={{ height: THUMB_H }} />
            <div className="flex gap-3 px-1 py-2 shrink-0" style={{ height: META_H }}>
                <Skeleton className="rounded-full shrink-0" style={{ width: 36, height: 36 }} />
                <div className="flex-1 min-w-0 space-y-2 pt-1">
                    <Skeleton className="h-3.5 w-full" />
                    <Skeleton className="h-3 w-2/3" />
                    <Skeleton className="h-3 w-1/2" />
                </div>
            </div>
        </div>
    );
}

/* ── Card ─────────────────────────────────────────────────────────── */
export default function VideoCard({
    title,
    thumbnail,
    channel_avatar,
    channel_name,
    views,
    timeAgo,
    loading = false,
    horizontal = false,
}: VideoCardProps) {
    if (loading) return <CardSkeleton horizontal={horizontal} />;

    // Use \u00b7 escape (middle dot) to avoid raw-byte encoding issues
    const meta = [formatViews(views), timeAgo].filter(Boolean).join(" \u00b7 ");

    /* ── Horizontal (Watch sidebar) ───────────────────────────────── */
    if (horizontal) {
        return (
            <div className="flex gap-2 group">
                <div className="relative shrink-0 rounded-xl overflow-hidden bg-muted" style={{ width: 168, height: 94 }}>
                    <img
                        src={thumbnail}
                        alt={title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                        loading="lazy"
                        decoding="async"
                    />
                </div>
                <div className="flex-1 min-w-0 pt-0.5">
                    <p className="text-sm font-semibold line-clamp-2 leading-snug">{title}</p>
                    <p className="text-xs text-muted-foreground mt-1 truncate">{channel_name}</p>
                    {meta && <p className="text-xs text-muted-foreground truncate">{meta}</p>}
                </div>
            </div>
        );
    }

    /* ── Vertical (Home grid) — fixed total height ────────────────── */
    return (
        <div
            className="flex flex-col group cursor-pointer w-full"
            style={{ height: THUMB_H + META_H }}
        >
            {/* Thumbnail — rounded top only, fixed height */}
            <div
                className="relative w-full overflow-hidden rounded-t-xl bg-muted shrink-0"
                style={{ height: THUMB_H }}
            >
                <img
                    src={thumbnail}
                    alt={title}
                    className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    loading="lazy"
                    decoding="async"
                />
            </div>

            {/* Meta — fixed height, overflow hidden so text never expands card */}
            <div
                className="flex gap-3 px-1 py-2 overflow-hidden shrink-0"
                style={{ height: META_H }}
            >
                <div className="pt-0.5 shrink-0">
                    <Avatar src={channel_avatar} name={channel_name} size={36} />
                </div>
                <div className="flex-1 min-w-0 overflow-hidden">
                    <h3 className="text-sm font-semibold line-clamp-2 leading-snug">{title}</h3>
                    <p className="text-xs text-muted-foreground mt-0.5 truncate">{channel_name}</p>
                    {meta && <p className="text-xs text-muted-foreground truncate">{meta}</p>}
                </div>
            </div>
        </div>
    );
}
