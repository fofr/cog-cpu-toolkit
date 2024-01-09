"""
To set up, first run a local cog server using:
   cog run -p 5000 python -m cog.server.http
Then, in a separate terminal, generate samples
   python samples.py
"""

import base64
import os
import sys
import requests
import glob
import time


def run(output_fn, **kwargs):
    if glob.glob(f"{output_fn.rsplit('.', 1)[0]}*"):
        print("Already ran", output_fn)
        return

    prediction_start = time.time()
    print("Running prediction", output_fn)
    url = "http://localhost:5000/predictions"
    response = requests.post(url, json={"input": kwargs})
    print(f"Prediction took: {time.time() - prediction_start:.2f}s")
    data = response.json()
    try:
        for i, datauri in enumerate(data["output"]):
            base64_encoded_data = datauri.split(",")[1]
            decoded_data = base64.b64decode(base64_encoded_data)
            with open(
                f"{output_fn.rsplit('.', 1)[0]}_{i}.{output_fn.rsplit('.', 1)[1]}", "wb"
            ) as f:
                f.write(decoded_data)
            print("Wrote", output_fn)
    except Exception as e:
        print("Error!", str(e))
        print("input:", kwargs)
        print(data["logs"])
        sys.exit(1)


def main():
    run(
        "sample_reverse_video.mp4",
        task="reverse_video",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )

    run(
        "sample_bounce_video.mp4",
        task="bounce_video",
        input_file="https://replicate.delivery/pbxt/CmppJesjwO3jPSmdd1fflCjGeODlOpVy5I0PyXlgLeMmanVRC/video.mp4",
    )

    run(
        "sample_bounce_gif.gif",
        task="bounce_video",
        input_file="https://replicate.delivery/pbxt/KCBdyVkWcgjiCM3nzdg9JpqX8xzTGUimj4mWdpWgCQOm6umr/replicate-prediction-3rcqh5dbvob5u7gsd5vammyfwy.gif",
    )

    run(
        "sample_extract_video_audio_as_mp3.mp3",
        task="extract_video_audio_as_mp3",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )

    run(
        "sample_convert_to_mp4.mp4",
        task="convert_input_to_mp4",
        input_file="https://replicate.delivery/pbxt/RU9CI33SMCKMFBFQplELLexGPsOGNIU42VpauosBZZLkhW2IA/tmp.gif",
    )

    run(
        "sample_convert_to_mp4_with_fps.mp4",
        task="convert_input_to_mp4",
        fps=1,
        input_file="https://replicate.delivery/pbxt/RU9CI33SMCKMFBFQplELLexGPsOGNIU42VpauosBZZLkhW2IA/tmp.gif",
    )

    run(
        "sample_convert_to_gif.gif",
        task="convert_input_to_gif",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )

    run(
        "sample_frames_to_mp4.mp4",
        task="zipped_frames_to_mp4",
        input_file="https://replicate.delivery/pbxt/IyPciuTwd9miRkQm3AVd4ZZrNta1i1M8rKs7vJtpy83uAIIi/frames.zip",
    )

    run(
        "sample_frames_to_mp4_with_fps.mp4",
        task="zipped_frames_to_mp4",
        fps=1,
        input_file="https://replicate.delivery/pbxt/IyPciuTwd9miRkQm3AVd4ZZrNta1i1M8rKs7vJtpy83uAIIi/frames.zip",
    )

    run(
        "sample_frames_to_gif.gif",
        task="zipped_frames_to_gif",
        input_file="https://replicate.delivery/pbxt/IyPciuTwd9miRkQm3AVd4ZZrNta1i1M8rKs7vJtpy83uAIIi/frames.zip",
    )

    run(
        "sample_frames_to_gif_with_fps.gif",
        task="zipped_frames_to_gif",
        fps=1,
        input_file="https://replicate.delivery/pbxt/IyPciuTwd9miRkQm3AVd4ZZrNta1i1M8rKs7vJtpy83uAIIi/frames.zip",
    )

    run(
        "sample_extract_frames_from_input.zip",
        task="extract_frames_from_input",
        fps=12,
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )


if __name__ == "__main__":
    main()
