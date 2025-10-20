import os
import yaml
import svgwrite
import math
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from base64 import b64encode
from Core.pattern_generators.cone_generator import generate_cone_pattern, generate_cone_instructions
from Core.pattern_generators.tube_generator import generate_tube_pattern, generate_tube_instructions
from Core.pattern_generators.inflatable_generator import generate_inflatable_pattern, generate_inflatable_instructions
from Core.applications.scaling import scale_design

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
    
    # Scale if 'scale' in YAML
    scale_factor = config.get("scale", 1.0)
    if scale_factor != 1.0:
        config = scale_design(config, scale_factor)
        print(f"Scaled config by {scale_factor}")

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
    instructions = ""
    if config.get("shape", "").lower() == "cone":
        print(f"Generating cone pattern for {config.get('name')}")
        try:
            pattern = generate_cone_pattern(config)
            instructions = generate_cone_instructions(config, pattern)
            dwg = svgwrite.Drawing(size=("210mm", "297mm"))  # A4
            base = pattern['pieces'][0]['base_width_mm']
            tip = pattern['pieces'][0]['tip_width_mm']
            height = pattern['pieces'][0]['height_mm']
            # Single curved gore
            dwg.add(dwg.path(d=f"M10,287 Q105,{287-height/2+10} 200,287", fill="none", stroke="black", stroke_width=2))
            patterns.append({"name": f"{pattern['pieces'][0]['name']} (A4)", "svg_base64": b64encode(dwg.tostring().encode()).decode()})
            print(f"Generated single curved SVG template for {pattern['pieces'][0]['name']}")
        except ValueError as e:
            print(f"Error generating cone pattern: {e}")
            return None
    elif config.get("shape", "").lower() == "tube":
        print(f"Generating tube pattern for {config.get('name')}")
        try:
            pattern = generate_tube_pattern(parameters)
            instructions = generate_tube_instructions(parameters, pattern)
            dwg = svgwrite.Drawing(size=("210mm", "297mm"))
            dwg.add(dwg.rect(insert=(10, 10), size=(190, 277), rx=10, ry=10, fill="none", stroke="black", stroke_width=2))
            patterns.append({"name": f"{pattern['pieces'][0]['name']} (A4)", "svg_base64": b64encode(dwg.tostring().encode()).decode()})
            if len(pattern['pieces']) > 1:
                ribbon_dwg = svgwrite.Drawing(size=("210mm", "297mm"))
                ribbon_dwg.add(dwg.rect(insert=(10, 10), size=(20, 100), fill="none", stroke="black", stroke_width=2))
                patterns.append({"name": f"{pattern['pieces'][1]['name']} (A4)", "svg_base64": b64encode(ribbon_dwg.tostring().encode()).decode()})
        except ValueError as e:
            print(f"Error generating tube pattern: {e}")
            return None
    elif config.get("shape", "").lower() == "inflatable":
        print(f"Generating inflatable pattern for {config.get('name')}")
        try:
            pattern = generate_inflatable_pattern(config)
            instructions = generate_inflatable_instructions(config, pattern)
            # Single template per piece type
            for piece_type in set(p['name'] for p in pattern['pieces']):
                piece = next(p for p in pattern['pieces'] if p['name'] == piece_type)
                dwg = svgwrite.Drawing(size=("210mm", "297mm"))
                if piece["shape"] == "curved_gore":
                    dwg.add(dwg.path(d=f"M10,287 Q105,148 200,287", fill="none", stroke="black", stroke_width=2))
                elif piece["shape"] == "triangle":
                    dwg.add(dwg.polygon(points=[(10,287), (200,287), (105,10)], fill="none", stroke="black", stroke_width=2))
                elif piece["shape"] == "circle":
                    dwg.add(dwg.circle(center=(105,148), r=50, fill="none", stroke="black", stroke_width=2))
                patterns.append({"name": f"{piece_type} (A4)", "svg_base64": b64encode(dwg.tostring().encode()).decode()})
        except ValueError as e:
            print(f"Error generating inflatable pattern: {e}")
            return None
    else:
        patterns = [generate_star_pattern(config)]
        print(f"Generated star pattern for non-cone/tube shape")
    
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
