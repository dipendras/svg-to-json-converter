#!/usr/bin/env python3

import argparse
import json
from math import pi
from svgpathtools import svg2paths2

# Scaling and configuration parameters
A4_WIDTH, A4_HEIGHT = 210.0, 297.0
A4_MARGIN = 10.0
MAX_WIDTH, MAX_HEIGHT = A4_WIDTH - 2 * A4_MARGIN, A4_HEIGHT - 2 * A4_MARGIN
DRAW_HEIGHT = 0.0
LIFT_HEIGHT = 100.0
TOLERANCE = 1e-2  # Threshold for detecting connected segments
INTERPOLATION_SPACING = 10  # Interpolated points every 100 units


def get_interpolated_points(segment, spacing=INTERPOLATION_SPACING):
    """Extract evenly spaced points along a segment."""
    length = segment.length()
    num_points = int(length / spacing)
    points = [segment.start]

    for i in range(1, num_points + 1):
        t = segment.ilength(i * spacing)
        points.append(segment.point(t))

    points.append(segment.end)
    return [(p.real, p.imag) for p in points]


def are_points_connected(p1, p2, threshold=TOLERANCE):
    """Check if two points are connected based on a threshold."""
    return abs(p1[0] - p2[0]) < threshold and abs(p1[1] - p2[1]) < threshold


def process_svg_to_json(svg_path, json_path):
    """Process an SVG file and save its transformed path data into a JSON file."""
    paths, attributes, svg_attributes = svg2paths2(svg_path)

    all_points_3d = []
    previous_end_point = None

    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = float("-inf"), float("-inf")

    for path in paths:
        path_min_x, path_max_x, path_min_y, path_max_y = path.bbox()
        min_x, max_x = min(min_x, path_min_x), max(max_x, path_max_x)
        min_y, max_y = min(min_y, path_min_y), max(max_y, path_max_y)

        path_points = []
        for seg in path:
            interpolated_points = get_interpolated_points(seg)

            if path_points and not are_points_connected(path_points[-1][:2], interpolated_points[0]):
                path_points.append((path_points[-1][0], path_points[-1][1], LIFT_HEIGHT))
                path_points.append((interpolated_points[0][0], interpolated_points[0][1], LIFT_HEIGHT))

            path_points.extend((x, y, DRAW_HEIGHT) for x, y in interpolated_points)

        if previous_end_point and path_points and not are_points_connected(previous_end_point[:2], path_points[0][:2]):
            all_points_3d.append([(previous_end_point[0], previous_end_point[1], LIFT_HEIGHT)])
            all_points_3d.append([(path_points[0][0], path_points[0][1], LIFT_HEIGHT)])

        if path_points:
            all_points_3d.append(path_points)
            previous_end_point = path_points[-1]

    original_width, original_height = max_x - min_x, max_y - min_y
    scale_factor = min(MAX_WIDTH / original_width, MAX_HEIGHT / original_height)

    pX, pY, pZ, rZ, rY, rz2, typ = [], [], [], [], [], [], []

    x, y, z = all_points_3d[0][0]
    pX.append(scale_factor * (x - min_x) + A4_MARGIN)
    pY.append(scale_factor * (max_y - y) + A4_MARGIN)
    pZ.append(LIFT_HEIGHT)
    rZ.append(0)
    rY.append(pi)
    rz2.append(0)
    typ.append(0)

    for path in all_points_3d:
        for x, y, z in path:
            pX.append(scale_factor * (x - min_x) + A4_MARGIN)
            pY.append(scale_factor * (max_y - y) + A4_MARGIN)
            pZ.append(z)
            rZ.append(0)
            rY.append(pi)
            rz2.append(0)
            typ.append(0)

    x, y, z = all_points_3d[-1][-1]
    pX.append(scale_factor * (x - min_x) + A4_MARGIN)
    pY.append(scale_factor * (max_y - y) + A4_MARGIN)
    pZ.append(LIFT_HEIGHT)
    rZ.append(0)
    rY.append(pi)
    rz2.append(0)
    typ.append(0)

    output_data = {
        "targets": {"pX": pX, "pY": pY, "pZ": pZ, "rZ": rZ, "rY": rY, "rz2": rz2, "type": typ},
        "velocity": {"i": [0], "value": [100.0]},
        "tool": {"i": [0], "value": [1]},
        "spindle": {"i": [0], "value": [796]},
    }

    with open(json_path, "w") as outfile:
        json.dump(output_data, outfile, indent=4)

    print(f"Transformed path data saved to {json_path}.")


def main():
    parser = argparse.ArgumentParser(description="Convert SVG paths to IRBCAM-compatible JSON format.")
    parser.add_argument("svg_path", type=str, help="Path to the input SVG file.")
    parser.add_argument("json_path", type=str, help="Path to save the output JSON file.")
    args = parser.parse_args()

    process_svg_to_json(args.svg_path, args.json_path)


if __name__ == "__main__":
    main()
