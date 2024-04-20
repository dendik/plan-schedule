#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import argparse

from lib import GPX


def ele(elevation: float, plus: str = "") -> str:
    """Represent elevation nicely"""
    return f"{round(elevation, -1):{plus}.0f}"


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("tracks", nargs="*")
    args = parser.parse_args()

    for filename in args.tracks:
        gpx = GPX.from_xml(ET.parse(filename).getroot())
        for n, segment in enumerate(
            (segment for track in gpx.tracks for segment in track.segments), start=1
        ):
            print(
                filename,
                n,
                ele(segment.points[-1].elevation),
                ele(segment.max_elevation()),
                "'"
                + ",".join(ele(change, "+") for change in segment.elevation_changes()),
                ele(segment.elevation_gain()),
                ele(segment.elevation_loss()),
                f"{segment.length() / 1000:.1f}",
                sep="\t",
            )
