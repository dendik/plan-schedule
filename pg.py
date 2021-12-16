#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import argparse
import math

ns = dict(gpx="http://www.topografix.com/GPX/1/1")

args = argparse.ArgumentParser()
args.add_argument('tracks', nargs='*')
args.add_argument('-s', '--sort', action="store_true",
	help="Apply topological sort to track segments")
args = args.parse_args()

class Segment:
	def __init__(self, segment_xml):
		self.segment_xml = segment_xml
		self.points = self.get_points()
		self.elevations = self.get_elevations()
		self.start = self.points[0]
		self.end = self.points[-1]

	def get_points(self):
		return [
			(float(point.get('lat')), float(point.get('lon')))
			for point in self.segment_xml.findall('gpx:trkpt', ns)
		]

	def get_elevations(self):
		return [
			float(ele.text)
			for ele in self.segment_xml.findall('gpx:trkpt/gpx:ele', ns)
		]

def segmentsort(segments):
	segments = dict(enumerate(segments))
	for n, segment in segments.items():
		segment.n = n
	closest = {
		segment.n: min(segments.values(),
			key=lambda other: haversine(segment.end, other.start))
		for segment in segments.values()
	}
	incoming_distance = {
		segment.n: min(
			haversine(segment.start, other.end)
			for other in segments.values())
		for segment in segments.values()
	}
	first_n = max(incoming_distance, key=incoming_distance.__getitem__)
	segment = segments[first_n]
	seen = set()
	while closest:
		yield segment
		seen.add(segment.n)
		segment = closest.pop(segment.n)
	if segment.n not in seen:
		yield segment

def simplify(elevations, grid=100):
	return [
		round(elevation / grid) * grid
		for elevation in elevations
	]

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
    R = 6372800/1000  # Earth radius in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

def length(points):
	return sum(haversine(a, b) for a, b in zip(points, points[1:]))

for filename in args.tracks:
	root = ET.parse(filename).getroot()
	segments = map(Segment, root.findall('.//gpx:trkseg', ns))
	if args.sort:
		segments = segmentsort(segments)
	for n, segment in enumerate(segments, start=1):
		elevations = segment.elevations
		points = segment.points
		ele_extrema = list(extrema(simplify(elevations)))
		ele_gains = ",".join("{:+d}".format(gain) for gain in gains(ele_extrema))
		print(filename, n, ele_extrema[-1], max(ele_extrema), "'" + ele_gains, "{:.1f}".format(length(points)), sep='\t')
