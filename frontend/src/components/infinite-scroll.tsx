import {useEffect, useRef} from "react";

interface InfiniteScrollProps {
    loadMore: () => void;
    hasMore: boolean;
    children: React.ReactNode;
}

const InfiniteScroll = ({loadMore, hasMore, children}: InfiniteScrollProps) => {
    const loaderRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (!hasMore) return;

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting) {
                    loadMore();
                }
            },
            {threshold: 1.0}
        );

        if (loaderRef.current) {
            observer.observe(loaderRef.current);
        }

        return () => observer.disconnect();
    }, [hasMore, loadMore]);

    return (
        <>
            {children}
            {hasMore && (
                <div ref={loaderRef} style={{height: "40px", background: "transparent"}}/>
            )}
        </>
    );
};

export default InfiniteScroll;
