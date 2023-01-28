#!/usr/bin/env python3
import argparse

from join import join, itersegments
from pg import haversine

args = argparse.ArgumentParser()
args.add_argument("tracks", nargs="*")
args.add_argument("-o", "--output", required=True)
args = args.parse_args()


class Segment:
    def __init__(self, xml_segment, n=None, next=None):
        self.xml_segment = xml_segment
        self.n = n
        self.next = next

    def 


def segmentsort(segments):
    n_segments = {}
    for n, segment in enumerate(segments):
        n_segments[n] = Segment(segment, n)
    for segment in n_segments.values():
        segment.next = min(
            n_segments.values(), key=lambda other: haversine(segment.end, other.start)
        )
    segment = None
    while n_segments:
        if last is None or last.n not in n_segments:
            last = max(
                n_segments.values(), key=lambda segment: haversine(segment, segment.next)
            )
            segment = last.next
        yield segment
        segment = n_segments.pop(segment.n).next


track = join(segmentsort(itersegments(args.tracks)))
joined_track.write(args.output, method="xml", xml_declaration=True, encoding="utf-8")
