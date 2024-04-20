#!/usr/bin/env python3
import argparse

from lib import GPX
from lib import Track

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("tracks", nargs="*")
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    gpxes = [GPX.from_xml_path(gpx_path) for gpx_path in args.tracks]

    segments = [
        segment for gpx in gpxes for track in gpx.tracks for segment in track.segments
    ]

    waypoints = [point for gpx in gpxes for point in gpx.waypoints]

    joined_gpx = GPX(tracks=[Track(segments=segments)], waypoints=waypoints)
    joined_gpx.to_xml_path(args.output)
