import os
import yaml
import svgwrite
import math
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from base64 import b64encode
from Core.pattern_generators.cone_generator import generate_cone_pattern, generate_cone_instructions

def load_resources(resources_dir="Core/configurations/resources"):
    resources = {}
    resources_path = Path(resources_dir)
    print(f"Loading resources from: {resources_path}")
    suppliers_path = resources_path / "suppliers.yaml"
    if suppliers_path.exists():
        print(f"Loading suppliers: {suppliers_path}")
        try:
            with open(suppliers_path, "r") as f:
                data = yaml.safe_load(f)
                resources.update({k: v for k, v in data.items() if k != "suppliers"})
                resources["suppliers"] = data.get("suppliers", {})
        except yaml.YAMLError as e:
            print(f"YAML error in {suppliers_path}: {e}")
    return resources

def generate_star_pattern(config):
    print(f"Generating star pattern for config: {config.get('name')}")
    width = config.get("dimensions", {}).get("width", 30) * 10
    segments = config.get("segments", 8)
    dwg = svgwrite.Drawing(size=(width, width))
    center = (width / 2, width / 2)
    radius_outer = width / 2 * 0.9
    radius_inner = width / 2 * 0.4
    points = []
    for i in range(segments * 2):
        angle = i * 360 / (segments * 2)
        radius = radius_outer if i % 2 == 0 else radius_inner
        x = center[0] + radius * math.cos(math.radians(angle))
        y = center[1] + radius * math.sin(math.radians(angle))
        points.append((x, y))
    colors = config.get("colors", ["red", "blue"])
    fill_color = colors[0] if colors else "none"
    dwg.add(dwg.polygon(points, fill=fill_color, stroke="black", stroke_width=2))
    return {"name": "Star Template (A4)", "svg_base64": b64encode(dwg.tostring().encode()).decode()}

def generate_article(design_yaml_path, output_dir="output", resources=None):
    print(f"Generating article for: {design_yaml_path}")
    if resources is None:
        resources = load_resources()
    
    design_path = Path(design_yaml_path)
    try:
        with open(design_path, "r") as f:
            config = yaml.safe_load(f)
        print(f"Config loaded: {config}")
    except yaml.YAMLError as e:
        print(f"YAML error in {design_path}: {e}")
        return None
    except FileNotFoundError as e:
        print(f"File not found {design_path}: {e}")
        return None
    
    enriched_materials = []
    for mat_key in config.get("materials", []):
        if mat_key in resources and mat_key != "suppliers":
            mat_data = resources[mat_key].copy()
            mat_data["suppliers"] = resources.get("suppliers", {}).get(mat_key, [])
            enriched_materials.append(mat_data)
            print(f"Enriched material: {mat_key}")
        else:
            print(f"Material {mat_key} not found in resources")
    
    patterns = []
    cone_pattern = None
    cone_instructions = ""
    if config.get("shape", "").lower() == "cone":
        print(f"Generating cone pattern for {config.get('name')}")
        try:
            cone_pattern = generate_cone_pattern(config)
            cone_instructions = generate_cone_instructions(config, cone_pattern)
            for piece in cone_pattern['pieces']:
                dwg = svgwrite.Drawing(size=(210, 297))  # A4 mm
                points = [
                    (piece['seam_allowance'], piece['seam_allowance']),
                    (piece['base_width_mm'] - piece['seam_allowance'], piece['seam_allowance']),
                    (piece['tip_width_mm'] + piece['seam_allowance'], piece['height_mm'] - piece['seam_allowance']),
                    (piece['seam_allowance'], piece['height_mm'] - piece['seam_allowance'])
                ] if piece['shape'] == "trapezoid" else [
                    (piece['seam_allowance'], piece['seam_allowance']),
                    (piece['base_width_mm'] - piece['seam_allowance'], piece['seam_allowance']),
                    (piece['base_width_mm'] / 2, piece['height_mm'] - piece['seam_allowance'])
                ]
                dwg.add(dwg.polygon(points, fill="lightblue", stroke="black", stroke_width=2))
                patterns.append({"name": f"Gore {piece['name']} (A4)", "svg_base64": b64encode(dwg.tostring().encode()).decode()})
                print(f"Generated SVG for gore {piece['name']}")
        except ValueError as e:
            print(f"Error generating cone pattern: {e}")
            return None
    else:
        patterns = [generate_star_pattern(config)]
        print(f"Generated star pattern for non-cone shape")
    
    env = Environment(loader=FileSystemLoader("Core/web/templates"))
    print(f"Jinja2 loader path: Core/web/templates")
    try:
        template = env.get_template("article_template.html")
        print(f"Loaded article_template.html")
    except Exception as e:
        print(f"Failed to load article_template.html: {e}")
        return None
    
    html_content = template.render(
        config=config,
        materials=enriched_materials,
        patterns=patterns,
        article_notes=config.get("article_notes", []),
        generated_date="2025-10-20",
        cone_pattern=cone_pattern,
        cone_instructions=cone_instructions
    )
    
    output_path = Path(output_dir) / f"{config['name'].replace(' ', '_')}.html"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"Article generated: {output_path}")
    return str(output_path)
