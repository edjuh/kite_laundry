# -*- coding: utf-8 -*-
import math


def validate_parameters(parameters):
    """Validate input parameters"""
    errors = []

    # Validate diameter
    diameter = parameters.get("diameter", 50)
    is_valid_diameter = isinstance(diameter, (int, float))
    if not is_valid_diameter or diameter < 10 or diameter > 2000:
        errors.append("Diameter must be between 10 and 2000mm")

    # Validate length
    length = parameters.get("length", 10000)
    is_valid_length = isinstance(length, (int, float))
    if not is_valid_length or length < 100 or length > 1000000:
        errors.append("Length must be between 100 and 100000mm")

    # Validate seam allowance
    seam_allowance = parameters.get("seam_allowance", 10)
    is_valid_seam = isinstance(seam_allowance, (int, float))
    if not is_valid_seam or seam_allowance < 5 or seam_allowance > 30:
        errors.append("Seam allowance must be between 5 and 30mm")

    # Validate num_gores
    num_gores = parameters.get("num_gores", 1)
    if not isinstance(num_gores, int) or num_gores < 1 or num_gores > 24:
        errors.append("Number of gores must be between 1 and 24")

    return errors


def generate_tube_pattern(parameters):
    """Generate a 2D pattern for a tube based on parameters

    Args:
        parameters (dict): Dictionary of tube parameters

    Returns:
        dict: Pattern information including dimensions and pieces
    """
    # Validate parameters first
    errors = validate_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")

    # Ensure parameters is a dictionary
    if parameters is None:
        parameters = {}

    diameter = parameters.get("diameter", 50)
    length = parameters.get("length", 10000)
    seam_allowance = parameters.get("seam_allowance", 10)
    num_gores = parameters.get("num_gores", 1)

    # Calculate dimensions
    circumference = math.pi * diameter

    if num_gores == 1:
        # Single piece - traditional tube
        pattern_width = circumference + (2 * seam_allowance)
        pattern_height = length + (2 * seam_allowance)

        # Create single main piece
        pieces = [
            {
                "name": "A",
                "description": "Main tube body (single piece)",
                "shape": "rectangle",
                "width_mm": round(pattern_width, 1),
                "height_mm": round(pattern_height, 1),
                "width_cm": round(pattern_width / 10, 1),
                "height_cm": round(pattern_height / 10, 1),
                "width_m": round(pattern_width / 1000, 2),
                "height_m": round(pattern_height / 1000, 2),
                "seam_allowance": seam_allowance,
            }
        ]

    else:
        # Multi-gore tube
        gore_width = circumference / num_gores
        gore_width_with_seam = gore_width + (2 * seam_allowance)
        gore_height_with_seam = length + (2 * seam_allowance)

        # Create gore pieces
        pieces = []
        for i in range(num_gores):
            letter = chr(65 + i)  # A, B, C, D...
            gore = {
                "name": letter,
                "description": f"Gore panel {i + 1} of {num_gores}",
                "shape": "rectangle",
                "width_mm": round(gore_width_with_seam, 1),
                "height_mm": round(gore_height_with_seam, 1),
                "width_cm": round(gore_width_with_seam / 10, 1),
                "height_cm": round(gore_height_with_seam / 10, 1),
                "seam_allowance": seam_allowance,
            }
            pieces.append(gore)

    # Calculate total material
    total_area_mm2 = circumference * length
    if num_gores > 1:
        # Add seam allowances for multi-gore
        total_area_mm2 += num_gores * seam_allowance * 2 * length

    material_area_cm2 = total_area_mm2 / 100
    material_area_m2 = material_area_cm2 / 10000

    # Add reinforcement pieces at attachment points
    attachment_points = parameters.get("attachment_points", [])
    reinforcement_start = len(pieces)

    for i, point in enumerate(attachment_points):
        position_str = point.get("position", 0)
        reinforcement_type = point.get("type", "carabiner")

        # Convert position string to float
        if isinstance(position_str, str) and position_str.endswith("%"):
            position = float(position_str.rstrip("%")) / 100.0
        else:
            position = float(position_str)

        # Calculate position on the pattern
        y_position = position * length

        # Create reinforcement piece
        letter = chr(65 + reinforcement_start + i)
        if reinforcement_type == "carabiner":
            percent_pos = position * 100
            description = f"Reinforcement at {percent_pos:.1f}% position"

            width_mm = round(diameter + (2 * seam_allowance), 1)
            height_mm = round(seam_allowance * 2, 1)
            width_cm = round(width_mm / 10, 1)
            height_cm = round(height_mm / 10, 1)

            reinforcement = {
                "name": letter,
                "description": description,
                "shape": "rectangle",
                "width_mm": width_mm,
                "height_mm": height_mm,
                "width_cm": width_cm,
                "height_cm": height_cm,
                "position": {"x": 0, "y": round(y_position, 1)},
                "position_percent": position * 100,
            }
            pieces.append(reinforcement)

    # Build return value
    result = {
        "pieces": pieces,
        "num_gores": num_gores,
        "total_material": {
            "width_mm": round(
                circumference / num_gores if num_gores > 1 else circumference, 1
            ),
            "height_mm": round(length, 1),
            "width_cm": round(
                (circumference / num_gores if num_gores > 1 else circumference) / 10, 1
            ),
            "height_cm": round(length / 10, 1),
            "width_m": round(
                (circumference / num_gores if num_gores > 1 else circumference) / 1000,
                2,
            ),
            "height_m": round(length / 1000, 2),
            "area_cm2": round(material_area_cm2, 1),
            "area_m2": round(material_area_m2, 4),
            "area_m": round(material_area_m2, 2),
            "circumference_mm": round(circumference, 1),
            "circumference_cm": round(circumference / 10, 1),
        },
    }
    return result


def generate_tube_instructions(parameters):
    """Generate sewing instructions for a tube

    Args:
        parameters (dict): Dictionary of tube parameters

    Returns:
        str: Markdown formatted instructions
    """
    if parameters is None:
        parameters = {}

    diameter = parameters.get("diameter", 50)
    length = parameters.get("length", 10000)
    material = parameters.get("material", "ripstop")
    color = parameters.get("color", "single")
    attachment_points = parameters.get("attachment_points", [])
    seam_allowance = parameters.get("seam_allowance", 10)
    num_gores = parameters.get("num_gores", 1)

    # Convert measurements to user-friendly units
    length_cm = length / 10
    diameter_cm = diameter / 10
    seam_allowance_cm = seam_allowance / 10
    circumference = math.pi * diameter
    circumference_cm = circumference / 10

    instructions = f"""# Tube Tail Instructions

## Design Specifications
- Type: {"Single-piece tube" if num_gores == 1 else f"Multi-gore tube ({num_gores} panels)"}
- Diameter: {diameter_cm:.1f} cm
- Length: {length_cm:.1f} cm
- Circumference: {circumference_cm:.1f} cm
- Seam allowance: {seam_allowance}mm ({seam_allowance_cm}cm)

## Materials Needed
- {material} fabric
- Thread matching fabric color
- {len(attachment_points) if attachment_points else 2} carabiners
"""

    if num_gores == 1:
        # Single piece instructions
        pattern_width_cm = circumference_cm + 2 * seam_allowance_cm
        instructions += f"""
## Cutting Instructions (Single Piece)
1. Cut a rectangle of {material} fabric:
   - Width: {pattern_width_cm:.1f} cm
   - Length: {length_cm + 2 * seam_allowance_cm:.1f} cm
2. Add {seam_allowance_cm}cm seam allowance (already included above)
"""
    else:
        # Multi-gore instructions
        gore_width = circumference / num_gores
        gore_width_cm = gore_width / 10
        instructions += f"""
## Cutting Instructions (Multi-Gore)
1. Cut {num_gores} identical rectangular panels:
   - Width per panel: {gore_width_cm:.1f} cm (+ {seam_allowance_cm}cm on each side)
   - Length per panel: {length_cm:.1f} cm (+ {seam_allowance_cm}cm top and bottom)
2. Total fabric: {gore_width_cm * num_gores:.1f} cm × {length_cm:.1f} cm

### Cutting Layout Tip
- Arrange panels side by side on fabric
- Pay attention to fabric grain direction
- All panels should have grain running lengthwise
"""

    if color == "multicolor" and num_gores > 1:
        instructions += """
## Color Pattern
1. Alternate colors between gores for spiral effect
2. Example for 8 gores: Color1, Color2, Color1, Color2...
"""

    instructions += f"""
## Sewing Instructions
"""

    if num_gores == 1:
        instructions += f"""
### Single-Piece Assembly
1. Fold fabric lengthwise, right sides together
2. Pin along long edge
3. Sew with {seam_allowance_cm}cm seam allowance
4. Leave a small opening (about 5cm) for turning if desired
5. Finish seam edges with zigzag or serger
6. Turn right side out if opening was left
7. Hem both ends with double-fold hem
"""
    else:
        instructions += f"""
### Multi-Gore Assembly
1. **Sew gores together**:
   - Place two gore panels right sides together
   - Pin along one long edge
   - Sew with {seam_allowance_cm}cm seam allowance
   - Press seam to one side or open
   - Repeat until all {num_gores} panels are joined in a strip

2. **Close the tube**:
   - Bring first and last gore together, right sides facing
   - Pin along edge carefully to avoid twisting
   - Sew final seam
   - Check tube hangs straight before finishing

3. **Finish ends**:
   - Fold top edge {seam_allowance_cm * 2}cm to inside
   - Press and pin
   - Topstitch hem
   - Repeat for bottom edge

4. **Press all seams** flat for professional finish
"""

    instructions += """
## Attachment Points
"""

    for i, point in enumerate(attachment_points):
        position_str = point.get("position", 0)
        if isinstance(position_str, str) and position_str.endswith("%"):
            position = float(position_str.rstrip("%")) / 100.0
        else:
            position = float(position_str)

        instructions += f"""
{i + 1}. At {position * 100}% of the length ({position * length_cm:.1f}cm from top):
    - Create reinforcement patch (double layer fabric, 3cm × 3cm)
    - Sew through all layers with box stitch pattern
    - Attach carabiner through reinforced section
"""

    instructions += """
## Finishing
1. Inspect all seams for gaps or loose stitching
2. Press the entire tube
3. Check that carabiners move freely
4. Test fly in light winds first

## Flying Tips
- The tube should hang vertically from the kite line
- For stronger winds, consider lighter fabric or reduce length
- Length can be adjusted by cutting and re-hemming
- Multiple tubes can be attached to same line for visual impact
"""

    if num_gores > 1:
        instructions += f"""
## Multi-Gore Benefits
- Easier to handle during sewing (narrower pieces)
- Allows color patterns and designs
- More professional appearance with clean seams
- Better fabric utilization (less waste)
"""

    return instructions


def perform_web_search(search_terms):
    """Simulate web search functionality"""
    simulated_results = {
        "kite tube tail": [
            {
                "title": "Tube Tail Design Guide",
                "url": "https://www.kiteplans.org/planos/tubetail/tubetail.html",
                "description": "Comprehensive guide to making tube tails",
            },
            {
                "title": "Kite Line Laundry",
                "url": "https://example.com/line-laundry",
                "description": "Various types of kite decorations",
            },
        ],
        "line laundry tube": [
            {
                "title": "Line Laundry Techniques",
                "url": "https://example.com/line-laundry-techniques",
                "description": "Advanced techniques for line laundry",
            },
            {
                "title": "Tube Tail Patterns",
                "url": "https://example.com/tube-patterns",
                "description": "Free patterns for tube tails",
            },
        ],
    }

    results = []
    for term in search_terms:
        if term in simulated_results:
            results.extend(simulated_results[term])

    return results
