"use client"

import { AnimatePresence, motion } from "framer-motion"
import { Toast, ToastDescription, ToastTitle } from "./toast"
import { useToast } from "./use-toast"

export function Toaster() {
    const { toasts } = useToast()

    return (
        <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
            <AnimatePresence>
                {toasts.map((toast) =>
                    toast.open ? (
                        <motion.div
                            key={toast.id}
                            initial={{ opacity: 0, y: -20, scale: 0.9 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                        >
                            <Toast>
                                <div className="grid gap-1">
                                    {toast.title && <ToastTitle>{toast.title}</ToastTitle>}
                                    {toast.description && <ToastDescription>{toast.description}</ToastDescription>}
                                </div>
                            </Toast>
                        </motion.div>
                    ) : null
                )}
            </AnimatePresence>
        </div>
    )
}
