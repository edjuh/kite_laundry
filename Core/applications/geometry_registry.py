# -*- coding: utf-8 -*-
"""
Geometry Registry - Comprehensive catalog of kite laundry types with aerodynamic properties
Based on kiteplans.org, DrachenForum, and kite community knowledge
"""

KITE_LAUNDRY_TYPES = {
    # === ACTIVE COMPONENTS (Generate Lift/Stability) ===
    "bol": {
        "type": "active",
        "category": "rotor",
        "description": "Rotating cylinder that generates lift through autorotation",
        "aerodynamics": {
            "lift_factor": 0.3,
            "drag_factor": 0.8,
            "stability": "high",
            "rotation": "auto",
            "wind_range": "Beaufort 2-5",
        },
        "complexity": "advanced",
        "safety_notes": "High rotational energy, dangerous at large sizes",
        "typical_sizes": "0.5m - 10m diameter",
        "reference": "EasyBol, Roberto Vañacek",
    },
    "drogue": {
        "type": "active",
        "category": "drag_device",
        "description": "Conical drogue that provides stability and visual interest",
        "aerodynamics": {
            "lift_factor": 0.1,
            "drag_factor": 0.6,
            "stability": "medium",
            "rotation": "optional",
            "wind_range": "Beaufort 2-4",
        },
        "complexity": "intermediate",
        "safety_notes": "Moderate drag, good for line stabilization",
        "typical_sizes": "0.3m - 2m length",
    },
    # === PASSIVE COMPONENTS (Decorative/Drag) ===
    "flag": {
        "type": "passive",
        "category": "banner",
        "description": "Rectangular flag that flaps in wind, purely decorative",
        "aerodynamics": {
            "lift_factor": 0.0,
            "drag_factor": 0.4,
            "stability": "low",
            "rotation": "none",
            "wind_range": "Beaufort 1-4",
        },
        "complexity": "beginner",
        "safety_notes": "Low drag, safe for beginners",
        "typical_sizes": "0.5m - 3m length",
    },
    "banner": {
        "type": "passive",
        "category": "banner",
        "description": "Long horizontal banner with text or patterns",
        "aerodynamics": {
            "lift_factor": 0.0,
            "drag_factor": 0.5,
            "stability": "medium",
            "rotation": "none",
            "wind_range": "Beaufort 1-3",
        },
        "complexity": "beginner",
        "safety_notes": "Moderate drag, watch for twisting",
        "typical_sizes": "1m - 10m length",
    },
    "tube": {
        "type": "passive",
        "category": "streamer",
        "description": "Cylindrical tube that streams behind kite",
        "aerodynamics": {
            "lift_factor": 0.0,
            "drag_factor": 0.3,
            "stability": "high",
            "rotation": "optional",
            "wind_range": "Beaufort 1-5",
        },
        "complexity": "beginner",
        "safety_notes": "Low drag, very stable",
        "typical_sizes": "1m - 20m length",
    },
    "windsock": {
        "type": "semi-active",
        "category": "hybrid",
        "description": "Tapered fabric tube that inflates and streams",
        "aerodynamics": {
            "lift_factor": 0.05,
            "drag_factor": 0.7,
            "stability": "medium",
            "rotation": "none",
            "wind_range": "Beaufort 1-4",
        },
        "complexity": "intermediate",
        "safety_notes": "Moderate drag, can develop oscillations",
        "typical_sizes": "0.5m - 3m length",
    },
    "spinner": {
        "type": "semi-active",
        "category": "rotating",
        "description": "Flat panels that spin around central axis",
        "aerodynamics": {
            "lift_factor": 0.1,
            "drag_factor": 0.6,
            "stability": "medium",
            "rotation": "forced",
            "wind_range": "Beaufort 2-4",
        },
        "complexity": "intermediate",
        "safety_notes": "Rotational energy, moderate drag",
        "typical_sizes": "0.3m - 1.5m diameter",
    },
    "parachute": {
        "type": "active",
        "category": "drag_device",
        "description": "Small parachute drogue for high drag",
        "aerodynamics": {
            "lift_factor": 0.2,
            "drag_factor": 0.9,
            "stability": "high",
            "rotation": "none",
            "wind_range": "Beaufort 1-3",
        },
        "complexity": "intermediate",
        "safety_notes": "High drag, can significantly slow kite",
        "typical_sizes": "0.5m - 2m diameter",
    },
}


def get_geometry_info(geometry_type):
    """Get comprehensive information about a geometry type"""
    return KITE_LAUNDRY_TYPES.get(
        geometry_type,
        {
            "type": "unknown",
            "category": "unknown",
            "description": "Unknown geometry type",
            "aerodynamics": {"lift_factor": 0.0, "drag_factor": 0.0},
            "complexity": "unknown",
            "safety_notes": "Exercise caution",
            "typical_sizes": "Varies",
        },
    )


def calculate_drag_force(drag_factor, area_m2, wind_speed_mps):
    """Calculate drag force in Newtons"""
    # Fd = 0.5 * ρ * v² * Cd * A
    air_density = 1.225  # kg/m³ at sea level
    return 0.5 * air_density * (wind_speed_mps**2) * drag_factor * area_m2


def calculate_safety_level(geometry_type, size, wind_speed):
    """Calculate safety level based on geometry and conditions"""
    info = get_geometry_info(geometry_type)
    area = size * 0.1  # Approximate area estimation

    drag_force = calculate_drag_force(
        info["aerodynamics"]["drag_factor"], area, wind_speed
    )

    if drag_force > 100:  # 100N ≈ 10kg force
        return "DANGEROUS", drag_force
    elif drag_force > 50:
        return "CAUTION", drag_force
    elif drag_force > 20:
        return "MODERATE", drag_force
    else:
        return "SAFE", drag_force


def recommend_geometry(use_case, wind_conditions, skill_level):
    """Recommend geometry types based on use case"""
    recommendations = []

    for geo_type, info in KITE_LAUNDRY_TYPES.items():
        # Filter by skill level
        skill_match = (
            (skill_level == "beginner" and info["complexity"] == "beginner")
            or (
                skill_level == "intermediate"
                and info["complexity"] in ["beginner", "intermediate"]
            )
            or (skill_level == "advanced")
        )

        # Filter by wind conditions
        wind_range = info["aerodynamics"]["wind_range"]
        wind_ok = (
            "Beaufort 1-2" in wind_range or f"Beaufort {wind_conditions}" in wind_range
        )

        if skill_match and wind_ok:
            recommendations.append(
                {
                    "geometry": geo_type,
                    "reason": f"{info['description']}. Suitable for {wind_range} winds.",
                    "complexity": info["complexity"],
                }
            )

    return recommendations
