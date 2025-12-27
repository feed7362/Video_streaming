import { useCallback } from "react";

import { useToast } from "@/components/ui/toast/use-toast";
import { downloadVideo } from "@api/videoApi";
import type { VideoDetail } from "@api/types";

interface UseDownloadProps {
  video: VideoDetail | null;
  resolution: string;
}

export function useDownload({ video, resolution }: UseDownloadProps) {
  const { toast } = useToast();

  const handleDownload = useCallback(async () => {
    if (!video?.id) {
      toast({
        title: "Cannot download: Video is missing.",
        variant: "default",
      });
      return;
    }

    try {
      toast({ title: `Downloading ${resolution}...` });

      const blob = await downloadVideo(video.id, resolution);

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      a.download = `${video.title || "video"}_${resolution}.mp4`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      toast({ title: "Download complete!" });
    } catch (error) {
      console.error("Download failed:", error);
      toast({ title: "Download failed", variant: "default" });
    }
  }, [video, resolution, toast]);

  return { handleDownload };
}
