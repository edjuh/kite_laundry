"""
geometry_registry.py
Central registry for all geometry generators used by the Kite Laundry Builder.
Each function defines how a project type (like drogue, spinner, chute) generates its panels.
"""


from .geometry import (
    generate_drogue_geometry,
    generate_spinner_geometry,
    generate_streamer_geometry,
    generate_chute_geometry,
    generate_parachute_gore_geometry,
    generate_bol_geometry,
)

GEOMETRY_FUNCTIONS = {
    "drogue": generate_drogue_geometry,
    "spinner": generate_spinner_geometry,
    "streamer": generate_streamer_geometry,
    "chute": generate_chute_geometry,
    "parachute_gore_geometry": generate_parachute_gore_geometry,
    "bol_geometry": generate_bol_geometry,
}
