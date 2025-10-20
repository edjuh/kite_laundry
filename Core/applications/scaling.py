# -*- coding: utf-8 -*-
"""
Scaling module for kite laundry designs
Scales dimensions while maintaining usability (e.g., drag, inlet size)
"""
def calculate_drag(area_m2, shape_factor=1.0):
    """Estimate drag coefficient based on area and shape (simplified)"""
    # Drag ≈ k * A * v² (k ~ 0.5 for flat objects, adjusted by shape)
    # Here, approximate drag factor for usability (no velocity, static design)
    drag_factor = 0.5 * area_m2 * shape_factor  # Shape_factor: 1.0 (cone), 0.8 (tube), 1.2 (inflatable)
    return round(drag_factor, 2)

def scale_design(config, scale_factor):
    """Scale design parameters while maintaining usability"""
    if not 0.5 <= scale_factor <= 2.0:
        raise ValueError("Scale factor must be between 0.5 and 2.0")
    scaled = config.copy()
    dimensions = scaled.get("dimensions", {})
    for key in dimensions:
        dimensions[key] = dimensions[key] * scale_factor
    scaled["dimensions"] = dimensions
    for key in ['diameter', 'length', 'bridle_length', 'tip_diameter']:
        if key in scaled:
            scaled[key] = scaled[key] * scale_factor
    # Scale other params like diameter, length
    for key in ['diameter', 'length', 'bridle_length', 'tip_diameter']:
        if key in scaled:
            scaled[key] = scaled[key] * scale_factor
    # Scale area proportionally for drag
    if 'area' in scaled:
        scaled['area'] = scaled['area'] * (scale_factor ** 2)
    # Calculate drag for scaled design
    shape_factor = 1.0  # Default for cone; adjust for tube (0.8), inflatable (1.2)
    if scaled.get("shape", "").lower() == "tube":
        shape_factor = 0.8
    elif scaled.get("shape", "").lower() == "inflatable":
        shape_factor = 1.2
    scaled["drag"] = calculate_drag(scaled.get("area", 0.1), shape_factor)  # Default area 0.1m² if not set
    return scaled
