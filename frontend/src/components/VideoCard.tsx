import {Link} from "react-router-dom";
import {Card} from "@/components/ui/card";

interface VideoCardProps {
    id: string;
    title: string;
    thumbnail: string;
}

export default function VideoCard({id, title, thumbnail}: VideoCardProps) {
    return (
        <Link to={`/video/${id}`}>
            <Card className="p-2 hover:shadow-lg transition">
                <img src={thumbnail} alt={title} className="w-full h-40 object-cover rounded-md"/>
                <h2 className="mt-2 font-semibold">{title}</h2>
            </Card>
        </Link>
    );
}
