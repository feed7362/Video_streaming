import * as React from "react"
import { cn } from "@/lib/utils"
import { toastVariants, type ToastProps } from "./toast-variants"

export { type ToastProps } from "./toast-variants"
export { type ToastActionElement } from "./toast-variants"

export const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
    ({ className, ...props }, ref) => (
        <div ref={ref} className={cn(toastVariants(), className)} {...props} />
    )
)
Toast.displayName = "Toast"

export const ToastTitle = ({
    className,
    ...props
}: React.HTMLAttributes<HTMLHeadingElement>) => (
    <div className={cn("font-semibold", className)} {...props} />
)

export const ToastDescription = ({
    className,
    ...props
}: React.HTMLAttributes<HTMLParagraphElement>) => (
    <div className={cn("text-sm opacity-90", className)} {...props} />
)
