import math
from utils.math_utils import deg_to_rad, rad_to_deg, EARTH_RADIUS


class CoordinateCalculator:
    """Handles forward geodesic projection.

    Given a starting point (lat, lon), a bearing, and a distance,
    calculates the destination point on the Earth's surface.
    Uses the spherical Earth model which is accurate enough for
    distances under ~100km.
    """

    def __init__(self, earth_radius=EARTH_RADIUS):
        self._R = earth_radius

    def calculate_destination(self, lat, lon, bearing_deg, distance_m):
        """Project a point from (lat, lon) along bearing for given distance.

        Args:
            lat: starting latitude in degrees
            lon: starting longitude in degrees
            bearing_deg: compass bearing in degrees (0=N, 90=E, etc.)
            distance_m: distance to project in meters

        Returns:
            tuple of (dest_lat, dest_lon) in degrees

        Raises:
            ValueError: if distance is negative or zero
        """
        if distance_m <= 0:
            raise ValueError(f"Distance must be positive, got {distance_m}")

        lat1 = deg_to_rad(lat)
        lon1 = deg_to_rad(lon)
        bearing = deg_to_rad(bearing_deg)

        d_over_r = distance_m / self._R

        # forward geodesic formula (spherical approximation)
        lat2 = math.asin(
            math.sin(lat1) * math.cos(d_over_r)
            + math.cos(lat1) * math.sin(d_over_r) * math.cos(bearing)
        )

        lon2 = lon1 + math.atan2(
            math.sin(bearing) * math.sin(d_over_r) * math.cos(lat1),
            math.cos(d_over_r) - math.sin(lat1) * math.sin(lat2),
        )

        return (rad_to_deg(lat2), rad_to_deg(lon2))

    def estimate_accuracy(self, gps_accuracy_m, distance_m, compass_error_deg=5.0):
        """Rough estimate of how accurate the projected point is.

        Takes into account GPS error, compass error, and the fact that
        angular error grows linearly with distance.
        """
        # lateral error from compass inaccuracy
        angular_error_rad = deg_to_rad(compass_error_deg)
        lateral_error = distance_m * math.tan(angular_error_rad)

        total_error = math.sqrt(gps_accuracy_m ** 2 + lateral_error ** 2)
        return round(total_error, 1)
