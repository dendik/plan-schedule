#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import argparse
import math

ns = dict(gpx="http://www.topografix.com/GPX/1/1")

args = argparse.ArgumentParser()
args.add_argument('tracks', nargs='*')
args = args.parse_args()

def simplify(elevations, grid=50):
	return [
		round(elevation / grid) * grid
		for elevation in elevations
	]

def extrema(elevations):
	yield elevations[0]
	for a, b, c in zip(elevations, elevations[1:], elevations[2:]):
		if b < a and b < c:
			yield b
		if b > a and b > c:
			yield b
	yield elevations[-1]

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
	for n, segment in enumerate(root.findall('.//gpx:trkseg', ns), start=1):
		elevations = [
			float(ele.text)
			for ele in segment.findall('gpx:trkpt/gpx:ele', ns)
		]
		points = [
			(float(point.get('lat')), float(point.get('lon')))
			for point in segment.findall('gpx:trkpt', ns)
		]
		ele_extrema = list(extrema(simplify(elevations)))
		ele_gains = ",".join("{:+d}".format(gain) for gain in gains(ele_extrema))
		print(filename, n, ele_extrema[-1], max(ele_extrema), "'" + ele_gains, "{:.1f}".format(length(points)), sep='\t')
