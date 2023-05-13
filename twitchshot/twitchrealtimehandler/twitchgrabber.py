from dataclasses import dataclass
import numpy as np

from twitchrealtimehandler.twitchhandler import (
    _TwitchHandlerGrabber,
    _TwitchHandlerVideo,
)

@dataclass
class TwitchImageGrabber(_TwitchHandlerVideo, _TwitchHandlerGrabber):
    """Handler to retrieve audio segment in realtime from a
    twitch stream"""

    _resolution = {
        "160p": (320, 160),
        "360p": (640, 360),
        "480p": (854, 480),
        "720p": (1280, 720),
        "720p60": (1280, 720),
        "1080p": (1920, 1080),
        "1080p60": (1920, 1080),
    }

    def __post_init__(self):
        super().__post_init__()
        if self.quality not in self._resolution:
            raise ValueError("Unrecognized quality")
        self.width, self.height = self._resolution[self.quality]
        self.dtype = np.uint8
        self.get_stream_url()
        self._cmd_pipe = [
            "ffmpeg",
            "-i",
            self._stream_url,
            "-f",
            "image2pipe",
            "-r",
            f"{self.rate}",
            "-pix_fmt",
            "rgb24",
            "-s",
            "{}x{}".format(self.width, self.height),
            "-vcodec",
            "rawvideo",
            "-",
        ]
        self._n_bytes_per_payload = self.width * self.height * 3
        self._reshape_size = [self.height, self.width, 3]
        if self._auto_start:
            self._start_thread()
