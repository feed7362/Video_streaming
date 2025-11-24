import { useState } from "react";
import { toast } from "react-hot-toast";
import { sendPasswordReset } from "@api/authApi";
export function useForgotPass() {
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!email) {
            toast.error("Please enter your email");
            return;
        }

        try {
            setLoading(true);
            await sendPasswordReset(email);
            toast.success("Password reset email sent!");
            setEmail("");
        } catch (err: unknown) {
            console.error(err);
            toast.error("Failed to send reset email");
        } finally {
            setLoading(false);
        }
    };

    return {
        email,
        setEmail,
        loading,
        handleSubmit,
    };
}