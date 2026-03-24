"""Image search via Bing HTML scraping — no API key needed"""
import re
import hashlib
import os
import requests

from config import STATIC_IMG_DIR

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def search_images(topic, num_images=16, source="bing"):
    """Search images from Bing or Pexels. Returns list of {url, thumb, title}."""
    if source == "pexels":
        return _search_pexels(topic, num_images)
    return _search_bing(topic, num_images)


def _search_bing(topic, num_images=16):
    query = topic.replace(" ", "+")
    url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first=1"

    images = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+?)&quot;', resp.text)
            if not matches:
                matches = re.findall(r'murl":"(https?://[^"]+?)"', resp.text)

            seen = set()
            for m_url in matches:
                if m_url in seen:
                    continue
                seen.add(m_url)
                if any(ext in m_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    images.append({
                        "url": m_url,
                        "thumb": m_url,
                        "title": topic,
                    })
                if len(images) >= num_images:
                    break
    except Exception as e:
        print(f"[bing] error: {e}")
    return images


def _search_pexels(topic, num_images=16):
    """Scrape Pexels for free stock images (no API key needed)"""
    query = topic.replace(" ", "+")
    url = f"https://www.pexels.com/search/{query}/"

    images = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            # Pexels stores image data in data-attributes and srcset
            # Extract photo URLs from srcset or data-src patterns
            matches = re.findall(
                r'https://images\.pexels\.com/photos/\d+/[^"\'?\s]+\.(?:jpeg|jpg|png)',
                resp.text
            )
            seen = set()
            for m_url in matches:
                # Prefer medium size
                base = m_url.split('?')[0]
                if base in seen:
                    continue
                seen.add(base)
                thumb = base + "?auto=compress&cs=tinysrgb&w=300"
                images.append({
                    "url": base + "?auto=compress&cs=tinysrgb&w=1260",
                    "thumb": thumb,
                    "title": f"{topic} (Pexels)",
                })
                if len(images) >= num_images:
                    break
    except Exception as e:
        print(f"[pexels] error: {e}")
    return images


def download_image(url, filename=None):
    """Download a single image to STATIC_IMG_DIR. Return local filename or None."""
    if not filename:
        ext = ".png" if ".png" in url.lower() else ".jpg"
        filename = f"scene_{hashlib.md5(url.encode()).hexdigest()[:8]}{ext}"

    filepath = os.path.join(STATIC_IMG_DIR, filename)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, stream=True)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            if os.path.getsize(filepath) > 5000:
                return filepath
            os.remove(filepath)
    except Exception:
        pass
    return None


def download_images_parallel(urls, max_workers=4):
    """Download multiple images concurrently. Return list of local paths."""
    from concurrent.futures import ThreadPoolExecutor

    paths = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(download_image, url): url for url in urls}
        for future in futures:
            result = future.result()
            if result:
                paths.append(result)
    return paths
