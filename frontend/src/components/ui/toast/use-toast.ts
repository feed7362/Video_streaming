import * as React from "react"
import type { ToastProps, ToastActionElement } from "./toast"

const TOAST_LIMIT = 1

type ToasterToast = ToastProps & {
    id: string
    title?: string
    description?: string
    action?: ToastActionElement
}

let count = 0
function genId() {
    count = (count + 1) % Number.MAX_SAFE_INTEGER
    return count.toString()
}

type Action =
    | { type: "ADD_TOAST"; toast: ToasterToast }
    | { type: "UPDATE_TOAST"; toast: Partial<ToasterToast> }
    | { type: "DISMISS_TOAST"; toastId?: string }
    | { type: "REMOVE_TOAST"; toastId?: string }

function reducer(state: ToasterToast[], action: Action): ToasterToast[] {
    switch (action.type) {
        case "ADD_TOAST":
            return [...state, action.toast].slice(0, TOAST_LIMIT)
        case "UPDATE_TOAST":
            return state.map((t) => (t.id === action.toast.id ? { ...t, ...action.toast } : t))
        case "DISMISS_TOAST":
            return state.map((t) => (t.id === action.toastId ? { ...t, open: false } : t))
        case "REMOVE_TOAST":
            return state.filter((t) => t.id !== action.toastId)
        default:
            return state
    }
}

const listeners: Array<(toasts: ToasterToast[]) => void> = []
let memoryState: ToasterToast[] = []

function notify(toasts: ToasterToast[]) {
    memoryState = toasts
    listeners.forEach((listener) => listener(toasts))
}

export function toast(props: Omit<ToasterToast, "id">) {
    const id = genId();

    notify([{ ...props, id, open: true }, ...memoryState]);

    setTimeout(() => {
        dispatch({ type: "REMOVE_TOAST", toastId: id });
    }, 2000);

    return {
        id,
        dismiss: () => dispatch({ type: "DISMISS_TOAST", toastId: id }),
        update: (toastProps: Partial<ToasterToast>) =>
            dispatch({ type: "UPDATE_TOAST", toast: { ...toastProps, id } }),
    };
}

function dispatch(action: Action) {
    memoryState = reducer(memoryState, action)
    notify(memoryState)

    if (action.type === "DISMISS_TOAST") {
        const toastId = action.toastId

        setTimeout(() => {
            dispatch({ type: "REMOVE_TOAST", toastId })
        }, 2000)
    }
}

export function useToast() {
    const [toasts, setToasts] = React.useState<ToasterToast[]>(memoryState)

    React.useEffect(() => {
        listeners.push(setToasts)
        return () => {
            const index = listeners.indexOf(setToasts)
            if (index > -1) listeners.splice(index, 1)
        }
    }, [])

    return {
        toasts,
        toast,
        dismiss: (toastId?: string) => dispatch({ type: "DISMISS_TOAST", toastId }),
    }
}
