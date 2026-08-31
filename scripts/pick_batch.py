#!/usr/bin/env python3
"""
يختار BATCH_SIZE صورة عشوائية لم تُنشر من قبل، من images.json،
بناءً على سجل published.json، ويكتب النتيجة في next-batch.json
لكي يقرأها Make.com وينشرها في Pinterest.

- لا يوجد تكرار: أي صورة نُشرت مرة واحدة لا تُختار مرة أخرى.
- عند انتهاء كل الصور، يكتب next-batch.json فارغًا مع status = "done"
  حتى يتوقف Make.com عن محاولة النشر.
"""

import json
import random
import sys
from pathlib import Path

BATCH_SIZE = 3


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    images_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("images.json")
    published_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("published.json")
    next_batch_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("next-batch.json")

    images = load_json(images_path, [])
    published_ids = set(load_json(published_path, []))

    remaining = [img for img in images if img["id"] not in published_ids]

    if not remaining:
        save_json(next_batch_path, {"status": "done", "items": []})
        print("خلصت كل الصور — next-batch.json فارغ، status = done.")
        return

    batch = random.sample(remaining, k=min(BATCH_SIZE, len(remaining)))

    save_json(next_batch_path, {"status": "ok", "items": batch})

    published_ids.update(img["id"] for img in batch)
    save_json(published_path, sorted(published_ids))

    print(f"تم اختيار {len(batch)} صورة. متبقي بعد هاذ التشغيلة: {len(remaining) - len(batch)}.")


if __name__ == "__main__":
    main()
