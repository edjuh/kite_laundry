# -*- coding: utf-8 -*-
import math


def generate_banner_pattern(parameters):
    """Generate pattern for long horizontal banner"""
    length = parameters.get("length", 5000)
    height = parameters.get("height", 800)
    seam_allowance = parameters.get("seam_allowance", 10)
    num_sections = parameters.get("sections", 1)  # For multi-panel banners

    pieces = []
    total_area = 0

    for i in range(num_sections):
        section_length = length / num_sections
        pieces.append(
            {
                "name": f"Section_{i+1}",
                "description": f"Banner section {i+1} of {num_sections}",
                "shape": "rectangle",
                "width_mm": section_length + (2 * seam_allowance),
                "height_mm": height + (2 * seam_allowance),
                "seam_allowance": seam_allowance,
            }
        )
        total_area += section_length * height

    # Reinforcement strips
    reinforcement_length = length
    reinforcement_height = 50
    pieces.append(
        {
            "name": "Top_Reinforcement",
            "description": "Top edge reinforcement",
            "shape": "rectangle",
            "width_mm": reinforcement_length + (2 * seam_allowance),
            "height_mm": reinforcement_height + (2 * seam_allowance),
        }
    )

    total_area += reinforcement_length * reinforcement_height

    return {
        "pieces": pieces,
        "total_material": {
            "area_mm2": total_area,
            "area_m2": total_area / 1000000,
            "length_mm": length,
            "height_mm": height,
            "sections": num_sections,
        },
        "banner_specific": {
            "recommended_attachment_interval": min(2000, length / 5),
            "resistant_to_twisting": "high",
            "visibility": "excellent",
        },
    }


def generate_banner_instructions(parameters):
    length = parameters.get("length", 5000)
    height = parameters.get("height", 800)
    sections = parameters.get("sections", 1)

    return f"""# Banner Construction Guide

## Design Specifications
- Type: Horizontal Banner
- Length: {length/10:.1f} cm
- Height: {height/10:.1f} cm
- Sections: {sections}
- Total Area: {(length * height / 1000000):.2f} m²

## Construction
1. Cut {sections} banner sections
2. Sew sections together with reinforced seams
3. Add continuous top reinforcement strip
4. Install attachment points every {min(200, length/1000/5):.1f} meters

## Flying Characteristics
- Excellent visibility for messages/art
- Resists twisting due to horizontal orientation
- Moderate drag - consider kite strength
- Best in steady winds

Perfect for events and messages! 🎯
"""
