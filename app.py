# -*- coding: utf-8 -*-
import math
import os

from flask import Flask, redirect, render_template, request, url_for

from Core.applications.article_generator import generate_production_article
from Core.pattern_generators.cone_generator import (generate_cone_instructions,
                                                    generate_cone_pattern)
from Core.pattern_generators.tube_generator import (generate_tube_instructions,
                                                    generate_tube_pattern)

app = Flask(
    __name__,
    template_folder="Core/web/templates",
    static_url_path="/Core/web/static",
    static_folder="Core/web/static",
)

try:
    from Core.configurations.resources.colors import (get_color_hex,
                                                      get_color_name,
                                                      load_color_palette)

    COLOR_SUPPORT = True
except ImportError:
    print("Warning: Colors module not available. Using fallback color functions.")
    COLOR_SUPPORT = False

    def load_color_palette():
        return {}

    def get_color_name(color_code):
        return color_code

    def get_color_hex(color_code):
        return "#CCCCCC"


# Register Jinja2 filters
@app.template_filter("color_hex")
def color_hex_filter(color_code):
    """Jinja2 filter to get hex code from DPIC color code"""
    return get_color_hex(color_code)


@app.template_filter("color_name")
def color_name_filter(color_code):
    """Jinja2 filter to get name from DPIC color code"""
    return get_color_name(color_code)


def parse_attachment_points(attachment_spacing):
    spacing_map = {
        "2": [
            {"position": "25%", "type": "carabiner"},
            {"position": "75%", "type": "carabiner"},
        ],
        "3": [
            {"position": "20%", "type": "carabiner"},
            {"position": "50%", "type": "carabiner"},
            {"position": "80%", "type": "carabiner"},
        ],
        "4": [
            {"position": "15%", "type": "carabiner"},
            {"position": "35%", "type": "carabiner"},
            {"position": "65%", "type": "carabiner"},
            {"position": "85%", "type": "carabiner"},
        ],
    }
    return spacing_map.get(attachment_spacing, spacing_map["2"])


def calculate_material_requirements(parameters, geometry_type):
    diameter = parameters.get("diameter", 600)
    length = parameters.get("length", 1000)
    num_gores = parameters.get("num_gores", 1)
    seam_allowance = parameters.get("seam_allowance", 10)

    if geometry_type == "pipe":
        if num_gores == 1:
            circumference = math.pi * diameter
            area_mm2 = circumference * length
        else:
            gore_width = (math.pi * diameter) / num_gores
            area_mm2 = gore_width * length * num_gores

    elif geometry_type == "cone":
        base_circumference = math.pi * diameter
        tip_diameter = parameters.get("tip_diameter", 0)
        tip_circumference = math.pi * tip_diameter if tip_diameter > 0 else 0
        avg_circumference = (base_circumference + tip_circumference) / 2
        area_mm2 = avg_circumference * length

    area_m2 = area_mm2 / 1000000
    return area_m2


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        geometry_type = request.form.get("geometry_type")
        design_name = request.form.get("name", "Custom Design")
        colors = request.form.getlist("colors")
        material = request.form.get("material", "ripstop nylon")
        weight = request.form.get("weight", "30")

        parameters = {
            "diameter": int(request.form.get("diameter", 600)),
            "length": int(request.form.get("length", 1000)),
            "num_gores": int(request.form.get("num_gores", 1)),
            "seam_allowance": 10,
            "material": material,
            "weight": f"{weight}g/m²",
            "colors": colors,
        }

        if geometry_type == "cone":
            parameters["tip_diameter"] = int(request.form.get("tip_diameter", 0))
        elif geometry_type == "pipe":
            attachment_spacing = request.form.get("attachment_spacing", "2")
            parameters["attachment_points"] = parse_attachment_points(
                attachment_spacing
            )

        material_area = calculate_material_requirements(parameters, geometry_type)

        design_params = {
            "name": design_name,
            "complexity": 2 if geometry_type == "pipe" else 3,
            "geometry": {"type": geometry_type},
            "parameters": parameters,
            "materials": [
                {"item": material, "qty": f"≈ {material_area:.2f} m²"},
                {"item": "Polyester thread", "qty": "1 spool"},
                {
                    "item": "Carabiners",
                    "qty": f"{len(parameters.get('attachment_points', [])) if geometry_type == 'pipe' else 1} pcs",
                },
            ],
            "colors": colors,
            "description": f"Custom {geometry_type} design '{design_name}' created via form",
            "author": "Kite Laundry Builder",
            "version": "1.0",
        }

        article_data = generate_production_article(design_params)

        if geometry_type == "pipe":
            article_data["instructions"] = generate_tube_instructions(parameters)
            pattern_data = generate_tube_pattern(parameters)
        elif geometry_type == "cone":
            article_data["instructions"] = generate_cone_instructions(parameters)
            pattern_data = generate_cone_pattern(parameters)
        else:
            pattern_data = {"pieces": [], "total_material": {}}

        article_data["pattern"] = pattern_data
        article_data["pattern_details"] = {
            "num_pieces": len(pattern_data.get("pieces", [])),
            "total_area": pattern_data.get("total_material", {}).get("area_m2", 0),
        }

        return render_template("result.html", **article_data)

    return render_template("generate.html")


@app.route("/designs")
def designs():
    designs = []
    projects_dir = "projects"

    for root, dirs, files in os.walk(projects_dir):
        for file in files:
            if file.endswith(".yaml"):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, projects_dir)
                designs.append(
                    {
                        "filename": relative_path,
                        "name": os.path.splitext(relative_path)[0]
                        .replace("/", " ")
                        .title(),
                        "complexity": 2,
                        "category": relative_path.split("/")[0]
                        if "/" in relative_path
                        else "General",
                        "subcategory": relative_path.split("/")[1]
                        if len(relative_path.split("/")) > 1
                        else "N/A",
                    }
                )

    return render_template("designs.html", designs=designs, total=len(designs))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
