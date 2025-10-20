import os
import yaml
import svgwrite
import math
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from base64 import b64encode
from Core.pattern_generators.cone_generator import generate_cone_pattern, generate_cone_instructions
from Core.pattern_generators.tube_generator import generate_tube_pattern, generate_tube_instructions
from Core.applications.scaling import scale_design

# (Rest of the code from previous, with additions)
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
        print(f"Scaled config by {scale_factor}: {config}")

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
                dwg = svgwrite.Drawing(width=210, height=297)  # A4 mm
                # Curved gore for improved usability (based on cone math)
                base = piece['base_width_mm']
                tip = piece['tip_width_mm']
                height = piece['height_mm']
                radius = height / 2  # Approximate curve
                dwg.add(dwg.path(d=f"M10,287 Q105,148 200,287", fill="lightblue", stroke="black", stroke_width=2))
                patterns.append({"name": f"Gore {piece['name']} (A4)", "svg_base64": b64encode(dwg.tostring().encode()).decode()})
                print(f"Generated curved SVG for gore {piece['name']}")
        except ValueError as e:
            print(f"Error generating cone pattern: {e}")
            return None
    elif config.get("shape", "").lower() == "tube":
        print(f"Generating tube pattern for {config.get('name')}")
        try:
            tube_pattern = generate_tube_pattern(config)
            tube_instructions = generate_tube_instructions(config, tube_pattern)
            # SVG for sleeve (rectangle with curved ends)
            dwg = svgwrite.Drawing(width=210, height=297)
            dwg.add(dwg.rect(x=10, y=10, width=190, height=277, rx=10, ry=10, fill="lightblue", stroke="black", stroke_width=2))
            patterns.append({"name": "Tube Sleeve (A4 Scaled)", "svg_base64": b64encode(dwg.tostring().encode()).decode()})
            # Ribbons as small rectangles
            for i in range(tube_pattern['pieces'][1]['count']):
                dwg = svgwrite.Drawing(width=210, height=297)
                dwg.add(dwg.rect(x=10, y=10, width=20, height=100, fill="red", stroke="black", stroke_width=2))
                patterns.append({"name": f"Ribbon {i+1} (A4 Scaled)", "svg_base64": b64encode(dwg.tostring().encode()).decode()})
        except ValueError as e:
            print(f"Error generating tube pattern: {e}")
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
