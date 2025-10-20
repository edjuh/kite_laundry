# -*- coding: utf-8 -*-
"""
Cone Pattern Generator for Kite Laundry
Generates a single cutting template for cone-shaped line laundry
"""
import math

def validate_parameters(parameters):
    errors = []
    diameter = parameters.get("diameter", 400)
    if not isinstance(diameter, (int, float)) or diameter < 50 or diameter > 1000:
        errors.append("Diameter must be between 50 and 1000mm")
    length = parameters.get("length", 1200)
    if not isinstance(length, (int, float)) or length < 200 or length > 20000:
        errors.append("Length must be between 200 and 20000mm")
    num_gores = parameters.get("num_gores", 6)
    if not isinstance(num_gores, int) or num_gores < 3 or num_gores > 12:
        errors.append("Number of gores must be between 3 and 12")
    return errors

def generate_cone_pattern(parameters):
    errors = validate_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")
    diameter = parameters.get("diameter", 400)
    length = parameters.get("length", 1200)
    num_gores = parameters.get("num_gores", 6)
    seam_allowance = parameters.get("seam_allowance", 10)
    tip_diameter = parameters.get("tip_diameter", 0)
    base_width = math.pi * diameter / num_gores
    tip_width = math.pi * tip_diameter / num_gores if tip_diameter else 0
    gore_height = length
    pieces = [
        {
            "name": "Gore Template",
            "shape": "trapezoid",
            "base_width_mm": base_width + (2 * seam_allowance),
            "tip_width_mm": tip_width + (2 * seam_allowance),
            "height_mm": gore_height + (2 * seam_allowance),
            "count": num_gores
        }
    ]
    total_area_mm2 = num_gores * ((base_width + tip_width) * gore_height / 2)
    total_area_m2 = total_area_mm2 / 1e6
    return {
        "pieces": pieces,
        "total_material": {"area_m2": round(total_area_m2, 4)},
    }

def generate_cone_instructions(parameters, pattern):
    diameter = parameters.get("diameter", 400)
    length = parameters.get("length", 1200)
    num_gores = parameters.get("num_gores", 6)
    seam_allowance_cm = parameters.get("seam_allowance", 10) / 10
    instructions = f"""
## {parameters.get('name', 'Cone Drogue')} Instructions

### Materials Required
- Ripstop nylon: approximately {pattern['total_material']['area_m2']:.2f} m² (add 20% for waste)
- Thread: high-strength polyester
- Seam tape (optional)
- Lightweight ring for attachment
- Sewing machine recommended

### Preparation
1. Print this sheet
2. Iron fabric
3. Plan colors

### Cutting
- Cut {num_gores} gores using template: base {pattern['pieces'][0]['base_width_mm']/10:.1f}cm, tip {pattern['pieces'][0]['tip_width_mm']/10:.1f}cm, height {pattern['pieces'][0]['height_mm']/10:.1f}cm

### Sewing
1. Sew {num_gores} gores together along sides with {seam_allowance_cm}cm seams
2. Hem edges
3. Attach ring at tip for line connection

### Quality Check
- Even seams
- Test spin in light wind

Happy flying!
"""
    return instructions
