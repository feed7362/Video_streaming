import { useEffect, useRef } from "react";

interface InfiniteScrollProps {
    loadMore: () => void;
    hasMore: boolean;
    children: React.ReactNode;
    rootMargin?: string;
}

const InfiniteScroll = ({
    loadMore,
    hasMore,
    children,
    rootMargin = "300px",
}: InfiniteScrollProps) => {
    const loaderRef = useRef<HTMLDivElement | null>(null);
    const observerRef = useRef<IntersectionObserver | null>(null);

    useEffect(() => {
        if (!hasMore || !loaderRef.current) return;

        // якщо вже є спостерігач — очищаємо
        if (observerRef.current) observerRef.current.disconnect();

        observerRef.current = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting) {
                    loadMore();
                }
            },
            { root: null, rootMargin, threshold: 0.1 }
        );

        observerRef.current.observe(loaderRef.current);

        return () => {
            observerRef.current?.disconnect();
        };
    }, [hasMore, loadMore, rootMargin]);

    return (
        <>
            {children}
            {hasMore && (
                <div
                    ref={loaderRef}
                    style={{
                        height: "1px",
                        marginTop: "200px",
                        background: "transparent",
                    }}
                />
            )}
        </>
    );
};

export default InfiniteScroll;
