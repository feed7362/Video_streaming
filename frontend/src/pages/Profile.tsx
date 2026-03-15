import { useAuth } from "@/contexts/AuthContext";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Profile() {
    const { user, isLoading } = useAuth();

    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-12">
                <p className="text-muted-foreground">Loading...</p>
            </div>
        );
    }

    if (!user) {
        return (
            <div className="flex items-center justify-center p-12">
                <p className="text-muted-foreground">Not authenticated</p>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-2xl mx-auto">
            <h1 className="text-2xl font-bold mb-6">Profile</h1>
            <Card>
                <CardHeader>
                    <CardTitle>{user.username}</CardTitle>
                    <CardDescription>{user.email}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-muted-foreground">Status:</span>
                        <Badge variant={user.is_active ? "default" : "destructive"}>
                            {user.is_active ? "Active" : "Inactive"}
                        </Badge>
                    </div>
                    {user.is_verified !== undefined && (
                        <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-muted-foreground">Verified:</span>
                            <Badge variant={user.is_verified ? "default" : "secondary"}>
                                {user.is_verified ? "Yes" : "No"}
                            </Badge>
                        </div>
                    )}
                    {user.created_at && (
                        <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-muted-foreground">Member since:</span>
                            <span className="text-sm">
                                {new Date(user.created_at).toLocaleDateString()}
                            </span>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
