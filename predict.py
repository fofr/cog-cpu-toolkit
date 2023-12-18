from cog import BasePredictor, Input, Path
from typing import List
import subprocess
import os

VIDEO_FILE_EXTENSIONS = [
    ".3g2",
    ".3gp",
    ".a64",
    ".avi",
    ".flv",
    ".gif",
    ".gifv",
    ".m2v",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".mv",
    ".mxf",
    ".nsv",
    ".ogg",
    ".ogv",
    ".rm",
    ".rmvb",
    ".roq",
    ".svi",
    ".vob",
    ".webm",
    ".wmv",
    ".yuv",
]


class Predictor(BasePredictor):
    def predict(
        self,
        task: str = Input(
            description="Task to perform", choices=["extract_video_audio_as_mp3"]
        ),
        input_file: Path = Input(description="File – zip, image or video to process"),
        fps: int = Input(
            description="frames per second, if relevant",
            default=1,
            ge=1,
        ),
    ) -> List[Path]:
        """Run prediction"""
        os.makedirs("/tmp/frames", exist_ok=True)
        if task == "extract_video_audio_as_mp3":
            if input_file.suffix.lower() not in VIDEO_FILE_EXTENSIONS:
                raise ValueError(
                    "Input file must be a video file with one of the following extensions: "
                    + ", ".join(VIDEO_FILE_EXTENSIONS)
                )
            return self.extract_audio(input_file)

        return "ok"

    def extract_audio(self, video_path: Path) -> List[Path]:
        """Extract audio from video using ffmpeg"""
        output_path = "/tmp/audio.mp3"

        ffmpeg_command = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-q:a",
            "0",  # Specify audio quality (0 is the highest)
            "-map",
            "a",  # Map audio tracks (ignore video)
            output_path,
        ]

        subprocess.run(ffmpeg_command)
        return [Path(output_path)]
