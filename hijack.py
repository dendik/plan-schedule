#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path

ns = dict(gpx="http://www.topografix.com/GPX/1/1")

args = argparse.ArgumentParser()
args.add_argument('-t', '--track')
args.add_argument('-d', '--data-track')
args.add_argument('-o', '--output')
args = args.parse_args()

if args.output is None:
    args.output = Path(args.track).with_suffix("-with-data")

track = ET.parse(args.track).getroot()
data_track = ET.parse(args.data_track).getroot()
ET.register_namespace('', ns['gpx'])

def key(point):
    return tuple(
        f"{float(point.attrib[attr]):.6f}"
        for attr in ('lat', 'lon')
    )

def replace(source, target):
    tail = target.tail
    target.clear()
    target.attrib = source.attrib
    target.text = source.text
    target.tail = tail
    for element in source:
        target.append(element)

data = {
    key(point): point
    for point in data_track.findall('.//gpx:trkpt', ns)
}
print(sorted(data))
for point in track.findall('.//gpx:trkpt', ns):
    data_point = data.get(key(point))
    print(key(point), data_point)
    if data_point is not None:
        replace(data_point, point)

assert not Path(args.output).exists()
ET.ElementTree(track).write(args.output, method='xml', xml_declaration=True, encoding='utf-8')
