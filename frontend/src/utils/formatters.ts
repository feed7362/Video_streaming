
export const formatViews = (views: number | undefined): string => {
    if (views === undefined) return '';
    if (views < 1000) return `${views}`;
    if (views < 1000000) return `${(views / 1000).toFixed(1).replace(/\.0$/, '')}K`;
    return `${(views / 1000000).toFixed(1).replace(/\.0$/, '')}M`;
};