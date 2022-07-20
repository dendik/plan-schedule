#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import argparse
import math
from pathlib import Path

ns = dict(gpx="http://www.topografix.com/GPX/1/1")

gpx_template_root = ET.fromstring(
    """
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx
    xmlns="http://www.topografix.com/GPX/1/1"
    creator="http://nakarte.me"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
    version="1.1">
    <trk></trk>
</gpx>
""".strip()
)
ET.register_namespace("", ns["gpx"])


def join(segments):
    gpx_track = gpx_template_root.find(".//gpx:trk", ns)
    gpx_template = ET.ElementTree(gpx_template_root)
    for segment in segments:
        gpx_track.append(segment)
    return gpx_template


def itersegments(filenames):
    for filename in filenames:
        root = ET.parse(filename).getroot()
        for segment in root.findall(".//gpx:trkseg", ns):
            yield segment


if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("tracks", nargs="*")
    args.add_argument("-o", "--output", required=True)
    args = args.parse_args()

    joined_track = join(itersegments(args.tracks))
    joined_track.write(args.output, method="xml", xml_declaration=True, encoding="utf-8")
