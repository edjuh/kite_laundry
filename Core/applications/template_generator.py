# -*- coding: utf-8 -*-
import os

import yaml
from pattern_templates.tube_template import TubePatternTemplate


def generate_pattern_template(project_path, output_dir="templates"):
    """Generate pattern templates for a design

    Args:
        project_path (str): Path to the project directory
        output_dir (str): Output directory for templates

    Returns:
        dict: Information about generated templates
    """
    # Load the YAML configuration
    tube_yaml_path = os.path.join(project_path, "tube.yaml")

    if not os.path.exists(tube_yaml_path):
        raise FileNotFoundError(f"tube.yaml not found at {tube_yaml_path}")

    try:
        with open(tube_yaml_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading YAML from {tube_yaml_path}: {e}")

    if config is None:
        raise Exception(f"YAML file is empty or invalid: {tube_yaml_path}")

    # Ensure parameters exists
    if "parameters" not in config:
        config["parameters"] = {}

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate template
    template = TubePatternTemplate(config["parameters"])
    design_name = config.get("name", "Tube")
    output_filename = f"{design_name}_pattern.svg"
    output_path = os.path.join(output_dir, output_filename)
    template.generate_template(output_path)

    return {
        "template_path": output_path,
        "design_name": design_name,
        "dimensions": {
            "width": template.pattern_width,
            "height": template.pattern_height,
            "circumference": template.circumference,
        },
    }
