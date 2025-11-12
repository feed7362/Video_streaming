// src/utils/timeAgo.ts

// Допоміжна функція для обробки англійської однини/множини
const pluralize = (number: number, unit: string): string => {
    return number === 1 ? `${unit}` : `${unit}s`;
};

export const timeAgo = (dateString: string): string => {
    if (!dateString) return '';

    const date = new Date(dateString);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffSec < 0) return 'in the future';

    const secInMinute = 60;
    const secInHour = 3600;
    const secInDay = 86400;
    const secInMonth = 2629744;
    const secInYear = 31556952;

    // 1. Seconds/Just now
    if (diffSec < secInMinute) {
        return "just now";
    }

    // 2. Minutes
    if (diffSec < secInHour) {
        const minutes = Math.floor(diffSec / secInMinute);
        return `${minutes} ${pluralize(minutes, "minute")} ago`;
    }

    // 3. Hours
    if (diffSec < secInDay) {
        const hours = Math.floor(diffSec / secInHour);
        return `${hours} ${pluralize(hours, "hour")} ago`;
    }

    // 4. Days
    if (diffSec < secInMonth) {
        const days = Math.floor(diffSec / secInDay);
        return `${days} ${pluralize(days, "day")} ago`;
    }

    // 5. Months
    if (diffSec < secInYear) {
        const months = Math.floor(diffSec / secInMonth);
        return `${months} ${pluralize(months, "month")} ago`;
    }

    // 6. Years
    const years = Math.floor(diffSec / secInYear);
    return `${years} ${pluralize(years, "year")} ago`;
};