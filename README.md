# Converts a svg file to IRBCAM Compatible json path

# Usage
```
python3 convert_svg.py path/to/svg.svg /path/to/json.json
```

# Parameters (See convert_svg.py)
```
A4_WIDTH, A4_HEIGHT = 210.0, 297.0
A4_MARGIN = 10.0
MAX_WIDTH, MAX_HEIGHT = A4_WIDTH - 2 * A4_MARGIN, A4_HEIGHT - 2 * A4_MARGIN
DRAW_HEIGHT = 0.0
LIFT_HEIGHT = 100.0
TOLERANCE = 1e-2  # Threshold for detecting connected segments
INTERPOLATION_SPACING = 10  # Interpolated points every 10 units
```