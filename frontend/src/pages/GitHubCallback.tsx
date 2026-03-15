import { useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "react-hot-toast";

export default function GitHubCallback() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { refreshUser } = useAuth();
    const handled = useRef(false);

    useEffect(() => {
        if (handled.current) return;
        handled.current = true;

        const token = searchParams.get("token");
        if (!token) {
            toast.error("GitHub login failed: no token received");
            navigate("/login", { replace: true });
            return;
        }

        localStorage.setItem("token", token);
        refreshUser().then(() => {
            toast.success("Logged in with GitHub");
            navigate("/", { replace: true });
        });
    }, []);

    return (
        <div className="flex min-h-screen items-center justify-center">
            <p className="text-gray-500">Completing GitHub login...</p>
        </div>
    );
}
