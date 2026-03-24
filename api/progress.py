"""Shared progress state for real-time step tracking"""

STEPS = [
    "Tạo giọng đọc (TTS)",
    "Tải ảnh đã chọn",
    "Encode từng scene",
    "Ghép scenes + transitions",
    "Mix audio",
    "Hoàn tất",
]

_state = {
    "status": "idle",
    "step": "",
    "percent": 0,
    "steps": [],
}


def reset():
    """Reset progress for a new generation job"""
    global _state
    _state = {
        "status": "running",
        "step": "",
        "percent": 0,
        "steps": [{"name": s, "status": "pending", "detail": ""} for s in STEPS],
    }


def update(index, status, detail="", percent=None):
    """Update a specific step's status and optional detail text"""
    global _state
    if index < len(_state["steps"]):
        _state["steps"][index]["status"] = status
        if detail:
            _state["steps"][index]["detail"] = detail
    if percent is not None:
        _state["percent"] = percent
    _state["step"] = detail or _state["steps"][index]["name"]


def finish(success=True):
    global _state
    if success:
        _state["status"] = "done"
        _state["percent"] = 100
        _state["step"] = "Hoàn tất!"
    else:
        _state["status"] = "error"


def get():
    return dict(_state)
