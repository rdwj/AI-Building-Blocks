#!/usr/bin/env python3
"""
Debug KML parsing
"""

import xml.etree.ElementTree as ET

# Test simple placemark file
test_file = "sample_data/test_files_synthetic/small/kml/simple_placemark.kml"

tree = ET.parse(test_file)
root = tree.getroot()

print(f"Root tag: {root.tag}")
print(f"Root namespaces: {root.attrib}")

# Check for placemarks
placemarks = root.findall('.//Placemark')
print(f"Placemarks found: {len(placemarks)}")

for placemark in placemarks:
    print(f"Placemark tag: {placemark.tag}")
    name = placemark.find('name')
    if name is not None:
        print(f"  Name: {name.text}")

# Check all elements
print("\nAll elements:")
for elem in root.iter():
    print(f"  {elem.tag}")