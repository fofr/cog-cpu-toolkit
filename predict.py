from cog import BasePredictor, Input, Path
from typing import List
import subprocess
import os
import shutil
import zipfile

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

VIDEO_TASKS = [
    "convert_input_to_mp4",
    "convert_input_to_gif",
    "extract_video_audio_as_mp3",
    "extract_frames_from_input",
    "reverse_video",
    "bounce_video",
]
ZIP_TASKS = ["zipped_frames_to_mp4", "zipped_frames_to_gif"]


class Predictor(BasePredictor):
    def validate_inputs(self, task: str, input_file: Path):
        """Validate inputs"""
        if task in ZIP_TASKS:
            if input_file.suffix.lower() != ".zip":
                raise ValueError("Input file must be a zip file")

        elif task in VIDEO_TASKS:
            if input_file.suffix.lower() not in VIDEO_FILE_EXTENSIONS:
                raise ValueError(
                    "Input file must be a video file with one of the following extensions: "
                    + ", ".join(VIDEO_FILE_EXTENSIONS)
                )

    def predict(
        self,
        task: str = Input(
            description="Task to perform",
            choices=[
                "convert_input_to_mp4",
                "convert_input_to_gif",
                "extract_video_audio_as_mp3",
                "zipped_frames_to_mp4",
                "zipped_frames_to_gif",
                "extract_frames_from_input",
                "reverse_video",
                "bounce_video",
            ],
        ),
        input_file: Path = Input(description="File – zip, image or video to process"),
        fps: int = Input(
            description="frames per second, if relevant. Use 0 to keep original fps (or use default). Converting to GIF defaults to 12fps",
            default=0,
        ),
    ) -> List[Path]:
        """Run prediction"""
        if os.path.exists("/tmp/outputs"):
            shutil.rmtree("/tmp/outputs")
        os.makedirs("/tmp/outputs")

        self.validate_inputs(task, input_file)
        self.fps = fps

        if task == "convert_input_to_mp4":
            return self.convert_video_to(input_file, "mp4")
        elif task == "convert_input_to_gif":
            return self.convert_video_to(input_file, "gif")
        elif task == "extract_video_audio_as_mp3":
            return self.extract_video_audio_as_mp3(input_file)
        elif task == "zipped_frames_to_mp4":
            return self.zipped_frames_to(input_file, "mp4")
        elif task == "zipped_frames_to_gif":
            return self.zipped_frames_to(input_file, "gif")
        elif task == "extract_frames_from_input":
            return self.extract_frames_from_input(input_file)
        elif task == "reverse_video":
            return self.reverse_video(input_file)
        elif task == "bounce_video":
            return self.bounce_video(input_file)

        return []

    def unzip(self, input_path: Path) -> List[Path]:
        """Unzip file"""
        print("Unzipping file")
        with zipfile.ZipFile(input_path, "r") as zip_ref:
            zip_ref.extractall("/tmp/outputs/zip")

        for filename in os.listdir("/tmp/outputs/zip"):
            os.rename(
                "/tmp/outputs/zip/" + filename,
                "/tmp/outputs/zip/" + filename.lower(),
            )

        print("Files in zip:")
        for filename in sorted(os.listdir("/tmp/outputs/zip")):
            print(filename)

    def run_ffmpeg(self, input, output_path: str, command: List[str]):
        """Run ffmpeg command"""

        prepend = ["ffmpeg"]
        if input:
            prepend.extend(["-i", str(input)])

        append = [output_path]
        command = prepend + command + append
        print("Running ffmpeg command: " + " ".join(command))
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "Command '{}' returned with error (code {}): {}".format(
                    e.cmd, e.returncode, e.output
                )
            )
        return [Path(output_path)]

    def convert_video_to(self, video_path: Path, type: str = "mp4") -> List[Path]:
        """Convert video to format using ffmpeg"""
        command = [
            "-pix_fmt",
            "yuv420p",  # Pixel format: YUV with 4:2:0 chroma subsampling
        ]

        if type == "gif":
            command.extend(
                [
                    "-vf",
                    f"fps={self.fps or 12},scale=512:-1:flags=lanczos",  # Set frame rate and scale
                    "-c:v",
                    "gif",  # Video codec: GIF
                ]
            )
        else:
            command.extend(
                [
                    "-c:v",
                    "libx264",  # Video codec: H.264
                    "-c:a",
                    "aac",  # Audio codec: AAC
                    "-q:a",
                    "0",  # Specify audio quality (0 is the highest)
                ]
            )

            if self.fps != 0:
                command.extend(["-r", str(self.fps)])

        return self.run_ffmpeg(video_path, f"/tmp/outputs/video.{type}", command)

    def extract_video_audio_as_mp3(self, video_path: Path) -> List[Path]:
        """Extract audio from video using ffmpeg"""
        command = [
            "-q:a",
            "0",  # Specify audio quality (0 is the highest)
            "-map",
            "a",  # Map audio tracks (ignore video)
        ]

        return self.run_ffmpeg(video_path, "/tmp/outputs/audio.mp3", command)

    def extract_frames_from_input(self, video_path: Path) -> List[Path]:
        """Extract frames from video using ffmpeg"""
        command = ["-vf", f"fps={self.fps}"] if self.fps != 0 else []
        self.run_ffmpeg(video_path, "/tmp/outputs/out%03d.png", command)

        output_files = []
        for filename in os.listdir("/tmp/outputs"):
            if filename.endswith(".png") and filename.startswith("out"):
                output_files.append(filename)

        with zipfile.ZipFile("/tmp/outputs/frames.zip", "w") as zip_ref:
            for filename in output_files:
                zip_ref.write(f"/tmp/outputs/{filename}", filename)

        return [Path("/tmp/outputs/frames.zip")]

    def zipped_frames_to(self, input_file: Path, type: str = "mp4") -> List[Path]:
        """Convert frames to video using ffmpeg"""
        self.unzip(input_file)
        frames_directory = "/tmp/outputs/zip"
        image_filetypes = ["jpg", "jpeg", "png"]
        frame_filetype = None
        for file in os.listdir(frames_directory):
            potential_filetype = file.split(".")[-1]
            if potential_filetype in image_filetypes:
                frame_filetype = potential_filetype
                break
        if frame_filetype is None:
            raise ValueError("No image files found in the zip file.")

        command = [
            "-framerate",
            str(12 if self.fps == 0 else self.fps),  # Set the frame rate
            "-pattern_type",
            "glob",  # Use glob pattern matching
            "-i",
            f"{frames_directory}/*.{frame_filetype}",
            "-pix_fmt",
            "yuv420p",  # Pixel format: YUV with 4:2:0 chroma subsampling
        ]

        if type == "gif":
            command.extend(
                [
                    "-vf",
                    "scale=512:-1:flags=lanczos",
                    "-c:v",
                    "gif",  # Video codec: GIF
                ]
            )
        else:
            command.extend(
                [
                    "-c:v",
                    "libx264",  # Video codec: H.264
                ]
            )

        return self.run_ffmpeg(False, f"/tmp/outputs/video.{type}", command)

    def reverse_video(self, video_path: Path) -> List[Path]:
        """Reverse video using ffmpeg"""
        output_file = "/tmp/outputs/reversed" + video_path.suffix
        command = [
            "-vf",
            "reverse",
            "-af",
            "areverse",
        ]

        return self.run_ffmpeg(video_path, output_file, command)

    def bounce_video(self, video_path: Path) -> List[Path]:
        """Bounce video or gif using ffmpeg"""
        reversed_video_path = "/tmp/outputs/reversed" + video_path.suffix
        self.reverse_video(video_path)

        with open("/tmp/outputs/concat_list.txt", "w") as f:
            f.write(f"file '{video_path}'\nfile '{reversed_video_path}'\n")

        command = [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "/tmp/outputs/concat_list.txt",  # Use the temporary file as input
        ]

        if video_path.suffix == ".gif":
            command.extend(
                [
                    "-vf",
                    "scale=512:-1:flags=lanczos",
                    "-c:v",
                    "gif",  # Video codec: GIF
                ]
            )
        else:
            command.extend(
                [
                    "-c",
                    "copy",
                ]
            )

        return self.run_ffmpeg(
            None, f"/tmp/outputs/bounced{video_path.suffix}", command
        )
