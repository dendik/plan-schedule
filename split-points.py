#!/usr/bin/env python3
import argparse

from lib import GPX
from lib import Track

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("track")
    parser.add_argument("-o", "--output", help="Output one file with segments")
    parser.add_argument("--format", default="{filename}_{segment:03d}.gpx")
    args = parser.parse_args()

    gpx = GPX.from_xml_path(args.track)
    for waypoint in gpx.waypoints:
        trackpoint = waypoint.find_nearest_track_point(gpx.tracks)
        gpx.split_at_point(trackpoint)

    if args.output:
        gpx.to_xml_path(args.output)
    else:
        for n, segment in enumerate(gpx.itersegments()):
            gpx = GPX(tracks=[Track(segments=[segment])], waypoints=[])
            gpx.to_xml_path(args.format.format(filename=args.track, segment=n))
