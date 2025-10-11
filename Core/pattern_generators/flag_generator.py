# -*- coding: utf-8 -*-
import math


def generate_flag_pattern(parameters):
    """Generate pattern for rectangular flag"""
    width = parameters.get("width", 1000)
    height = parameters.get("height", 600)
    seam_allowance = parameters.get("seam_allowance", 10)

    # Reinforcement for flag attachment
    reinforcement_width = min(200, width * 0.2)
    reinforcement_height = 50

    pieces = [
        {
            "name": "Flag",
            "description": "Main flag body",
            "shape": "rectangle",
            "width_mm": width + (2 * seam_allowance),
            "height_mm": height + (2 * seam_allowance),
            "seam_allowance": seam_allowance,
        },
        {
            "name": "Reinforcement",
            "description": "Attachment reinforcement",
            "shape": "rectangle",
            "width_mm": reinforcement_width + (2 * seam_allowance),
            "height_mm": reinforcement_height + (2 * seam_allowance),
            "position": "top_center",
            "purpose": "attachment_strength",
        },
    ]

    total_area = (width * height) + (reinforcement_width * reinforcement_height)

    return {
        "pieces": pieces,
        "total_material": {
            "area_mm2": total_area,
            "area_m2": total_area / 1000000,
            "width_mm": width,
            "height_mm": height,
        },
        "flag_specific": {
            "aspect_ratio": width / height,
            "recommended_attachment": "reinforced_grommets",
            "flapping_frequency": "moderate",
        },
    }


def generate_flag_instructions(parameters):
    width = parameters.get("width", 1000)
    height = parameters.get("height", 600)

    return f"""# Flag Construction Guide

## Design Specifications
- Type: Rectangular Flag
- Width: {width/10:.1f} cm
- Height: {height/10:.1f} cm
- Aspect Ratio: {width/height:.2f}

## Construction
1. Cut rectangular fabric piece
2. Hem all edges with double fold
3. Reinforce top edge for attachment
4. Install grommets or reinforced attachment points

## Flying Characteristics
- Purely decorative
- Flaps in wind creating visual interest
- Low drag impact on main kite
- Suitable for light to moderate winds

Simple and effective line laundry! 🏁
"""
