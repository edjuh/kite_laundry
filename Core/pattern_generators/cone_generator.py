# -*- coding: utf-8 -*-
"""
Cone Pattern Generator for Kite Laundry
Generates cutting patterns and instructions for cone-shaped line laundry
"""
import math

def validate_parameters(parameters):
    """Validate cone input parameters"""
    errors = []
    diameter = parameters.get("diameter", 600)
    if not isinstance(diameter, (int, float)) or diameter < 50 or diameter > 2000:
        errors.append("Diameter must be between 50 and 2000mm")
    length = parameters.get("length", 1000)
    if not isinstance(length, (int, float)) or length < 200 or length > 20000:
        errors.append("Length must be between 200 and 20000mm")
    num_gores = parameters.get("num_gores", 8)
    if not isinstance(num_gores, int) or num_gores < 4 or num_gores > 24:
        errors.append("Number of gores must be between 4 and 24")
    seam_allowance = parameters.get("seam_allowance", 10)
    if not isinstance(seam_allowance, (int, float)) or seam_allowance < 5 or seam_allowance > 30:
        errors.append("Seam allowance must be between 5 and 30mm")
    return errors

def generate_cone_pattern(parameters):
    """Generate a 2D pattern for a cone (drogue) based on parameters"""
    errors = validate_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")
    if parameters is None:
        parameters = {}
    diameter = parameters.get("diameter", 600)
    length = parameters.get("length", 1000)
    num_gores = parameters.get("num_gores", 8)
    seam_allowance = parameters.get("seam_allowance", 10)
    tip_diameter = parameters.get("tip_diameter", 0)
    base_circumference = math.pi * diameter
    tip_circumference = math.pi * tip_diameter if tip_diameter > 0 else 0
    gore_base_width = base_circumference / num_gores
    gore_tip_width = tip_circumference / num_gores if tip_diameter > 0 else 0
    gore_height = length
    gore_base_with_seam = gore_base_width + (2 * seam_allowance)
    gore_tip_with_seam = gore_tip_width + (2 * seam_allowance) if tip_diameter > 0 else seam_allowance
    gore_height_with_seam = gore_height + (2 * seam_allowance)
    avg_width = (gore_base_with_seam + gore_tip_with_seam) / 2
    gore_area_mm2 = avg_width * gore_height_with_seam
    total_area_mm2 = gore_area_mm2 * num_gores
    total_area_cm2 = total_area_mm2 / 100
    total_area_m2 = total_area_cm2 / 10000
    pieces = []
    for i in range(num_gores):
        gore_letter = chr(65 + i)
        gore_piece = {
            "name": gore_letter,
            "description": f"Gore panel {i + 1} of {num_gores}",
            "shape": "trapezoid" if tip_diameter > 0 else "triangle",
            "base_width_mm": round(gore_base_with_seam, 1),
            "tip_width_mm": round(gore_tip_with_seam, 1),
            "height_mm": round(gore_height_with_seam, 1),
            "base_width_cm": round(gore_base_with_seam / 10, 1),
            "tip_width_cm": round(gore_tip_with_seam / 10, 1),
            "height_cm": round(gore_height_with_seam / 10, 1),
            "seam_allowance": seam_allowance,
            "angle_at_base": round(360 / num_gores, 1),
        }
        pieces.append(gore_piece)
    result = {
        "pieces": pieces,
        "gore_count": num_gores,
        "total_material": {
            "area_mm2": round(total_area_mm2, 1),
            "area_cm2": round(total_area_cm2, 1),
            "area_m2": round(total_area_m2, 4),
            "base_circumference_mm": round(base_circumference, 1),
            "base_circumference_cm": round(base_circumference / 10, 1),
            "tip_circumference_mm": round(tip_circumference, 1) if tip_diameter > 0 else 0,
            "cone_length_mm": length,
            "cone_length_cm": round(length / 10, 1),
        },
        "gore_dimensions": {
            "base_width_mm": round(gore_base_width, 1),
            "base_width_cm": round(gore_base_width / 10, 1),
            "tip_width_mm": round(gore_tip_width, 1) if tip_diameter > 0 else 0,
            "height_mm": gore_height,
            "height_cm": round(gore_height / 10, 1),
        },
    }
    return result

def generate_cone_instructions(parameters, pattern):
    """Generate sewing and assembly instructions for the cone"""
    diameter = parameters.get("diameter", 600)
    length = parameters.get("length", 1000)
    num_gores = parameters.get("num_gores", 8)
    seam_allowance = parameters.get("seam_allowance", 10)
    tip_diameter = parameters.get("tip_diameter", 0)
    seam_allowance_cm = seam_allowance / 10
    length_cm = length / 10
    base_circumference = math.pi * diameter
    gore_base_width = base_circumference / num_gores
    gore_base_width_cm = gore_base_width / 10
    gore_tip_width_cm = 0
    if tip_diameter > 0:
        tip_circumference = math.pi * tip_diameter
        gore_tip_width = tip_circumference / num_gores
        gore_tip_width_cm = gore_tip_width / 10
    instructions = f"""
## {parameters.get("name", "Cone Drogue")} Instructions

### Materials Required
- Ripstop nylon: approximately {pattern['total_material']['area_m2']:.2f} m² (add 20% for waste)
- Thread: high-strength polyester, matching colors
- Seam tape or binding (optional for edges)
- Lightweight ring or swivel for attachment (diameter 50-100mm)
- Webbing or cord for bridle (1m, breaking strength 50kg+)
- Sewing machine with walking foot recommended
- Pins, scissors, ruler, marking tool

### Preparation
1. Print this instruction sheet
2. Wash and iron fabric to pre-shrink
3. Plan color layout for gores (alternating colors for visual effect)
4. Prepare work space for large pieces
5. Test stitch on scrap fabric

### Cutting
Cut {num_gores} gore panels from ripstop.
Each gore is a curved triangle/trapezoid:
- Base: {gore_base_width_cm:.1f} cm (+ {seam_allowance_cm} cm seam on sides)
- Height: {length_cm:.1f} cm (+ {seam_allowance_cm} cm seam on top/bottom)
- Tip: {gore_tip_width_cm:.1f} cm if open tip (+ {seam_allowance_cm} cm seam)
- Sides: Curved to form cone when sewn

Note: For pointed tip, the sides converge to a point.

### Sewing Gores
1. Pin two gores right sides together along one curved side
2. Sew with {seam_allowance_cm} cm seam allowance
3. Press seam to one side
4. Topstitch if desired for strength
5. Repeat for all gores, forming a tube
6. Sew the last seam to close the cone

### Finishing Edges
1. Hem the base opening with double fold for strength
2. If open tip, hem the tip opening similarly
3. For pointed tip, reinforce the point with extra stitching

### Attachment
1. Attach ring to base with strong webbing
2. Sew webbing in a loop around the ring
3. Attach bridle cord to ring for kite line connection

### Quality Check
- Check for even gore sizes
- Ensure no pucks or twists
- Test inflation by blowing into base
- Check seams for strength

Happy flying!
"""
    return instructions
