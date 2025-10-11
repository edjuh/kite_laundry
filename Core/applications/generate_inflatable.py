# -*- coding: utf-8 -*-
# Core/applicationgenerate_inflatable.py
import sys

import yaml

from Core.aerodynamics.inflatable_drag import InflatableDragCalculator
from Core.pattern_generators.inflatable_generator import \
    InflatablePatternGenerator


def main(config_path):
    # Generate pattern
    generator = InflatablePatternGenerator(config_path)
    pattern = generator.generate_pattern()
    pattern.save()

    # Calculate aerodynamic properties
    with open(config_path) as f:
        config = yaml.safe_load(f)

    drag_calc = InflatableDragCalculator(config)
    print(f"Drag at 5 m/s: {drag_calc.calculate_drag(5):.2f} N")

    print(f"Pattern saved for {config['inflatable_laundry']['name']}")


if __name__ == "__main__":
    main(sys.argv[1])
