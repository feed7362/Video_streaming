export const timeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);

    const secInHour = 3600;
    const secInDay = 86400;
    const secInWeek = secInDay * 7;
    const secInMonth = secInDay * 30;
    const secInYear = secInDay * 365;

    if (diffSec < secInHour) {
        return "годину тому";
    } else if (diffSec < secInDay) {
        const hours = Math.floor(diffSec / secInHour);
        return `${hours} годин тому`;
    } else if (diffSec < secInWeek) {
        const days = Math.floor(diffSec / secInDay);
        return `${days} дн≥в тому`;
    } else if (diffSec < secInYear) {
        const months = Math.floor(diffSec / secInMonth);
        return `${months} м≥с€ц≥в тому`;
    } else {
        const years = Math.floor(diffSec / secInYear);
        return `${years} рок≥в тому`;
    }
};
