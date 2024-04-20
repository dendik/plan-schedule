#!/usr/bin/env python3
import argparse
from pathlib import Path

from lib import GPX


def key(point):
    return f"{float(point.latitude):.6f}" f"{float(point.longitude):.6f}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--track")
    parser.add_argument("-d", "--data-track")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    if args.output is None:
        args.output = Path(args.track).with_suffix(".with-data.gpx")

    data_points = {
        key(point): point
        for point in GPX.from_xml_path(args.data_track).itertrackpoints()
    }

    gpx = GPX.from_xml_path(args.track)
    for point in gpx.itertrackpoints():
        if (data_point := data_points.get(key(point))) is not None:
            point.elevation = data_point.elevation
            point.timestamp = data_point.timestamp

    assert not Path(args.output).exists()
    gpx.to_xml_path(args.output)
