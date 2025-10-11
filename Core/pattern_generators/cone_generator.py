# -*- coding: utf-8 -*-
# kite_laundry/core/pattern_generators/cone_generator.py
# -*- coding: utf-8 -*-
"""
Cone Pattern Generator for Kite Laundry
Generates cutting patterns and instructions for cone-shaped line laundry
"""
import math


def validate_parameters(parameters):
    """Validate cone input parameters"""
    errors = []

    # Validate diameter (can be top or single diameter)
    diameter = parameters.get("diameter", 600)
    if not isinstance(diameter, (int, float)) or diameter < 50 or diameter > 2000:
        errors.append("Diameter must be between 50 and 2000mm")

    # Validate length
    length = parameters.get("length", 1000)
    if not isinstance(length, (int, float)) or length < 200 or length > 20000:
        errors.append("Length must be between 200 and 20000mm")

    # Validate number of gores
    num_gores = parameters.get("num_gores", 8)
    if not isinstance(num_gores, int) or num_gores < 4 or num_gores > 24:
        errors.append("Number of gores must be between 4 and 24")

    # Validate seam allowance
    seam_allowance = parameters.get("seam_allowance", 10)
    if (
        not isinstance(seam_allowance, (int, float))
        or seam_allowance < 5
        or seam_allowance > 30
    ):
        errors.append("Seam allowance must be between 5 and 30mm")

    return errors


def generate_cone_pattern(parameters):
    """Generate a 2D pattern for a cone (drogue) based on parameters

    Args:
        parameters (dict): Dictionary of cone parameters
            - diameter: diameter at wide end (mm)
            - length: length of cone (mm)
            - num_gores: number of gore panels (typically 6-12)
            - seam_allowance: seam allowance (mm)
            - tip_diameter: optional, diameter at narrow end (mm), default 0

    Returns:
        dict: Pattern information including dimensions and pieces
    """
    # Validate parameters first
    errors = validate_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")

    if parameters is None:
        parameters = {}

    # Get parameters
    diameter = parameters.get("diameter", 600)
    length = parameters.get("length", 1000)
    num_gores = parameters.get("num_gores", 8)
    seam_allowance = parameters.get("seam_allowance", 10)
    tip_diameter = parameters.get("tip_diameter", 0)  # 0 = pointed cone

    # Calculate gore dimensions
    base_circumference = math.pi * diameter
    tip_circumference = math.pi * tip_diameter if tip_diameter > 0 else 0

    # Each gore is a curved triangle (or trapezoid if has tip diameter)
    gore_base_width = base_circumference / num_gores
    gore_tip_width = tip_circumference / num_gores if tip_diameter > 0 else 0
    gore_height = length

    # Add seam allowances
    gore_base_with_seam = gore_base_width + (2 * seam_allowance)
    gore_tip_with_seam = (
        gore_tip_width + (2 * seam_allowance) if tip_diameter > 0 else seam_allowance
    )
    gore_height_with_seam = gore_height + (2 * seam_allowance)

    # Calculate material per gore
    # Approximation: average width × height
    avg_width = (gore_base_with_seam + gore_tip_with_seam) / 2
    gore_area_mm2 = avg_width * gore_height_with_seam

    # Total material
    total_area_mm2 = gore_area_mm2 * num_gores
    total_area_cm2 = total_area_mm2 / 100
    total_area_m2 = total_area_cm2 / 10000

    # Create pattern pieces
    pieces = []

    # Gore pieces
    for i in range(num_gores):
        gore_letter = chr(65 + i)  # A, B, C, D...
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

    # Build result
    result = {
        "pieces": pieces,
        "gore_count": num_gores,
        "total_material": {
            "area_mm2": round(total_area_mm2, 1),
            "area_cm2": round(total_area_cm2, 1),
            "area_m2": round(total_area_m2, 4),
            "base_circumference_mm": round(base_circumference, 1),
            "base_circumference_cm": round(base_circumference / 10, 1),
            "tip_circumference_mm": (
                round(tip_circumference, 1) if tip_diameter > 0 else 0
            ),
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


def generate_cone_instructions(parameters):
    """Generate sewing instructions for a cone

    Args:
        parameters (dict): Dictionary of cone parameters

    Returns:
        str: Markdown formatted instructions
    """
    if parameters is None:
        parameters = {}

    diameter = parameters.get("diameter", 600)
    length = parameters.get("length", 1000)
    num_gores = parameters.get("num_gores", 8)
    material = parameters.get("material", "ripstop nylon")
    seam_allowance = parameters.get("seam_allowance", 10)
    tip_diameter = parameters.get("tip_diameter", 0)

    # Convert to user-friendly units
    diameter_cm = diameter / 10
    length_cm = length / 10
    seam_allowance_cm = seam_allowance / 10
    tip_diameter_cm = tip_diameter / 10 if tip_diameter > 0 else 0

    # Calculate gore dimensions
    base_circumference = math.pi * diameter
    gore_base_width = base_circumference / num_gores
    gore_base_width_cm = gore_base_width / 10

    cone_type = "pointed cone" if tip_diameter == 0 else "truncated cone"

    instructions = f"""# Cone Drogue Instructions

## Design Specifications
- Type: {cone_type.capitalize()}
- Base diameter: {diameter_cm:.1f} cm
- Length: {length_cm:.1f} cm
- Number of gores: {num_gores}
- Seam allowance: {seam_allowance}mm ({seam_allowance_cm}cm)
"""

    if tip_diameter > 0:
        instructions += f"- Tip diameter: {tip_diameter_cm:.1f} cm\n"

    instructions += f"""
## Materials Needed
- {material}
- Polyester thread (matching color)
- Lightweight ring or swivel for attachment ({diameter_cm * 0.1:.1f} cm diameter)
- Optional: Reinforcement webbing for attachment point

## Gore Pattern Dimensions
Each gore is a {"trapezoid" if tip_diameter > 0 else "curved triangle"}:
- Base width: {gore_base_width_cm:.1f} cm (+ {seam_allowance_cm}cm seam allowance on each side)
- Height: {length_cm:.1f} cm (+ {seam_allowance_cm}cm seam allowance top and bottom)
"""

    if tip_diameter > 0:
        gore_tip_width = (math.pi * tip_diameter) / num_gores
        gore_tip_width_cm = gore_tip_width / 10
        instructions += f"- Tip width: {gore_tip_width_cm:.1f} cm (+ {seam_allowance_cm}cm seam allowance)\n"
    else:
        instructions += "- Tip: Pointed (comes to a point)\n"

    instructions += f"""
## Cutting Instructions

### Method 1: Paper Template
1. Draw the gore pattern on paper:
   - Mark base width: {gore_base_width_cm:.1f} cm
   - Mark height: {length_cm:.1f} cm
"""

    if tip_diameter > 0:
        instructions += f"   - Mark tip width: {gore_tip_width / 10:.1f} cm\n"
    else:
        instructions += "   - Draw to a point at the top\n"

    instructions += f"""   - Draw curved sides (the curve creates the cone shape)
   - Add {seam_allowance_cm}cm seam allowance all around

2. Cut {num_gores} pieces using this template

### Method 2: Direct Calculation
Each gore can be approximated as:
- A triangle with base {gore_base_width_cm:.1f}cm and height {length_cm:.1f}cm
- Sides should be slightly curved (bow outward about 5-10mm at midpoint)

## Assembly Instructions

### Step 1: Prepare Gore Panels
1. Cut all {num_gores} gore panels from fabric
2. Mark seam allowance lines on each piece
3. If using multiple colors, arrange in desired pattern

### Step 2: Sew Gores Together
1. Take two gore panels, place right sides together
2. Pin along one long edge, matching top and bottom points
3. Sew with {seam_allowance_cm}cm seam allowance
4. Repeat until all gores are connected in a circle
5. Press seams to one side or open

### Step 3: Reinforce Base Opening
1. Fold base edge {seam_allowance_cm * 2}cm to inside
2. Topstitch to create hem/casing
3. This reinforces the opening where the ring attaches

### Step 4: Finish Tip
"""

    if tip_diameter > 0:
        instructions += f"""1. Similar to base, fold tip edge {seam_allowance_cm * 2}cm to inside
2. Topstitch to create clean edge
3. The tip opening allows air to flow through
"""
    else:
        instructions += """1. All gore seams should meet at the tip point
2. Reinforce the tip with additional stitching in a circle
3. Trim excess fabric carefully
4. Consider adding a small reinforcement patch at the tip
"""

    instructions += f"""
### Step 5: Attach Mounting Ring
1. Insert lightweight ring into base opening
2. Fold fabric over ring
3. Sew securely using box stitch or zigzag
4. Ensure ring can rotate freely

## Quality Checks
- [ ] All {num_gores} seams are straight and secure
- [ ] Base and tip are properly hemmed
- [ ] Mounting ring is firmly attached
- [ ] Cone inflates properly when held in wind
- [ ] No puckering or uneven sections

## Flying Instructions
1. Attach to kite line using the mounting ring
2. The cone should hang with base facing up (wide end catches wind)
3. Suitable for winds: Beaufort 2-4 (light to moderate breeze)
4. The drogue will spin and provide visual interest
5. Can be used for:
   - Kite line decoration
   - Stabilization (reduces kite pulling)
   - Visual marker on the line

## Tips for Success
- Use lightweight ripstop (30-40 g/m²) for best performance
- Ensure all gores are identical for symmetrical inflation
- Test fly in light winds first
- The cone will naturally rotate when catching wind
- Fluorescent colors are most visible
- Can string multiple drogues on same line

## Troubleshooting
- **Not inflating**: Check that seams are tight, no air leaks
- **Spinning too fast**: Use heavier fabric or reduce base diameter
- **Tangling**: Ensure swivel ring rotates freely
- **Uneven shape**: Check that all gores are identical

## Variations
- **Windsock style**: Add streamers at the tip
- **Multiple colors**: Alternate gore colors for spiral effect
- **Graduated sizes**: Make several in different sizes for cascading effect
"""

    return instructions


def perform_web_search(search_terms):
    """Simulate web search for cone/drogue references"""
    simulated_results = {
        "cone drogue": [
            {
                "title": "Drogue Design Guide",
                "url": "https://www.kiteplans.org/planos/drogue2/drogue2.html",
                "description": "Traditional drogue construction",
            },
            {
                "title": "Manga Rotor Plans",
                "url": "https://www.kiteplans.org/planos/manga_rotor/manga_rotor.html",
                "description": "Rotating cone design",
            },
        ],
        "gore panel construction": [
            {
                "title": "Gore Panel Techniques",
                "url": "https://example.com/gore-panels",
                "description": "Advanced gore sewing methods",
            },
        ],
    }

    results = []
    for term in search_terms:
        if term in simulated_results:
            results.extend(simulated_results[term])

    return results
