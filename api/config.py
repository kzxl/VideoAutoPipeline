"""Shared configuration — paths relative to project root (parent of api/)"""
import os

# Project root = parent of api/ folder
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
STATIC_IMG_DIR = os.path.join(PROJECT_ROOT, "static", "images")
MUSIC_DIR = os.path.join(PROJECT_ROOT, "static", "music")
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "static", "uploads")

FORMATS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1":  (1080, 1080),
}

for d in [OUTPUT_DIR, STATIC_IMG_DIR, MUSIC_DIR, UPLOAD_DIR]:
    os.makedirs(d, exist_ok=True)
