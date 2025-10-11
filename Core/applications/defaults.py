# -*- coding: utf-8 -*-
from typing import Any, Dict


# -*- coding: utf-8 -*-
class DefaultsProvider:
    """Provides default values for incomplete YAML definitions"""

    DEFAULTS = {
        "parameters": {
            "diameter": 100,
            "length": 300,
            "width": 200,
            "height": 400,
            "num_gores": 8,
            "opening_size": 0.3,
        },
        "colors": {"main": "#FFB6C1", "accent": "#FF69B4"},
        "aerodynamics": {
            "drag_coefficient": 1.0,
            "optimal_wind_range": "5-15 mph",
        },
        "assembly": [
            "Cut panels with 10 mm seam allowance",
            "Sew panels together",
            "Attach to line",
        ],
        "performance": {"primary": "decoration", "secondary": "none"},
    }

    @classmethod
    def get_defaults(cls, section: str) -> Dict[str, Any]:
        """Get defaults for a specific section"""
        return cls.DEFAULTS.get(section, {})

    @classmethod
    def apply_defaults(cls, project: Dict[str, Any]) -> Dict[str, Any]:
        """Apply defaults to incomplete project"""
        for section, defaults in cls.DEFAULTS.items():
            if section not in project:
                project[section] = defaults.copy()
            else:
                # Fill in missing values
                for key, value in defaults.items():
                    if key not in project[section]:
                        project[section][key] = value
        return project
