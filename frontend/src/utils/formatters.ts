
export const formatViews = (views: number | undefined): string => {
    if (views === undefined || views === null) return '';
    // ... ваша логіка форматування
    if (views < 1000) return views.toString();
    if (views < 1000000) return `${(views / 1000).toFixed(1).replace(/\.0$/, '')}K`;
    return `${(views / 1000000).toFixed(1).replace(/\.0$/, '')}M`;
};