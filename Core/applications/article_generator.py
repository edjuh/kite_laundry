# -*- coding: utf-8 -*-
import math

from Core.pattern_generators.bol_generator import (generate_bol_instructions,
                                                   generate_bol_pattern)
from Core.pattern_generators.cone_generator import (generate_cone_instructions,
                                                    generate_cone_pattern)
from Core.pattern_generators.tube_generator import (generate_tube_instructions,
                                                    generate_tube_pattern)


def generate_production_article(params):
    geometry_type = params["geometry"]["type"]
    parameters = params["parameters"]

    # Generate pattern based on geometry type
    if geometry_type == "pipe":
        pattern_data = generate_tube_pattern(parameters)
        instructions = generate_tube_instructions(parameters)
        complexity_description = (
            "Easy" if len(pattern_data.get("pieces", [])) <= 3 else "Moderate"
        )
    elif geometry_type == "cone":
        pattern_data = generate_cone_pattern(parameters)
        instructions = generate_cone_instructions(parameters)
        complexity_description = (
            "Moderate" if parameters.get("num_gores", 8) <= 8 else "Advanced"
        )
    elif geometry_type == "bol":
        pattern_data = generate_bol_pattern(parameters)
        instructions = generate_bol_instructions(parameters)
        complexity_description = "Advanced"  # Bol is more complex
    else:
        pattern_data = generate_fallback_pattern(parameters)
        instructions = generate_fallback_instructions(parameters)
        complexity_description = "Unknown"

    # Rest of the function remains the same...
    total_material = pattern_data.get("total_material", {})
    num_pieces = len(pattern_data.get("pieces", []))

    color_info = generate_color_information(params.get("colors", []))

    return {
        "name": params["name"],
        "complexity": params["complexity"],
        "complexity_description": complexity_description,
        "time": estimate_construction_time(geometry_type, num_pieces),
        "skill": estimate_skill_level(geometry_type, num_pieces),
        "geometry": geometry_type,
        "diameter": parameters.get("diameter", 0),
        "length": parameters.get(
            "length",
            parameters.get("diameter", 0) * 0.7 if geometry_type == "bol" else 0,
        ),
        "gores": parameters.get("num_gores", 1),
        "materials": params.get("materials", []),
        "description": params.get("description", ""),
        "author": params.get("author", "Unknown"),
        "version": params.get("version", "1.0"),
        "pattern": pattern_data,
        "instructions": instructions,
        "color_info": color_info,
        "pattern_details": {
            "num_pieces": num_pieces,
            "total_area_m2": total_material.get("area_m2", 0),
            "total_area_cm2": total_material.get("area_cm2", 0),
            "estimated_fabric_required": calculate_fabric_requirements(total_material),
            "seam_allowance": parameters.get("seam_allowance", 10),
        },
        "construction_tips": generate_construction_tips(geometry_type, parameters),
    }


# Update helper functions for Bol
def estimate_construction_time(geometry_type, num_pieces):
    base_time = 60
    if geometry_type == "pipe":
        if num_pieces == 1:
            return "30-45 minutes"
        else:
            return f"{30 + (num_pieces * 10)}-{45 + (num_pieces * 15)} minutes"
    elif geometry_type == "cone":
        return f"{45 + (num_pieces * 15)}-{60 + (num_pieces * 25)} minutes"
    elif geometry_type == "bol":
        return f"90-180 minutes"  # Bol takes longer due to complexity
    else:
        return "60-90 minutes"


def estimate_skill_level(geometry_type, num_pieces):
    if geometry_type == "pipe" and num_pieces == 1:
        return "Beginner"
    elif geometry_type == "pipe" and num_pieces > 1:
        return "Intermediate"
    elif geometry_type == "cone":
        return "Intermediate" if num_pieces <= 8 else "Advanced"
    elif geometry_type == "bol":
        return "Advanced"  # Bol requires advanced skills
    else:
        return "Intermediate"


def generate_construction_tips(geometry_type, parameters):
    tips = []

    if geometry_type == "bol":
        num_gores = parameters.get("num_gores", 8)
        tips.extend(
            [
                "Use walking foot for even fabric feed on curves",
                "Pin every 5-10cm when sewing curved seams",
                "Test rotation before finalizing bridle attachments",
                "Balance is crucial - ensure all gores are identical",
                "Use reinforced webbing for bridle attachment points",
                "Consider alternating colors for visual rotation effect",
            ]
        )
    elif geometry_type == "pipe":
        tips.extend([...])  # Existing pipe tips
    elif geometry_type == "cone":
        tips.extend([...])  # Existing cone tips

    # General tips
    tips.extend(
        [
            "Use polyester thread for UV resistance",
            "Set sewing machine tension slightly lower for synthetic fabrics",
            "Backstitch at beginning and end of all seams",
            "Test in light winds (Beaufort 2-3) first",
        ]
    )

    return tips


# Keep the other helper functions the same...
def generate_fallback_pattern(parameters):
    diameter = parameters.get("diameter", 600)
    length = parameters.get("length", 1000)
    return {
        "pieces": [
            {
                "name": "Main Panel",
                "description": "Primary fabric panel",
                "shape": "rectangle",
                "width_mm": diameter,
                "height_mm": length,
                "width_cm": round(diameter / 10, 1),
                "height_cm": round(length / 10, 1),
            }
        ],
        "total_material": {
            "area_m2": (diameter * length) / 1000000,
            "area_cm2": (diameter * length) / 100,
        },
    }


def generate_fallback_instructions(parameters):
    return """
    <h3>Basic Construction Instructions</h3>
    <ol>
        <li>Cut fabric according to pattern dimensions</li>
        <li>Sew seams with appropriate seam allowance</li>
        <li>Reinforce attachment points</li>
        <li>Test the design in light winds</li>
    </ol>
    """


def generate_color_information(colors):
    if not colors:
        return {
            "selected_colors": [],
            "pattern_notes": "Single color design",
            "visibility_tips": "Consider adding high-visibility accents",
        }

    color_info = {
        "selected_colors": colors,
        "pattern_notes": f"Multi-color design with {len(colors)} colors",
        "visibility_tips": "Good visibility with selected color combination",
    }

    if len(colors) >= 2:
        color_info[
            "pattern_suggestion"
        ] = f"Alternate colors every gore for spiral effect"
    if any(color in ["DPIC057", "DPIC058", "DPIC059", "DPIC060"] for color in colors):
        color_info[
            "visibility_tips"
        ] += ". Fluorescent colors enhance low-light visibility"

    return color_info


def calculate_fabric_requirements(total_material):
    area_m2 = total_material.get("area_m2", 0)
    required_m2 = area_m2 * 1.2
    return f"{required_m2:.2f} m² (including 20% waste allowance)"
