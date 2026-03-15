import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import { resetPassword } from "@api/authApi";

export default function ResetPass() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const token = searchParams.get("token") || "";

    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!password || !confirmPassword) {
            toast.error("All fields are required");
            return;
        }

        if (password !== confirmPassword) {
            toast.error("Passwords do not match");
            return;
        }

        if (password.length < 8) {
            toast.error("Password must be at least 8 characters long");
            return;
        }

        if (!token) {
            toast.error("Invalid or missing reset token");
            return;
        }

        try {
            setLoading(true);
            await resetPassword(token, password);
            toast.success("Password reset successful! You can now log in.");
            navigate("/login");
        } catch {
            toast.error("Failed to reset password. The link may have expired.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-gradient-to-b from-gray-900 via-gray-800 to-black flex min-h-screen flex-col items-center justify-center p-4 sm:p-6 md:p-10">
            <div className="w-full max-w-sm sm:max-w-md md:max-w-lg lg:max-w-xl flex flex-col gap-6">
                <Card className="w-full">
                    <CardHeader className="text-center">
                        <CardTitle className="text-lg sm:text-xl md:text-2xl">
                            Reset password
                        </CardTitle>
                        <CardDescription className="text-sm sm:text-base md:text-lg">
                            Write your new password
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form className="w-full" onSubmit={handleSubmit}>
                            <div className="flex flex-col gap-4">
                                <div className="flex flex-col gap-2">
                                    <Label htmlFor="password">Password</Label>
                                    <Input
                                        id="password"
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="flex flex-col gap-2">
                                    <Label htmlFor="confirm-password">Confirm password</Label>
                                    <Input
                                        id="confirm-password"
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        required
                                    />
                                </div>
                                <Button type="submit" className="w-full mt-4" disabled={loading}>
                                    {loading ? "Resetting..." : "Reset password"}
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
