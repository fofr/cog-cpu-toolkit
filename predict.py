from cog import BasePredictor, Input, Path
from typing import List
import subprocess
import os
import shutil

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

VIDEO_TASKS = ["convert_to_mp4", "extract_video_audio_as_mp3"]


class Predictor(BasePredictor):
    def validate_inputs(self, task: str, input_file: Path):
        if task in VIDEO_TASKS:
            if input_file.suffix.lower() not in VIDEO_FILE_EXTENSIONS:
                raise ValueError(
                    "Input file must be a video file with one of the following extensions: "
                    + ", ".join(VIDEO_FILE_EXTENSIONS)
                )

    def predict(
        self,
        task: str = Input(
            description="Task to perform",
            choices=["convert_to_mp4", "extract_video_audio_as_mp3"],
        ),
        input_file: Path = Input(description="File – zip, image or video to process"),
        fps: int = Input(
            description="frames per second, if relevant (use 0 to keep original fps)",
            default=0,
        ),
    ) -> List[Path]:
        """Run prediction"""
        if os.path.exists('/tmp/outputs'):
            shutil.rmtree('/tmp/outputs')
        os.makedirs('/tmp/outputs')

        self.validate_inputs(task, input_file)
        self.fps = fps

        if task == "convert_to_mp4":
            return self.convert_to_mp4(input_file)
        elif task == "extract_video_audio_as_mp3":
            return self.extract_video_audio_as_mp3(input_file)

        return "ok"

    def run_ffmpeg(self, input_path: Path, output_path: str, command: List[str]):
        """Run ffmpeg command"""
        prepend = ["ffmpeg", "-i", str(input_path)]
        append = output_path
        command = prepend + command
        self.add_fps(command)
        command.append(append)

        print("Running ffmpeg command: " + " ".join(command))
        subprocess.run(command)
        return [Path(output_path)]

    def add_fps(self, command: List[str]):
        """Add fps to ffmpeg command"""
        if self.fps != 0:
            command.extend(["-r", str(self.fps)])

    def convert_to_mp4(self, video_path: Path) -> List[Path]:
        """Convert video to mp4 using ffmpeg"""
        ffmpeg_command = [
            "-c:v",
            "libx264",  # Video codec: H.264
            "-c:a",
            "aac",  # Audio codec: AAC
            "-q:a",
            "0",  # Specify audio quality (0 is the highest)
        ]

        return self.run_ffmpeg(video_path, "/tmp/outputs/video.mp4", ffmpeg_command)

    def extract_video_audio_as_mp3(self, video_path: Path) -> List[Path]:
        """Extract audio from video using ffmpeg"""
        ffmpeg_command = [
            "-q:a",
            "0",  # Specify audio quality (0 is the highest)
            "-map",
            "a",  # Map audio tracks (ignore video)
        ]

        return self.run_ffmpeg(video_path, "/tmp/outputs/audio.mp3", ffmpeg_command)
