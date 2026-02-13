import math

EARTH_RADIUS = 6_371_000  # meters


def deg_to_rad(deg):
    return deg * math.pi / 180.0


def rad_to_deg(rad):
    return rad * 180.0 / math.pi


def normalize_heading(heading):
    """Keep heading in [0, 360) range."""
    return heading % 360.0


def heading_to_cardinal(heading):
    """Convert numeric heading to cardinal direction label like N, NE, etc."""
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    idx = round(heading / 22.5) % 16
    return directions[idx]


def smooth_values(values, window=5):
    """Simple moving average for sensor smoothing.

    Not the fanciest filter but works well enough for compass readings
    and accelerometer data without introducing too much lag.
    """
    if not values:
        return 0.0
    window = min(window, len(values))
    recent = values[-window:]
    return sum(recent) / len(recent)


def smooth_heading(headings, window=5):
    """Circular average for heading values.

    Can't just average angles normally because of the 0/360 wraparound.
    Using sin/cos decomposition instead.
    """
    if not headings:
        return 0.0
    window = min(window, len(headings))
    recent = headings[-window:]

    sin_sum = sum(math.sin(deg_to_rad(h)) for h in recent)
    cos_sum = sum(math.cos(deg_to_rad(h)) for h in recent)

    avg_rad = math.atan2(sin_sum / len(recent), cos_sum / len(recent))
    avg_deg = rad_to_deg(avg_rad)

    return normalize_heading(avg_deg)
