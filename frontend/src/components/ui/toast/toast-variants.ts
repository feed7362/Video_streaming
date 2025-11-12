import { cva, type VariantProps } from "class-variance-authority"

export const toastVariants = cva(
    "group pointer-events-auto relative flex w-full items-center justify-between space-x-2 overflow-hidden rounded-md border p-4 pr-6 shadow-lg transition-all",
    {
        variants: {
            variant: {
                default: "bg-background text-foreground",
                destructive: "border-destructive bg-destructive text-destructive-foreground",
            },
        },
        defaultVariants: {
            variant: "default",
        },
    }
)

export type ToastActionElement = React.ReactElement | null

export type ToastProps = React.HTMLAttributes<HTMLDivElement> &
    VariantProps<typeof toastVariants> & {
        open?: boolean
        onOpenChange?: (open: boolean) => void
        title?: string
        description?: string
        action?: ToastActionElement
    }
