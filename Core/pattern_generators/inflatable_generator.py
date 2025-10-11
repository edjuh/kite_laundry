# -*- coding: utf-8 -*-
# Core/pattern_generators/inflatable_generator.py
import math

import yaml
from svgwrite import Drawing


class InflatablePatternGenerator:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def generate_pattern(self):
        shape = self.config["shape"]

        if shape == "tube":
            return self._generate_tube_pattern()
        elif shape == "windsock":
            return self._generate_windsock_pattern()
        elif shape == "animal":
            return self._generate_animal_pattern()

    def _generate_tube_pattern(self):
        # Calculate dimensions from config
        circumference = math.pi * self.config["diameter"]
        length = self.config["length"]

        # Create SVG pattern
        dwg = Drawing(
            filename=f"{self.config['name']}_pattern.svg",
            size=(circumference + 2, length + 2),
        )

        # Draw rectangle (tube pattern)
        dwg.add(
            dwg.rect(
                insert=(1, 1),
                size=(circumference, length),
                fill="white",
                stroke="black",
            )
        )

        # Add seam allowance indicators
        # ...

        return dwg
