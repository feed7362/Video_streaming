import {useEffect, useState} from "react";
import VideoCard from "@/components/VideoCard";
import axios from "axios";
import {ScrollArea, ScrollBar} from "@/components/ui/scroll-area"
import {Skeleton} from "@/components/ui/skeleton"

export function SkeletonCard() {
    return (
        <div className="flex flex-col space-y-3">
            <Skeleton className="h-[125px] w-[250px] rounded-xl"/>
            <div className="space-y-2">
                <Skeleton className="h-4 w-[250px]"/>
                <Skeleton className="h-4 w-[200px]"/>
            </div>
        </div>
    )
}

interface Video {
    id: string;
    title: string;
    thumbnail: string;
}

export default function Home() {
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get("http://localhost:8000/api/videos")
            .then(res => {
                setVideos(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    return (
        <ScrollArea className="flex-1 w-full rounded-md">
            <div
                className="grid auto-rows-min grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-6 p-4 justify-start ml-[30px]">
                {loading
                    ? Array.from({length: 24}).map((_, i) => <SkeletonCard key={i}/>)
                    : videos.map(video => <VideoCard key={video.id} video={video}/>)
                }
            </div>
            <ScrollBar orientation="vertical"/>
        </ScrollArea>
    );
}
