# -*- coding: utf-8 -*-
"""
Scaling module for kite laundry designs
Scales dimensions while maintaining usability (e.g., drag, inlet size)
"""
def scale_design(config, scale_factor):
    """Scale design parameters"""
    if not 0.5 <= scale_factor <= 2.0:
        raise ValueError("Scale factor must be between 0.5 and 2.0")
    scaled = config.copy()
    dimensions = scaled.get("dimensions", {})
    for key in dimensions:
        dimensions[key] = dimensions[key] * scale_factor
    scaled["dimensions"] = dimensions
    # Scale other params like diameter, length
    for key in ['diameter', 'length', 'bridle_length', 'tip_diameter']:
        if key in scaled:
            scaled[key] = scaled[key] * scale_factor
    # Maintain drag: scale area proportionally
    if 'area' in scaled:
        scaled['area'] = scaled['area'] * (scale_factor ** 2)
    return scaled
