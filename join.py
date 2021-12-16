#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import argparse
import math
from pathlib import Path

ns = dict(gpx="http://www.topografix.com/GPX/1/1")

args = argparse.ArgumentParser()
args.add_argument('tracks', nargs='*')
args.add_argument('-o', '--output', required=True)
args = args.parse_args()

gpx_template_root = ET.fromstring("""
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx
	xmlns="http://www.topografix.com/GPX/1/1"
	creator="http://nakarte.me"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
	version="1.1">
	<trk></trk>
</gpx>
""".strip())
gpx_track = gpx_template_root.find('.//gpx:trk', ns)
gpx_template = ET.ElementTree(gpx_template_root)
ET.register_namespace('', ns['gpx'])

for filename in args.tracks:
	root = ET.parse(filename).getroot()
	for segment in root.findall('.//gpx:trkseg', ns):
		gpx_track.append(segment)
	gpx_template.write(args.output, method='xml', xml_declaration=True, encoding='utf-8')
