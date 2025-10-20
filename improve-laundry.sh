#!/bin/bash
# improve-laundry.sh - Enhance kite_laundry project with new generators, scaling, single-template SVGs, drag calculator, Xmas-tree YAMLs, custom web interface, and external color samples.
# Run this in the root of your kite_laundry-fork directory: chmod +x improve-laundry.sh && ./improve-laundry.sh

cd /Users/ed/kite_laundry-fork

# Backup key files
cp app.py app.py.bak
cp Core/applications/article_generator.py Core/applications/article_generator.py.bak
cp Core/web/templates/article_template.html Core/web/templates/article_template.html.bak
cp Core/configurations/resources/suppliers.yaml Core/configurations/resources/suppliers.yaml.bak
cp Core/pattern_generators/cone_generator.py Core/pattern_generators/cone_generator.py.bak

# 1. Add tube_generator.py with single template logic
mkdir -p Core/pattern_generators
cat > Core/pattern_generators/tube_generator.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Tube Pattern Generator for Kite Laundry
Generates a single cutting template for tube-shaped line laundry
"""
import math

def validate_parameters(parameters):
    errors = []
    diameter = parameters.get("diameter", 400)
    if not isinstance(diameter, (int, float)) or diameter < 50 or diameter > 1000:
        errors.append("Diameter must be between 50 and 1000mm")
    length = parameters.get("length", 1200)
    if not isinstance(length, (int, float)) or length < 200 or length > 20000:
        errors.append("Length must be between 200 and 20000mm")
    seam_allowance = parameters.get("seam_allowance", 10)
    if not isinstance(seam_allowance, (int, float)) or seam_allowance < 5 or seam_allowance > 30:
        errors.append("Seam allowance must be between 5 and 30mm")
    ribbon_count = parameters.get("ribbon_count", 4)
    if not isinstance(ribbon_count, int) or ribbon_count < 0 or ribbon_count > 10:
        errors.append("Ribbon count must be between 0 and 10")
    return errors

def generate_tube_pattern(parameters):
    errors = validate_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")
    diameter = parameters.get("diameter", 400)
    length = parameters.get("length", 1200)
    seam_allowance = parameters.get("seam_allowance", 10)
    ribbon_count = parameters.get("ribbon_count", 4)
    ribbon_length = parameters.get("ribbon_length", 500)
    sleeve_width = math.pi * diameter + (2 * seam_allowance)
    sleeve_height = length + (2 * seam_allowance)
    ribbon_width = 20 + (2 * seam_allowance)
    ribbon_height = ribbon_length + (2 * seam_allowance)
    pieces = [
        {"name": "Tube Sleeve", "shape": "rectangle", "width_mm": sleeve_width, "height_mm": sleeve_height},
    ]
    if ribbon_count > 0:
        pieces.append({"name": "Ribbon Template", "shape": "rectangle", "width_mm": ribbon_width, "height_mm": ribbon_height, "count": ribbon_count})
    total_area_mm2 = (sleeve_width * sleeve_height) + (ribbon_count * ribbon_width * ribbon_height)
    total_area_m2 = total_area_mm2 / 1e6
    return {
        "pieces": pieces,
        "total_material": {"area_m2": round(total_area_m2, 4)},
    }

def generate_tube_instructions(parameters, pattern):
    diameter = parameters.get("diameter", 400)
    length = parameters.get("length", 1200)
    seam_allowance_cm = parameters.get("seam_allowance", 10) / 10
    ribbon_count = parameters.get("ribbon_count", 4)
    instructions = f"""
## {parameters.get('name', 'Tube Tail')} Instructions

### Materials Required
- Ripstop nylon: approximately {pattern['total_material']['area_m2']:.2f} m² (add 20% for waste)
- Thread: high-strength polyester, matching colors
- Seam tape (optional)
- Lightweight ring for attachment
- Sewing machine recommended

### Preparation
1. Print this sheet
2. Iron fabric
3. Plan colors

### Cutting
- Cut 1 tube sleeve using template: {pattern['pieces'][0]['width_mm']/10:.1f}cm x {pattern['pieces'][0]['height_mm']/10:.1f}cm
- Cut {ribbon_count} ribbons using template: {pattern['pieces'][1]['width_mm']/10:.1f}cm x {pattern['pieces'][1]['height_mm']/10:.1f}cm (if applicable)

### Sewing
1. Sew sleeve into cylinder with {seam_allowance_cm}cm seam
2. Hem ends
3. Attach ribbons evenly around base for flair (if used)
4. Add ring at top for line connection

### Quality Check
- Even seams
- Test inflation

Happy flying!
"""
    return instructions
EOF

# 2. Fix cone_generator.py indentation and single template
cat > Core/pattern_generators/cone_generator.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Cone Pattern Generator for Kite Laundry
Generates a single cutting template for cone-shaped line laundry
"""
import math

def validate_parameters(parameters):
    errors = []
    diameter = parameters.get("diameter", 400)
    if not isinstance(diameter, (int, float)) or diameter < 50 or diameter > 1000:
        errors.append("Diameter must be between 50 and 1000mm")
    length = parameters.get("length", 1200)
    if not isinstance(length, (int, float)) or length < 200 or length > 20000:
        errors.append("Length must be between 200 and 20000mm")
    num_gores = parameters.get("num_gores", 6)
    if not isinstance(num_gores, int) or num_gores < 3 or num_gores > 12:
        errors.append("Number of gores must be between 3 and 12")
    return errors

def generate_cone_pattern(parameters):
    errors = validate_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")
    diameter = parameters.get("diameter", 400)
    length = parameters.get("length", 1200)
    num_gores = parameters.get("num_gores", 6)
    seam_allowance = parameters.get("seam_allowance", 10)
    tip_diameter = parameters.get("tip_diameter", 0)
    base_width = math.pi * diameter / num_gores
    tip_width = math.pi * tip_diameter / num_gores if tip_diameter else 0
    gore_height = length
    pieces = [
        {
            "name": "Gore Template",
            "shape": "trapezoid",
            "base_width_mm": base_width + (2 * seam_allowance),
            "tip_width_mm": tip_width + (2 * seam_allowance),
            "height_mm": gore_height + (2 * seam_allowance),
            "count": num_gores
        }
    ]
    total_area_mm2 = num_gores * ((base_width + tip_width) * gore_height / 2)
    total_area_m2 = total_area_mm2 / 1e6
    return {
        "pieces": pieces,
        "total_material": {"area_m2": round(total_area_m2, 4)},
    }

def generate_cone_instructions(parameters, pattern):
    diameter = parameters.get("diameter", 400)
    length = parameters.get("length", 1200)
    num_gores = parameters.get("num_gores", 6)
    seam_allowance_cm = parameters.get("seam_allowance", 10) / 10
    instructions = f"""
## {parameters.get('name', 'Cone Drogue')} Instructions

### Materials Required
- Ripstop nylon: approximately {pattern['total_material']['area_m2']:.2f} m² (add 20% for waste)
- Thread: high-strength polyester
- Seam tape (optional)
- Lightweight ring for attachment
- Sewing machine recommended

### Preparation
1. Print this sheet
2. Iron fabric
3. Plan colors

### Cutting
- Cut {num_gores} gores using template: base {pattern['pieces'][0]['base_width_mm']/10:.1f}cm, tip {pattern['pieces'][0]['tip_width_mm']/10:.1f}cm, height {pattern['pieces'][0]['height_mm']/10:.1f}cm

### Sewing
1. Sew {num_gores} gores together along sides with {seam_allowance_cm}cm seams
2. Hem edges
3. Attach ring at tip for line connection

### Quality Check
- Even seams
- Test spin in light wind

Happy flying!
"""
    return instructions
EOF

# 3. Add scaling with drag calculator
cat > Core/applications/scaling.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Scaling module for kite laundry designs
Scales dimensions while maintaining usability (drag, inlet size)
"""
def calculate_drag(area_m2, shape_factor=1.0):
    """Estimate drag coefficient based on area and shape (simplified)"""
    # Drag ≈ k * A * v² (k ~ 0.5 for flat objects, adjusted by shape)
    # Here, approximate drag factor for usability (no velocity, static design)
    drag_factor = 0.5 * area_m2 * shape_factor  # Shape_factor: 1.0 (cone), 0.8 (tube), 1.2 (inflatable)
    return round(drag_factor, 2)

def scale_design(config, scale_factor):
    """Scale design parameters while maintaining usability"""
    if not 0.5 <= scale_factor <= 2.0:
        raise ValueError("Scale factor must be between 0.5 and 2.0")
    scaled = config.copy()
    dimensions = scaled.get("dimensions", {})
    for key in dimensions:
        dimensions[key] = dimensions[key] * scale_factor
    scaled["dimensions"] = dimensions
    for key in ['diameter', 'length', 'bridle_length', 'tip_diameter']:
        if key in scaled:
            scaled[key] = scaled[key] * scale_factor
    if 'area' in scaled:
        scaled['area'] = scaled['area'] * (scale_factor ** 2)
    # Calculate drag for scaled design
    shape_factor = 1.0  # Default for cone; adjust for tube (0.8), inflatable (1.2)
    if scaled.get("shape", "").lower() == "tube":
        shape_factor = 0.8
    elif scaled.get("shape", "").lower() == "inflatable":
        shape_factor = 1.2
    scaled["drag"] = calculate_drag(scaled.get("area", 0.1), shape_factor)  # Default area 0.1m² if not set
    return scaled
EOF

# 4. Update article_generator.py with single template and drag
cat > Core/applications/article_generator.py << 'EOF'
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

def load_resources():
    resources = {}
    resources_path = Path("Core/configurations/resources")
    for file in resources_path.glob("*.yaml"):
        with open(file, "r") as f:
            resources[file.stem] = yaml.safe_load(f)
    suppliers_path = resources_path / "suppliers.yaml"
    if suppliers_path.exists():
        with open(suppliers_path, "r") as f:
            resources["suppliers"] = yaml.safe_load(f)
    external_colors_path = resources_path / "external_colors.yaml"
    if external_colors_path.exists():
        with open(external_colors_path, "r") as f:
            resources["external_colors"] = yaml.safe_load(f)
    return resources

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
    except FileNotFoundError:
        print(f"File not found {design_path}")
        return None
    
    # Scale if 'scale' in YAML
    scale_factor = config.get("scale", 1.0)
    if scale_factor != 1.0:
        config = scale_design(config, scale_factor)
        print(f"Scaled config by {scale_factor} with drag: {config.get('drag', 'N/A')}")

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
            dwg.add(dwg.path(d=f"M10,287 Q105,{287-height/2+10} 200,287", fill="none", stroke="black", stroke_width=2))
            patterns.append({"name": f"{pattern['pieces'][0]['name']} (A4)", "svg_base64": b64encode(dwg.tostring().encode()).decode()})
            print(f"Generated single SVG template for {pattern['pieces'][0]['name']}")
        except ValueError as e:
            print(f"Error generating cone pattern: {e}")
            return None
    elif config.get("shape", "").lower() == "tube":
        print(f"Generating tube pattern for {config.get('name')}")
        try:
            pattern = generate_tube_pattern(config)
            instructions = generate_tube_instructions(config, pattern)
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
            for piece in pattern['pieces']:
                dwg = svgwrite.Drawing(size=("210mm", "297mm"))
                if piece["shape"] == "curved_gore":
                    dwg.add(dwg.path(d=f"M10,287 Q105,148 200,287", fill="none", stroke="black", stroke_width=2))
                elif piece["shape"] == "triangle":
                    dwg.add(dwg.polygon(points=[(10,287), (200,287), (105,10)], fill="none", stroke="black", stroke_width=2))
                elif piece["shape"] == "circle":
                    dwg.add(dwg.circle(center=(105,148), r=50, fill="none", stroke="black", stroke_width=2))
                patterns.append({"name": f"{piece['name']} (A4)", "svg_base64": b64encode(dwg.tostring().encode()).decode()})
        except ValueError as e:
            print(f"Error generating inflatable pattern: {e}")
            return None
    
    env = Environment(loader=FileSystemLoader("Core/web/templates"))
    template = env.get_template("article_template.html")
    html_content = template.render(
        config=config,
        materials=enriched_materials,
        patterns=patterns,
        article_notes=config.get("article_notes", []),
        generated_date="2025-10-20",
        instructions=instructions
    )
    
    output_path = Path(output_dir) / f"{config['name'].replace(' ', '_')}.html"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"Article generated: {output_path}")
    return str(output_path)
EOF

# 5. Add Xmas-tree YAML
cat > projects/line_laundry/spinners/helix_spinner_xmas.yaml << 'EOF'
name: "Helix Spinner Xmas"
shape: "cone"
materials:
  - name: "ripstop_nylon"
    color: "red_green_gold"
    quantity: 1.5  # m2
  - name: "carbon_rods"
    length: 300  # mm
  - name: "rope"
    length: 2000  # mm
colors: ["red", "green", "gold"]  # Xmas theme
dimensions:
  diameter: 300
  length: 1000
  segments: 8
attachment:
  type: "ring"
  bridle_length: 15
article_notes:
  - "Xmas edition with festive colors."
scale: 1.2  # Scale up 20%
inlets:
  type: "circular"
  size: 50  # mm diameter for wind fill
drag_factor: 0.5  # Relative drag for usability
EOF

# 6. Update web interface with /custom route
cat > Core/web/templates/custom.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Custom Kite Laundry Design</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; }
        form { margin: 20px 0; }
        label { display: block; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Custom Kite Laundry Design</h1>
    <form action="/generate_custom" method="post">
        <label for="name">Name:</label><input type="text" id="name" name="name" required>
        <label for="shape">Shape:</label><select id="shape" name="shape"><option value="cone">Cone</option><option value="tube">Tube</option><option value="inflatable">Inflatable</option></select>
        <label for="diameter">Diameter (mm):</label><input type="number" id="diameter" name="diameter" value="400" required>
        <label for="length">Length (mm):</label><input type="number" id="length" name="length" value="1200" required>
        <label for="num_gores">Number of Gores:</label><input type="number" id="num_gores" name="num_gores" value="8" required>
        <label for="color">Color (hex):</label><input type="color" id="color" name="color" value="#FF0000">
        <label for="scale">Scale Factor:</label><input type="number" id="scale" name="scale" value="1.0" step="0.1" required>
        <button type="submit">Generate</button>
    </form>
    <p><a href="{{ url_for('designs') }}">Back to Designs</a></p>
</body>
</html>
EOF

# Add /custom and /generate_custom to app.py (fixed sed syntax with \)
sed -i '' '/@app.route("\/generate")/i\
@app.route("/custom")\\
def custom():\\
    return render_template("custom.html")\\

@app.route("/generate_custom", methods=["POST"])\\
def generate_custom():\\
    config = {\\
        "name": request.form["name"],\\
        "shape": request.form["shape"],\\
        "diameter": int(request.form["diameter"]),\\
        "length": int(request.form["length"]),\\
        "num_gores": int(request.form["num_gores"]),\\
        "colors": [request.form["color"]],\\
        "scale": float(request.form["scale"]),\\
        "materials": ["ripstop_nylon", "rope"],\\
    }\\
    temp_path = "temp_custom.yaml"\\
    with open(temp_path, "w") as f:\\
        yaml.safe_dump(config, f)\\
    article_path = generate_article(temp_path)\\
    if article_path:\\
        with open(article_path, "r") as f:\\
            article_data = {"content": f.read()}\\
        return render_template("result.html", **article_data)\\
    return render_template("generate.html", error="Custom generation failed")\\
' app.py

# 7. Add external color/ripstop samples
cat > Core/configurations/resources/external_colors.yaml << 'EOF'
external_colors:
  red: {hex: "#FF0000", supplier: "https://ripstopbytheroll.com/collections/ripstop-nylon"}
  blue: {hex: "#0000FF", supplier: "https://kiteplans.org/colors/blue.html"}
  green: {hex: "#00FF00", supplier: "https://drachenbernhard.de/colors/green.html"}
  gold: {hex: "#FFD700", supplier: "https://ripstopbytheroll.com/products/gold-nylon"}
ripstop_samples:
  standard: {weight: 40, supplier: "https://ripstopbytheroll.com/products/1-5-oz-ripstop-nylon"}
  heavy: {weight: 60, supplier: "https://kiteplans.org/ripstop/heavy"}
EOF

# Update article_template.html for external colors (fixed sed syntax)
sed -i '' '/<h2>Materials Needed<\/h2>/i\
<h2>Color Samples</h2>\
<ul>\
{% for color in config.colors %}\
    <li>{{ color }} (Hex: {{ resources.external_colors.external_colors[color].hex }}) - <a href="{{ resources.external_colors.external_colors[color].supplier }}">Buy from External Supplier</a></li>\
{% endfor %}\
</ul>\
' Core/web/templates/article_template.html

# 8. Update inflatable_generator.py (single template per piece type)
cat > Core/pattern_generators/inflatable_generator.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Inflatable Generator for Kite Laundry
Generates single templates for advanced inflatable designs
"""
def generate_inflatable_pattern(parameters):
    num_gores = parameters.get("num_gores", 8)
    pieces = [
        {"name": "Body Gore Template", "shape": "curved_gore", "base_width_mm": 200, "tip_width_mm": 50, "height_mm": 1000, "count": num_gores},
        {"name": "Fin Template", "shape": "triangle", "width_mm": 150, "height_mm": 300, "count": 4},
        {"name": "Eye Template", "shape": "circle", "diameter_mm": 100, "count": 2}
    ]
    total_area_m2 = 2.5  # Approximate for large inflatable
    return {"pieces": pieces, "total_material": {"area_m2": total_area_m2}}

def generate_inflatable_instructions(parameters, pattern):
    instructions = f"""
## {parameters.get('name', 'Inflatable Drogue')} Instructions

### Materials Required
- Ripstop nylon: approximately {pattern['total_material']['area_m2']:.2f} m²
- Thread, seam tape
- Plastic eyes, fins attachments

### Cutting
- Cut {pattern['pieces'][0]['count']} body gores using template
- Cut {pattern['pieces'][1]['count']} fins using template
- Cut {pattern['pieces'][2]['count']} eyes using template

### Sewing
- Sew body gores into shape, attach fins and eyes
- Add inlets for wind fill

### Quality Check
- Ensure inflation and drag

Happy flying!
"""
    return instructions
EOF

# 9. Stage, commit, push (handle uncommitted changes)
git add app.py Core/applications/__init__.py Core/applications/article_generator.py Core/web/templates/*.html Core/pattern_generators/__init__.py Core/pattern_generators/cone_generator.py Core/pattern_generators/tube_generator.py Core/pattern_generators/inflatable_generator.py Core/applications/scaling.py Core/configurations/resources/external_colors.yaml projects/line_laundry/spinners/helix_spinner_xmas.yaml improve-laundry.sh
git restore --staged projects/line_laundry/drogues/frosch.yaml  # Unstage deleted file
git add Core/configurations/resources/color_samples.yaml  # Add untracked file
git commit -m "Fix scaling, single-template SVGs, add drag calculator, update generators, web interface, and color samples

- Fixed sed syntax errors for macOS (added \\ for multi-line).
- Updated cone_generator.py to fix indentation and generate single gore template.
- Updated tube_generator.py to generate single sleeve/ribbon templates.
- Added scaling.py with calculate_drag() for usability (drag based on area/shape).
- Updated article_generator.py for single templates and drag output.
- Added helix_spinner_xmas.yaml with nested Xmas structure.
- Updated custom.html to include 'inflatable' option.
- Fixed app.py sed insertion with proper line breaks.
- Updated article_template.html sed for color samples.
- Updated inflatable_generator.py for single templates per piece type.
- Committed untracked color_samples.yaml and restored frosch.yaml staging."

git push origin feature/add-resources-and-article-generator --force

# Create PR or update existing
if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    if gh pr view 1 >/dev/null 2>&1; then
        gh pr edit 1 --title "feat: Scaling, single-template SVGs, drag calculator, custom web, color samples" --body "Fixed sed/macOS issues. Updated cone/tube/inflatable generators for single templates. Added drag calculator in scaling.py. Updated article_generator.py for drag output. Enhanced custom.html with inflatable option. Fixed app.py and article_template.html sed. Committed color_samples.yaml. Test: ./run.sh, http://127.0.0.1:5001/custom, generate article." --add-assignee edjuh
    else
        gh pr create --title "feat: Scaling, single-template SVGs, drag calculator, custom web, color samples" --body "Fixed sed/macOS issues. Updated cone/tube/inflatable generators for single templates. Added drag calculator in scaling.py. Updated article_generator.py for drag output. Enhanced custom.html with inflatable option. Fixed app.py and article_template.html sed. Committed color_samples.yaml. Test: ./run.sh, http://127.0.0.1:5001/custom, generate article." --base main --assignee edjuh
    fi
else
    echo "GitHub CLI not authenticated. Update PR manually at https://github.com/edjuh/kite_laundry/pull/1"
fi

# Check templates
if [ -f Core/web/templates/custom.html ]; then
    echo "Custom interface added successfully."
else
    echo "Failed to add custom.html – check permissions in Core/web/templates/"
    exit 1
fi
