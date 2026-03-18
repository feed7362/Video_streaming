import { useCallback } from "react";

export function useDraggableScroll() {
    const onMouseDown = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
        const container = e.currentTarget;
        const startX = e.pageX - container.offsetLeft;
        const scrollLeft = container.scrollLeft;

        const mouseMoveHandler = (eMove: MouseEvent) => {
            eMove.preventDefault();
            const x = eMove.pageX - container.offsetLeft;
            const walk = (x - startX) * 1.5;
            container.scrollLeft = scrollLeft - walk;
        };

        const mouseUpHandler = () => {
            document.removeEventListener("mousemove", mouseMoveHandler);
            document.removeEventListener("mouseup", mouseUpHandler);
        };

        document.addEventListener("mousemove", mouseMoveHandler);
        document.addEventListener("mouseup", mouseUpHandler);
    }, []);

    return { onMouseDown };
}