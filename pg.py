#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import argparse

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

for filename in args.tracks:
	root = ET.parse(filename).getroot()
	for n, track in enumerate(root.findall('.//gpx:trkseg', ns), start=1):
		elevations = [
			float(ele.text)
			for ele in track.findall('gpx:trkpt/gpx:ele', ns)
		]
		ele_extrema = list(extrema(simplify(elevations)))
		ele_gains = ",".join("{:+d}".format(gain) for gain in gains(ele_extrema))
		print()
		print(elevations)
		print(simplify(elevations))
		print(ele_extrema)
		print(list(gains(ele_extrema)))
		print(filename, n, ele_extrema[-1], max(ele_extrema), "'" + ele_gains, sep='\t')
