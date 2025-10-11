# -*- coding: utf-8 -*-
import math


def validate_bol_parameters(parameters):
    errors = []

    diameter = parameters.get("diameter", 1000)
    if not isinstance(diameter, (int, float)) or diameter < 300 or diameter > 10000:
        errors.append("Bol diameter must be between 300 and 10000mm")

    num_gores = parameters.get("num_gores", 8)
    if not isinstance(num_gores, int) or num_gores < 6 or num_gores > 32:
        errors.append("Number of gores must be between 6 and 32")

    seam_allowance = parameters.get("seam_allowance", 10)
    if (
        not isinstance(seam_allowance, (int, float))
        or seam_allowance < 5
        or seam_allowance > 30
    ):
        errors.append("Seam allowance must be between 5 and 30mm")

    return errors


def calculate_easybol_bridle_points(diameter, num_gores):
    """Calculate bridle points based on EasyBol design principles"""
    # Each gore gets bridle attachments on both edges at multiple heights
    bridle_points = []

    # Top reinforcement band (like EasyBol design)
    bridle_points.append(
        {
            "position": "top_band",
            "type": "reinforcement_band",
            "description": "Circular reinforcement at top edge",
            "diameter": diameter,
            "width": 50,  # 5cm band
        }
    )

    # Bottom reinforcement band
    bridle_points.append(
        {
            "position": "bottom_band",
            "type": "reinforcement_band",
            "description": "Circular reinforcement at bottom edge",
            "diameter": diameter,
            "width": 50,
        }
    )

    # Individual gore edge attachments (CRITICAL - EasyBol does this!)
    bol_height = diameter * 0.65
    attachment_heights = [
        bol_height * 0.1,  # 10% from top
        bol_height * 0.5,  # 50% middle
        bol_height * 0.9,  # 90% from top (10% from bottom)
    ]

    for gore_num in range(num_gores):
        for height_pos in attachment_heights:
            # Left edge of gore (when laid flat)
            bridle_points.append(
                {
                    "position": f"gore_{gore_num+1}_left_edge_{int(height_pos)}mm",
                    "type": "gore_edge_attachment",
                    "gore_number": gore_num + 1,
                    "edge": "left",
                    "height_from_top": height_pos,
                    "purpose": "bridle_connection",
                }
            )

            # Right edge of gore
            bridle_points.append(
                {
                    "position": f"gore_{gore_num+1}_right_edge_{int(height_pos)}mm",
                    "type": "gore_edge_attachment",
                    "gore_number": gore_num + 1,
                    "edge": "right",
                    "height_from_top": height_pos,
                    "purpose": "bridle_connection",
                }
            )

    return bridle_points


def calculate_bridle_network(num_gores, attachment_points):
    """Calculate how bridle lines connect between attachment points"""
    bridle_connections = []

    # Connect adjacent gore edges (forms the bridle network)
    for gore_num in range(num_gores):
        next_gore = (gore_num + 1) % num_gores

        # Connect left edge of current gore to right edge of previous gore
        # Connect right edge of current gore to left edge of next gore
        for height in ["10%", "50%", "90%"]:
            # Connection between gores
            bridle_connections.append(
                {
                    "from": f"gore_{gore_num+1}_left_edge_{height}",
                    "to": f"gore_{gore_num if gore_num > 0 else num_gores}_right_edge_{height}",
                    "type": "inter_gore_connection",
                    "length_adjustable": True,
                }
            )

            # Connection to central bridle point
            bridle_connections.append(
                {
                    "from": f"gore_{gore_num+1}_right_edge_{height}",
                    "to": "central_bridle_point",
                    "type": "main_bridle_line",
                    "length_adjustable": True,
                }
            )

    return bridle_connections


def generate_bol_pattern(parameters):
    errors = validate_bol_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")

    diameter = parameters.get("diameter", 1000)
    num_gores = parameters.get("num_gores", 8)
    seam_allowance = parameters.get("seam_allowance", 10)

    radius = diameter / 2
    circumference = math.pi * diameter
    bol_height = diameter * 0.65  # EasyBol ratio

    # EasyBol specific: circular reinforcement bands
    top_band_width = 50  # 5cm reinforcement at top
    bottom_band_width = 50  # 5cm reinforcement at bottom

    gore_base_width = circumference / num_gores
    gore_height = bol_height

    # Account for reinforcement bands in pattern
    gore_height_with_bands = gore_height + top_band_width + bottom_band_width

    gore_width_with_seam = gore_base_width + (2 * seam_allowance)
    gore_height_with_seam = gore_height_with_bands + (2 * seam_allowance)

    # Area calculation including reinforcement bands
    band_area = circumference * (top_band_width + bottom_band_width)
    gore_area = (gore_base_width * gore_height) * 0.85
    total_area_mm2 = (gore_area * num_gores) + band_area
    total_area_m2 = total_area_mm2 / 1000000

    pieces = []

    # Main gore pieces
    for i in range(num_gores):
        piece = {
            "name": chr(65 + i),
            "description": f"Bol gore panel {i+1} of {num_gores}",
            "shape": "curved_triangle_with_bands",
            "base_width_mm": round(gore_base_width, 1),
            "height_mm": round(gore_height, 1),
            "total_height_with_bands_mm": round(gore_height_with_bands, 1),
            "width_with_seam_mm": round(gore_width_with_seam, 1),
            "height_with_seam_mm": round(gore_height_with_seam, 1),
            "seam_allowance": seam_allowance,
            "top_band_width": top_band_width,
            "bottom_band_width": bottom_band_width,
            "bridle_attachments": [
                {"position": "left_edge_10%", "height": gore_height * 0.1},
                {"position": "left_edge_50%", "height": gore_height * 0.5},
                {"position": "left_edge_90%", "height": gore_height * 0.9},
                {"position": "right_edge_10%", "height": gore_height * 0.1},
                {"position": "right_edge_50%", "height": gore_height * 0.5},
                {"position": "right_edge_90%", "height": gore_height * 0.9},
            ],
        }
        pieces.append(piece)

    # Reinforcement bands (like EasyBol)
    pieces.append(
        {
            "name": "TB",
            "description": "Top reinforcement band",
            "shape": "circular_band",
            "diameter_mm": diameter,
            "width_mm": top_band_width,
            "purpose": "structural_reinforcement",
        }
    )

    pieces.append(
        {
            "name": "BB",
            "description": "Bottom reinforcement band",
            "shape": "circular_band",
            "diameter_mm": diameter,
            "width_mm": bottom_band_width,
            "purpose": "structural_reinforcement",
        }
    )

    # Bridle system (CRITICAL - EasyBol style)
    attachment_points = calculate_easybol_bridle_points(diameter, num_gores)
    bridle_network = calculate_bridle_network(num_gores, attachment_points)

    return {
        "pieces": pieces,
        "num_gores": num_gores,
        "attachment_points": attachment_points,
        "bridle_network": bridle_network,
        "total_material": {
            "area_mm2": round(total_area_mm2, 1),
            "area_cm2": round(total_area_mm2 / 100, 1),
            "area_m2": round(total_area_m2, 4),
            "diameter_mm": diameter,
            "height_mm": bol_height,
            "circumference_mm": circumference,
            "recommended_wind": "Beaufort 2-5",
            "reinforcement_bands": True,
        },
        "easybol_specific": {
            "design_reference": "Roberto Vañacek EasyBol",
            "rotation_ratio": 0.65,
            "bridle_attachments_per_gore": 6,  # 3 heights × 2 edges
            "total_bridle_attachments": num_gores * 6,
            "reinforcement_bands": True,
            "complex_bridle_network": True,
        },
    }


def generate_bol_instructions(parameters):
    diameter = parameters.get("diameter", 1000)
    num_gores = parameters.get("num_gores", 8)

    diameter_cm = diameter / 10
    bol_height = diameter * 0.65
    height_cm = bol_height / 10

    instructions = f"# EasyBol-Style Rotor Construction Guide\n\n"
    instructions += f"## Based on Roberto Vañacek's EasyBol Design\n\n"

    instructions += f"## CRITICAL DESIGN FEATURES (EasyBol Method):\n"
    instructions += (
        f"1. **Each gore edge gets bridle attachments** (6 per gore total)\n"
    )
    instructions += (
        f"2. **Top and bottom reinforcement bands** for structural integrity\n"
    )
    instructions += f"3. **Complex bridle network** connecting all attachment points\n"
    instructions += (
        f"4. **Precise 0.65 height:diameter ratio** for optimal rotation\n\n"
    )

    instructions += f"## Bridle System Complexity:\n"
    instructions += f"- **Attachments per gore**: 6 (3 heights × 2 edges)\n"
    instructions += f"- **Total attachments**: {num_gores * 6}\n"
    instructions += f"- **Bridle lines**: Complex network connecting all points\n"
    instructions += f"- **Adjustability**: All lines should be length-adjustable\n\n"

    instructions += f"## Construction Sequence (EasyBol Method):\n"
    instructions += (
        f"1. **Cut {num_gores} gore panels** with reinforcement band extensions\n"
    )
    instructions += f"2. **Sew top and bottom reinforcement bands**\n"
    instructions += (
        f"3. **Mark and reinforce bridle attachment points** on each gore edge\n"
    )
    instructions += f"4. **Sew gores together** to form cylinder\n"
    instructions += (
        f"5. **Install complex bridle network** connecting all attachment points\n"
    )
    instructions += f"6. **Test and adjust bridle lengths** for balanced rotation\n\n"

    instructions += f"## Reference: DrachenForum Discussion\n"
    instructions += f"For advanced techniques and community experience, visit:\n"
    instructions += f"https://www.drachenforum.net - German kite forum with extensive bol knowledge\n\n"

    instructions += f"**This is an advanced project requiring careful attention to the bridle system!** 🌀🪁"

    return instructions


def perform_bol_web_search():
    return [
        {
            "title": "EasyBol Plans by Roberto Vañacek",
            "url": "https://www.kiteplans.org/planos/easybol/EasyBol.pdf",
            "description": "Original EasyBol construction plans with detailed bridle system",
        },
        {
            "title": "DrachenForum - Bol Discussions",
            "url": "https://www.drachenforum.net",
            "description": "German kite forum with extensive bol building experience",
        },
        {
            "title": "Brasington Bol 2m",
            "url": "https://www.metropolis-drachen.de/en/Kites/Line-laundry/Bols/Brasington-Bol-2m.html",
            "description": "Professional bol with proper edge bridling",
        },
    ]
