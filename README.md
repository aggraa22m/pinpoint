# Object Locator

A cross-platform mobile application that calculates the GPS coordinates of a distant object based on where you're pointing your phone.

You point your phone at something, enter how far away you think it is, and the app projects the GPS coordinates of that object using your current position + compass heading + forward geodesic math.

---

## How It Works

1. The app reads your GPS position and compass heading in real time
2. You aim your phone at a target using the camera viewfinder
3. You enter the estimated distance to the object
4. The app calculates the projected GPS coordinates using a spherical Earth model
5. Results can be viewed on a map, saved locally, or shared

## Architecture

```
object_locator/
├── main.py                     # App entry point
├── domain/
│   └── coordinate_calculator.py  # Forward geodesic projection engine
├── data/
│   └── location_repository.py    # Local JSON storage for saved locations
├── services/
│   ├── location_service.py       # GPS wrapper (real on mobile, mock on desktop)
│   ├── compass_service.py        # Compass heading with circular smoothing
│   ├── sensor_service.py         # Accelerometer/gyroscope for tilt detection
│   └── camera_service.py         # Camera preview with crosshair overlay
├── presentation/
│   ├── theme.py                  # Colors, sizing, Material 3 palette
│   ├── screens/
│   │   ├── camera_screen.py      # Main viewfinder screen
│   │   ├── result_screen.py      # Calculated coordinates display
│   │   └── history_screen.py     # Saved locations list
│   └── widgets/
│       ├── heading_display.py    # Compass heading badge
│       ├── accuracy_indicator.py # GPS accuracy indicator
│       └── styled_button.py      # Custom Material buttons
├── utils/
│   ├── math_utils.py             # Angle conversions, smoothing functions
│   └── permissions.py            # Platform permission handling
├── tests/
│   ├── test_coordinate_calculator.py
│   ├── test_math_utils.py
│   └── test_services.py
├── buildozer.spec                # Android build config
└── requirements.txt
```

The project follows a layered architecture:

- **domain/** — Core business logic. The coordinate calculator is pure math with no framework dependencies.
- **data/** — Persistence layer. JSON-based local storage.
- **services/** — Sensor abstraction. Each service wraps a hardware sensor and provides mock fallbacks for desktop testing.
- **presentation/** — UI layer. Kivy screens and widgets with Material 3 styling.
- **utils/** — Shared utilities (math helpers, permission wrappers).

## Mathematical Model

The coordinate projection uses the **forward geodesic formula** on a spherical Earth:

```
lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(bearing))
lon2 = lon1 + atan2(sin(bearing) * sin(d/R) * cos(lat1), cos(d/R) - sin(lat1) * sin(lat2))
```

Where:
- `(lat1, lon1)` = user's current GPS position (radians)
- `bearing` = compass heading (radians)
- `d` = estimated distance (meters)
- `R` = Earth's mean radius (6,371,000 m)

This is the Vincenty/Haversine forward projection. It's accurate to within a few meters for distances under 100 km, which is well within our use case.

### Accuracy Estimation

The app estimates total error by combining:
- **GPS accuracy** (typically ±5–15m on modern phones)
- **Compass angular error** (typically ±3–5°, grows linearly with distance)
- Combined via: `total_error = sqrt(gps_error² + (distance * tan(compass_error))²)`

## Setup & Running

### Prerequisites

- Python 3.10+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run on Desktop (Testing Mode)

```bash
python main.py
```

On desktop, the app uses mock sensors:
- GPS simulates being in San Francisco with realistic drift
- Compass slowly rotates with noise
- Camera falls back to a grid background with crosshair

### Build for Android

Install buildozer:
```bash
pip install buildozer
```

Then build:
```bash
buildozer android debug
```

The APK will be in `bin/`. You need the Android SDK/NDK — buildozer handles downloading them on first build.

### Build for iOS

Requires macOS with Xcode:
```bash
pip install kivy-ios
toolchain build kivy
toolchain create ObjectLocator .
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All 28 tests should pass. Tests cover:
- Forward geodesic calculation with known reference points
- Edge cases (zero/negative distance, full-circle bearings, round-trip projections)
- Angle conversion and normalization
- Heading smoothing (including 0°/360° wraparound)
- Data persistence and serialization

## Sensor Integration

| Sensor | Mobile | Desktop |
|--------|--------|---------|
| GPS | plyer GPS (real coordinates) | Mock: San Francisco with drift |
| Compass | plyer compass (magnetic field → heading) | Mock: slow rotation with noise |
| Accelerometer | plyer accelerometer (pitch/roll) | Mock: near-level with jitter |
| Camera | Kivy Camera widget (live preview) | Webcam or fallback grid |

All sensor readings are smoothed:
- Compass uses **circular averaging** (sin/cos decomposition) to handle the 0°/360° wraparound correctly
- Accelerometer uses a simple moving average window
- Both trim their history buffers to prevent memory growth

## Known Limitations

1. **GPS accuracy**: Consumer phone GPS is typically ±5–15m. This is the baseline error floor regardless of everything else.
2. **Compass drift**: Magnetic interference from metal objects, buildings, or the phone itself can throw the compass off by several degrees. The app smooths readings but can't correct for persistent bias.
3. **Distance estimation**: The user manually estimates distance, which is the biggest source of error by far. A 20% error in distance estimation at 1 km means 200m of error in the result.
4. **Spherical Earth model**: We use a sphere, not an ellipsoid. For distances under 100 km, the error from this approximation is negligible (<0.3%).
5. **Tilt sensitivity**: The app warns if the phone is tilted significantly, but the compass reading is most accurate when the phone is held level.
6. **No magnetic declination correction**: The compass gives magnetic north, not true north. Depending on your location, this can differ by up to 20°. A future version could correct for this using a declination model.

## Future Improvements

- AR-based distance estimation using camera depth sensors (LiDAR on iPhone Pro, ToF on some Androids)
- Magnetic declination auto-correction based on GPS location
- Integration with topographic data to snap projected points to terrain
- Multi-point triangulation (take readings from 2+ positions to refine accuracy)
- Export to KML/GPX for use in mapping software
- Offline map tiles for the result screen
- Kalman filter for sensor fusion instead of simple moving average

## Suggested Presentation Outline

1. **Problem Statement** — Why do we need to find GPS coordinates of distant objects?
2. **Demo** — Live demo of the app on a phone
3. **Architecture** — Clean layered design, separation of concerns
4. **Math** — The forward geodesic formula, why it works, accuracy bounds
5. **Sensor Integration** — How we read and smooth GPS, compass, accelerometer data
6. **Challenges** — Compass wraparound, sensor noise, tilt handling
7. **Accuracy Analysis** — What contributes to error, how bad is it at various distances
8. **Future Work** — AR distance estimation, declination correction, triangulation
