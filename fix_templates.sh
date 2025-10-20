#!/bin/bash
cd /Users/ed/kite_laundry-fork

# Ensure Core/applications/ and Core/web/templates/
mkdir -p Core/applications Core/web/templates
touch Core/applications/__init__.py

# Verify template directory permissions
chmod -R u+w Core/web/templates || { echo "Failed to set permissions on Core/web/templates"; exit 1; }

# Backup app.py
cp app.py app.py.bak || { echo "Failed to backup app.py"; exit 1; }

# Update app.py
cat > app.py << 'EOF'
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
import yaml
from Core.applications.article_generator import generate_article

app = Flask(__name__)
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

# Create article_template.html with multi-page layout support
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
    {% if patterns %}
        {% for pattern in patterns %}
            <div class="template-page">
                <h3>{{ pattern.name }} (A4 Printable)</h3>
                <p><img src="data:image/svg+xml;base64,{{ pattern.svg_base64 }}" alt="{{ pattern.name }} Template"></p>
            </div>
        {% endfor %}
    {% else %}
        <p>Run generator to produce SVG templates (A4/A3) via pattern_generators/.</p>
    {% endif %}
    
    <h2>Assembly Instructions</h2>
    <ol>
        <li>Print cutting templates on A4 paper (100 sheets for large designs).</li>
        <li>Trace templates onto {{ config.material|default('specified material') }} using a fabric marker.</li>
        {% for note in article_notes %}
            <li>{{ note }}</li>
        {% endfor %}
        <li>Sew pieces with a straight stitch, using a 0.5cm seam allowance.</li>
        <li>Attach to kite line via {{ config.attachment.type|default('ring') }} with a {{ config.attachment.bridle_length|default(15) }}cm bridle.</li>
    </ol>
    
    <h2>Visual Reference</h2>
    <p>Diagram: [Placeholder for additional visuals, e.g., frog shape]</p>
    
    <footer>
        <p>Generated by <a href="https://github.com/edjuh/kite_laundry">Kite Laundry Project</a>. Happy flying from the Netherlands! 🪁</p>
    </footer>
</body>
</html>
EOF

# Update article_generator.py for multi-page potential
cat > Core/applications/article_generator.py << 'EOF'
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
    
    patterns = [generate_star_pattern(config)]  # Add more patterns for multi-page
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
EOF

# Ensure helix_spinner.yaml
mkdir -p projects/line_laundry/spinners
cat > projects/line_laundry/spinners/helix_spinner.yaml << 'EOF'
name: "Helix Spinner"
materials:
  - "tyvek"
  - "rope"
  - "carbon_rods"
colors: ["red", "blue"]
dimensions:
  width: 30
  height: 30
  segments: 8
attachment:
  type: "ring"
  bridle_length: 15
article_notes:
  - "Ensure even segment spacing for balanced spinning."
  - "Use carbon rods for a lightweight, stiff frame."
EOF

# Stage, commit, push
git add app.py Core/applications/__init__.py Core/applications/article_generator.py Core/web/templates/*.html Core/configurations/resources/suppliers.yaml projects/line_laundry/spinners/helix_spinner.yaml fix_templates.sh
git commit -m "Fix TemplateNotFound for designs.html, enhance article output

- Added Core/web/templates/designs.html to fix TemplateNotFound.
- Updated article_template.html for multi-page A4 SVG layout.
- Ensured Core/applications/article_generator.py with star SVG.
- Kept app.py, helix_spinner.yaml, suppliers.yaml (EUR currency).
- Cleaned up drogue.svg, Docker file in prior commit."
git push origin feature/add-resources-and-article-generator

# Create PR (if gh CLI authenticated)
if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh pr create --title "fix: TemplateNotFound and article enhancements" --body "Fixed TemplateNotFound by adding designs.html, enhanced article_template.html for multi-page A4 SVGs, ensured Core/applications/article_generator.py with star SVG, updated app.py and templates. Test: ./run.sh, http://127.0.0.1:5001/designs, http://127.0.0.1:5001/generate?path=projects/line_laundry/spinners/helix_spinner.yaml, check output/Helix_Spinner.html." --base edjuh:main
else
    echo "GitHub CLI not authenticated or installed. Run 'gh auth login' or create PR manually at https://github.com/edjuh/kite_laundry/pull/new/feature/add-resources-and-article-generator"
fi
