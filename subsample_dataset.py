"""
Create a subsample of the dataset with only the top 10 most frequent classes.
Only annotations are used to determine classes and image filenames.
"""

import os
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

SRC_ANNOTATIONS = Path("data/dataset_20210629145407_top_600/annotations")
SRC_IMAGES = Path("data/dataset_20210629145407_top_600/images")
DST_ROOT = Path("data/dataset_subsample_top10")
DST_ANNOTATIONS = DST_ROOT / "annotations"
DST_IMAGES = DST_ROOT / "images"

TOP_N = 10

print("Scanning annotations for class frequencies...")
class_counter = Counter()
xml_files = list(SRC_ANNOTATIONS.glob("*.xml"))
print(f"  Found {len(xml_files)} annotation files")

for xml_path in xml_files:
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        continue
    root = tree.getroot()
    for obj in root.findall("object"):
        name = obj.find("name").text.strip()
        class_counter[name] += 1

top_classes = set(cls for cls, _ in class_counter.most_common(TOP_N))
print(f"\nTop {TOP_N} classes:")
for cls, count in class_counter.most_common(TOP_N):
    print(f"  {cls}: {count} occurrences")

# Keep all images that contain at least one top-10 object.
# Non-top-10 objects are marked difficult=1 so training frameworks skip them
# in loss and mAP computation, but the model is not penalized for detecting them.
print("\nSelecting annotations that contain at least one top-10 class object...")
selected_xmls = []
for xml_path in xml_files:
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        continue
    root = tree.getroot()
    names_in_file = {obj.find("name").text.strip() for obj in root.findall("object")}
    if names_in_file & top_classes:
        selected_xmls.append((xml_path, tree, root))

print(f"  Selected {len(selected_xmls)} annotation files")

# Write output
DST_ANNOTATIONS.mkdir(parents=True, exist_ok=True)
DST_IMAGES.mkdir(parents=True, exist_ok=True)

copied_images = 0
skipped_images = 0

for xml_path, tree, root in selected_xmls:
    # Mark non-top-10 objects as difficult=1
    for obj in root.findall("object"):
        if obj.find("name").text.strip() not in top_classes:
            diff_el = obj.find("difficult")
            if diff_el is None:
                diff_el = ET.SubElement(obj, "difficult")
            diff_el.text = "1"

    dst_xml = DST_ANNOTATIONS / xml_path.name
    tree.write(str(dst_xml), xml_declaration=True, encoding="utf-8")

    # Copy image if it exists
    filename = root.find("filename").text.strip()
    src_img = SRC_IMAGES / filename
    dst_img = DST_IMAGES / filename
    if src_img.exists():
        shutil.copy2(src_img, dst_img)
        copied_images += 1
    else:
        skipped_images += 1

print(f"\nDone!")
print(f"  Annotations written : {len(selected_xmls)}")
print(f"  Images copied       : {copied_images}")
print(f"  Images not found    : {skipped_images}")
print(f"  Output directory    : {DST_ROOT}")
