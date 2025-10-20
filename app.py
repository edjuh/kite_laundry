from flask import Flask, render_template, request
import os
import yaml
from Core.applications.article_generator import generate_production_article
from Core.applications.base import normalize_project_dict

app = Flask(__name__)

@app.route("/")
def index():
    # Count valid designs for display
    designs = []
    project_root = "projects"
    for root, _, files in os.walk(project_root):
        for filename in files:
            if filename.endswith(".yaml"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r") as f:
                        config = yaml.safe_load(f)
                        if config and isinstance(config, dict) and "name" in config:
                            designs.append(normalize_project_dict(config))
                except yaml.YAMLError:
                    continue
    return render_template("index.html", design_count=len(designs))

@app.route("/designs")
def designs():
    designs = []
    project_root = "projects"
    for root, _, files in os.walk(project_root):
        for filename in files:
            if filename.endswith(".yaml"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r") as f:
                        config = yaml.safe_load(f)
                        if config and isinstance(config, dict) and "name" in config:
                            normalized_config = normalize_project_dict(config)
                            designs.append({
                                "name": normalized_config["name"],
                                "complexity": normalized_config.get("complexity", 2),
                                "file_path": file_path
                            })
                except yaml.YAMLError as e:
                    print(f"Error loading {file_path}: {e}")
                    continue
    return render_template("designs.html", designs=designs)

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        try:
            config = yaml.safe_load(request.files["file"])
            if not isinstance(config, dict):
                raise ValueError("Invalid YAML format")
            config = normalize_project_dict(config)
            article_data = generate_production_article(config)
            return render_template("result.html", **article_data)
        except (yaml.YAMLError, ValueError) as e:
            return render_template("generate.html", error=f"Error processing YAML: {str(e)}")
    else:
        design_path = request.args.get("design")
        if design_path:
            try:
                with open(design_path, "r") as f:
                    config = yaml.safe_load(f)
                    if not isinstance(config, dict):
                        raise ValueError("Invalid YAML format")
                    config = normalize_project_dict(config)
                    article_data = generate_production_article(config)
                    return render_template("result.html", **article_data)
                except (yaml.YAMLError, ValueError, FileNotFoundError) as e:
                    return render_template("generate.html", error=f"Error loading design: {str(e)}")
        return render_template("generate.html")

@app.route("/design_form")
def design_form():
    return render_template("design_form.html")

@app.route("/material_calculator")
def material_calculator():
    return render_template("material_calculator.html")

@app.route("/template_generator")
def template_generator():
    return render_template("template_generator.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)