import subprocess
from pathlib import Path
import json
import os
import re
import sys

project_root = Path(__file__).resolve().parent.parent
ffmpeg_bin_dir = project_root / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
os.environ["PATH"] = str(ffmpeg_bin_dir) + os.pathsep + os.environ["PATH"]
ffmpeg_path = ffmpeg_bin_dir / "ffmpeg.exe"

def reencode_for_keyframes(
    input_path,               # Input video file path
    output_path,              # Output file path for reencoded video
    keyframe_interval=12,     # Keyframe interval to enforce
    quality=23,               # Quality setting for QSV (1=best, 51=worst)
    preset="veryfast"         # Preset for Intel QSV encoder
):subprocess.run([
    str(ffmpeg_path),
    "-hide_banner",
    "-loglevel", "error",
    "-init_hw_device", "qsv=hw",              # Initialize QSV
    "-filter_hw_device", "hw",                # Use it for filters
    "-hwaccel", "qsv",                        # Decode with QSV
    "-hwaccel_output_format", "qsv",          # Use QSV-compatible format
    "-c:v", "hevc_qsv",                       # explicitly use hevc_qsv decoder (if source is HEVC)
    "-i", str(input_path),
    "-vf", "vpp_qsv=format=nv12",             # vpp_qsv is required to convert pixel format with QSV
    "-g", "12",
    "-sc_threshold", "0",
    "-c:v", "h264_qsv",
    "-preset", "veryfast",
    "-b:v", "0",
    "-global_quality", "23",
    "-look_ahead", "0",
    "-c:a", "copy",
    "-y", str(output_path)
], check=True)

# /\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\
# /\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\
"""Cut a clip from input_path between start_time and end_time, re-encoding using the edit preset.
    Assumes input video already has suitable keyframe intervals if fast keyframe cuts are needed."""
def edit_cut_scene_ffmpeg(
    input_path,               # Input video file path (can be original or reencoded)
    start_time,               # Start time in seconds (float/int)
    end_time,                 # End time in seconds (float/int)
    output_path,              # Output file path
    crf=28,                   # Constant Rate Factor for 'edit' preset
    preset="fast",            # Encoding speed preset for 'edit'
    resolution="1280:720",    # Scale resolution as WxH string
    keep_audio=True,          # Keep audio for 'edit'
    keyframe_interval=12,     # Keyframe interval for 'edit'
    force_keyframes=True,     # Force keyframe at start time for 'edit'
    sc_threshold=0            # Scene change threshold
):
    duration = end_time - start_time

    cmd = [str(ffmpeg_path),
           "-hide_banner",
           "-loglevel", "error"
    ]
    print("duration)
    cmd += [
        "-t", f"{duration:.3f}",        # Duration of the clip
        "-ss", f"{start_time:.3f}",     # Seek to start time (before input for faster cuts)
        "-i", str(input_path),          # Input file path
        "-g", str(keyframe_interval),   # GOP (keyframe) interval
        "-c:v", "libx264",              # Video codec
        "-crf", str(crf),               # Quality setting
        "-preset", preset               # Encoding speed preset
    ]

    if force_keyframes:
        cmd += ["-force_key_frames", "0"]  # Force keyframe at start time

    if resolution:
        cmd += ["-vf", f"scale={resolution}"]  # Scale video

    cmd += ["-sc_threshold", str(sc_threshold)]  # Scene change threshold

    if keep_audio:
        cmd += ["-c:a", "copy"]  # Copy audio
    else:
        cmd += ["-an"]           # Remove audio

    cmd += [str(output_path)]    # Output file path

    subprocess.run(cmd, check=True)  # Run ffmpeg

# /\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\
# /\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\
# takes in a video and changes playback speed
def change_speed_ffmpeg(
    input_path,               # Input video file path
    output_path,              # Output video file path
    speed=1.0,                # Playback speed multiplier (e.g. 0.8 = slower, 1.5 = faster)
    mode="preserve_pitch",    # Mode: 'preserve_pitch' (rubberband), 'simple' (no pitch correction)
    crf=23,                   # Constant Rate Factor for quality (lower = better)
    preset="medium",          # FFmpeg encoding speed preset
    resolution="original"     # 'original', or '720p', '480p', etc.
):
    project_root = Path(__file__).resolve().parent.parent
    ffmpeg_bin_dir = project_root / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
    os.environ["PATH"] = str(ffmpeg_bin_dir) + os.pathsep + os.environ["PATH"]
    ffmpeg_path = ffmpeg_bin_dir / "ffmpeg.exe"

    resolution_map = {
        "240p": "426:240",
        "480p": "854:480",
        "720p": "1280:720",
        "1080p": "1920:1080",
        "original": None
    }
    scale_filter = resolution_map.get(resolution)

    # Calculate video PTS multiplier (inverse of speed)
    video_pts = 1 / speed
    audio_filter = ""
    video_filter = f"setpts={video_pts:.5f}*PTS"

    if mode == "preserve_pitch":
        # Use rubberband to preserve pitch while stretching tempo
        audio_filter = f"rubberband=tempo={speed:.5f}"
    elif mode == "simple":
        # Simple speed change with pitch change
        atempo_vals = []
        temp_speed = speed
        while temp_speed > 2.0:
            atempo_vals.append(2.0)
            temp_speed /= 2.0
        while temp_speed < 0.5:
            atempo_vals.append(0.5)
            temp_speed /= 0.5
        atempo_vals.append(temp_speed)
        audio_filter = ",".join([f"atempo={v:.5f}" for v in atempo_vals])
    else:
        raise ValueError("Invalid mode. Use 'preserve_pitch' or 'simple'.")

    filter_complex = f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]"
    cmd = [
        str(ffmpeg_path),
        "-i", str(input_path),
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset
    ]

    if scale_filter:
        cmd += ["-vf", f"scale={scale_filter}"]

    cmd += [str(output_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output_name = Path(output_path).name

    if result.returncode != 0:
        print(f"FFmpeg error while creating '{output_name}':")
        print(result.stderr)
    else:
        print(f"Speed-adjusted clip created: '{output_name}' (speed: {speed}x, mode: {mode})")
        

# /\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\/\/\///\\\/\/\

def get_video_length(video_path):
    """
    Returns the duration of the video in seconds as a float.
    Relies on ffprobe being in the PATH, added dynamically.
    """

    # Dynamically add ffmpeg/ffprobe to PATH
    project_root = Path(__file__).resolve().parent.parent
    ffmpeg_bin_dir = project_root / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
    os.environ["PATH"] = str(ffmpeg_bin_dir) + os.pathsep + os.environ["PATH"]

    cmd = [
        "ffprobe",                          # No need for full path anymore
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        str(video_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except subprocess.CalledProcessError as e:
        print("Error running ffprobe:", e.stderr)
    except (KeyError, ValueError, json.JSONDecodeError):
        print("Failed to parse duration from ffprobe output.")

    return None