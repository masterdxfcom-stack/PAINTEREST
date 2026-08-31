
#!/usr/bin/env python3
"""
يحول ملف sitemap الصور (sitemap-images.xml) إلى images.json
جاهز للاستهلاك من Make.com عبر raw.githubusercontent.com

كل عنصر في images.json يحتوي على:
- id           : معرف ثابت مبني على رابط الصفحة (يستعمل كمفتاح فريد)
- page_url     : رابط صفحة التصميم (loc)
- image_url    : رابط الصورة (image:loc)
- title        : عنوان الصورة (image:title)
- description  : الوصف (image:caption)
- hashtags     : هاشتاغات قوية مولدة تلقائيًا من العنوان + الوصف
- pin_text     : نص جاهز للنشر مباشرة (title + description + hashtags)
"""

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
}

# هاشتاغات أساسية ثابتة تنضاف دايمًا (النيتش العام: CNC / Laser / DXF)
BASE_TAGS = ["#CNC", "#LaserCutting", "#DXFFile", "#CNCDesign", "#WoodworkingDIY"]

# خريطة كلمات مفتاحية -> هاشتاغات مرتبطة (تتفحص في العنوان + الوصف)
KEYWORD_TAGS = {
    "door": ["#DoorDesign", "#DoorPanel"],
    "wall art": ["#MetalWallArt", "#WallDecor"],
    "wall panel": ["#WallPanel", "#HomeDecor"],
    "mandala": ["#MandalaArt", "#MandalaDesign"],
    "arabesque": ["#ArabesqueDesign", "#IslamicArt"],
    "islamic": ["#IslamicPattern", "#IslamicArt"],
    "geometric": ["#GeometricDesign", "#GeometricArt"],
    "lattice": ["#PrivacyScreen", "#LatticeDesign"],
    "screen": ["#PrivacyScreen", "#RoomDivider"],
    "gate": ["#MetalGate", "#GateDesign"],
    "animal": ["#AnimalArt"],
    "eagle": ["#EagleArt", "#WildlifeArt"],
    "wolf": ["#WolfArt", "#WildlifeArt"],
    "lion": ["#LionArt", "#WildlifeArt"],
    "horse": ["#HorseArt", "#EquineArt"],
    "shark": ["#SharkArt", "#OceanArt"],
    "pirate": ["#PirateArt", "#NauticalDecor"],
    "ship": ["#NauticalDecor", "#ShipArt"],
    "peacock": ["#PeacockArt"],
    "floral": ["#FloralDesign"],
    "damask": ["#DamaskPattern"],
    "plasma": ["#PlasmaCutting"],
    "router": ["#CNCRouter", "#Woodworking"],
    "metal": ["#MetalArt"],
    "furniture": ["#FurnitureDesign"],
}

MAX_HASHTAGS = 12


def slugify_id(page_url: str) -> str:
    """معرف قصير وثابت مبني على رابط الصفحة (لا يتغير حتى لو تغيّر ترتيب الملف)."""
    return hashlib.sha1(page_url.encode("utf-8")).hexdigest()[:12]


def build_hashtags(title: str, description: str) -> list[str]:
    text = f"{title} {description}".lower()
    tags: list[str] = []

    for keyword, kw_tags in KEYWORD_TAGS.items():
        if keyword in text:
            for t in kw_tags:
                if t not in tags:
                    tags.append(t)

    for t in BASE_TAGS:
        if t not in tags:
            tags.append(t)

    return tags[:MAX_HASHTAGS]


def build_pin_text(title: str, description: str, hashtags: list[str]) -> str:
    return f"{title}\n\n{description}\n\n{' '.join(hashtags)}"


def parse_sitemap(xml_path: Path) -> list[dict]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    items = []
    for url_el in root.findall("sm:url", NS):
        loc_el = url_el.find("sm:loc", NS)
        img_el = url_el.find("image:image", NS)
        if loc_el is None or img_el is None:
            continue

        page_url = (loc_el.text or "").strip()
        image_loc_el = img_el.find("image:loc", NS)
        title_el = img_el.find("image:title", NS)
        caption_el = img_el.find("image:caption", NS)

        image_url = (image_loc_el.text or "").strip() if image_loc_el is not None else ""
        title = (title_el.text or "").strip() if title_el is not None else ""
        description = (caption_el.text or "").strip() if caption_el is not None else ""

        if not page_url or not image_url:
            continue

        hashtags = build_hashtags(title, description)

        items.append({
            "id": slugify_id(page_url),
            "page_url": page_url,
            "image_url": image_url,
            "title": title,
            "description": description,
            "hashtags": hashtags,
            "pin_text": build_pin_text(title, description, hashtags),
        })

    return items


def main():
    xml_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sitemap-images.xml")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("images.json")

    if not xml_path.exists():
        print(f"خطأ: الملف غير موجود: {xml_path}", file=sys.stderr)
        sys.exit(1)

    items = parse_sitemap(xml_path)

    # تحذف أي تكرار محتمل لنفس الصورة (نفس id)
    seen = set()
    unique_items = []
    for it in items:
        if it["id"] in seen:
            continue
        seen.add(it["id"])
        unique_items.append(it)

    out_path.write_text(
        json.dumps(unique_items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"تم إنشاء {out_path} — {len(unique_items)} صورة.")


if __name__ == "__main__":
    main()
