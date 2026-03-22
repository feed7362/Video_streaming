import { useState } from "react";
import { Link } from "react-router-dom";
import { ListVideo, Lock, Globe, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Playlist {
    id: string;
    title: string;
    thumbnail: string;
    videoCount: number;
    privacy: "public" | "private";
    updatedAt: string;
}

const MOCK: Playlist[] = Array.from({ length: 8 }).map((_, i) => ({
    id: `pl-${i + 1}`,
    title: i === 0 ? "Watch Later" : i === 1 ? "Liked Videos" : `My Playlist ${i - 1}`,
    thumbnail: `https://via.placeholder.com/320x180?text=Playlist+${i + 1}`,
    videoCount: Math.floor(Math.random() * 40) + 1,
    privacy: i < 2 ? "private" : "public",
    updatedAt: `${Math.floor(Math.random() * 30) + 1} days ago`,
}));

export default function Playlists() {
    const [playlists] = useState<Playlist[]>(MOCK);

    return (
        <div className="px-4 py-6">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold">Playlists</h1>
                <Button variant="outline" className="gap-2 rounded-full">
                    <Plus className="h-4 w-4" />
                    New playlist
                </Button>
            </div>

            <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {playlists.map((pl) => (
                    <Link key={pl.id} to={`/playlist/${pl.id}`} className="group block">
                        {/* Thumbnail stack */}
                        <div className="relative aspect-video rounded-xl overflow-hidden bg-muted mb-3">
                            <img
                                src={pl.thumbnail}
                                alt={pl.title}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                                loading="lazy"
                            />
                            {/* Video count overlay */}
                            <div className="absolute inset-y-0 right-0 w-1/3 bg-black/80 flex flex-col items-center justify-center gap-1">
                                <ListVideo className="h-5 w-5 text-white" />
                                <span className="text-white text-xs font-semibold">{pl.videoCount}</span>
                            </div>
                        </div>

                        <h3 className="font-semibold text-sm line-clamp-2 leading-snug">{pl.title}</h3>
                        <div className="flex items-center gap-1 mt-0.5 text-xs text-muted-foreground">
                            {pl.privacy === "private"
                                ? <Lock className="h-3 w-3" />
                                : <Globe className="h-3 w-3" />}
                            <span className="capitalize">{pl.privacy}</span>
                            <span>·</span>
                            <span>Updated {pl.updatedAt}</span>
                        </div>
                    </Link>
                ))}
            </div>

            {playlists.length === 0 && (
                <div className="flex flex-col items-center justify-center py-24 text-center">
                    <ListVideo className="h-16 w-16 text-muted-foreground mb-4" />
                    <h2 className="text-lg font-semibold mb-1">No playlists yet</h2>
                    <p className="text-sm text-muted-foreground mb-6">
                        Create a playlist to organise your favourite videos.
                    </p>
                    <Button className="rounded-full gap-2">
                        <Plus className="h-4 w-4" />
                        New playlist
                    </Button>
                </div>
            )}
        </div>
    );
}
