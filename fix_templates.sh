#!/bin/bash
cd /Users/ed/kite_laundry-fork

# Ensure directories
mkdir -p Core/applications Core/web/templates Core/pattern_generators Core/pattern_templates
touch Core/applications/__init__.py
touch Core/pattern_generators/__init__.py
touch Core/pattern_templates/__init__.py

# Fix requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.3
PyYAML==6.0.2
Jinja2==3.1.4
svgwrite==1.4.3
EOF

# Update app.py with template path debugging
cp app.py app.py.bak
cat > app.py << 'EOF'
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
import yaml
from Core.applications.article_generator import generate_article

app = Flask(__name__, template_folder='Core/web/templates')
PROJECTS_DIR = Path("projects")

def get_yaml_designs():
    designs = []
    for yaml_file in PROJECTS_DIR.rglob("*.yaml"):
        try:
            with open(yaml_file, "r") as f:
                config = yaml.safe_load(f)
                if config and isinstance(config, dict) and "name" in config:
                    designs.append({
                        "name": config["name"],
                        "path": str(yaml_file.relative_to(PROJECTS_DIR)),
                        "full_path": str(yaml_file)
                    })
        except yaml.YAMLError as e:
            print(f"YAML error in {yaml_file}: {e}")
        except ValueError as e:
            print(f"Value error in {yaml_file}: {e}")
        except FileNotFoundError as e:
            print(f"File not found {yaml_file}: {e}")
    return designs

@app.route("/")
def home():
    return redirect(url_for("designs"))

@app.route("/designs")
def designs():
    yaml_designs = get_yaml_designs()
    print(f"Template folder: {app.template_folder}")
    print(f"Looking for designs.html in: {Path(app.template_folder) / 'designs.html'}")
    return render_template("designs.html", designs=yaml_designs)

@app.route("/generate")
def generate():
    file_path = request.args.get("path")
    if not file_path:
        return render_template("generate.html", error="No design selected")
    try:
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
        article_path = generate_article(file_path)
        if article_path:
            with open(article_path, "r") as f:
                article_data = {"content": f.read()}
            return render_template("result.html", **article_data)
        return render_template("generate.html", error="Article generation failed")
    except yaml.YAMLError as e:
        return render_template("generate.html", error=f"YAML error in {file_path}: {e}")
    except ValueError as e:
        return render_template("generate.html", error=f"Value error in {file_path}: {e}")
    except FileNotFoundError as e:
        return render_template("generate.html", error=f"File not found {file_path}: {e}")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
EOF

# Update cone_generator.py
cat > Core/pattern_generators/cone_generator.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Cone Pattern Generator for Kite Laundry
Generates cutting patterns and instructions for cone-shaped line laundry
"""
import math

def validate_parameters(parameters):
    """Validate cone input parameters"""
    errors = []
    diameter = parameters.get("diameter", 600)
    if not isinstance(diameter, (int, float)) or diameter < 50 or diameter > 2000:
        errors.append("Diameter must be between 50 and 2000mm")
    length = parameters.get("length", 1000)
    if not isinstance(length, (int, float)) or length < 200 or length > 20000:
        errors.append("Length must be between 200 and 20000mm")
    num_gores = parameters.get("num_gores", 8)
    if not isinstance(num_gores, int) or num_gores < 4 or num_gores > 24:
        errors.append("Number of gores must be between 4 and 24")
    seam_allowance = parameters.get("seam_allowance", 10)
    if not isinstance(seam_allowance, (int, float)) or seam_allowance < 5 or seam_allowance > 30:
        errors.append("Seam allowance must be between 5 and 30mm")
    return errors

def generate_cone_pattern(parameters):
    """Generate a 2D pattern for a cone (drogue) based on parameters"""
    errors = validate_parameters(parameters)
    if errors:
        raise ValueError(f"Invalid parameters: {', '.join(errors)}")
    if parameters is None:
        parameters = {}
    diameter = parameters.get("diameter", 600)
    length = parameters.get("length", 1000)
    num_gores = parameters.get("num_gores", 8)
    seam_allowance = parameters.get("seam_allowance", 10)
    tip_diameter = parameters.get("tip_diameter", 0)
    base_circumference = math.pi * diameter
    tip_circumference = math.pi * tip_diameter if tip_diameter > 0 else 0
    gore_base_width = base_circumference / num_gores
    gore_tip_width = tip_circumference / num_gores if tip_diameter > 0 else 0
    gore_height = length
    gore_base_with_seam = gore_base_width + (2 * seam_allowance)
    gore_tip_with_seam = gore_tip_width + (2 * seam_allowance) if tip_diameter > 0 else seam_allowance
    gore_height_with_seam = gore_height + (2 * seam_allowance)
    avg_width = (gore_base_with_seam + gore_tip_with_seam) / 2
    gore_area_mm2 = avg_width * gore_height_with_seam
    total_area_mm2 = gore_area_mm2 * num_gores
    total_area_cm2 = total_area_mm2 / 100
    total_area_m2 = total_area_cm2 / 10000
    pieces = []
    for i in range(num_gores):
        gore_letter = chr(65 + i)
        gore_piece = {
            "name": gore_letter,
            "description": f"Gore panel {i + 1} of {num_gores}",
            "shape": "trapezoid" if tip_diameter > 0 else "triangle",
            "base_width_mm": round(gore_base_with_seam, 1),
            "tip_width_mm": round(gore_tip_with_seam, 1),
            "height_mm": round(gore_height_with_seam, 1),
            "base_width_cm": round(gore_base_with_seam / 10, 1),
            "tip_width_cm": round(gore_tip_with_seam / 10, 1),
            "height_cm": round(gore_height_with_seam / 10, 1),
            "seam_allowance": seam_allowance,
            "angle_at_base": round(360 / num_gores, 1),
        }
        pieces.append(gore_piece)
    result = {
        "pieces": pieces,
        "gore_count": num_gores,
        "total_material": {
            "area_mm2": round(total_area_mm2, 1),
            "area_cm2": round(total_area_cm2, 1),
            "area_m2": round(total_area_m2, 4),
            "base_circumference_mm": round(base_circumference, 1),
            "base_circumference_cm": round(base_circumference / 10, 1),
            "tip_circumference_mm": round(tip_circumference, 1) if tip_diameter > 0 else 0,
            "cone_length_mm": length,
            "cone_length_cm": round(length / 10, 1),
        },
        "gore_dimensions": {
            "base_width_mm": round(gore_base_width, 1),
            "base_width_cm": round(gore_base_width / 10, 1),
            "tip_width_mm": round(gore_tip_width, 1) if tip_diameter > 0 else 0,
            "height_mm": gore_height,
            "height_cm": round(gore_height / 10, 1),
        },
    }
    return result

def generate_cone_instructions(parameters, pattern):
    """Generate sewing and assembly instructions for the cone"""
    diameter = parameters.get("diameter", 600)
    length = parameters.get("length", 1000)
    num_gores = parameters.get("num_gores", 8)
    seam_allowance = parameters.get("seam_allowance", 10)
    tip_diameter = parameters.get("tip_diameter", 0)
    seam_allowance_cm = seam_allowance / 10
    length_cm = length / 10
    base_circumference = math.pi * diameter
    gore_base_width = base_circumference / num_gores
    gore_base_width_cm = gore_base_width / 10
    gore_tip_width_cm = 0
    if tip_diameter > 0:
        tip_circumference = math.pi * tip_diameter
        gore_tip_width = tip_circumference / num_gores
        gore_tip_width_cm = gore_tip_width / 10
    instructions = f"""
## {parameters.get("name", "Cone Drogue")} Instructions

### Materials Required
- Ripstop nylon: approximately {pattern['total_material']['area_m2']:.2f} m² (add 20% for waste)
- Thread: high-strength polyester, matching colors
- Seam tape or binding (optional for edges)
- Lightweight ring or swivel for attachment (diameter 50-100mm)
- Webbing or cord for bridle (1m, breaking strength 50kg+)
- Sewing machine with walking foot recommended
- Pins, scissors, ruler, marking tool

### Preparation
1. Print this instruction sheet
2. Wash and iron fabric to pre-shrink
3. Plan color layout for gores (alternating colors for visual effect)
4. Prepare work space for large pieces
5. Test stitch on scrap fabric

### Cutting
Cut {num_gores} gore panels from ripstop.
Each gore is a curved triangle/trapezoid:
- Base: {gore_base_width_cm:.1f} cm (+ {seam_allowance_cm} cm seam on sides)
- Height: {length_cm:.1f} cm (+ {seam_allowance_cm} cm seam on top/bottom)
- Tip: {gore_tip_width_cm:.1f} cm if open tip (+ {seam_allowance_cm} cm seam)
- Sides: Curved to form cone when sewn

Note: For pointed tip, the sides converge to a point.

### Sewing Gores
1. Pin two gores right sides together along one curved side
2. Sew with {seam_allowance_cm} cm seam allowance
3. Press seam to one side
4. Topstitch if desired for strength
5. Repeat for all gores, forming a tube
6. Sew the last seam to close the cone

### Finishing Edges
1. Hem the base opening with double fold for strength
2. If open tip, hem the tip opening similarly
3. For pointed tip, reinforce the point with extra stitching

### Attachment
1. Attach ring to base with strong webbing
2. Sew webbing in a loop around the ring
3. Attach bridle cord to ring for kite line connection

### Quality Check
- Check for even gore sizes
- Ensure no pucks or twists
- Test inflation by blowing into base
- Check seams for strength

Happy flying!
"""
    return instructions
EOF

# Update article_generator.py
cat > Core/applications/article_generator.py << 'EOF'
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
    
    patterns = []
    cone_pattern = None
    cone_instructions = ""
    if config.get("shape", "").lower() == "cone":
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
    else:
        patterns = [generate_star_pattern(config)]
    
    env = Environment(loader=FileSystemLoader("Core/web/templates"))
    template = env.get_template("article_template.html")
    
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
EOF

# Create article_template.html
cat > Core/web/templates/article_template.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ config.name }} - Kite Laundry Guide</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1, h2 { color: #4CAF50; }
        ul, ol { line-height: 1.6; }
        a { color: #1E90FF; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .template-page { page-break-after: always; margin-bottom: 20px; }
        img { max-width: 100%; height: auto; }
        .checklist { list-style: square; }
    </style>
</head>
<body>
    <h1>{{ config.name }}</h1>
    <p><strong>Description:</strong> {{ config.description|default('Custom kite laundry design for single-line kites.') }}</p>
    <p><strong>Generated on:</strong> {{ generated_date }}</p>
    
    <h2>Materials Needed</h2>
    <ul>
        {% for mat in materials %}
            <li><strong>{{ mat.name }}</strong> ({{ mat.type }})
                <ul>
                    <li><strong>Properties:</strong> Weight {{ mat.properties.weight }} gsm{% if mat.properties.thickness %}, Thickness {{ mat.properties.thickness }} mm{% endif %}</li>
                    <li><strong>Suppliers:</strong>
                        <ul>
                            {% for sup in mat.suppliers %}
                                <li><a href="{{ sup.url }}">{{ sup.name }}</a> ({{ sup.regions|join(', ') }}) - {{ sup.notes }} (Currency: {{ sup.currency }})</li>
                            {% endfor %}
                        </ul>
                    </li>
                    <li><strong>Build Notes:</strong> {{ mat.article_notes|join(' | ') }}</li>
                </ul>
            </li>
        {% endfor %}
    </ul>
    
    <h2>Cutting Templates</h2>
    <p>Print on A4 paper (multiple sheets for large designs).</p>
    {% if patterns %}
        {% for pattern in patterns %}
            <div class="template-page">
                <h3>{{ pattern.name }}</h3>
                <p><img src="data:image/svg+xml;base64,{{ pattern.svg_base64 }}" alt="{{ pattern.name }} Template"></p>
            </div>
        {% endfor %}
    {% else %}
        <p>Run generator to produce SVG templates (A4/A3) via pattern_generators/.</p>
    {% endif %}
    
    <h2>Assembly Instructions</h2>
    <ol>
        <li>Print cutting templates on A4 paper (multiple sheets for large designs).</li>
        <li>Trace templates onto {{ config.material|default('specified material') }} using a fabric marker.</li>
        {% for note in article_notes %}
            <li>{{ note }}</li>
        {% endfor %}
        <li>Sew pieces with a straight stitch, using a 0.5cm seam allowance.</li>
        <li>Attach to kite line via {{ config.attachment.type|default('ring') }} with a {{ config.attachment.bridle_length|default(15) }}cm bridle.</li>
    </ol>
    
    {% if cone_instructions %}
        {{ cone_instructions | safe }}
    {% endif %}
    
    <h2>Visual Reference</h2>
    <p>Diagram: [Placeholder for additional visuals]</p>
    
    <footer>
        <p>Generated by <a href="https://github.com/edjuh/kite_laundry">Kite Laundry Project</a>. Happy flying from the Netherlands! 🪁</p>
    </footer>
</body>
</html>
EOF

# Create designs.html
cat > Core/web/templates/designs.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Kite Laundry Designs</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #4CAF50; }
        ul { list-style: none; padding: 0; }
        li { margin: 10px 0; }
        a { color: #1E90FF; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Kite Laundry Designs</h1>
    {% if designs %}
        <ul>
            {% for design in designs %}
                <li>
                    <a href="{{ url_for('generate', path=design.full_path) }}">{{ design.name }}</a>
                    ({{ design.path }})
                </li>
            {% endfor %}
        </ul>
    {% else %}
        <p>No designs found in projects/ directory.</p>
    {% endif %}
    <p><a href="https://github.com/edjuh/kite_laundry">Back to Kite Laundry Project</a></p>
</body>
</html>
EOF

# Create generate.html
cat > Core/web/templates/generate.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Generate Kite Laundry</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Generate Kite Laundry</h1>
    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}
    <p>Select a design from <a href="{{ url_for('designs') }}">Designs</a> to generate.</p>
</body>
</html>
EOF

# Create result.html
cat > Core/web/templates/result.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Kite Laundry Article</title>
</head>
<body>
    {{ content | safe }}
</body>
</html>
EOF

# Ensure helix_spinner.yaml
mkdir -p projects/line_laundry/spinners
cat > projects/line_laundry/spinners/helix_spinner.yaml << 'EOF'
name: "Helix Spinner"
shape: "cone"
materials:
  - "tyvek"
  - "rope"
  - "carbon_rods"
colors: ["red", "blue"]
diameter: 300
length: 1000
num_gores: 8
seam_allowance: 10
tip_diameter: 0
attachment:
  type: "ring"
  bridle_length: 15
article_notes:
  - "Ensure even segment spacing for balanced spinning."
  - "Use carbon rods for a lightweight, stiff frame."
EOF

# Verify template permissions and existence
chmod -R u+rw Core/web/templates
ls -l Core/web/templates/designs.html || echo "designs.html not found"
if [ -f Core/web/templates/designs.html ]; then
    echo "designs.html exists at $(realpath Core/web/templates/designs.html)"
else
    echo "Failed to create designs.html – check permissions in Core/web/templates/"
    exit 1
fi

# Debug Flask template path
echo "Checking Flask template path..."
python3 - << 'EOF'
from flask import Flask
app = Flask(__name__, template_folder='Core/web/templates')
print(f"Flask template folder: {app.template_folder}")
print(f"Full path to designs.html: {app.template_folder}/designs.html")
EOF

# Stage all changes
git add app.py Core/applications/__init__.py Core/applications/article_generator.py Core/web/templates/*.html Core/pattern_generators/__init__.py Core/pattern_generators/cone_generator.py Core/configurations/resources/suppliers.yaml projects/line_laundry/spinners/helix_spinner.yaml requirements.txt fix_templates.sh
git status

# Commit changes
git commit -m "Fix TemplateNotFound, ensure designs.html, debug template path

- Ensured designs.html with proper HTML structure.
- Added template_folder='Core/web/templates' and debug logging in app.py.
- Updated helix_spinner.yaml with cone parameters.
- Committed uncommitted changes (__init__.py, article_generator.py).
- Fixed PR base branch to 'main'.
- Added template path verification."

# Push to feature branch
git push origin feature/add-resources-and-article-generator --force

# Create PR
if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh pr create --title "fix: TemplateNotFound, cone integration" --body "Fixed TemplateNotFound by ensuring designs.html with proper HTML structure, setting template_folder='Core/web/templates' in app.py, and adding debug logging. Integrated cone_generator.py for cone shapes with A4 SVGs. Updated helix_spinner.yaml with cone parameters. Committed uncommitted changes. Test: ./run.sh, http://127.0.0.1:5001/designs, http://127.0.0.1:5001/generate?path=projects/line_laundry/spinners/helix_spinner.yaml, check output/Helix_Spinner.html." --base main
else
    echo "GitHub CLI not authenticated. Run 'gh auth login' or create PR manually at https://github.com/edjuh/kite_laundry/pull/new/feature/add-resources-and-article-generator"
fi

# Check templates
if [ -f Core/web/templates/designs.html ]; then
    echo "designs.html created successfully at $(realpath Core/web/templates/designs.html)"
else
    echo "Failed to create designs.html – check permissions in Core/web/templates/"
    exit 1
fi
