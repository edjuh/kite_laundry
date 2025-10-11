# -*- coding: utf-8 -*-
# kite_laundry/core/applications/generator.py
import json
import os
import sys
from pathlib import Path

import yaml
from jsonschema import validate

# Helper to locate the repo root
BASE_DIR = Path(__file__).resolve().parents[2]  # two levels up


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def validate_yaml(data: dict, schema_path: Path):
    with schema_path.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    validate(instance=data, schema=schema)


def run_pipeline():
    # Example: load first design
    design_yaml = BASE_DIR / "projects/drogue.yaml"
    design = load_yaml(design_yaml)

    # Validate against a schema
    schema_file = BASE_DIR / "schema.json"  # you need to create this
    validate_yaml(design, schema_file)

    # Rest of the pipeline ...
    # 1. Geometry
    from .geometry import compute_geometry

    geom = compute_geometry(design)

    # 2. Template
    from .template import build_svg

    svg_path = BASE_DIR / "output/drogue.svg"
    build_svg(geom, svg_path)

    # 3. Webpage
    from .webpage import render_page

    html_path = BASE_DIR / "output/drogue.html"
    render_page(design, svg_path, html_path)

    print(f"Finished: {html_path}")
