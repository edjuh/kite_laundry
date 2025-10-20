# -*- coding: utf-8 -*-
"""
Tube Pattern Generator for Kite Laundry
Generates cutting patterns and instructions for tube-shaped line laundry (long pipe/tail)
"""
import math

def validate_parameters(parameters):
    """Validate tube input parameters"""
    errors = []
    diameter = parameters.get("diameter", 400)
    if not isinstance(diameter, (int, float)) or diameter < 50 or diameter > 1000:
        errors.append("Diameter must be between 50 and 1000mm")
    length = parameters.get("length", 1200)
    if not isinstance(length, (int, float)) or length < 200 or length > 20000:
        errors.append("Length must be between 200 and 20000mm")
    seam_allowance = parameters.get("seam_allowance", 10)
    if not isinstance(seam_allowance, (int, float)) or seam_allowance < 5 or seam_allowance > 30:
        errors.append("Seam allowance must be between 5 and 30mm")
    ribbon_count = parameters.get("ribbon_count", 4)
    if not isinstance(ribbon_count, int) or ribbon_count < 0 or ribbon_count > 10:
        errors.append("Ribbon count must be between 0 and 10")
    return errors

def generate_tube_pattern(parameters):
    """Generate a 2D pattern for a tube (long pipe/tail) based on parameters"""
    errors = validate_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")
    diameter = parameters.get("diameter", 400)
    length = parameters.get("length", 1200)
    seam_allowance = parameters.get("seam_allowance", 10)
    ribbon_count = parameters.get("ribbon_count", 4)
    ribbon_length = parameters.get("ribbon_length", 500)
    sleeve_width = math.pi * diameter + (2 * seam_allowance)
    sleeve_height = length + (2 * seam_allowance)
    ribbon_width = 20 + (2 * seam_allowance)
    ribbon_height = ribbon_length + (2 * seam_allowance)
    pieces = [
        {"name": "Tube Sleeve", "shape": "rectangle", "width_mm": sleeve_width, "height_mm": sleeve_height},
    ]
    if ribbon_count > 0:
        pieces.append({"name": "Ribbon Template", "shape": "rectangle", "width_mm": ribbon_width, "height_mm": ribbon_height, "count": ribbon_count})
    total_area_mm2 = (sleeve_width * sleeve_height) + (ribbon_count * ribbon_width * ribbon_height)
    total_area_m2 = total_area_mm2 / 1e6
    result = {
        "pieces": pieces,
        "total_material": {"area_m2": round(total_area_m2, 4)},
    }
    return result

def generate_tube_instructions(parameters, pattern):
    diameter = parameters.get("diameter", 400)
    length = parameters.get("length", 1200)
    seam_allowance_cm = parameters.get("seam_allowance", 10) / 10
    ribbon_count = parameters.get("ribbon_count", 4)
    instructions = f"""
## {parameters.get("name", "Tube Tail")} Instructions

### Materials Required
- Ripstop nylon: approximately {pattern['total_material']['area_m2']:.2f} m² (add 20% for waste)
- Thread: high-strength polyester, matching colors
- Seam tape (optional for edges)
- Lightweight ring for attachment
- Sewing machine recommended

### Preparation
1. Print this sheet
2. Iron fabric
3. Plan colors

### Cutting
Cut 1 tube sleeve from template: {pattern['pieces'][0]['width_mm']/10:.1f}cm x {pattern['pieces'][0]['height_mm']/10:.1f}cm
Cut {ribbon_count} ribbons from template: {pattern['pieces'][1]['width_mm']/10:.1f}cm x {pattern['pieces'][1]['height_mm']/10:.1f}cm (if applicable)

### Sewing
1. Sew sleeve into cylinder with {seam_allowance_cm}cm seam
2. Hem ends
3. Attach ribbons evenly around base for flair (if used)
4. Add ring at top for line connection

### Quality Check
- Even seams
- Test inflation

Happy flying!
"""
    return instructions
