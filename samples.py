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
    if glob.glob(f"{output_fn}*"):
        return

    prediction_start = time.time()
    print("Running prediction", output_fn)
    url = "http://localhost:5000/predictions"
    response = requests.post(url, json={"input": kwargs})
    print(f"Prediction took: {time.time() - prediction_start:.2f}s")
    data = response.json()
    print(data)

    try:
        for i, datauri in enumerate(data["output"]):
            base64_encoded_data = datauri.split(",")[1]
            decoded_data = base64.b64decode(base64_encoded_data)
            with open(
                f"{output_fn.rsplit('.', 1)[0]}_{i}.{output_fn.rsplit('.', 1)[1]}", "wb"
            ) as f:
                f.write(decoded_data)
    except Exception as e:
        print("Error!", str(e))
        print("input:", kwargs)
        print(data["logs"])
        sys.exit(1)


def main():
    run(
        "sample_extract_video_audio_as_mp3.mp3",
        task="extract_video_audio_as_mp3",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )


if __name__ == "__main__":
    main()
