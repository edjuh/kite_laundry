"""
Geometry generation functions for kite laundry patterns.
Each function returns a list of panels with coordinates, ready for rendering.
"""

import math


# ---------- DROGUE GEOMETRY ----------
def generate_drogue_geometry(project, length_mm, settings):
    """Generate simple drogue (cone) panels."""
    gores = project.get("gores", 4)
    top_diam = project.get("top_diam", length_mm / 4)
    bottom_diam = project.get("bottom_diam", 0)
    height = project.get("length", length_mm)
    
    panels = []
    half_top = top_diam / 2
    for i in range(gores):
        angle = i * (360 / gores)
        points = [
            (0, 0),
            (half_top, height),
            (-half_top, height)
        ]
        panels.append({
            "name": f"Gore_{i+1}",
            "points": points,
            "color": "#FF4444" if i % 2 == 0 else "#FFFFFF"
        })
    return panels


# ---------- SPINNER GEOMETRY ----------
def generate_spinner_geometry(project, length_mm, settings):
    """Generate simple 4-panel spinner geometry."""
    num_panels = project.get("num_panels", 4)
    radius = project.get("radius", length_mm / 6)
    height = project.get("length", length_mm)

    panels = []
    for i in range(num_panels):
        angle = i * (360 / num_panels)
        points = [
            (0, 0),
            (radius, height / 2),
            (0, height),
            (-radius, height / 2)
        ]
        panels.append({
            "name": f"Panel_{i+1}",
            "points": points,
            "color": "#FFD700" if i % 2 == 0 else "#FF6600"
        })
    return panels


# ---------- STREAMER GEOMETRY ----------
def generate_streamer_geometry(project, length_mm, settings):
    """Generate a simple rectangular streamer."""
    width = project.get("width", length_mm / 10)
    length = project.get("length", length_mm)
    panels = [{
        "name": "Streamer",
        "points": [(0, 0), (width, 0), (width, length), (0, length)],
        "color": "#88CCFF"
    }]
    return panels


# ---------- Fallback ----------
def default_geometry(project, length_mm, settings):
    """Fallback shape if no geometry is specified."""
    return [{
        "name": "DefaultPanel",
        "points": [(0, 0), (100, 0), (50, 150)],
        "color": "#CCCCCC"
    }]

def generate_parachute_gore_geometry(project, length, settings):
    """Generate a simple radial parachute gore shape."""
    import math
    gores = project.get("gores", 8)
    top_diam = project.get("top_diam", length / 3)
    points = [(0, 0)]
    for i in range(gores + 1):
        angle = i * (math.pi / gores)
        x = (top_diam / 2) * math.cos(angle)
        y = (length / 2) * math.sin(angle)
        points.append((x, y))
    return [{"name": f"Gore_{i}", "points": points, "color": "#FFFFFF"}
