"""AI Script generation using Google Gemini free API"""
import os
import requests

# Gemini free tier: 15 RPM, 1M tokens/day — no credit card needed
# Set env GEMINI_API_KEY or use default (user should get their own key)
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = "gemini-2.0-flash"


def generate_script(topic, lang="vi"):
    """Generate a narration script for video. Returns text string."""
    if not API_KEY:
        return _fallback_script(topic, lang)

    prompts = {
        "vi": f"Viết một kịch bản ngắn (3-5 câu) cho video review/giới thiệu về: {topic}. Chỉ viết nội dung đọc, không ghi tiêu đề hay chú thích. Phong cách tự nhiên, hấp dẫn.",
        "en": f"Write a short narration script (3-5 sentences) for a video about: {topic}. Only write the narration text, no titles or notes. Natural, engaging style.",
        "ja": f"以下のトピックについて、短いナレーション（3〜5文）を書いてください: {topic}",
        "ko": f"다음 주제에 대한 짧은 나레이션(3-5문장)을 작성하세요: {topic}",
        "zh": f"为以下主题写一段简短的旁白（3-5句话）: {topic}",
    }
    prompt = prompts.get(lang, prompts["en"])

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
        resp = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 300},
        }, timeout=15)
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip()
    except Exception as e:
        print(f"[AI] Gemini failed: {e}")
        return _fallback_script(topic, lang)


def _fallback_script(topic, lang="vi"):
    """Fallback when no API key — generate a template script"""
    templates = {
        "vi": f"Hôm nay chúng ta cùng tìm hiểu về {topic}. Đây là một chủ đề thú vị với nhiều điều đáng khám phá. Hãy cùng nhau khám phá những điều thú vị nhất nhé.",
        "en": f"Today we explore {topic}. This is a fascinating subject with many interesting aspects to discover. Let's dive into the most compelling details together.",
    }
    return templates.get(lang, templates["en"])
