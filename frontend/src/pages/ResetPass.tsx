import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Link } from "react-router-dom";

export default function ResetPass() {
    return (
        <div className="bg-muted flex min-h-svh flex-col items-center justify-center bg-gradient-to-b from-gray-900 via-gray-800 to-black gap-6 p-6 md:p-10">
            <div className="flex w-full max-w-sm flex-col gap-6">
                <Card>
                    <CardHeader className="text-center">
                        <CardTitle className="text-xl">Reset password</CardTitle>
                        <CardDescription>
                            Write your new password
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form>
                            <div className="grid gap-6">
                                <div className="grid gap-3">
                                    <Label htmlFor="password">Password</Label>
                                    <Input
                                        id="password"
                                        type="password"
                                        required
                                    />
                                    <Label htmlFor="password">Confirm password</Label>
                                    <Input
                                        id="password"
                                        type="password"
                                        required
                                    />
                                    <Link to="/">
                                        <Button type="submit" className="w-full">Reset password</Button>
                                    </Link>
                                </div>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
