<<<<<<< HEAD
# PinPoint


A cross-platform mobile application that calculates the GPS coordinates of a distant object based on where you're pointing your phone.

Point your phone at something, enter how far away you think it is, and PinPoint projects the GPS coordinates of that object using your current position, compass heading, and forward geodesic math.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | **Python 3.10+** | Core application logic |
| UI Framework | **Kivy 2.3** | Cross-platform GUI (iOS, Android, Desktop) |
| Styling | **Custom Material 3 theme** | Dark/light mode, rounded cards, clean typography |
| Sensors | **Plyer** | Cross-platform access to GPS, compass, accelerometer, gyroscope |
| Camera | **Kivy Camera + OpenCV** | Live camera preview with crosshair overlay |
| Storage | **JSON (stdlib)** | Lightweight local persistence for saved locations |
| Images | **Pillow** | Image processing support |
| Math | **Python math (stdlib)** | Trigonometry, geodesic calculations |
| Testing | **pytest** | Unit and integration tests |
| Android Build | **Buildozer** | Compiles Python app to APK |
| iOS Build | **kivy-ios** | Compiles Python app for iPhone/iPad |

### Python Packages Used

- `kivy` — GUI framework, handles rendering, input, camera, window management
- `plyer` — Platform-agnostic API for GPS, compass, accelerometer, gyroscope
- `opencv-python` — Camera provider for desktop (webcam access)
- `Pillow` — Image handling dependency for Kivy
- `pytest` — Test runner

---

## How It Works

1. The app reads your GPS position and compass heading in real time
2. You aim your phone at a target using the camera viewfinder with crosshair
3. You enter the estimated distance to the object in meters
4. The app calculates the projected GPS coordinates using a spherical Earth model
5. Results can be viewed on a map, saved locally, or copied/shared

---

## Project Structure

```
pinpoint/
├── main.py                          # App entry point, initializes services and screens
├── domain/
│   └── coordinate_calculator.py     # Forward geodesic projection engine
├── data/
│   └── location_repository.py       # JSON-based local storage for saved locations
├── services/
│   ├── location_service.py          # GPS wrapper (plyer on mobile, manual input on desktop)
│   ├── compass_service.py           # Compass heading with circular smoothing
│   ├── sensor_service.py            # Accelerometer/gyroscope for tilt detection
│   └── camera_service.py            # Camera preview + crosshair overlay
├── presentation/
│   ├── theme.py                     # Material 3 color palette, sizing constants
│   ├── screens/
│   │   ├── camera_screen.py         # Main viewfinder screen with controls
│   │   ├── result_screen.py         # Calculated coordinates display card
│   │   └── history_screen.py        # Saved locations list
│   └── widgets/
│       ├── heading_display.py       # Compass heading badge (e.g. "135° SE")
│       ├── accuracy_indicator.py    # GPS accuracy with color coding
│       └── styled_button.py         # Custom Material 3 buttons
├── utils/
│   ├── math_utils.py                # Angle conversions, circular averaging, smoothing
│   └── permissions.py               # Android/iOS runtime permission handling
├── tests/
│   ├── test_coordinate_calculator.py  # Geodesic math tests
│   ├── test_math_utils.py             # Utility function tests
│   └── test_services.py               # Storage layer tests
├── buildozer.spec                   # Android build configuration
├── requirements.txt                 # Python dependencies
└── .gitignore
```

### Architecture

The project follows a **layered architecture** with clear separation of concerns:

- **domain/** — Pure business logic. The coordinate calculator has zero framework dependencies and can be tested standalone.
- **data/** — Persistence layer. JSON file storage, no database needed.
- **services/** — Sensor abstraction. Each service wraps hardware (GPS, compass, accelerometer, camera) and provides mock fallbacks for desktop testing.
- **presentation/** — UI layer built with Kivy. Screens, widgets, and theme definitions.
- **utils/** — Shared helpers for math operations and platform permissions.

---

## Mathematical Model

The coordinate projection uses the **forward geodesic formula** on a spherical Earth:

```
lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(bearing))
lon2 = lon1 + atan2(sin(bearing) * sin(d/R) * cos(lat1), cos(d/R) - sin(lat1) * sin(lat2))
```

Where:
- `(lat1, lon1)` = user's current GPS position (converted to radians)
- `bearing` = compass heading (converted to radians)
- `d` = estimated distance in meters
- `R` = Earth's mean radius (6,371,000 m)

Accurate to within a few meters for distances under 100 km.

### Accuracy Estimation

Total projected error combines:
- **GPS accuracy** (typically ±5–15m on modern phones)
- **Compass angular error** (typically ±3–5°, grows with distance)
- Formula: `total_error = sqrt(gps_error² + (distance * tan(compass_error))²)`

---

## Setup & Running

### Prerequisites

- Python 3.10 or higher
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run on Desktop

```bash
python main.py
```

On desktop, the app runs in a 400x750 window. Since there's no real GPS or compass:
- You manually enter your lat/lon coordinates
- Compass simulates a slow rotation
- Camera uses your webcam or falls back to a grid background

### Build for Android

```bash
pip install buildozer
buildozer android debug
```

The APK will be in `bin/`. Buildozer downloads the Android SDK/NDK automatically on first build.

### Build for iOS

Requires macOS with Xcode installed:
```bash
pip install kivy-ios
toolchain build kivy
toolchain create PinPoint .
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

28 tests covering:
- Forward geodesic calculation against known reference points (London → Paris, equator traversals)
- Edge cases (zero/negative distance, 360° bearing, round-trip projections)
- Angle conversion and heading normalization
- Circular heading smoothing (handles the 0°/360° wraparound)
- Data persistence, serialization, and deletion

---

## Sensor Integration

| Sensor | Mobile (Android/iOS) | Desktop (Windows/Mac/Linux) |
|--------|---------------------|---------------------------|
| GPS | plyer GPS — real coordinates | Manual lat/lon input |
| Compass | plyer compass — magnetic field to heading | Simulated slow rotation |
| Accelerometer | plyer accelerometer — pitch/roll | Simulated near-level |
| Camera | Kivy Camera widget — live feed | OpenCV webcam or grid fallback |

Sensor smoothing:
- Compass uses **circular averaging** (sin/cos decomposition) so the 0°/360° wraparound doesn't cause jumps
- Accelerometer uses a moving average window (5 samples)
- History buffers are trimmed automatically to prevent memory buildup

---

## Known Limitations

1. **GPS accuracy** — Consumer phone GPS is ±5–15m. This is the baseline error floor.
2. **Compass drift** — Metal objects, buildings, or the phone case itself can bias the compass by several degrees.
3. **Distance estimation** — The user guesses the distance, which is the biggest error source. 20% off at 1 km = 200m error.
4. **Spherical Earth model** — Uses a sphere, not WGS84 ellipsoid. Error is <0.3% for distances under 100 km.
5. **Tilt sensitivity** — Compass works best when the phone is held level. The app warns if tilted.
6. **No declination correction** — Reads magnetic north, not true north. Can differ by up to 20° depending on location.

---

## Future Improvements

- AR-based distance estimation using LiDAR (iPhone Pro) or ToF sensors
- Magnetic declination auto-correction based on GPS location
- Topographic data integration to snap points to terrain
- Multi-point triangulation from 2+ positions for better accuracy
- KML/GPX export for mapping software
- Offline map tiles on the result screen
- Kalman filter for sensor fusion

---

## Presentation Outline

1. **Problem Statement** — Why locate distant objects by GPS?
2. **Live Demo** — Run the app on a phone, locate a landmark
3. **Architecture** — Layered design, separation of concerns, service abstraction
4. **The Math** — Forward geodesic formula, why spherical approximation works
5. **Sensor Integration** — GPS, compass, accelerometer — reading and smoothing
6. **Challenges Solved** — Compass wraparound, sensor noise, tilt detection
7. **Accuracy Analysis** — Error sources, how accuracy degrades with distance
8. **Future Work** — AR distance estimation, declination correction, triangulation
