class GPX:
    ns: str
    tracks: List["Track"]

    _gpx_template = """
        <?xml version="1.0" encoding="UTF-8" standalone="no" ?>
        <gpx
            xmlns="http://www.topografix.com/GPX/1/1"
            creator="http://nakarte.me"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
            version="1.1">
        </gpx>
    """

    def __init__(self, filename: str) -> None:
        pass

    def write(self, filename: str) -> None:
        root = ET.fromstring(self._gpx_template.strip())
        gpx = root.find(".//gpx:gpx")
        for track in self.tracks:
            gpx.append(track.xml)

    def add_track(self, track: "Track") -> "GPX":
        self.tracks.append(track)

    def add_segment(self, segment: "Segment") -> "GPX":
        return self.add_track(Track().add_segment(segment))


class Track:
    segments: List["Segment"]

    def __init__(self, xml_root: Etree) -> None:
        pass

    def add_segment(self, segment: "Segment") -> "Track":
        self.segments.append(segment)
        return self


class Segment:
    points: List["Point"]

    def __init__(self, xml_root: Etree) -> None:
        pass

    def length(self) -> float:
        return sum(a.haversine(b) for a, b in zip(self.points, self.points[1:]))

    def elevation_gains(self, ndigits: int = -2) -> List[float]:
        elevations = [round(point.elevations, ndigits) for point in self.points]
        extrema = self._extrema(elevations)
        gains = self._gains(extrema)
        return gains

    @statimethod
    def _extrema(elevations: List[float]) -> List[float]:
        yield elevations[0]
        for a, b, c in zip(elevations, elevations[1:], elevations[2:]):
            if b < a and b < c:
                yield b
            elif b > a and b > c:
                yield b
        yield elevations[-1]

    @statimethod
    def _gains(elevations: List[float]) -> List[float]:
        pass


class Point:
    def __init__(self, xml_root: Etree) -> None:
        pass

    def haversine(self, other: "Point") -> float:
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
