import { useEffect, useState } from "react";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, BarChart, Bar,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
    getOverview, getContent, getAudience,
    type OverviewData, type ContentData, type AudienceData,
} from "@/lib/api/analyticsApi";

type Tab = "overview" | "content" | "audience";

function StatCard({ label, value, loading }: { label: string; value: number | string; loading: boolean }) {
    return (
        <Card>
            <CardHeader className="pb-1">
                <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
            </CardHeader>
            <CardContent>
                {loading
                    ? <Skeleton className="h-8 w-24" />
                    : <p className="text-2xl font-bold">{typeof value === "number" ? value.toLocaleString() : value}</p>
                }
            </CardContent>
        </Card>
    );
}

function ChartSkeleton() {
    return <Skeleton className="h-[200px] w-full" />;
}

// ── Overview Tab ─────────────────────────────────────────────────────────────

function OverviewTab() {
    const [data, setData] = useState<OverviewData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getOverview().then(setData).finally(() => setLoading(false));
    }, []);

    return (
        <div className="space-y-6">
            {/* Stat cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard label="Total Views" value={data?.total_views ?? 0} loading={loading} />
                <StatCard label="Subscribers" value={data?.total_subscribers ?? 0} loading={loading} />
                <StatCard label="Likes" value={data?.total_likes ?? 0} loading={loading} />
                <StatCard label="Comments" value={data?.total_comments ?? 0} loading={loading} />
            </div>

            {/* Views over time */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Views — last 30 days</CardTitle>
                </CardHeader>
                <CardContent>
                    {loading ? <ChartSkeleton /> : (
                        data?.views_per_day.length ? (
                            <ResponsiveContainer width="100%" height={200}>
                                <LineChart data={data.views_per_day}>
                                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                                    <YAxis tick={{ fontSize: 11 }} />
                                    <Tooltip />
                                    <Line type="monotone" dataKey="count" name="Views" stroke="hsl(var(--primary))" dot={false} strokeWidth={2} />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <p className="text-sm text-muted-foreground text-center py-12">No view data yet</p>
                        )
                    )}
                </CardContent>
            </Card>

            {/* Top videos */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Top videos</CardTitle>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="space-y-3">
                            {Array.from({ length: 3 }).map((_, i) => (
                                <Skeleton key={i} className="h-10 w-full" />
                            ))}
                        </div>
                    ) : data?.top_videos.length ? (
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b text-muted-foreground text-left">
                                    <th className="pb-2 font-medium">Title</th>
                                    <th className="pb-2 font-medium text-right">Views</th>
                                    <th className="pb-2 font-medium text-right">Likes</th>
                                    <th className="pb-2 font-medium text-right">Comments</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.top_videos.map((v) => (
                                    <tr key={v.id} className="border-b last:border-0 hover:bg-muted/30">
                                        <td className="py-2 max-w-60 truncate">{v.title}</td>
                                        <td className="py-2 text-right">{v.views_count.toLocaleString()}</td>
                                        <td className="py-2 text-right">{v.likes_count.toLocaleString()}</td>
                                        <td className="py-2 text-right">{v.comments_count.toLocaleString()}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <p className="text-sm text-muted-foreground text-center py-8">No videos yet</p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

// ── Content Tab ───────────────────────────────────────────────────────────────

function ContentTab() {
    const [data, setData] = useState<ContentData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getContent().then(setData).finally(() => setLoading(false));
    }, []);

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-base">Your videos</CardTitle>
            </CardHeader>
            <CardContent>
                {loading ? (
                    <div className="space-y-3">
                        {Array.from({ length: 5 }).map((_, i) => (
                            <Skeleton key={i} className="h-12 w-full" />
                        ))}
                    </div>
                ) : data?.videos.length ? (
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b text-muted-foreground text-left">
                                    <th className="pb-2 font-medium">Title</th>
                                    <th className="pb-2 font-medium">Status</th>
                                    <th className="pb-2 font-medium text-right">Views</th>
                                    <th className="pb-2 font-medium text-right">Likes</th>
                                    <th className="pb-2 font-medium text-right">Dislikes</th>
                                    <th className="pb-2 font-medium text-right">Comments</th>
                                    <th className="pb-2 font-medium text-right">Uploaded</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.videos.map((v) => (
                                    <tr key={v.id} className="border-b last:border-0 hover:bg-muted/30">
                                        <td className="py-2 max-w-[200px] truncate">{v.title}</td>
                                        <td className="py-2">
                                            <Badge variant={v.privacy === "public" ? "default" : "secondary"}>
                                                {v.privacy}
                                            </Badge>
                                        </td>
                                        <td className="py-2 text-right">{v.views_count.toLocaleString()}</td>
                                        <td className="py-2 text-right">{v.likes_count.toLocaleString()}</td>
                                        <td className="py-2 text-right">{v.dislikes_count.toLocaleString()}</td>
                                        <td className="py-2 text-right">{v.comments_count.toLocaleString()}</td>
                                        <td className="py-2 text-right text-muted-foreground whitespace-nowrap">
                                            {new Date(v.created_at).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="text-sm text-muted-foreground text-center py-12">No videos uploaded yet</p>
                )}
            </CardContent>
        </Card>
    );
}

// ── Audience Tab ──────────────────────────────────────────────────────────────

function AudienceTab() {
    const [data, setData] = useState<AudienceData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getAudience().then(setData).finally(() => setLoading(false));
    }, []);

    return (
        <div className="space-y-6">
            {/* Viewer type stats */}
            <div className="grid grid-cols-2 gap-4">
                <StatCard label="Unique viewers" value={data?.unique_viewers ?? 0} loading={loading} />
                <StatCard label="Returning viewers" value={data?.returning_viewers ?? 0} loading={loading} />
            </div>

            {/* Subscribers gained */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Subscribers gained — last 30 days</CardTitle>
                </CardHeader>
                <CardContent>
                    {loading ? <ChartSkeleton /> : (
                        data?.subscribers_per_day.length ? (
                            <ResponsiveContainer width="100%" height={200}>
                                <BarChart data={data.subscribers_per_day}>
                                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                                    <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                                    <Tooltip />
                                    <Bar dataKey="count" name="Subscribers" fill="hsl(var(--primary))" radius={[3, 3, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <p className="text-sm text-muted-foreground text-center py-12">No subscription data yet</p>
                        )
                    )}
                </CardContent>
            </Card>

            {/* Comments over time */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Comments — last 30 days</CardTitle>
                </CardHeader>
                <CardContent>
                    {loading ? <ChartSkeleton /> : (
                        data?.comments_per_day.length ? (
                            <ResponsiveContainer width="100%" height={200}>
                                <LineChart data={data.comments_per_day}>
                                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                                    <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                                    <Tooltip />
                                    <Line type="monotone" dataKey="count" name="Comments" stroke="hsl(var(--primary))" dot={false} strokeWidth={2} />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <p className="text-sm text-muted-foreground text-center py-12">No comment data yet</p>
                        )
                    )}
                </CardContent>
            </Card>

            {/* Placeholder for unavailable data */}
            <Card className="border-dashed">
                <CardHeader>
                    <CardTitle className="text-base text-muted-foreground">Geographic data</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground">
                        Geographic analytics are not yet available — viewer location data is not tracked.
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

const TABS: { id: Tab; label: string }[] = [
    { id: "overview", label: "Overview" },
    { id: "content",  label: "Content" },
    { id: "audience", label: "Audience" },
];

export default function Studio() {
    const [activeTab, setActiveTab] = useState<Tab>("overview");

    return (
        <div className="max-w-5xl mx-auto p-6 space-y-6">
            <h1 className="text-2xl font-bold">Creator Studio</h1>

            {/* Tab bar */}
            <div className="flex gap-1 border-b">
                {TABS.map((t) => (
                    <Button
                        key={t.id}
                        variant="ghost"
                        size="sm"
                        onClick={() => setActiveTab(t.id)}
                        className={`rounded-none border-b-2 px-4 ${
                            activeTab === t.id
                                ? "border-primary text-foreground font-medium"
                                : "border-transparent text-muted-foreground"
                        }`}
                    >
                        {t.label}
                    </Button>
                ))}
            </div>

            {/* Tab content — each tab mounts independently and fetches its own data */}
            {activeTab === "overview" && <OverviewTab />}
            {activeTab === "content"  && <ContentTab />}
            {activeTab === "audience" && <AudienceTab />}
        </div>
    );
}
