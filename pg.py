#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import argparse
import math

ns = dict(gpx="http://www.topografix.com/GPX/1/1")


class Segment:
    def __init__(self, segment_xml):
        self.segment_xml = segment_xml
        self.points = self.get_points()
        self.elevations = self.get_elevations()
        self.start = self.points[0]
        self.end = self.points[-1]

    def get_points(self):
        return [
            (float(point.get("lat")), float(point.get("lon")))
            for point in self.segment_xml.findall("gpx:trkpt", ns)
        ]

    def get_elevations(self):
        return [
            float(ele.text) for ele in self.segment_xml.findall("gpx:trkpt/gpx:ele", ns)
        ]


def simplify(elevations, grid=100):
    return [round(elevation / grid) * grid for elevation in elevations]


def extrema(elevations):
    is_ascending = None
    yield elevations[0]
    for previous, this in zip(elevations, elevations[1:]):
        if is_ascending is True and previous > this:
            yield previous
        elif is_ascending is False and previous < this:
            yield previous
        if previous != this:
            is_ascending = previous < this
    yield this


def gains(extrema):
    for a, b in zip(extrema, extrema[1:]):
        yield b - a


def haversine(coord1, coord2):
    # Source: https://janakiev.com/blog/gps-points-distance-python/
    R = 6372800 / 1000  # Earth radius in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def length(points):
    return sum(haversine(a, b) for a, b in zip(points, points[1:]))


if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("tracks", nargs="*")
    args = args.parse_args()

    for filename in args.tracks:
        root = ET.parse(filename).getroot()
        segments = map(Segment, root.findall(".//gpx:trkseg", ns))
        for n, segment in enumerate(segments, start=1):
            elevations = segment.elevations
            points = segment.points
            ele_extrema = list(extrema(simplify(elevations)))
            ele_gains = ",".join("{:+d}".format(gain) for gain in gains(ele_extrema))
            print(
                filename,
                n,
                ele_extrema[-1],
                max(ele_extrema),
                "'" + ele_gains,
                "{:.1f}".format(length(points)),
                sep="\t",
            )
