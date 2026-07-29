import os
import requests

FIREBASE_DB_URL = os.environ.get("FIREBASE_DB_URL", "").rstrip("/")
FIREBASE_DB_SECRET = os.environ.get("FIREBASE_DB_SECRET", "")


def _admin_get(path: str):
    if not FIREBASE_DB_URL or not FIREBASE_DB_SECRET:
        return None
    url = f"{FIREBASE_DB_URL}/{path}.json?auth={FIREBASE_DB_SECRET}"
    res = requests.get(url, timeout=15)
    res.raise_for_status()
    return res.json()


def _admin_patch(path: str, data: dict):
    url = f"{FIREBASE_DB_URL}/{path}.json?auth={FIREBASE_DB_SECRET}"
    res = requests.patch(url, json=data, timeout=15)
    res.raise_for_status()


def get_pending_unconfirmed() -> list[dict]:
    """Subscribers waiting for a confirmation email to be sent."""
    subs = _admin_get("subscribers") or {}
    return [
        {"id": sub_id, **sub}
        for sub_id, sub in subs.items()
        if sub.get("status") == "pending" and not sub.get("confirmSent")
    ]


def mark_confirmation_sent(sub_id: str):
    _admin_patch(f"subscribers/{sub_id}", {"confirmSent": True})


def get_confirmed() -> list[dict]:
    """Confirmed subscribers, ready to receive the digest."""
    subs = _admin_get("subscribers") or {}
    return [
        {"id": sub_id, **sub}
        for sub_id, sub in subs.items()
        if sub.get("status") == "confirmed" and sub.get("email")
    ]
