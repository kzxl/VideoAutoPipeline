<div align="center">

# 🎬 Video Creator

**Auto Pipeline — From Topic to Video in Minutes**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-green?logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

*A sleek, web-based video creation tool that transforms images and narration into polished videos — powered by AI, built with modern architecture.*

[English](#-features) • [Tiếng Việt](#-tính-năng)

<img src="https://raw.githubusercontent.com/phongvo/VideoAutoPipeline/main/docs/preview.png" alt="Video Creator Preview" width="800" />

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Multi-Source Image Search** | Search from **Bing** or **Pexels** (free stock photos) |
| 📤 **Image Upload** | Drag & drop or upload your own images |
| 🖱 **Drag & Drop Reorder** | Visually reorder selected images by dragging |
| ✨ **AI Script Generator** | Auto-generate narration scripts via **Google Gemini** free API |
| 🗣 **12 TTS Voices** | Vietnamese, English, Japanese, Korean, Chinese neural voices |
| ⚡ **Speed Control** | Adjust narration speed from -50% to +50% |
| 🎧 **Audio Preview** | Listen before generating the full video |
| 🔄 **Ken Burns Effect** | Cinematic zoom-in/zoom-out animations |
| ✨ **Crossfade Transitions** | Smooth fade transitions between scenes |
| 📝 **Subtitle Overlay** | Auto-generated subtitles burned into video |
| 🎵 **Background Music** | Upload music with volume control |
| 📱 **Multi-Format** | 9:16 (TikTok/Reels), 16:9 (YouTube), 1:1 (Instagram) |
| ⚡ **Parallel Processing** | Concurrent image download & scene encoding |
| 📊 **Step-by-Step Progress** | Real-time 6-step progress with visual indicators |
| 🔥 **Vite HMR** | Instant UI updates during development |

## 🏗 Architecture

Built with **Universe Architecture** principles — modular, decoupled, and scalable.

```
VideoAutoPipeline/
├── api/                         # 🐍 Python Backend (Flask REST)
│   ├── app.py                   # Routes + CORS
│   ├── ai_script.py             # Gemini AI script generation
│   ├── search.py                # Bing + Pexels scraping
│   ├── tts.py                   # edge-tts neural voices
│   ├── video.py                 # FFmpeg composition engine
│   ├── config.py                # Shared configuration
│   └── progress.py              # Step-based progress tracking
│
├── web/                         # ⚡ Vite Frontend (Vanilla JS)
│   ├── src/
│   │   ├── core/                # 🧠 Core (Stable)
│   │   │   ├── EventBus.js      # Pub/Sub messaging
│   │   │   ├── api.js           # Contract-First API client
│   │   │   └── state.js         # Reactive shared state
│   │   ├── components/          # 🧩 Components (Volatile)
│   │   │   ├── SearchPanel.js   # Source tabs + search
│   │   │   ├── ImageGrid.js     # Grid + select + drag reorder
│   │   │   ├── NarrationPanel.js # Text + AI script
│   │   │   ├── VoicePanel.js    # Voice + speed
│   │   │   ├── OptionsPanel.js  # Format + effects + music
│   │   │   ├── GeneratePanel.js # Generate + progress + player
│   │   │   └── Toast.js         # Notifications
│   │   └── style.css            # Design system
│   └── vite.config.js           # Proxy config
│
└── start.bat                    # 🚀 Launch both servers
```

### Design Principles (Universe Architecture)

| Principle | Implementation |
|---|---|
| **Core Stable, Modules Volatile** | `core/` rarely changes; components iterate freely |
| **Module Independence** | Components never import each other |
| **Contract-First** | All API calls defined in `api.js` interface |
| **Registry** | `main.js` auto-mounts components by selector |
| **Indirect Communication** | `EventBus` for all cross-component messaging |
| **Data Sovereignty** | Each component owns its DOM; shared state via `state.js` |

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **FFmpeg** installed and in PATH

### Install

```bash
# Clone
git clone https://github.com/kzxl/VideoAutoPipeline.git
cd VideoAutoPipeline

# Backend dependencies
pip install flask flask-cors edge-tts requests

# Frontend dependencies
cd web && npm install && cd ..
```

### Run

```bash
# Option 1: One click
start.bat

# Option 2: Manual (two terminals)
cd api && python app.py          # Backend → http://localhost:5050
cd web && npx vite --port 5173   # Frontend → http://localhost:5173
```

### AI Script (Optional)

Set your **free** [Google Gemini API key](https://aistudio.google.com/apikey):

```bash
set GEMINI_API_KEY=your_key_here
```

> Free tier: 15 requests/minute, 1M tokens/day — no credit card needed.

## 🎯 Workflow

```
1. Search images → Bing / Pexels / Upload
2. Select & reorder images (drag to reorder)
3. Write narration (or use AI Script ✨)
4. Choose voice, speed, format, effects
5. Generate → watch progress → download video 🎉
```

---

# 🇻🇳 Tiếng Việt

## 🎬 Video Creator — Tạo Video Tự Động

Tool tạo video chuyên nghiệp từ ảnh + giọng đọc, chạy local, **hoàn toàn miễn phí**.

## ✨ Tính năng

- 🔍 Tìm ảnh từ **Bing** hoặc **Pexels** (ảnh miễn phí bản quyền)
- 📤 Upload ảnh từ máy tính (kéo thả)
- ✨ **AI viết kịch bản** — nhập chủ đề → Gemini tự viết script
- 🗣 **12 giọng đọc** — Việt, Anh, Nhật, Hàn, Trung
- 🎧 Nghe thử giọng trước khi tạo video
- 🖱 Kéo thả sắp xếp thứ tự ảnh
- 🔄 Hiệu ứng Ken Burns (zoom) + Crossfade (chuyển cảnh mượt)
- 📝 Phụ đề tự động
- 🎵 Upload nhạc nền + chỉnh volume
- 📱 Hỗ trợ TikTok (9:16), YouTube (16:9), Instagram (1:1)
- ⚡ Xử lý song song — tải ảnh + encode nhanh hơn
- 📊 Thanh tiến trình 6 bước real-time

## 🚀 Cài đặt

```bash
# Cài Python dependencies
pip install flask flask-cors edge-tts requests

# Cài frontend
cd web && npm install && cd ..

# Chạy
start.bat
# Mở http://localhost:5173
```

## 🔑 AI Script (tuỳ chọn)

Lấy API key miễn phí tại [Google AI Studio](https://aistudio.google.com/apikey), rồi:

```bash
set GEMINI_API_KEY=your_key
```

## 📋 Quy trình

```
1. Tìm ảnh → chọn nguồn Bing / Pexels / Upload
2. Chọn ảnh, kéo thả sắp xếp thứ tự
3. Viết nội dung (hoặc AI viết ✨)
4. Chọn giọng, tốc độ, định dạng, hiệu ứng
5. Bấm Generate → xem tiến trình → tải video 🎉
```

---

## 📄 License

MIT License — use freely for personal and commercial projects.

## 🤝 Credits

- [edge-tts](https://github.com/rany2/edge-tts) — Microsoft Neural TTS
- [FFmpeg](https://ffmpeg.org) — Video processing
- [Vite](https://vitejs.dev) — Frontend build tool
- [Pexels](https://pexels.com) — Free stock photos
- [Google Gemini](https://ai.google.dev) — AI script generation
