from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
from getters import config
import os
import json
from pathlib import Path
import time

def detectClips(film_path):
    # time for logging
    start = time.time()

    # check output folder exists and delete previous media
    output_path = project_root / "processingMedia" / "detectedFilmClips"
    os.makedirs(output_path, exist_ok=True)
    for item in output_path.iterdir():
        if item.is_file():
            item.unlink()

    from ffWrapper import cut_scene_ffmpeg
    from scenedetect import open_video, SceneManager
    from scenedetect.detectors import ContentDetector

    video = open_video(str(film_path))
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()

    # cut using wrapper
    from tqdm import tqdm
    detected_scenes_info = {}

    for i, (start, end) in enumerate(tqdm(scene_list, desc="Cutting scenes")):
        start_sec = start.get_seconds()
        end_sec = end.get_seconds()
        out_file = os.path.join(output_path, f"scene_{i+1:03d}.mp4")

        # call the cutting function
        cut_scene_ffmpeg(film_path, start_sec, end_sec, out_file, mode="edit")

        # store params
        detected_scenes_info[out_file] = {
            "input_path": str(film_path),
            "start_time": str(start_sec),
            "end_time": str(end_sec),
            "output_path": str(out_file),
            "output_filename": str(os.path.basename(out_file))
        }

    info_output_path = output_path / "detected_scenes_info.json"
    with open(str(info_output_path), "w") as f:
        json.dump(detected_scenes_info, f, indent=4)

    end = time.time()
    print(f"Elapsed time: {end - start:.2f} seconds")


film_path = config.get_test_path()
detectClips(film_path)

