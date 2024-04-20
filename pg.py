#!/usr/bin/env python3
import argparse
import xml.etree.ElementTree as ET

from lib import GPX


def ele(elevation: float, plus: str = "") -> str:
    """Represent elevation nicely"""
    return f"{round(elevation, args.round):{plus}.0f}"


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("tracks", nargs="*")
    parser.add_argument(
        "--fuzz",
        type=float,
        default=50,
        help="Fuzz factor for elevation changes. Default: 50",
    )
    parser.add_argument(
        "--round",
        type=int,
        default=-1,
        help="Print elevations rounded to this sign. Default: -1",
    )
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
                + ",".join(
                    ele(change, "+") for change in segment.elevation_changes(args.fuzz)
                ),
                ele(segment.elevation_gain()),
                ele(segment.elevation_loss()),
                f"{segment.length() / 1000:.1f}",
                sep="\t",
            )
