import os
import yaml
import svgwrite
import math
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from base64 import b64encode

def load_resources(resources_dir="Core/configurations/resources"):
    resources = {}
    resources_path = Path(resources_dir)
    for yaml_file in resources_path.rglob("*.yaml"):
        if yaml_file.stem != "suppliers":
            try:
                with open(yaml_file, "r") as f:
                    resources[yaml_file.stem] = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"YAML error in {yaml_file}: {e}")
            except FileNotFoundError as e:
                print(f"File not found {yaml_file}: {e}")
    suppliers_path = resources_path / "suppliers.yaml"
    if suppliers_path.exists():
        try:
            with open(suppliers_path, "r") as f:
                resources["suppliers"] = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"YAML error in {suppliers_path}: {e}")
    return resources

def generate_star_pattern(config):
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
    return {"name": "Star Template", "svg_base64": b64encode(dwg.tostring().encode()).decode()}

def generate_article(design_yaml_path, output_dir="output", resources=None):
    if resources is None:
        resources = load_resources()
    
    design_path = Path(design_yaml_path)
    try:
        with open(design_path, "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"YAML error in {design_path}: {e}")
        return None
    except FileNotFoundError as e:
        print(f"File not found {design_path}: {e}")
        return None
    
    enriched_materials = []
    for mat_key in config.get("materials", []):
        if mat_key in resources:
            mat_data = resources[mat_key].copy()
            mat_data["suppliers"] = resources.get("suppliers", {}).get(mat_key, [])
            enriched_materials.append(mat_data)
    
    patterns = [generate_star_pattern(config)]
    env = Environment(loader=FileSystemLoader("Core/web/templates"))
    template = env.get_template("article_template.html")
    
    html_content = template.render(
        config=config,
        materials=enriched_materials,
        patterns=patterns,
        article_notes=config.get("article_notes", []),
        generated_date="2025-10-20"
    )
    
    output_path = Path(output_dir) / f"{config['name'].replace(' ', '_')}.html"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"Article generated: {output_path}")
    return str(output_path)
