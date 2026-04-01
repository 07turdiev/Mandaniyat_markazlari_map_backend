import json
import urllib.request
import urllib.error

BASE_URL = "https://websocket.tahrirchi.uz"
AUTH_BASE_URL = "https://auth.tahrirchi.uz"
REFRESH_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJleHAiOjE4MDM3OTkwNDAsImlhdCI6MTc3MjY5NTA0MCwic3ViIjoiZWI2YWI5YWItMzBiYy0xMWYwLWE4ZTEtMDI0MmFjMTMwMDE4IiwidHNpZCI6ImZiMDY2ZDIwLTYyY2MtNGQ1Yy1hOGE0LTA5OWJmOTkwNTZiNyIsInR5cGUiOjB9."
    "28UfZSJo1UVHa1LMtYSCrQmrz3C-X0jOvCqb-oep9Mw"
)
ACCESS_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJleHAiOjE3ODgyNDcwNDAsImlhdCI6MTc3MjY5NTA0MCwic3ViIjoiZWI2YWI5YWItMzBiYy0xMWYwLWE4ZTEtMDI0MmFjMTMwMDE4IiwidHNpZCI6ImZiMDY2ZDIwLTYyY2MtNGQ1Yy1hOGE0LTA5OWJmOTkwNTZiNyIsInR5cGUiOjB9."
    "Rq2KqWnWwEdFxdPNOn4ZESE7Sc8j37Z5Jod-H7gDdXM"
)

_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

_current_access_token = ACCESS_TOKEN


def _refresh_token():
    global _current_access_token
    url = f"{AUTH_BASE_URL}/v1/token/refresh"
    data = json.dumps({}).encode("utf-8")
    headers = {**_HEADERS, "Authorization": f"Bearer {REFRESH_TOKEN}"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        _current_access_token = body["access_token"]


def translate_text(text):
    """
    Bitta matnni o'zbekchadan ruschaga tarjima qiladi.
    Xatolik bo'lsa None qaytaradi.
    """
    if not text or not text.strip():
        return None

    global _current_access_token
    payload = {
        "jobs": [{"text": text.strip(), "id": 1}],
        "source_lang": "uzn_Latn",
        "target_lang": "rus_Cyrl",
    }

    url = f"{BASE_URL}/handle-batch"
    data = json.dumps(payload).encode("utf-8")
    headers = {**_HEADERS, "Authorization": f"Bearer {_current_access_token}"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            sentences = body.get("sentences", [])
            if sentences:
                return sentences[0].get("translated")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            try:
                _refresh_token()
                return translate_text(text)
            except Exception:
                pass
    except Exception:
        pass

    return None


def translate_batch(texts_with_ids):
    """
    Bir nechta matnni tarjima qiladi.
    texts_with_ids: [(id, text), ...]
    Qaytaradi: {id: translated_text, ...}
    """
    if not texts_with_ids:
        return {}

    global _current_access_token
    jobs = [{"text": text.strip(), "id": job_id} for job_id, text in texts_with_ids if text.strip()]
    payload = {
        "jobs": jobs,
        "source_lang": "uzn_Latn",
        "target_lang": "rus_Cyrl",
    }

    url = f"{BASE_URL}/handle-batch"
    data = json.dumps(payload).encode("utf-8")
    headers = {**_HEADERS, "Authorization": f"Bearer {_current_access_token}"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {
                item["id"]: item["translated"]
                for item in body.get("sentences", [])
            }
    except urllib.error.HTTPError as e:
        if e.code == 401:
            try:
                _refresh_token()
                return translate_batch(texts_with_ids)
            except Exception:
                pass
    except Exception:
        pass

    return {}
