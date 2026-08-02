"""Offline verification for the Vercel Telegram webhook contract.

This never calls Telegram and never needs a real token. It validates the
security envelope and representative Telegram updates across private chats,
groups, supergroups, channels, media, callbacks, and inline queries.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "api" / "telegram_webhook.py"
    spec = importlib.util.spec_from_file_location("telegram_webhook_verify", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load webhook module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def user() -> dict:
    return {"id": 123, "is_bot": False, "first_name": "Test", "username": "tester"}


def chat(chat_type: str = "private") -> dict:
    return {"id": 456, "type": chat_type}


def message(message_id: int, **fields) -> dict:
    return {
        "message_id": message_id,
        "date": 1,
        "chat": chat(fields.pop("chat_type", "private")),
        "from": user(),
        **fields,
    }


def update(update_id: int, key: str, value: dict) -> dict:
    return {"update_id": update_id, key: value}


def main() -> None:
    module = load_module()
    module.settings.WEBHOOK_SECRET = "offline-test-secret"
    headers = {"X-Telegram-Bot-Api-Secret-Token": "offline-test-secret"}
    updates = [
        update(1, "message", message(1, text="/start")),
        update(2, "message", message(2, photo=[{
            "file_id": "photo", "file_unique_id": "photo", "width": 1, "height": 1
        }])),
        update(3, "message", message(3, video={
            "file_id": "video", "file_unique_id": "video", "width": 1, "height": 1,
            "duration": 1
        })),
        update(4, "message", message(4, document={
            "file_id": "doc", "file_unique_id": "doc", "file_name": "test.txt",
            "mime_type": "text/plain"
        })),
        update(5, "message", message(5, voice={
            "file_id": "voice", "file_unique_id": "voice", "duration": 1
        })),
        update(6, "message", message(6, audio={
            "file_id": "audio", "file_unique_id": "audio", "duration": 1,
            "title": "test"
        })),
        update(7, "message", message(7, contact={
            "phone_number": "+000000000", "first_name": "Contact", "user_id": 123
        })),
        update(8, "message", message(8, location={"latitude": 0, "longitude": 0})),
        update(9, "message", message(9, sticker={
            "file_id": "sticker", "file_unique_id": "sticker", "type": "regular",
            "width": 1, "height": 1, "is_animated": False, "is_video": False
        })),
        update(10, "message", message(10, animation={
            "file_id": "gif", "file_unique_id": "gif", "width": 1, "height": 1,
            "duration": 1
        })),
        update(11, "message", message(11, text="group", chat_type="group")),
        update(12, "message", message(12, text="supergroup", chat_type="supergroup")),
        update(13, "channel_post", message(13, text="channel", chat_type="channel")),
        update(14, "callback_query", {
            "id": "callback-1", "from": user(), "chat_instance": "chat",
            "data": "menu:main", "message": message(14)
        }),
        update(15, "inline_query", {
            "id": "inline-1", "from": user(), "query": "test", "offset": ""
        }),
    ]
    for payload in updates:
        status, body, _ = module.handle_payload(
            headers,
            json.dumps(payload).encode(),
            process=False,
        )
        assert status == 200 and body["ok"], payload

    status, _, _ = module.handle_payload(
        {"X-Telegram-Bot-Api-Secret-Token": "wrong"},
        json.dumps(updates[0]).encode(),
        process=False,
    )
    assert status == 403
    assert len(module.ALL_UPDATE_TYPES) >= 20
    print(f"telegram_webhook_offline_ok updates={len(updates)}")


if __name__ == "__main__":
    main()