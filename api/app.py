"""
Video Creator — Flask API (Pure REST, no templates)
Frontend served by Vite dev server or static build.
"""
import os
import sys
import time

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

sys.stdout.reconfigure(encoding='utf-8')

from config import OUTPUT_DIR, STATIC_IMG_DIR, MUSIC_DIR, UPLOAD_DIR, FORMATS
import progress
import search
import tts
from tts import get_duration
import video
import ai_script

app = Flask(__name__)
CORS(app)  # Allow Vite dev server (port 5173) to call API
app.config['TEMPLATES_AUTO_RELOAD'] = True


# ============================================================
# API: AI Script Generation
# ============================================================
@app.route("/api/generate-script", methods=["POST"])
def api_generate_script():
    topic = request.json.get("topic", "").strip()
    lang = request.json.get("lang", "vi")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    try:
        script = ai_script.generate_script(topic, lang=lang)
        return jsonify({"script": script})
    except Exception as e:
        return jsonify({"error": str(e)[:300]}), 500


# ============================================================
# API: Search
# ============================================================
@app.route("/api/search", methods=["POST"])
def api_search():
    topic = request.json.get("topic", "").strip()
    source = request.json.get("source", "bing")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    images = search.search_images(topic, num_images=16, source=source)
    results = [{"id": i, **img} for i, img in enumerate(images)]
    return jsonify({"images": results, "count": len(results)})


# ============================================================
# API: Audio Preview
# ============================================================
@app.route("/api/preview-audio", methods=["POST"])
def api_preview_audio():
    data = request.json
    text = data.get("text", "").strip()
    voice = data.get("voice", "vi-VN-NamMinhNeural")
    rate = data.get("rate", "0")

    if not text:
        return jsonify({"error": "Text is required"}), 400
    try:
        path, dur = tts.generate(text, voice=voice, rate=rate)
        return jsonify({
            "audio_url": f"/output/voiceover.mp3?t={int(time.time())}",
            "duration": round(dur, 1),
        })
    except Exception as e:
        return jsonify({"error": str(e)[:300]}), 500


# ============================================================
# API: Generate Video
# ============================================================
@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.json
    narration = data.get("narration", "").strip()
    selected_urls = data.get("images", [])
    voice = data.get("voice", "vi-VN-NamMinhNeural")
    rate = data.get("rate", "0")
    video_format = data.get("format", "9:16")
    enable_kenburns = data.get("kenburns", True)
    enable_crossfade = data.get("crossfade", True)
    enable_subtitle = data.get("subtitle", False)
    music_volume = data.get("musicVolume", 0.15)

    if not narration:
        return jsonify({"error": "Nhập nội dung giọng đọc"}), 400
    if len(selected_urls) < 2:
        return jsonify({"error": "Chọn ít nhất 2 ảnh"}), 400

    try:
        progress.reset()

        # Step 0: TTS
        progress.update(0, "running", "Generating voiceover...", 5)
        voiceover_path, _ = tts.generate(narration, voice=voice, rate=rate)
        progress.update(0, "done", "Voiceover ready", 10)

        # Step 1: Download images (parallel) — skip for uploaded files
        progress.update(1, "running", f"Downloading {len(selected_urls)} images...", 12)
        image_paths = []
        upload_urls = [u for u in selected_urls if u.startswith("/static/uploads/")]
        web_urls = [u for u in selected_urls if not u.startswith("/static/uploads/")]

        # Local uploads — just resolve path
        for u in upload_urls:
            fp = os.path.join(os.path.dirname(OUTPUT_DIR), u.lstrip("/"))
            if os.path.exists(fp):
                image_paths.append(fp)

        # Web URLs — parallel download
        if web_urls:
            downloaded = search.download_images_parallel(web_urls, max_workers=4)
            image_paths.extend(downloaded)

        progress.update(1, "done", f"{len(image_paths)} images ready", 20)

        if len(image_paths) < 2:
            progress.finish(False)
            return jsonify({"error": "Không tải được đủ ảnh. Thử ảnh khác."}), 400

        # Step 2-5: Compose
        music_path = os.path.join(MUSIC_DIR, "background.mp3")
        if not os.path.exists(music_path):
            music_path = None

        output_video, duration, size_mb = video.compose(
            image_paths, voiceover_path,
            video_format=video_format,
            music_path=music_path,
            music_volume=music_volume,
            enable_kenburns=enable_kenburns,
            enable_crossfade=enable_crossfade,
            subtitle_text=narration if enable_subtitle else None,
        )

        W, H = FORMATS.get(video_format, (1080, 1920))
        return jsonify({
            "success": True,
            "video_url": f"/output/final_video.mp4?t={int(time.time())}",
            "duration": round(duration, 1),
            "size_mb": round(size_mb, 1),
            "resolution": f"{W}x{H}",
        })
    except Exception as e:
        progress.finish(False)
        return jsonify({"error": str(e)[:300]}), 500


# ============================================================
# API: Upload images from computer
# ============================================================
@app.route("/api/upload-images", methods=["POST"])
def api_upload_images():
    if "files" not in request.files:
        return jsonify({"error": "No files"}), 400
    files = request.files.getlist("files")
    results = []
    for f in files:
        if f.filename:
            import hashlib
            ext = os.path.splitext(f.filename)[1] or ".jpg"
            name = f"upload_{hashlib.md5(f.filename.encode()).hexdigest()[:8]}{ext}"
            path = os.path.join(UPLOAD_DIR, name)
            f.save(path)
            results.append({
                "url": f"/static/uploads/{name}",
                "thumb": f"/static/uploads/{name}",
                "title": f.filename,
                "uploaded": True,
            })
    return jsonify({"images": results, "count": len(results)})


# ============================================================
# API: Music
# ============================================================
@app.route("/api/upload-music", methods=["POST"])
def api_upload_music():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    filepath = os.path.join(MUSIC_DIR, "background.mp3")
    file.save(filepath)
    dur = get_duration(filepath)
    return jsonify({
        "success": True,
        "duration": round(dur, 1),
        "size_kb": round(os.path.getsize(filepath) / 1024),
        "filename": file.filename,
    })


@app.route("/api/remove-music", methods=["POST"])
def api_remove_music():
    fp = os.path.join(MUSIC_DIR, "background.mp3")
    if os.path.exists(fp):
        os.remove(fp)
    return jsonify({"success": True})


@app.route("/api/progress")
def api_progress():
    return jsonify(progress.get())


# Static file serving (output + uploaded images)
@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/static/<path:filename>")
def serve_static(filename):
    static_root = os.path.join(os.path.dirname(OUTPUT_DIR), "static")
    return send_from_directory(static_root, filename)


if __name__ == "__main__":
    print("=" * 50)
    print("🎬 Video Creator API")
    print("   http://localhost:5050")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5050, debug=False)
