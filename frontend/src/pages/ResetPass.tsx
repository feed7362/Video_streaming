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

export default function ResetPass() {
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
                        <form className="w-full">
                            <div className="flex flex-col gap-4">
                                <div className="flex flex-col gap-2">
                                    <Label htmlFor="password">Password</Label>
                                    <Input
                                        id="password"
                                        type="password"
                                        required />
                                </div>
                                <div className="flex flex-col gap-2">
                                    <Label htmlFor="confirm-password">Confirm password</Label>
                                    <Input
                                        id="confirm-password"
                                        type="password"
                                        required />
                                </div>
                                <Link to="/">
                                    <Button type="submit" className="w-full mt-4">
                                        Reset password
                                    </Button>
                                </Link>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
