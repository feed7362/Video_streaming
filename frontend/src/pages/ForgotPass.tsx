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
import { Link } from "react-router-dom";

export default function ForgotPass() {
    return (
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-900 via-gray-800 to-black p-4 sm:p-6 md:p-10">
            <Card className="w-full max-w-sm sm:max-w-md md:max-w-lg bg-gray-950/80 border-gray-800 shadow-lg backdrop-blur-md">
                <CardHeader className="text-center space-y-2">
                    <CardTitle className="text-lg sm:text-xl md:text-2xl font-semibold text-white">
                        Forgot your password?
                    </CardTitle>
                    <CardDescription className="text-gray-400 text-sm sm:text-base">
                        Write your email to recover the password
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form className="flex flex-col gap-5">
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="email" className="text-gray-300">
                                Email
                            </Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="m@example.com"
                                required
                                className="bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <Link to="/" className="w-full">
                            <Button
                                type="submit"
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm sm:text-base"
                            >
                                Recover password
                            </Button>
                        </Link>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
