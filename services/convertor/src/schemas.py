from pydantic import BaseModel


class VideoProperties(BaseModel):
    fps: float
    width: int
    height: int
    bitrate: int
    has_audio: bool
