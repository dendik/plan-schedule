#!/usr/bin/env python3
import argparse
from pathlib import Path

from lib import GPX
from lib import Track

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tracks", nargs="*")
    parser.add_argument("--format", default="{filename}_{segment:03d}.gpx")
    args = parser.parse_args()

    for filename in args.tracks:
        for n, segment in enumerate(GPX.from_xml_path(filename).itersegments()):
            gpx = GPX(tracks=[Track(segments=[segment])], waypoints=[])
            out_filename = args.format.format(filename=Path(filename).stem, segment=n)
            gpx.to_xml_path(out_filename)
