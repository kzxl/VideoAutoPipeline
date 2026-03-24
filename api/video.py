"""Video composition with FFmpeg — Ken Burns, crossfade, subtitles, music mix"""
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

from config import OUTPUT_DIR, FORMATS
import progress
from tts import get_duration


# ============================================================
# Scene encoding
# ============================================================
def _encode_scene(i, img_path, scene_out, scene_dur, W, H, enable_kenburns):
    """Encode a single image into a video clip"""
    if enable_kenburns:
        total_frames = int(scene_dur * 25)
        if i % 2 == 0:
            zoom_expr = f"min(1+0.15*on/{total_frames},1.15)"
        else:
            zoom_expr = f"max(1.15-0.15*on/{total_frames},1.0)"

        vf = (
            f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
            f"crop={W*2}:{H*2},"
            f"zoompan=z={zoom_expr}:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2)"
            f":d={total_frames}:s={W}x{H}:fps=25,"
            f"setsar=1,format=yuv420p"
        )
    else:
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},format=yuv420p"
        )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(scene_dur),
        "-i", img_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-r", "25",
        scene_out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)

    if r.returncode != 0:
        # Fallback: no Ken Burns
        vf_simple = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},format=yuv420p"
        )
        cmd2 = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(scene_dur),
            "-i", img_path,
            "-vf", vf_simple,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-r", "25",
            scene_out,
        ]
        subprocess.run(cmd2, capture_output=True, text=True, check=True)


# ============================================================
# Merge strategies
# ============================================================
def _merge_concat(scene_videos):
    merged = os.path.join(OUTPUT_DIR, "_merged.mp4")
    concat_file = os.path.join(OUTPUT_DIR, "_concat.txt")
    with open(concat_file, "w") as f:
        for sv in scene_videos:
            f.write(f"file '{sv}'\n")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p",
        merged,
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    os.remove(concat_file)
    return merged


def _merge_crossfade(scene_videos, fade_dur):
    merged = os.path.join(OUTPUT_DIR, "_merged.mp4")
    durs = [get_duration(sv) for sv in scene_videos]

    if len(scene_videos) == 2:
        offset = durs[0] - fade_dur
        cmd = [
            "ffmpeg", "-y",
            "-i", scene_videos[0], "-i", scene_videos[1],
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration={fade_dur}:offset={offset:.3f},format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            merged,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            return merged

    elif len(scene_videos) > 2:
        inputs = []
        for sv in scene_videos:
            inputs.extend(["-i", sv])

        fc_parts = []
        prev = "[0:v]"
        for i in range(1, len(scene_videos)):
            offset = sum(durs[:i]) - fade_dur * i
            is_last = i == len(scene_videos) - 1
            out = "[vout]" if is_last else f"[xf{i}]"
            fc_parts.append(
                f"{prev}[{i}:v]xfade=transition=fade:duration={fade_dur}:offset={offset:.3f}{out}"
            )
            prev = out

        filter_complex = ";".join(fc_parts) + ";[vout]format=yuv420p[final]"
        cmd = [
            "ffmpeg", "-y", *inputs,
            "-filter_complex", filter_complex,
            "-map", "[final]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            merged,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            return merged

    # Fallback
    return _merge_concat(scene_videos)


# ============================================================
# Subtitles
# ============================================================
def _srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _add_subtitles(video_path, text, W):
    temp = video_path + ".tmp.mp4"
    srt_path = os.path.join(OUTPUT_DIR, "subtitle.srt")
    dur = get_duration(video_path)

    # Split text into ~40-char chunks
    words = text.split()
    chunks, current = [], []
    for w in words:
        current.append(w)
        if len(" ".join(current)) > 40:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))

    chunk_dur = dur / max(len(chunks), 1)
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"{i+1}\n")
            f.write(f"{_srt_time(i*chunk_dur)} --> {_srt_time((i+1)*chunk_dur)}\n")
            f.write(f"{chunk}\n\n")

    font_size = int(W * 0.035)
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\\\:")

    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", (
            f"subtitles={srt_escaped}:force_style="
            f"'FontSize={font_size},PrimaryColour=&Hffffff,"
            f"OutlineColour=&H000000,Outline=2,Alignment=2,MarginV=80'"
        ),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "copy", temp,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        os.replace(temp, video_path)
    elif os.path.exists(temp):
        os.remove(temp)


# ============================================================
# Main compose
# ============================================================
def compose(image_paths, voiceover_path, video_format="9:16",
            music_path=None, music_volume=0.15,
            enable_kenburns=True, enable_crossfade=True,
            subtitle_text=None):
    """
    Full video composition pipeline:
      1. Encode scenes (parallel)
      2. Merge with/without crossfade
      3. Add audio (voiceover + optional music)
      4. Optional subtitles
    Returns (output_path, duration, size_mb)
    """
    W, H = FORMATS.get(video_format, (1080, 1920))
    output_video = os.path.join(OUTPUT_DIR, "final_video.mp4")
    audio_dur = get_duration(voiceover_path)

    fade_dur = 0.8 if enable_crossfade else 0
    n = len(image_paths)
    if enable_crossfade and n > 1:
        scene_dur = (audio_dur + fade_dur * (n - 1)) / n
    else:
        scene_dur = audio_dur / n

    # --- 1. Encode scenes (parallel) ---
    progress.update(2, "running", f"Encoding {n} scenes (parallel)...", 25)

    scene_outs = [os.path.join(OUTPUT_DIR, f"_tmp_scene{i}.mp4") for i in range(n)]

    def _do_encode(args):
        i, img = args
        _encode_scene(i, img, scene_outs[i], scene_dur, W, H, enable_kenburns)
        return scene_outs[i]

    with ThreadPoolExecutor(max_workers=min(4, n)) as pool:
        list(pool.map(_do_encode, enumerate(image_paths)))

    progress.update(2, "done", f"{n} scenes encoded", 55)

    # --- 2. Merge ---
    progress.update(3, "running", "Merging scenes...", 60)
    if enable_crossfade and n > 1:
        merged = _merge_crossfade(scene_outs, fade_dur)
    else:
        merged = _merge_concat(scene_outs)
    progress.update(3, "done", "Scenes merged", 70)

    # --- 3. Audio ---
    progress.update(4, "running", "Mixing audio...", 75)
    if music_path and os.path.exists(music_path):
        cmd_str = (
            f'ffmpeg -y -i "{merged}" -i "{voiceover_path}" -i "{music_path}" '
            f'-filter_complex "[1:a]volume=1.0[voice];[2:a]volume={music_volume},'
            f'aloop=loop=-1:size=2e9[music];[voice][music]amix=inputs=2:duration=first[aout]" '
            f'-map 0:v -map "[aout]" '
            f'-c:v copy -c:a aac -b:a 128k -shortest "{output_video}"'
        )
        subprocess.run(cmd_str, shell=True, capture_output=True, text=True, check=True)
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", merged, "-i", voiceover_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest", output_video,
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    progress.update(4, "done", "Audio mixed", 85)

    # --- 4. Subtitles ---
    if subtitle_text:
        progress.update(5, "running", "Burning subtitles...", 88)
        _add_subtitles(output_video, subtitle_text, W)

    # Cleanup temps
    for sv in scene_outs:
        if os.path.exists(sv):
            os.remove(sv)
    if os.path.exists(merged) and merged != output_video:
        os.remove(merged)

    dur = get_duration(output_video)
    size_mb = os.path.getsize(output_video) / (1024 * 1024)
    progress.update(5, "done", "Complete!", 100)
    progress.finish(True)

    return output_video, dur, size_mb
