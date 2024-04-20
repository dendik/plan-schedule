"""GPX processing library
"""

import math
import xml.etree.ElementTree as ET
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt
from typing import List
from typing import Optional
from typing import Tuple
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import QName

from config import app_name

earth_radius_m = 6371000


class GPX:
    """
    Represents a GPX file containing tracks and waypoints.
    """

    ns = "http://www.topografix.com/GPX/1/1"
    nsmap = dict(gpx=ns)

    def __init__(self, tracks: List["Track"], waypoints: List["Point"]):
        """
        Initialize a GPX object.

        Args:
            tracks (List[Track]): List of tracks in the GPX file.
            waypoints (List[Point]): List of waypoints in the GPX file.
        """
        self.tracks = tracks
        self.waypoints = waypoints

    @classmethod
    def from_xml(cls, xml_element: Element):
        """
        Parse XML Element to create a GPX object.

        Args:
            xml_element (Element): XML Element representing a GPX file.

        Returns:
            GPX: Parsed GPX object.
        """
        tracks = [
            Track.from_xml(track_xml)
            for track_xml in xml_element.findall("gpx:trk", cls.nsmap)
        ]
        waypoints = [
            Point.from_xml(waypoint_xml)
            for waypoint_xml in xml_element.findall("gpx:wpt", cls.nsmap)
        ]
        return cls(tracks, waypoints)

    def to_xml(self) -> Element:
        """
        Generate XML Element representing the GPX file.

        Returns:
            Element: XML Element representing the GPX file.
        """
        gpx = GPXElement("gpx", attrib={"version": "1.1", "creator": app_name})
        for waypoint in self.waypoints:
            gpx.append(waypoint.to_xml())
        for track in self.tracks:
            gpx.append(track.to_xml())
        return gpx

    def length(self) -> float:
        """
        Calculate the total length of all tracks in the GPX file.

        Returns:
            float: Total length of all tracks in meters.
        """
        return sum(track.length() for track in self.tracks)

    def min_elevation(self) -> float:
        """
        Calculate the minimum elevation among all points in all tracks of the GPX file.

        Returns:
            float: Minimum elevation in the GPX file.
        """
        return min(track.min_elevation() for track in self.tracks)

    def max_elevation(self) -> float:
        """
        Calculate the maximum elevation among all points in all tracks of the GPX file.

        Returns:
            float: Maximum elevation in the GPX file.
        """
        return max(track.max_elevation() for track in self.tracks)

    def elevation_gain(self) -> float:
        """
        Calculate the total elevation gain in all tracks of the GPX file.

        Returns:
            float: Total elevation gain in the GPX file.
        """
        return sum(track.elevation_gain() for track in self.tracks)

    def elevation_loss(self) -> float:
        """
        Calculate the total elevation loss in all tracks of the GPX file.

        Returns:
            float: Total elevation loss in the GPX file.
        """
        return sum(track.elevation_loss() for track in self.tracks)

    def elevation_changes(self, fuzz: float = 50) -> List[float]:
        """
        Calculate the elevation changes between local extrema in tracks of the GPX file, ignoring changes smaller than fuzz.

        Args:
            fuzz (float, optional): Threshold below which changes are ignored. Defaults to 50.

        Returns:
            List[float]: List of elevation changes.
        """
        return [
            change for track in self.tracks for change in track.elevation_changes(fuzz)
        ]


class Track:
    """
    Represents a track in a GPX file.
    """

    def __init__(self, segments: List["Segment"]):
        """
        Initialize a Track object.

        Args:
            segments (List[Segment]): List of segments in the track.
        """
        self.segments = segments

    @classmethod
    def from_xml(cls, xml_element: Element):
        """
        Parse XML Element to create a Track object.

        Args:
            xml_element (Element): XML Element representing a track.

        Returns:
            Track: Parsed Track object.
        """
        segments = [
            Segment.from_xml(segment_xml)
            for segment_xml in xml_element.findall("gpx:trkseg", GPX.nsmap)
        ]
        return cls(segments)

    def to_xml(self) -> Element:
        """
        Generate XML Element representing the track.

        Returns:
            Element: XML Element representing the track.
        """
        track = GPXElement("trk")
        for segment in self.segments:
            track.append(segment.to_xml())
        return track

    def split_track_at_point(self, point: "Point"):
        """
        Split the track into multiple segments at the given point.

        Args:
            point (Point): The point at which to split the track.
        """
        for n, segment in enumerate(self.segments):
            if point in segment.points:
                segment_a, segment_b = segment.split_segment_at_point(point)
                self.segments.insert(n, segment_a)
                self.segments.insert(n, segment_b)
                self.segments.pop(n)
                return

    def length(self) -> float:
        """
        Calculate the total length of all segments in the track.

        Returns:
            float: Total length of all segments in meters.
        """
        return sum(segment.length() for segment in self.segments)

    def min_elevation(self) -> float:
        """
        Calculate the minimum elevation among all points in all segments of the track.

        Returns:
            float: Minimum elevation in the track.
        """
        return min(segment.min_elevation() for segment in self.segments)

    def max_elevation(self) -> float:
        """
        Calculate the maximum elevation among all points in all segments of the track.

        Returns:
            float: Maximum elevation in the track.
        """
        return max(segment.max_elevation() for segment in self.segments)

    def elevation_gain(self) -> float:
        """
        Calculate the total elevation gain in the track.

        Returns:
            float: Total elevation gain in the track.
        """
        return sum(segment.elevation_gain() for segment in self.segments)

    def elevation_loss(self) -> float:
        """
        Calculate the total elevation loss in the track.

        Returns:
            float: Total elevation loss in the track.
        """
        return sum(segment.elevation_loss() for segment in self.segments)

    def elevation_changes(self, fuzz: float = 50) -> List[float]:
        """
        Calculate the elevation changes between local extrema of the track, ignoring changes smaller than fuzz.

        Args:
            fuzz (float, optional): Threshold below which changes are ignored. Defaults to 50.

        Returns:
            List[float]: List of elevation changes.
        """
        return [
            change
            for segment in self.segments
            for change in segment.elevation_changes(fuzz)
        ]


class Segment:
    """
    Represents a segment of track points in a GPX file.
    """

    def __init__(self, points: List["Point"]):
        """
        Initialize a Segment object.

        Args:
            points (List[Point]): List of points in the segment.
        """
        self.points = points

    @classmethod
    def from_xml(cls, xml_element: Element):
        """
        Parse XML Element to create a Segment object.

        Args:
            xml_element (Element): XML Element representing a segment.

        Returns:
            Segment: Parsed Segment object.
        """
        points = [
            Point.from_xml(point_xml)
            for point_xml in xml_element.findall("gpx:trkpt", GPX.nsmap)
        ]
        return cls(points)

    def to_xml(self) -> Element:
        """
        Generate XML Element representing the segment.

        Returns:
            Element: XML Element representing the segment.
        """
        segment = GPXElement("trkseg")
        for point in self.points:
            segment.append(point.to_xml())
        return segment

    def split_segment_at_point(self, point: "Point") -> Tuple["Segment", "Segment"]:
        """
        Split the segment into two segments at the given point.

        Args:
            point (Point): The point at which to split the segment.

        Returns:
            List[Segment]: The two new segments resulting from the split.
        """
        index = self.points.index(point)
        segment_a_points = self.points[: index + 1]
        segment_b_points = self.points[index:]
        return Segment(segment_a_points), Segment(segment_b_points)

    def length(self) -> float:
        """
        Calculate the length of the segment.

        Returns:
            float: Length of the segment in meters.
        """
        return sum(
            point_a.haversine_distance(point_b)
            for point_a, point_b in zip(self.points, self.points[1:])
        )

    def min_elevation(self) -> float:
        """
        Calculate the minimum elevation among all points in the segment.

        Returns:
            float: Minimum elevation in the segment.
        """
        return min(
            point.elevation for point in self.points if point.elevation is not None
        )

    def max_elevation(self) -> float:
        """
        Calculate the maximum elevation among all points in the segment.

        Returns:
            float: Maximum elevation in the segment.
        """
        return max(
            point.elevation for point in self.points if point.elevation is not None
        )

    def elevation_gain(self) -> float:
        """
        Calculate the total elevation gain in the segment.

        Returns:
            float: Total elevation gain in the segment.
        """
        return sum(
            max(0, elevation(point_b) - elevation(point_a))
            for point_a, point_b in zip(self.points, self.points[1:])
        )

    def elevation_loss(self) -> float:
        """
        Calculate the total elevation loss in the segment.

        Returns:
            float: Total elevation loss in the segment.
        """
        return sum(
            max(0, -elevation(point_b) + elevation(point_a))
            for point_a, point_b in zip(self.points, self.points[1:])
        )

    def elevation_changes(self, fuzz: float = 50) -> List[float]:
        """
        Calculate the elevation changes between local extrema in the segment.

        Args:
            fuzz (float): Maximal magnitude of elevation change to be ignored.

        Returns:
            List[float]: List of elevation changes.
        """
        elevation_changes = [
            elevation(point_b) - elevation(point_a)
            for point_a, point_b in zip(self.points, self.points[1:])
        ]
        elevation_changes = self._simplify_elevation_changes(elevation_changes)
        elevation_changes = self._defuzz_elevation_changes(elevation_changes, fuzz)
        return elevation_changes

    @staticmethod
    def _simplify_elevation_changes(elevation_changes: List[float]) -> List[float]:
        """
        Simplify a list of elevation changes by merging consecutive changes with the same sign.

        Args:
            elevation_changes (List[float]): List of elevation changes.

        Returns:
            List[float]: Simplified list of elevation changes.
        """
        if not elevation_changes:
            return []

        simplified_changes = [elevation_changes[0]]
        for change in elevation_changes[1:]:
            if change * simplified_changes[-1] >= 0:
                simplified_changes[-1] += change
            else:
                simplified_changes.append(change)

        return simplified_changes

    @staticmethod
    def _defuzz_elevation_changes(
        elevation_changes: List[float], fuzz: float
    ) -> List[float]:
        """
        Simplify a list of elevation changes by merging changes smaller than `fuzz`.

        Args:
            elevation-changes (List[float]): List of elevation changes.
            fuzz (float): magnitude of changes to be ignored.

        Returns:
            List[float]: Simplified list of elevation changes.
        """
        simplified_changes = [0.0]
        for change in elevation_changes:
            if abs(change) < fuzz:
                simplified_changes[-1] += change
            elif change * simplified_changes[-1] >= 0:
                simplified_changes[-1] += change
            else:
                simplified_changes.append(change)
        if simplified_changes[0] == 0.0:
            simplified_changes = simplified_changes[1:]
        return simplified_changes


class Point:
    """
    Represents a waypoint in a GPX file.
    """

    latitude: float
    longitude: float
    elevation: Optional[float]
    timestamp: Optional[str]

    def __init__(
        self,
        latitude: float,
        longitude: float,
        elevation: Optional[float] = None,
        timestamp: Optional[str] = None,
    ):
        """
        Initialize a Point object.

        Args:
            latitude (float): Latitude of the point.
            longitude (float): Longitude of the point.
            elevation (float, optional): Elevation of the point. Defaults to None.
            timestamp (str, optional): Timestamp of the point. Defaults to None.
        """
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.timestamp = timestamp

    @classmethod
    def from_xml(cls, xml_element: Element):
        """
        Parse XML Element to create a Point object.

        Args:
            xml_element (Element): XML Element representing a point.

        Returns:
            Point: Parsed Point object.
        """
        latitude = float(xml_element.attrib["lat"])
        longitude = float(xml_element.attrib["lon"])
        elevation = float(xml_element.findtext("gpx:ele", "NaN", GPX.nsmap))
        timestamp = xml_element.findtext("gpx:time", None, GPX.nsmap)
        return cls(latitude, longitude, nan2none(elevation), timestamp)

    def to_xml(self) -> Element:
        """
        Generate XML Element representing the point.

        Returns:
            Element: XML Element representing the point.
        """
        point = GPXElement(
            "wpt",
            attrib={"lat": str(self.latitude), "lon": str(self.longitude)},
        )
        if self.elevation is not None:
            ele = GPXElement("ele")
            ele.text = str(self.elevation)
            point.append(ele)
        if self.timestamp is not None:
            time = GPXElement("time")
            time.text = self.timestamp
            point.append(time)
        return point

    def haversine_distance(self, other: "Point") -> float:
        """
        Calculate the Haversine distance between two points.

        Args:
            other (Point): Another point to calculate the distance to.

        Returns:
            float: Haversine distance between the points in meters.
        """
        # Implementation of haversine formula
        # (assuming Earth is a perfect sphere)

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = earth_radius_m * c
        return distance

    def find_nearest_track_point(self, tracks: List[Track]) -> "Point":
        """
        Find the nearest track point to the current point from a list of tracks.

        Args:
            tracks (List[Track]): List of tracks to search for the nearest point.

        Returns:
            Point: The nearest track point.
        """
        min_distance = float("inf")
        nearest_point = None

        for track in tracks:
            for segment in track.segments:
                for track_point in segment.points:
                    distance = self.haversine_distance(track_point)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_point = track_point

        assert nearest_point is not None, "Could not find nearest point"
        return nearest_point


class GPXElement(Element):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tag = QName(GPX.ns, self.tag)  # type: ignore
        self.attrib = {
            QName(GPX.ns, name): value  # type: ignore
            for name, value in self.attrib.items()
        }


def nan2none(value: float) -> Optional[float]:
    if math.isnan(value):
        return None
    return value


def elevation(point: Point) -> float:
    """Return point elevation. Raise an error if a point has no elevation."""
    assert point.elevation is not None, "Point has no elevation"
    return point.elevation


if __name__ == "__main__":
    gpx_str = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
        <gpx
            xmlns="http://www.topografix.com/GPX/1/1"
            creator="plan-schedule"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
            version="1.1">
            <trk><trkseg>
                <trkpt lat="51.1234" lon="0.5678"><ele>100</ele><time>2024-04-19T12:00:00Z</time></trkpt>
                <trkpt lat="51.4567" lon="0.5879"><ele>150</ele><time>2024-04-19T12:00:00Z</time></trkpt>
                <trkpt lat="51.2345" lon="0.5789"><ele>120</ele><time>2024-04-19T12:00:00Z</time></trkpt>
            </trkseg></trk>
        </gpx>
    """
    gpx_xml = ET.fromstring(gpx_str)
    gpx = GPX.from_xml(gpx_xml)

    # Convert GPX object back to XML
    new_gpx_xml = gpx.to_xml()
    print(ET.tostring(new_gpx_xml, default_namespace=GPX.ns).decode())
    print("Length:", round(gpx.length()), "m")
    print("Min elevation:", round(gpx.min_elevation()), "m")
    print("Max elevation:", round(gpx.max_elevation()), "m")
    print("Elevation gain:", round(gpx.elevation_gain()), "m")
    print("Elevation loss:", round(gpx.elevation_loss()), "m")
